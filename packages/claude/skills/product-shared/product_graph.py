#!/usr/bin/env python3
"""只读产品追踪图工具；Python 3.11+，不扫描项目、不联网、不调度任务。"""
from __future__ import annotations

import argparse
from collections import deque
import hashlib
import json
import os
from pathlib import Path, PurePosixPath, PureWindowsPath
import re
import stat
import sys


NODE_TYPES = frozenset({"outcome", "opportunity", "hypothesis", "evidence", "experiment",
                        "decision", "solution", "requirement", "design", "acceptance", "metric", "code"})
RELATIONS = frozenset({"supports", "challenges", "motivates", "realized_by", "verified_by",
                       "measured_by", "depends_on"})
BASES = frozenset({"observed", "inferred", "hypothesis"})
TASK_STATUSES = frozenset({"pending", "running", "done", "blocked", "skipped"})
SHA256 = re.compile(r"sha256:[0-9a-fA-F]{64}\Z")
IMPACT_NOTE = "影响是待核验的传播线索；inferred/hypothesis 关系不构成已观察事实。"
READY_NOTE = "ready 仅表示依赖门槛满足，不等于可并行、写入范围无冲突或已获执行授权。"


class GraphArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        self.print_usage(sys.stderr)
        self.exit(1, f"{self.prog}: {message}\n")


def _text(value):
    return isinstance(value, str) and bool(value.strip())


def _strings(value, nonempty=False):
    return isinstance(value, list) and (not nonempty or bool(value)) and all(_text(v) for v in value)


def validate_graph(graph):
    """返回全部可识别的格式问题；不验证图中声明是否符合真实业务。"""
    errors = []
    if not isinstance(graph, dict):
        return ["graph 必须是 JSON object"]
    if type(graph.get("schema_version")) is not int or graph["schema_version"] != 1:
        errors.append("schema_version 必须为整数 1")
    groups = {}
    ids = {}
    for name in ("sources", "nodes", "edges", "tasks"):
        values = graph.get(name)
        if not isinstance(values, list):
            errors.append(f"{name} 必须是 list")
            values = []
        groups[name] = values
        ids[name] = set()
        for index, item in enumerate(values):
            where = f"{name}[{index}]"
            if not isinstance(item, dict):
                errors.append(f"{where} 必须是 object")
                continue
            if name != "edges":
                identifier = item.get("id")
                if not _text(identifier):
                    errors.append(f"{where}.id 必须为非空字符串")
                elif identifier in ids[name]:
                    errors.append(f"{where}.id 重复: {identifier}")
                else:
                    ids[name].add(identifier)

    def references(item, key, allowed, where):
        values = item.get(key)
        if not _strings(values):
            errors.append(f"{where}.{key} 必须为非空字符串组成的 list")
            return []
        for value in values:
            if value not in allowed:
                errors.append(f"{where}.{key} 悬空引用: {value}")
        return values

    for index, source in enumerate(groups["sources"]):
        if not isinstance(source, dict):
            continue
        where = f"sources[{index}]"
        kind = source.get("kind")
        if kind not in ("file", "url"):
            errors.append(f"{where}.kind 必须为 file 或 url")
        for key in ("ref", "version"):
            if not _text(source.get(key)):
                errors.append(f"{where}.{key} 必须为非空字符串")
        if kind == "file" and (not isinstance(source.get("version"), str) or not SHA256.fullmatch(source["version"])):
            errors.append(f"{where}.version 必须为 sha256:<64hex>")
    for index, node in enumerate(groups["nodes"]):
        if not isinstance(node, dict):
            continue
        where = f"nodes[{index}]"
        if not isinstance(node.get("type"), str) or node["type"] not in NODE_TYPES:
            errors.append(f"{where}.type 不受支持")
        for key in ("label", "status"):
            if not _text(node.get(key)):
                errors.append(f"{where}.{key} 必须为非空字符串")
        references(node, "sources", ids["sources"], where)
    for index, edge in enumerate(groups["edges"]):
        if not isinstance(edge, dict):
            continue
        where = f"edges[{index}]"
        for key in ("from", "to"):
            value = edge.get(key)
            if not _text(value) or value not in ids["nodes"]:
                errors.append(f"{where}.{key} 悬空或无效节点引用")
        if not isinstance(edge.get("relation"), str) or edge["relation"] not in RELATIONS:
            errors.append(f"{where}.relation 不受支持")
        if not isinstance(edge.get("basis"), str) or edge["basis"] not in BASES:
            errors.append(f"{where}.basis 不受支持")
        sources = references(edge, "sources", ids["sources"], where)
        if edge.get("basis") == "observed" and not sources:
            errors.append(f"{where} observed 边必须引用至少一个 source")
    task_map = {}
    for index, task in enumerate(groups["tasks"]):
        if not isinstance(task, dict):
            continue
        where = f"tasks[{index}]"
        references(task, "depends_on", ids["tasks"], where)
        if not _text(task.get("owner")):
            errors.append(f"{where}.owner 必须为非空字符串")
        for key in ("write_scope", "acceptance", "evidence"):
            if not _strings(task.get(key)):
                errors.append(f"{where}.{key} 必须为非空字符串组成的 list")
        status = task.get("status")
        if not isinstance(status, str) or status not in TASK_STATUSES:
            errors.append(f"{where}.status 不受支持")
        if "optional" in task and type(task["optional"]) is not bool:
            errors.append(f"{where}.optional 必须为 boolean")
        if "skip_reason" in task and not _text(task["skip_reason"]):
            errors.append(f"{where}.skip_reason 必须为非空字符串")
        if status == "done" and not _strings(task.get("evidence"), nonempty=True):
            errors.append(f"{where} done 必须有非空 evidence")
        if status == "skipped" and (task.get("optional") is not True or not _text(task.get("skip_reason"))):
            errors.append(f"{where} skipped 必须 optional=true 且 skip_reason 非空")
        if _text(task.get("id")) and _strings(task.get("depends_on")):
            task_map[task["id"]] = task
    # Kahn 算法避免深任务链递归溢出；产品关系图不受此 DAG 限制。
    degree = {key: 0 for key in task_map}
    dependents = {key: [] for key in task_map}
    for key, task in task_map.items():
        for dependency in set(task["depends_on"]):
            if dependency in task_map:
                degree[key] += 1
                dependents[dependency].append(key)
    queue = deque(key for key, value in degree.items() if value == 0)
    visited = 0
    while queue:
        key = queue.popleft()
        visited += 1
        for dependent in dependents[key]:
            degree[dependent] -= 1
            if degree[dependent] == 0:
                queue.append(dependent)
    if visited != len(task_map):
        errors.append("tasks.depends_on 存在环，必须为 DAG")
    return errors


