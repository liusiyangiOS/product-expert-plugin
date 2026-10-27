#!/usr/bin/env python3
"""交接包离线校验。只读、不派发任务、不授权、不证明外部结果。Python 3.11+。"""
import argparse
import json
import ntpath
from pathlib import Path
import re
import sys

STATUSES = {"draft", "ready", "dispatched", "in_progress", "returned", "accepted", "blocked", "cancelled"}
INTENTS = {"product-to-dev": {"implement", "feasibility"},
           "dev-to-product": {"clarify", "design-review", "acceptance-review"}}
ACTIVE = {"ready", "dispatched", "in_progress", "returned", "accepted"}
SENT = {"dispatched", "in_progress", "returned", "accepted"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def validate(data):
    require(isinstance(data, dict), "交接包必须为对象")
    required = {"schema_version", "request_id", "revision", "parent_request_id", "direction", "intent",
                "status", "coordinator", "return_to", "target", "authorization", "artifacts",
                "acceptance", "open_questions", "dispatch", "result"}
    require(required <= data.keys(), "缺少字段：" + ", ".join(sorted(required - data.keys())))
    require(type(data["schema_version"]) is int and data["schema_version"] == 1, "schema_version 必须是 1")
    request = data["request_id"]
    require(isinstance(request, str) and re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_-]{0,79}", request), "request_id 不是安全短名")
    revision = data["revision"]
    require(type(revision) is int and revision > 0, "revision 必须为正整数")
    parent = data["parent_request_id"]
    require(parent is None or (nonempty(parent) and parent != request), "parent_request_id 不得自指或为空串")
    direction, intent, status = data["direction"], data["intent"], data["status"]
    require(isinstance(direction, str) and direction in INTENTS, "direction 无效")
    require(isinstance(intent, str) and intent in INTENTS[direction], "方向与 intent 不匹配")
    require(isinstance(status, str) and status in STATUSES, "status 无效")
    for key in ("coordinator", "return_to"):
        require(nonempty(data[key]), f"{key} 必须非空")
    target, auth = data["target"], data["authorization"]
    require(isinstance(target, dict) and {"repo", "branch", "baseline", "snapshot"} <= target.keys(), "target 缺少仓库/分支/基线/快照")
    require(all(isinstance(target[k], str) for k in ("repo", "branch", "baseline", "snapshot")), "target 字段必须为字符串")
    require(isinstance(auth, dict) and isinstance(auth.get("scope"), str)
            and auth["scope"] in {"read-only", "implement"} and isinstance(auth.get("evidence"), str), "authorization 无效")
    for key in ("artifacts", "acceptance", "open_questions"):
        require(isinstance(data[key], list), f"{key} 必须为数组")
    for artifact in data["artifacts"]:
        require(isinstance(artifact, dict) and nonempty(artifact.get("ref"))
                and nonempty(artifact.get("version")) and nonempty(artifact.get("kind")), "artifact 需 ref/version/kind")
    seen = set()
    for ac in data["acceptance"]:
        require(isinstance(ac, dict) and nonempty(ac.get("id")) and nonempty(ac.get("criterion")), "验收项需 id/criterion")
        require(ac["id"] not in seen, "验收 ID 重复")
        seen.add(ac["id"])
    for question in data["open_questions"]:
        require(isinstance(question, dict) and nonempty(question.get("question"))
                and type(question.get("blocking")) is bool, "未决项需 question 和布尔 blocking")
    if status in ACTIVE:
        require(nonempty(target["repo"]) and (Path(target["repo"]).is_absolute() or ntpath.isabs(target["repo"])), "就绪请求需绝对仓库/输出路径")
        require(nonempty(target["snapshot"]), "就绪请求需快照")
        require(nonempty(auth["evidence"]), "就绪请求需授权来源，由接收方核实")
        require(bool(data["artifacts"]), "就绪请求需实际输入产物引用")
        if intent == "implement":
            require(not any(q["blocking"] for q in data["open_questions"]), "存在阻断实现的未决项")
            require(auth["scope"] == "implement", "实现请求没有实现授权记录")
            require(bool(data["acceptance"]), "实现请求缺少可观测验收")
            require(nonempty(target["baseline"]) and nonempty(target["branch"]), "实现请求需已确认的基线与分支")
    dispatch = data["dispatch"]
    require(dispatch is None or isinstance(dispatch, dict), "dispatch 必须为对象或 null")
    if status in SENT:
        require(isinstance(dispatch, dict), "已派发状态需真实 dispatch 回执")
    if dispatch is not None:
        require(nonempty(dispatch.get("task_id")) and nonempty(dispatch.get("entrypoint")), "dispatch 需 task_id/entrypoint")
        require(dispatch.get("request_id") == request and type(dispatch.get("revision")) is int
                and dispatch["revision"] == revision, "派发回执与请求版本不匹配")
    result = data["result"]
    require(result is None or isinstance(result, dict), "result 必须为对象或 null")
    if status in {"returned", "accepted"}:
        require(isinstance(result, dict) and isinstance(result.get("artifacts"), list)
                and isinstance(result.get("checks"), list) and nonempty(result.get("summary")), "返回结果需 artifacts/checks/summary")
    if status == "accepted":
        require(nonempty(result.get("accepted_by")) and nonempty(result.get("acceptance_evidence")), "accepted 需接收方和实际验收证据")
    if status == "blocked":
        require(nonempty(data.get("blocked_reason")), "blocked 需 blocked_reason")
    return {"request_id": request, "revision": revision, "status": status, "valid": True,
            "note": "仅结构与就绪条件通过；授权、引用、派发及验收证据仍需接收方核实"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["validate"])
    parser.add_argument("file", type=Path)
    args = parser.parse_args()
    try:
        result = validate(json.loads(args.file.read_text(encoding="utf-8")))
    except (ValueError, OSError) as exc:
        parser.exit(1, f"未通过：{exc}\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
