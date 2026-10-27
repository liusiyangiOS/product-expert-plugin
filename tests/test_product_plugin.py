"""离线发行、安装生命周期与双向交接行为验证；不使用真实个人配置。"""
from argparse import Namespace
import copy
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
ROLES = {"product-team-lead", "product-strategist", "product-researcher", "product-manager",
         "product-ux-designer", "product-ui-designer", "product-tech-analyst", "product-reviewer"}
SKILLS = {"product-expert-team", "product-discovery", "product-project-audit", "product-design",
          "product-dev-bridge", "product-validation"}


def load(path):
    spec = importlib.util.spec_from_file_location("product_test_module", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class DistributionTests(unittest.TestCase):
    def test_exact_names_and_native_role_metadata(self):
        for platform in ("codex", "claude"):
            root = ROOT / "packages" / platform
            self.assertEqual({p.stem for p in (root / "agents").iterdir()}, ROLES)
            self.assertEqual({p.name for p in (root / "skills").iterdir()}, SKILLS | {"product-shared"})
            for path in (root / "agents").iterdir():
                text = path.read_text(encoding="utf-8")
                if platform == "codex":
                    data = tomllib.loads(text)
                    self.assertEqual(data["name"], path.stem)
                    self.assertTrue(data["developer_instructions"].strip())
                    self.assertNotIn("model", data)
                else:
                    self.assertIn(f"name: {path.stem}\n", text)
                    self.assertIn("model: inherit\n", text)
            for skill in SKILLS:
                text = (root / "skills" / skill / "SKILL.md").read_text(encoding="utf-8")
                front = text.split("---", 2)[1]
                self.assertIn(f"name: {skill}\n", front)
                self.assertIn("description:", front)

    def test_local_references_resolve_inside_each_package(self):
        for platform in ("codex", "claude"):
            root = ROOT / "packages" / platform
            for path in root.rglob("*"):
                if path.suffix not in {".md", ".toml"} or path.name == "README.md":
                    continue
                text = path.read_text(encoding="utf-8")
                for link in re.findall(r"\]\(([^)\s]+)\)", text):
                    if ":" not in link and not link.startswith("#"):
                        self.assertTrue((path.parent / link.split("#")[0]).exists(), (path, link))
                for rel in re.findall(r"\$\{CLAUDE_PLUGIN_ROOT\}/([\w./-]+)", text):
                    self.assertTrue((root / rel).exists(), (path, rel))
                for rel in re.findall(r"~/.agents/skills/([\w./-]+)", text):
                    self.assertTrue((root / "skills" / rel).exists(), (path, rel))

    def test_packages_are_independent_normal_files(self):
        identities = set()
        for platform in ("codex", "claude"):
            root = ROOT / "packages" / platform
            for folder in ("agents", "skills"):
                for path in (root / folder).rglob("*"):
                    self.assertFalse(path.is_symlink())
                    if not path.is_file() or "__pycache__" in path.parts:
                        continue
                    info = path.stat()
                    self.assertEqual(info.st_nlink, 1)
                    self.assertNotIn((info.st_dev, info.st_ino), identities)
                    identities.add((info.st_dev, info.st_ino))
                    text = path.read_text(encoding="utf-8")
                    self.assertNotIn("/Users/", text)
                    forbidden = ("~/.claude/", "packages/claude") if platform == "codex" else ("~/.agents/", "~/.codex/", "packages/codex")
                    for token in forbidden:
                        self.assertNotIn(token, text, path)

    def test_generated_claude_matches_source(self):
        process = subprocess.run([sys.executable, str(ROOT / "scripts/product_sync_packages.py"), "--check"],
                                 capture_output=True, text=True)
        self.assertEqual(process.returncode, 0, process.stdout + process.stderr)

    def test_marketplace_targets_claude_with_same_version(self):
        market = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text())
        entry, = market["plugins"]
        self.assertEqual(entry["source"], "./packages/claude")
        package = ROOT / entry["source"]
        plugin = json.loads((package / ".claude-plugin/plugin.json").read_text())
        self.assertEqual(entry["name"], plugin["name"])
        self.assertEqual(market["metadata"]["version"], plugin["version"])
        for platform in ("codex", "claude"):
            self.assertEqual(load(ROOT / "packages" / platform / "install.py").VERSION,
                             plugin["version"])