def _direction(edge):
    if edge["relation"] == "depends_on":
        return edge["to"], edge["from"]
    return edge["from"], edge["to"]


def impact(graph, node_id):
    """包含起点和传播路径上的所有边；边的 basis 始终保留。"""
    if node_id not in {node["id"] for node in graph["nodes"]}:
        raise ValueError(f"未知 node-id: {node_id}")
    adjacency = {}
    for index, edge in enumerate(graph["edges"]):
        upstream, downstream = _direction(edge)
        adjacency.setdefault(upstream, []).append((index, downstream, edge))
    nodes = [node_id]
    seen = {node_id}
    triggers = []
    queue = deque([node_id])
    while queue:
        upstream = queue.popleft()
        for index, downstream, edge in adjacency.get(upstream, []):
            triggers.append({"edge_index": index, **edge, "propagation_from": upstream,
                             "propagation_to": downstream})
            if downstream not in seen:
                seen.add(downstream)
                nodes.append(downstream)
                queue.append(downstream)
    return {"start": node_id, "nodes": nodes, "triggers": triggers, "note": IMPACT_NOTE}


def ready(graph):
    tasks = {task["id"]: task for task in graph["tasks"]}
    satisfied = {key for key, task in tasks.items() if task["status"] == "done" or (
        task["status"] == "skipped" and task.get("optional") is True and _text(task.get("skip_reason")))}
    dependents = {key: [] for key in tasks}
    for key, task in tasks.items():
        for dependency in task["depends_on"]:
            dependents[dependency].append(key)
    blocked = {key for key, task in tasks.items() if task["status"] == "blocked"}
    queue = deque(blocked)
    while queue:
        for dependent in dependents[queue.popleft()]:
            if dependent not in blocked:
                blocked.add(dependent)
                queue.append(dependent)
    return {"ready": [key for key, task in tasks.items() if task["status"] == "pending"
                      and key not in blocked
                      and all(dependency in satisfied for dependency in task["depends_on"])],
            "note": READY_NOTE}


def _reject_credentials(parts):
    for part in parts:
        name = part.casefold()
        if (name in {".ssh", ".aws", "auth.json", "credentials", "credentials.json"}
                or name == ".env" or name.startswith(".env.")
                or name.endswith((".pem", ".key"))):
            raise ValueError("拒绝读取凭据路径")
    folded = [part.casefold() for part in parts]
    for index, part in enumerate(folded[:-1]):
        if part in {".codex", ".claude"} and folded[index + 1].startswith(("auth", "credentials")):
            raise ValueError("拒绝读取宿主凭据路径")


def _safe_parts(ref):
    if "\\" in ref or PurePosixPath(ref).is_absolute() or PureWindowsPath(ref).drive:
        raise ValueError("只接受 root 内的相对 POSIX 文件路径")
    parts = PurePosixPath(ref).parts
    if not parts or any(part in ("..", ".") for part in parts):
        raise ValueError("拒绝路径穿越或空路径")
    _reject_credentials(parts)
    return parts


