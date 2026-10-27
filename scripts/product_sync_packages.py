#!/usr/bin/env python3
"""从 Codex 角色/技能生成独立 Claude 发行内容；--check 不写文件。"""
import argparse
import json
from pathlib import Path
import sys
import tomllib

ROOT = Path(__file__).resolve().parents[1]


def adapt(text):
    return text.replace("~/.agents/skills", "${CLAUDE_PLUGIN_ROOT}/skills").replace(
        "~/.codex/agents", "${CLAUDE_PLUGIN_ROOT}/agents")


def expected_files():
    source = ROOT / "packages/codex"
    result = {}
    for path in sorted((source / "agents").glob("product-*.toml")):
        data = tomllib.loads(path.read_text(encoding="utf-8"))
        result[f"agents/{path.stem}.md"] = (
            f"---\nname: {data['name']}\ndescription: "
            f"{json.dumps(data['description'], ensure_ascii=False)}\nmodel: inherit\n---\n\n"
            + adapt(data["developer_instructions"].strip()) + "\n"
        ).encode("utf-8")
    for path in sorted((source / "skills").rglob("*")):
        if not path.is_file() or "__pycache__" in path.parts:
            continue
        if path.name == "openai.yaml" or path.name == ".DS_Store":
            continue
        relative = path.relative_to(source).as_posix()
        data = path.read_bytes()
        if path.suffix in {".md", ".json", ".yaml"}:
            data = adapt(data.decode("utf-8")).encode("utf-8")
        result[relative] = data
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    target = ROOT / "packages/claude"
    expected = expected_files()
    actual = {p.relative_to(target).as_posix() for folder in ("agents", "skills")
              for p in (target / folder).rglob("*")
              if p.is_file() and "__pycache__" not in p.parts and p.name != ".DS_Store"}
    extras = actual - expected.keys()
    if extras:
        parser.exit(1, "发现额外 Claude 源文件，先人工处理，不自动删除：" + ", ".join(sorted(extras)) + "\n")
    changed = []
    for name, data in expected.items():
        path = target / name
        if not path.exists() or path.read_bytes() != data:
            changed.append(name)
            if not args.check:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)
    if args.check and changed:
        parser.exit(1, "两端内容未同步：" + ", ".join(changed) + "\n")
    print(f"{'检查' if args.check else '生成'}完成：{len(expected)} 个独立文件，{len(changed)} 处差异。")


if __name__ == "__main__":
    main()