class InstallerBehavior:
    platform = None

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="产品插件 install ")
        self.home = Path(self.tmp.name).resolve()
        self.module = load(ROOT / "packages" / self.platform / "install.py")
        self.args = Namespace(home=self.home, explicit_home=True, command="install", dry_run=False, replace=False)
        self.config = ".codex" if self.platform == "codex" else ".claude"
        self.skillroot = ".agents/skills" if self.platform == "codex" else ".claude/skills"
        self.state = self.home / self.config / "product-expert-team/install-manifest.json"
        self.sample = self.home / self.skillroot / "product-design/SKILL.md"

    def tearDown(self):
        self.tmp.cleanup()

    def run_installer(self, command="install", **kwargs):
        args = copy.copy(self.args)
        args.command = command
        for key, value in kwargs.items():
            setattr(args, key, value)
        self.module.run(args)

    def test_lifecycle_preserves_dev_and_user_files(self):
        sentinels = [".codex/agents/dev-developer.toml", ".agents/skills/dev-shared/keep.md",
                     ".codex/expert-team/install-manifest.json", ".claude/agents/dev-developer.md",
                     ".claude/skills/dev-shared/keep.md", ".claude/expert-team/install-manifest.json",
                     ".codex/config.toml", ".claude/settings.json"]
        for name in sentinels:
            path = self.home / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("original", encoding="utf-8")
        self.run_installer(dry_run=True)
        self.assertFalse(self.sample.exists())
        self.run_installer()
        self.run_installer("check")
        before = self.sample.read_bytes()
        self.run_installer()
        self.assertEqual(before, self.sample.read_bytes())
        self.run_installer("uninstall")
        self.assertFalse(self.sample.exists())
        self.assertFalse(self.state.exists())
        for name in sentinels:
            self.assertEqual((self.home / name).read_text(), "original")

    def test_conflicts_preflight_and_replace_backs_up(self):
        self.sample.parent.mkdir(parents=True)
        self.sample.write_text("custom", encoding="utf-8")
        with self.assertRaises(ValueError):
            self.run_installer()
        self.assertFalse(self.state.exists())
        self.assertFalse((self.home / self.config / "agents").exists())
        self.run_installer(replace=True)
        backups = list((self.home / self.config / "product-expert-team/backups").rglob("SKILL.md"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_text(), "custom")
        self.sample.write_text("changed", encoding="utf-8")
        for command in ("check", "install", "uninstall"):
            with self.assertRaises(ValueError):
                self.run_installer(command)
        self.assertEqual(self.sample.read_text(), "changed")

    def test_foreign_and_traversal_manifests_rejected(self):
        self.run_installer()
        original = json.loads(self.state.read_text())
        cases = []
        wrong = copy.deepcopy(original)
        wrong["package"] = "dev-expert-codex"
        cases.append(wrong)
        for key in ("../outside", ".codex/config.toml", "C:/outside", ".agents/skills/product-shared/../../outside"):
            wrong = copy.deepcopy(original)
            wrong["files"][key] = "a" * 64
            cases.append(wrong)
        for wrong in cases:
            self.state.write_text(json.dumps(wrong), encoding="utf-8")
            with self.assertRaises(ValueError):
                self.run_installer("uninstall", replace=True)
            self.assertTrue(self.sample.exists())

    def test_symlink_and_hardlink_targets_rejected(self):
        outside = self.home / "outside"
        outside.write_text("outside", encoding="utf-8")
        self.sample.parent.mkdir(parents=True)
        try:
            self.sample.symlink_to(outside)
        except OSError as exc:
            if os.name == "nt" and getattr(exc, "winerror", None) == 1314:
                self.skipTest("宿主没有创建 symlink 权限")
            raise
        with self.assertRaises(ValueError):
            self.run_installer(replace=True)
        self.sample.unlink()
        os.link(outside, self.sample)
        with self.assertRaises(ValueError):
            self.run_installer(replace=True)
        self.assertEqual(outside.read_text(), "outside")

    def test_failed_write_rolls_back(self):
        original_write = self.module.atomic_write
        count = 0

        def fail_once(path, data):
            nonlocal count
            count += 1
            if count == 3:
                raise OSError("simulated write failure")
            original_write(path, data)

        with patch.object(self.module, "atomic_write", fail_once):
            with self.assertRaises(OSError):
                self.run_installer()
        self.assertFalse(self.state.exists())
        self.assertFalse(any(p.is_file() for p in self.home.rglob("*")))

    def test_personal_resources_resolve(self):
        self.run_installer()
        for path in self.home.rglob("*.md"):
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("${CLAUDE_PLUGIN_ROOT}", text)
            for rel in re.findall(r"~/([\w./-]+)", text):
                self.assertTrue((self.home / rel).exists(), (path, rel))

    def old_payload(self):
        """模拟已受管旧版：没有新增资源，现有技能还是旧正文。"""
        desired = self.module.payload()
        new_names = {"product-methods.md", "product-graph.md", "product_graph.py",
                     "product-graph.json", "product-experiment.md", "product-decision.md"}
        old = {name: data for name, data in desired.items() if Path(name).name not in new_names}
        old[f"{self.skillroot}/product-design/SKILL.md"] = b"previous managed skill version\n"
        return old

    def test_upgrade_old_managed_payload_adds_graph_and_preserves_backup(self):
        old = self.old_payload()
        with patch.object(self.module, "payload", return_value=old), patch.object(self.module, "VERSION", "1.0.0"):
            self.run_installer()
        self.assertFalse((self.home / self.skillroot / "product-shared/product_graph.py").exists())
        self.run_installer()
        self.run_installer("check")
        current = json.loads(self.state.read_text())
        self.assertEqual(current["version"], self.module.VERSION)
        self.assertEqual(self.sample.read_bytes(), self.module.payload()[f"{self.skillroot}/product-design/SKILL.md"])
        self.assertTrue((self.home / self.skillroot / "product-shared/product_graph.py").exists())
        backups = list((self.home / self.config / "product-expert-team/backups").rglob("SKILL.md"))
        self.assertTrue(any(p.read_bytes() == b"previous managed skill version\n" for p in backups))

    def test_upgrade_rejects_modified_old_file_before_any_new_write(self):
        old = self.old_payload()
        with patch.object(self.module, "payload", return_value=old):
            self.run_installer()
        self.sample.write_text("user customization", encoding="utf-8")
        before = self.state.read_bytes()
        with self.assertRaises(ValueError):
            self.run_installer()
        self.assertEqual(self.state.read_bytes(), before)
        self.assertEqual(self.sample.read_text(), "user customization")
        self.assertFalse((self.home / self.skillroot / "product-shared/product_graph.py").exists())

    def test_missing_graph_resource_refuses_distribution(self):
        package = self.home / "source package"
        shutil.copytree(self.module.PACKAGE, package, ignore=shutil.ignore_patterns("__pycache__"))
        (package / "skills/product-shared/templates/product-graph.json").unlink()
        with patch.object(self.module, "PACKAGE", package):
            with self.assertRaises(ValueError):
                self.run_installer()
        self.assertFalse(self.state.exists())

    def test_installed_graph_cli_uses_own_package(self):
        self.run_installer()
        shared = self.home / self.skillroot / "product-shared"
        result = subprocess.run([sys.executable, str(shared / "product_graph.py"), "validate",
                                 str(shared / "templates/product-graph.json")],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


class CodexInstallTests(InstallerBehavior, unittest.TestCase):
    platform = "codex"


class ClaudeInstallTests(InstallerBehavior, unittest.TestCase):
    platform = "claude"


class BridgeTests(unittest.TestCase):
    def setUp(self):
        shared = ROOT / "packages/codex/skills/product-shared"
        self.module = load(shared / "product_bridge.py")
        self.draft = json.loads((shared / "templates/product-handoff.json").read_text())

    def ready(self):
        data = copy.deepcopy(self.draft)
        data.update(status="ready", target={"repo": str(ROOT), "branch": "feature/1027/example",
                                            "baseline": "main@baseline-sha", "snapshot": "snapshot-reference"},
                    authorization={"scope": "implement", "evidence": "用户要求直接实现此需求"},
                    artifacts=[{"kind": "requirement", "ref": "docs/product/requirement.md", "version": "sha256:example"}],
                    acceptance=[{"id": "AC-1", "criterion": "用户取消操作时数据保持不变"}])
        return data

    def test_template_is_only_draft(self):
        self.assertEqual(self.module.validate(self.draft)["status"], "draft")
        self.draft["status"] = "ready"
        with self.assertRaises(ValueError):
            self.module.validate(self.draft)

    def test_implement_ready_and_authorization_boundary(self):
        data = self.ready()
        self.assertTrue(self.module.validate(data)["valid"])
        data["authorization"]["scope"] = "read-only"
        with self.assertRaises(ValueError):
            self.module.validate(data)

    def test_missing_acceptance_and_blocking_questions(self):
        data = self.ready()
        data["acceptance"] = []
        with self.assertRaises(ValueError):
            self.module.validate(data)
        data = self.ready()
        data["open_questions"] = [{"question": "删除后可恢复多久？", "blocking": True}]
        with self.assertRaises(ValueError):
            self.module.validate(data)
        data["open_questions"][0]["blocking"] = False
        self.assertTrue(self.module.validate(data)["valid"])

    def test_reverse_consultation_needs_no_implementation_authorization(self):
        data = self.ready()
        data.update(request_id="clarify-1", parent_request_id=self.draft["request_id"],
                    direction="dev-to-product", intent="clarify")
        data["authorization"] = {"scope": "read-only", "evidence": "开发主理人请求业务澄清"}
        data["target"]["branch"] = ""
        data["acceptance"] = []
        data["open_questions"] = [{"question": "删除后可恢复多久？", "blocking": True}]
        self.assertTrue(self.module.validate(data)["valid"])
        data["intent"] = "implement"
        with self.assertRaises(ValueError):
            self.module.validate(data)

    def test_feasibility_can_receive_the_blocker_it_needs_to_investigate(self):
        data = self.ready()
        data.update(intent="feasibility")
        data["authorization"] = {"scope": "read-only", "evidence": "用户要求先分析能力边界"}
        data["open_questions"] = [{"question": "离线模式能否支持核心路径？", "blocking": True}]
        self.assertTrue(self.module.validate(data)["valid"])

    def test_dispatch_receipt_must_match_request_revision(self):
        data = self.ready()
        data["status"] = "dispatched"
        with self.assertRaises(ValueError):
            self.module.validate(data)
        data["dispatch"] = {"task_id": "session/stage-1", "entrypoint": "dev-expert-team-review",
                            "request_id": data["request_id"], "revision": 1}
        self.assertTrue(self.module.validate(data)["valid"])
        data["revision"] = 2
        with self.assertRaises(ValueError):
            self.module.validate(data)

    def test_acceptance_requires_receiver_evidence(self):
        data = self.ready()
        data.update(status="accepted", dispatch={"task_id": "session/stage-1", "entrypoint": "dev-expert-team-review",
                                                 "request_id": data["request_id"], "revision": 1},
                    result={"artifacts": [], "checks": [], "summary": "开发返回"})
        with self.assertRaises(ValueError):
            self.module.validate(data)
        data["result"].update(accepted_by="product-reviewer", acceptance_evidence="验收报告引用")
        self.assertTrue(self.module.validate(data)["valid"])

    def test_reject_malformed_types_without_crashing(self):
        for key in ("schema_version", "request_id", "revision", "direction", "intent", "status", "target", "authorization", "artifacts"):
            data = self.ready()
            data[key] = []
            with self.subTest(key=key), self.assertRaises(ValueError):
                self.module.validate(data)

    def test_blocked_request_needs_reason(self):
        data = self.ready()
        data["status"] = "blocked"
        with self.assertRaises(ValueError):
            self.module.validate(data)
        data["blocked_reason"] = "开发插件未加载"
        self.assertTrue(self.module.validate(data)["valid"])


if __name__ == "__main__":
    unittest.main()