def _file_hash(root, ref):
    parts = _safe_parts(ref)
    candidate = root.joinpath(*parts)
    _reject_credentials(candidate.parts)
    # 在打开任何文件前检查路径和别名，拒绝 symlink（即便仍指向 root 内）。
    current = root
    for part in parts:
        current = current / part
        if current.is_symlink():
            raise ValueError("拒绝 symlink 文件或目录")
    if not candidate.resolve().is_relative_to(root):
        raise ValueError("路径超出 root")
    file_fd = None
    directory_fd = None
    try:
        if os.open in os.supports_dir_fd and hasattr(os, "O_NOFOLLOW") and hasattr(os, "O_DIRECTORY"):
            directory_fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY)
            for part in parts[:-1]:
                next_fd = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=directory_fd)
                os.close(directory_fd)
                directory_fd = next_fd
            file_fd = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW | getattr(os, "O_NONBLOCK", 0),
                              dir_fd=directory_fd)
        else:
            file_fd = os.open(candidate, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
                              | getattr(os, "O_NONBLOCK", 0))
        info = os.fstat(file_fd)
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
            raise ValueError("只允许普通文件")
        digest = hashlib.sha256()
        with os.fdopen(file_fd, "rb") as stream:
            file_fd = None
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
        return "sha256:" + digest.hexdigest()
    finally:
        if file_fd is not None:
            os.close(file_fd)
        if directory_fd is not None:
            os.close(directory_fd)


def check_files(graph, root):
    root = Path(root).resolve(strict=True)
    if not root.is_dir():
        raise ValueError("root 必须为项目目录")
    result = {"missing": [], "changed": [], "unsafe": [], "remote_unverified": [],
              "local_verified": [], "impacts": []}
    for source in graph["sources"]:
        record = {"id": source["id"], "ref": source["ref"]}
        category = None
        if source["kind"] == "url":
            category = "remote_unverified"
            record["reason"] = "未联网核验；记录的 version 不证明远端内容新鲜"
        else:
            try:
                actual = _file_hash(root, source["ref"])
                if actual.lower() != source["version"].lower():
                    category = "changed"
                    record.update(expected=source["version"], actual=actual)
                else:
                    result["local_verified"].append(record)
            except FileNotFoundError:
                category = "missing"
            except (OSError, ValueError, RuntimeError):
                category = "unsafe"
                record["reason"] = "路径不安全、不可读或不是普通文件；未输出文件内容"
        if category:
            result[category].append(record)
            seeds = {node["id"] for node in graph["nodes"] if source["id"] in node["sources"]}
            seeds.update(_direction(edge)[1] for edge in graph["edges"] if source["id"] in edge["sources"])
            result["impacts"].append({"source": source["id"], "status": category,
                                      "seeds": sorted(seeds),
                                      "paths": [impact(graph, key) for key in sorted(seeds)]})
    unresolved = any(result[key] for key in ("missing", "changed", "unsafe", "remote_unverified"))
    result["local_fresh"] = bool(result["local_verified"]) and not unresolved
    result["note"] = "只检查明确引用的本地文件；内容哈希相同不证明业务结论正确。" + IMPACT_NOTE
    return result


def main(argv=None):
    parser = GraphArgumentParser(description=__doc__, epilog=(
        "退出码：0=命令完成；1=JSON/schema/参数或执行错误；"
        "2=check-files 存在 changed/missing/unsafe/remote_unverified。所有命令默认只读。"))
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("validate", "impact", "ready", "check-files"):
        command = commands.add_parser(name)
        command.add_argument("graph", type=Path)
        if name == "impact":
            command.add_argument("node_id")
        if name == "check-files":
            command.add_argument("--root", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        graph = json.loads(args.graph.read_text(encoding="utf-8"))
        errors = validate_graph(graph)
        if errors:
            print(json.dumps({"ok": False, "errors": errors}, ensure_ascii=False, indent=2))
            return 1
        if args.command == "validate":
            result = {"ok": True, "schema_version": 1,
                      "note": "仅格式有效；未核验来源新鲜度、业务事实或执行授权。"}
        elif args.command == "impact":
            result = impact(graph, args.node_id)
        elif args.command == "ready":
            result = ready(graph)
        else:
            result = check_files(graph, args.root)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 2 if args.command == "check-files" and any(result[key] for key in (
            "missing", "changed", "unsafe", "remote_unverified")) else 0
    except (ValueError, OSError, UnicodeError, RuntimeError, RecursionError) as exc:
        print(json.dumps({"ok": False, "errors": [str(exc)]}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    sys.exit(main())
