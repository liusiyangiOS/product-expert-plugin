"""产品 graph 的格式、解释边界、任务依赖与只读文件核验行为。"""
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "packages/codex/skills/product-shared/product_graph.py"
TEMPLATE = SCRIPT.parent / "templates/product-graph.json"
spec = importlib.util.spec_from_file_location("product_graph", SCRIPT)
graph_tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(graph_tool)


def source(identifier="source", ref="input.txt", content=b"original"):
    return {"id": identifier, "kind": "file", "ref": ref,
            "version": "sha256:" + hashlib.sha256(content).hexdigest()}


def node(identifier, sources=None, kind="requirement"):
    return {"id": identifier, "type": kind, "label": "测试节点 " + identifier,
            "sources": sources or [], "status": "draft"}


def edge(upstream, downstream, relation="supports", basis="inferred", sources=None):
    return {"from": upstream, "to": downstream, "relation": relation,
            "basis": basis, "sources": sources or []}


def task(identifier, dependencies=None, status="pending", **kwargs):
    return {"id": identifier, "depends_on": dependencies or [], "owner": "测试负责人",
            "write_scope": [], "status": status, "acceptance": [], "evidence": [], **kwargs}


def graph():
    return {"schema_version": 1, "sources": [source()],
            "nodes": [node("a", ["source"]), node("b"), node("c"), node("d")],
            "edges": [edge("a", "b"), edge("b", "c", basis="hypothesis"),
                      edge("d", "c", relation="depends_on")], "tasks": []}


class SchemaTests(unittest.TestCase):
    def assert_invalid(self, value, text):
        errors = graph_tool.validate_graph(value)
        self.assertTrue(errors)
        self.assertIn(text, "\n".join(errors))

    def test_template_is_valid_and_explicitly_synthetic(self):
        value = json.loads(TEMPLATE.read_text(encoding="utf-8"))
        self.assertEqual(graph_tool.validate_graph(value), [])
        self.assertIn("完全合成", value["description"])
        self.assertTrue(all(s["kind"] == "url" and ".invalid/" in s["ref"] for s in value["sources"]))
        self.assertTrue(all(e["basis"] != "observed" for e in value["edges"]))
        self.assertIn("solution", {n["type"] for n in value["nodes"]})

    def test_dangling_node_source_and_task_references(self):
        for target in ("node", "edge", "node-source", "edge-source", "task"):
            with self.subTest(target=target):
                value = graph()
                if target == "node":
                    value["edges"][0]["from"] = "unknown"
                elif target == "edge":
                    value["edges"][0]["to"] = "unknown"
                elif target == "node-source":
                    value["nodes"][0]["sources"] = ["unknown-evidence"]
                elif target == "edge-source":
                    value["edges"][0]["sources"] = ["unknown-evidence"]
                else:
                    value["tasks"] = [task("x", ["unknown"])]
                self.assert_invalid(value, "悬空")

    def test_duplicate_identifiers_in_each_namespace(self):
        for group in ("sources", "nodes", "tasks"):
            with self.subTest(group=group):
                value = graph()
                if group == "tasks":
                    value[group] = [task("x")]
                value[group].append(copy.deepcopy(value[group][0]))
                self.assert_invalid(value, "重复")

    def test_types_versions_and_malformed_structures(self):
        cases = [("schema_version", True), ("nodes", {}), ("edges", [None]), ("tasks", "wrong")]
        for key, bad in cases:
            value = graph()
            value[key] = bad
            self.assertTrue(graph_tool.validate_graph(value))
        self.assertTrue(graph_tool.validate_graph([]))
        for group, key, bad in (("sources", "kind", []), ("sources", "version", "git:abcd"),
                                ("nodes", "type", []), ("nodes", "status", " "),
                                ("edges", "basis", []), ("edges", "relation", "unknown")):
            value = graph()
            value[group][0][key] = bad
            self.assertTrue(graph_tool.validate_graph(value))

    def test_observed_requires_known_evidence_and_inferred_remains_inferred(self):
        value = graph()
        value["edges"][0]["basis"] = "observed"
        self.assert_invalid(value, "observed")
        value["edges"][0]["sources"] = ["unknown"]
        self.assert_invalid(value, "悬空")
        value["edges"][0]["sources"] = ["source"]
        self.assertEqual(graph_tool.validate_graph(value), [])
        result = graph_tool.impact(value, "a")
        self.assertEqual([trigger["basis"] for trigger in result["triggers"]],
                         ["observed", "hypothesis", "inferred"])
        self.assertIn("不构成已观察事实", result["note"])

    def test_product_cycle_allowed_task_cycle_rejected(self):
        value = graph()
        value["edges"].append(edge("d", "a"))
        self.assertEqual(graph_tool.validate_graph(value), [])
        result = graph_tool.impact(value, "a")
        self.assertEqual(result["nodes"], ["a", "b", "c", "d"])
        self.assertEqual(len(result["triggers"]), 4)
        for tasks in ([task("x", ["x"])], [task("x", ["y"]), task("y", ["x"])]):
            value["tasks"] = tasks
            self.assert_invalid(value, "存在环")

    def test_long_task_dag_does_not_recurse(self):
        value = graph()
        value["tasks"] = [task(str(index), [str(index - 1)] if index else []) for index in range(1600)]
        self.assertEqual(graph_tool.validate_graph(value), [])
        self.assertEqual(graph_tool.ready(value)["ready"], ["0"])

    def test_completion_and_skip_gates(self):
        for bad in (task("x", status="done"), task("x", status="done", evidence=[""]),
                    task("x", status="skipped", skip_reason="无需执行"),
                    task("x", status="skipped", optional=True),
                    task("x", status="skipped", optional="true", skip_reason="无需执行")):
            value = graph()
            value["tasks"] = [bad]
            self.assertTrue(graph_tool.validate_graph(value))
        value = graph()
        value["tasks"] = [task("done", status="done", evidence=["人工验收记录"]),
                          task("skip", status="skipped", optional=True, skip_reason="范围外"),
                          task("ready", ["done", "skip"])]
        self.assertEqual(graph_tool.validate_graph(value), [])
        self.assertEqual(graph_tool.ready(value)["ready"], ["ready"])


