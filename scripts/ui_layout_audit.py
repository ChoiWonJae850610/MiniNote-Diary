from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

TARGET_PATTERNS = (
    "ui/pages/*.py",
    "ui/postit/*.py",
    "ui/postit/layouting/*.py",
    "ui/main_window_parts/*.py",
    "ui/theme_tokens.py",
    "ui/layout_metrics.py",
    "ui/ui_metrics.py",
)

NUMERIC_NAME_HINTS = (
    "height",
    "width",
    "margin",
    "padding",
    "spacing",
    "gap",
    "offset",
    "overlap",
    "radius",
    "stretch",
    "reserve",
    "adjust",
    "size",
    "top",
    "bottom",
    "left",
    "right",
)

CALL_NAME_HINTS = (
    "setFixedHeight",
    "setFixedWidth",
    "setMinimumHeight",
    "setMinimumWidth",
    "setMaximumHeight",
    "setMaximumWidth",
    "setContentsMargins",
    "setSpacing",
    "addSpacing",
    "move",
    "resize",
)

EXCLUDED_VALUES = {0, 1, -1}


@dataclass(frozen=True)
class Finding:
    path: str
    line: int
    kind: str
    detail: str


def _iter_target_files(root: Path) -> Iterable[Path]:
    seen: set[Path] = set()
    for pattern in TARGET_PATTERNS:
        for path in root.glob(pattern):
            if path.is_file() and path not in seen:
                seen.add(path)
                yield path


def _literal_value(node: ast.AST):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub) and isinstance(node.operand, ast.Constant):
        if isinstance(node.operand.value, (int, float)):
            return -node.operand.value
    return None


def _name_text(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return ""


def _looks_like_layout_name(name: str) -> bool:
    lowered = name.lower()
    return any(hint in lowered for hint in NUMERIC_NAME_HINTS)


def _call_name(node: ast.Call) -> str:
    if isinstance(node.func, ast.Attribute):
        return node.func.attr
    if isinstance(node.func, ast.Name):
        return node.func.id
    return ""


def _scan_assignments(tree: ast.AST, path: Path) -> list[Finding]:
    findings: list[Finding] = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        targets = []
        if isinstance(node, ast.Assign):
            targets = node.targets
            value_node = node.value
        else:
            targets = [node.target]
            value_node = node.value
        value = _literal_value(value_node)
        if value is None or value in EXCLUDED_VALUES:
            continue
        target_names = [name for t in targets if (name := _name_text(t))]
        if not any(_looks_like_layout_name(name) for name in target_names):
            continue
        rel = path.relative_to(path.parents[1])
        findings.append(Finding(str(rel), node.lineno, "assign", f"{'/'.join(target_names)} = {value}"))
    return findings


def _scan_calls(tree: ast.AST, path: Path, lines: list[str]) -> list[Finding]:
    findings: list[Finding] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = _call_name(node)
        if name not in CALL_NAME_HINTS:
            continue
        values = []
        for arg in list(node.args) + [kw.value for kw in node.keywords]:
            value = _literal_value(arg)
            if value is None or value in EXCLUDED_VALUES:
                continue
            values.append(value)
        if not values:
            continue
        snippet = lines[node.lineno - 1].strip()
        rel = path.relative_to(path.parents[1])
        findings.append(Finding(str(rel), node.lineno, "call", f"{name} -> {values} :: {snippet}"))
    return findings


def _scan_sizehint(lines: list[str], path: Path) -> list[Finding]:
    findings: list[Finding] = []
    for idx, line in enumerate(lines, 1):
        if "sizeHint()" in line:
            rel = path.relative_to(path.parents[1])
            findings.append(Finding(str(rel), idx, "sizehint", line.strip()))
    return findings


def collect_findings(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for path in _iter_target_files(root):
        text = path.read_text(encoding="utf-8")
        lines = text.splitlines()
        tree = ast.parse(text)
        findings.extend(_scan_assignments(tree, path))
        findings.extend(_scan_calls(tree, path, lines))
        findings.extend(_scan_sizehint(lines, path))
    findings.sort(key=lambda item: (item.path, item.line, item.kind, item.detail))
    return findings


def build_report(root: Path) -> str:
    findings = collect_findings(root)
    grouped: dict[str, list[Finding]] = {}
    for finding in findings:
        grouped.setdefault(finding.path, []).append(finding)

    lines: list[str] = []
    lines.append("MiniNote Diary UI Layout Audit Report")
    lines.append("=")
    lines.append("")
    lines.append("Purpose: phase-1 inventory of layout-sensitive hardcoded values and fragile patterns.")
    lines.append("Runtime behavior is not changed by this script.")
    lines.append("")
    lines.append(f"Scanned files: {len(grouped)}")
    lines.append(f"Total findings: {len(findings)}")
    lines.append("")

    priority_paths = [
        "ui/pages/work_order_page.py",
        "ui/theme_tokens.py",
        "ui/postit/layout.py",
        "ui/postit/layout_constants.py",
        "ui/postit/layout_containers.py",
        "ui/postit/layout_stack_hosts.py",
    ]
    lines.append("Priority review order:")
    for idx, path in enumerate(priority_paths, 1):
        count = len(grouped.get(path, []))
        lines.append(f"{idx}. {path} ({count} findings)")
    lines.append("")

    for path, items in grouped.items():
        lines.append(path)
        lines.append("-" * len(path))
        for item in items:
            lines.append(f"L{item.line:>4} [{item.kind}] {item.detail}")
        lines.append("")

    return "\n".join(lines)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = build_report(repo_root)
    output_path = repo_root / "ui_layout_audit_report.txt"
    output_path.write_text(report, encoding="utf-8")
    print(output_path)


if __name__ == "__main__":
    main()