class PropagationTests(unittest.TestCase):
    def test_multihop_and_reversed_depends_on_explain_each_trigger(self):
        value = graph()
        result = graph_tool.impact(value, "a")
        self.assertEqual(result["nodes"], ["a", "b", "c", "d"])
        self.assertEqual(result["triggers"][-1]["from"], "d")
        self.assertEqual(result["triggers"][-1]["propagation_from"], "c")
        self.assertEqual(result["triggers"][-1]["propagation_to"], "d")
        self.assertEqual(graph_tool.impact(value, "d")["nodes"], ["d"])
        with self.assertRaises(ValueError):
            graph_tool.impact(value, "unknown")

    def test_blocked_running_and_pending_dependencies_never_unlock_followups(self):
        value = graph()
        for status in ("blocked", "running", "pending"):
            with self.subTest(status=status):
                value["tasks"] = [task("root", status=status), task("child", ["root"]),
                                  task("grandchild", ["child"]), task("independent")]
                ready = graph_tool.ready(value)
                self.assertNotIn("child", ready["ready"])
                self.assertNotIn("grandchild", ready["ready"])
                self.assertIn("independent", ready["ready"])
                self.assertIn("不等于可并行", ready["note"])
        # 即使中间节点被不一致地标记为 done，blocked 的传递后继仍须重新核验。
        value["tasks"] = [task("root", status="blocked"),
                          task("child", ["root"], status="done", evidence=["旧验收记录"]),
                          task("grandchild", ["child"])]
        self.assertEqual(graph_tool.ready(value)["ready"], [])
        value["tasks"] = []
        self.assertEqual(graph_tool.ready(value)["ready"], [])


class FileCheckTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="产品 graph ")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.input = self.root / "input.txt"
        self.input.write_bytes(b"original")
        self.value = graph()

    def test_hash_changed_missing_and_affected_multihop_nodes(self):
        result = graph_tool.check_files(self.value, self.root)
        self.assertTrue(result["local_fresh"])
        self.assertEqual(result["local_verified"][0]["id"], "source")
        self.input.write_bytes(b"changed")
        result = graph_tool.check_files(self.value, self.root)
        self.assertFalse(result["local_fresh"])
        self.assertEqual(result["changed"][0]["actual"], "sha256:" + hashlib.sha256(b"changed").hexdigest())
        self.assertEqual(result["impacts"][0]["paths"][0]["nodes"], ["a", "b", "c", "d"])
        self.input.unlink()
        self.assertEqual(graph_tool.check_files(self.value, self.root)["missing"][0]["id"], "source")

    def test_source_on_edge_invalidates_its_downstream_in_impact_direction(self):
        self.value["nodes"][0]["sources"] = []
        self.value["edges"][-1]["sources"] = ["source"]
        self.input.unlink()
        result = graph_tool.check_files(self.value, self.root)
        self.assertEqual(result["impacts"][0]["seeds"], ["d"])

    def test_binary_content_hashed_without_printing_and_input_unchanged(self):
        data = b"\x00\xffsecret-content\n"
        self.input.write_bytes(data)
        self.value["sources"] = [source(content=data)]
        before = copy.deepcopy(self.value)
        result = graph_tool.check_files(self.value, self.root)
        self.assertTrue(result["local_fresh"])
        self.assertNotIn("secret-content", json.dumps(result))
        self.assertEqual(self.value, before)
        self.assertEqual(self.input.read_bytes(), data)

    def assert_unsafe(self, ref):
        self.value["sources"][0]["ref"] = ref
        result = graph_tool.check_files(self.value, self.root)
        self.assertEqual(len(result["unsafe"]), 1, (ref, result))
        self.assertFalse(result["local_fresh"])
        self.assertFalse(result["local_verified"])

    def test_traversal_absolute_and_windows_paths_are_rejected(self):
        for ref in ("../input.txt", "a/../../input.txt", str(self.input), "C:/input.txt",
                    "C:input.txt", "\\\\host\\share\\input.txt", "a\\..\\input.txt"):
            with self.subTest(ref=ref):
                self.assert_unsafe(ref)

    def test_credentials_paths_rejected_before_read(self):
        for ref in (".env", ".env.local", "nested/auth.json", "id.pem", "id.key", ".ssh/id_rsa",
                    ".aws/config", ".codex/auth.json", ".codex/auth/token", ".codex/credentials-v2",
                    "nested/credentials.json", "nested/.ENV.production"):
            with self.subTest(ref=ref), patch.object(graph_tool.os, "open", side_effect=AssertionError("must not open")):
                self.assert_unsafe(ref)

    def test_root_itself_cannot_bypass_credentials_path_filter(self):
        folder = self.root / ".aws"
        folder.mkdir()
        self.value["sources"][0]["ref"] = "config"
        with patch.object(graph_tool.os, "open", side_effect=AssertionError("must not open")):
            result = graph_tool.check_files(self.value, folder)
        self.assertEqual(len(result["unsafe"]), 1)

    def test_symlink_file_and_parent_directory_escape_rejected(self):
        outside = self.root.parent / (self.root.name + "-outside")
        outside.mkdir()
        self.addCleanup(outside.rmdir)
        outside_file = outside / "private.txt"
        outside_file.write_bytes(b"private")
        self.addCleanup(outside_file.unlink)
        try:
            (self.root / "link").symlink_to(outside_file)
            (self.root / "directory").symlink_to(outside, target_is_directory=True)
            (self.root / "inside-link").symlink_to(self.input)
            (self.root / "broken").symlink_to(outside / "missing")
        except OSError as exc:
            if os.name == "nt" and getattr(exc, "winerror", None) == 1314:
                self.skipTest("宿主没有创建 symlink 权限")
            raise
        for ref in ("link", "directory/private.txt", "inside-link", "broken"):
            with self.subTest(ref=ref):
                self.assert_unsafe(ref)

    def test_hardlink_alias_and_directory_are_rejected(self):
        os.link(self.input, self.root / "alias")
        self.assert_unsafe("alias")
        (self.root / "folder").mkdir()
        self.assert_unsafe("folder")

    def test_remote_unverified_without_network_and_empty_sources_not_fresh(self):
        self.value["sources"] = [{"id": "source", "kind": "url", "ref": "https://example.invalid/data",
                                  "version": "snapshot-v1"}]
        with patch.object(graph_tool.os, "open", side_effect=AssertionError("remote must not open")):
            result = graph_tool.check_files(self.value, self.root)
        self.assertEqual(len(result["remote_unverified"]), 1)
        self.assertFalse(result["local_fresh"])
        self.value["sources"] = []
        self.value["nodes"][0]["sources"] = []
        self.assertFalse(graph_tool.check_files(self.value, self.root)["local_fresh"])


class CliTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="产品 graph CLI ")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.graph_path = self.root / "graph.json"
        self.graph_path.write_text(json.dumps(graph()), encoding="utf-8")

    def run_cli(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), *map(str, args)],
                              capture_output=True, text=True, timeout=10)

    def test_cli_validation_impact_ready_and_no_mutation(self):
        before = self.graph_path.read_bytes()
        for args in (("validate", self.graph_path), ("impact", self.graph_path, "a"), ("ready", self.graph_path)):
            result = self.run_cli(*args)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIsInstance(json.loads(result.stdout), dict)
        self.assertEqual(self.graph_path.read_bytes(), before)

    def test_exit_codes_distinguish_invalid_and_unverified(self):
        result = self.run_cli("check-files", self.graph_path, "--root", self.root)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertTrue(json.loads(result.stdout)["missing"])
        (self.root / "input.txt").write_bytes(b"original")
        self.assertEqual(self.run_cli("check-files", self.graph_path, "--root", self.root).returncode, 0)
        result = self.run_cli("check-files", TEMPLATE, "--root", self.root)
        self.assertEqual(result.returncode, 2)
        self.assertTrue(json.loads(result.stdout)["remote_unverified"])
        value = graph()
        value["nodes"][0]["sources"] = ["unknown"]
        self.graph_path.write_text(json.dumps(value), encoding="utf-8")
        self.assertEqual(self.run_cli("validate", self.graph_path).returncode, 1)

    def test_malformed_json_and_unknown_node_fail_without_traceback(self):
        result = self.run_cli("impact", self.graph_path, "unknown")
        self.assertEqual(result.returncode, 1)
        self.assertNotIn("Traceback", result.stdout + result.stderr)
        for content in ("{bad", "[]", "{\"schema_version\": true}"):
            self.graph_path.write_text(content, encoding="utf-8")
            result = self.run_cli("validate", self.graph_path)
            self.assertEqual(result.returncode, 1)
            self.assertFalse(json.loads(result.stdout)["ok"])
            self.assertNotIn("Traceback", result.stdout + result.stderr)

    def test_help_describes_exit_codes_and_readonly(self):
        result = self.run_cli("--help")
        self.assertEqual(result.returncode, 0)
        self.assertIn("退出码", result.stdout)
        self.assertIn("remote_unverified", result.stdout)
        self.assertIn("只读", result.stdout)

    def test_argument_errors_use_one_instead_of_unverified_code(self):
        for args in ((), ("unknown",), ("check-files", self.graph_path),
                     ("impact", self.graph_path)):
            with self.subTest(args=args):
                result = self.run_cli(*args)
                self.assertEqual(result.returncode, 1)
                self.assertNotIn("Traceback", result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
