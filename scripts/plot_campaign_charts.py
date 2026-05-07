#!/usr/bin/env python3

import argparse
import html
import json
from pathlib import Path


COLORS = ["#0f766e", "#b7410e", "#2563eb", "#7c3aed", "#ca8a04", "#be123c"]


def parse_args():
    parser = argparse.ArgumentParser(description="Generate SVG line charts from a sanitized campaign summary JSON.")
    parser.add_argument("summary_json")
    parser.add_argument("--out-dir", default="docs/assets")
    return parser.parse_args()


def load_rows(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return data.get("by_scenario", [])


def by_id(rows):
    return {row["id"]: row for row in rows}


def value(row, key, default=0.0):
    item = row.get(key)
    return float(item) if item is not None else default


def pass_at(row, k):
    item = row.get("pass_at_k", {}).get(str(k))
    return float(item) if item is not None else 0.0


def svg_text_lines(x, y, lines, css_class, line_height=16, anchor="start"):
    parts = []
    for index, line in enumerate(lines):
        parts.append(
            f'<text x="{x}" y="{y + index * line_height}" text-anchor="{anchor}" class="{css_class}">'
            f"{html.escape(line)}</text>"
        )
    return parts


def line_chart(path, title, question, note, labels, series, glossary, y_label="Normalized metric, 0-1", y_max=1.0):
    width, height = 1280, 760
    left, right, top, bottom = 118, 78, 204, 186
    plot_w = width - left - right
    plot_h = height - top - bottom
    x_step = plot_w / max(1, len(labels) - 1)

    def x_pos(index):
        return left + index * x_step

    def y_pos(raw):
        val = max(0.0, min(y_max, raw))
        return top + plot_h - (val / y_max) * plot_h

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">',
        "<defs>",
        '<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">',
        '<stop offset="0%" stop-color="#eef8f4"/><stop offset="55%" stop-color="#ffffff"/><stop offset="100%" stop-color="#fff1e6"/>',
        "</linearGradient>",
        "<style>",
        ".title{font:800 30px Georgia,'Times New Roman',serif;fill:#172026}.question{font:700 15px -apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;fill:#172026}.note{font:500 13px -apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;fill:#5f6c73}.axis{font:700 12px -apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;fill:#5f6c73}.tick{font:650 11px -apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;fill:#5f6c73}.legend{font:700 12px -apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;fill:#172026}.gloss{font:500 11px -apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;fill:#5f6c73}.label{font:700 12px -apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;fill:#172026}",
        "</style>",
        "</defs>",
        f'<rect width="{width}" height="{height}" rx="28" fill="url(#bg)"/>',
        f'<rect x="34" y="34" width="{width - 68}" height="{height - 68}" rx="24" fill="#fff" stroke="#cfd7dc"/>',
        f'<text x="66" y="78" class="title">{html.escape(title)}</text>',
        f'<text x="66" y="112" class="question">{html.escape(question)}</text>',
        f'<text x="66" y="140" class="note">{html.escape(note)}</text>',
        '<line x1="66" y1="164" x2="1214" y2="164" stroke="#e5eaee"/>',
    ]

    for i in range(6):
        y = top + i * plot_h / 5
        score = y_max - i * y_max / 5
        parts.append(f'<line x1="{left}" y1="{y:.1f}" x2="{left + plot_w}" y2="{y:.1f}" stroke="#e5eaee"/>')
        parts.append(f'<text x="{left - 42}" y="{y + 4:.1f}" class="tick">{score:.1f}</text>')

    parts.append(f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top + plot_h}" stroke="#94a3ad"/>')
    parts.append(f'<line x1="{left}" y1="{top + plot_h}" x2="{left + plot_w}" y2="{top + plot_h}" stroke="#94a3ad"/>')
    parts.append(f'<text x="{left}" y="{top - 18}" class="axis">{html.escape(y_label)}; higher is better</text>')

    for index, label in enumerate(labels):
        x = x_pos(index)
        parts.append(f'<line x1="{x:.1f}" y1="{top + plot_h}" x2="{x:.1f}" y2="{top + plot_h + 6}" stroke="#94a3ad"/>')
        label_lines = str(label).split("\n")
        parts.extend(svg_text_lines(f"{x:.1f}", top + plot_h + 26, label_lines, "tick", 14, "middle"))

    legend_x = left
    legend_y = top + plot_h + 78
    for s_index, item in enumerate(series):
        color = COLORS[s_index % len(COLORS)]
        points = [(x_pos(i), y_pos(v)) for i, v in enumerate(item["values"])]
        point_text = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
        parts.append(f'<polyline points="{point_text}" fill="none" stroke="{color}" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"/>')
        for x, y in points:
            parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.5" fill="#fff" stroke="{color}" stroke-width="2.5"/>')
        lx = legend_x + (s_index % 4) * 260
        ly = legend_y + (s_index // 4) * 24
        parts.append(f'<line x1="{lx}" y1="{ly}" x2="{lx + 24}" y2="{ly}" stroke="{color}" stroke-width="3.2"/>')
        parts.append(f'<text x="{lx + 32}" y="{ly + 4}" class="legend">{html.escape(item["name"])}</text>')

    parts.append(f'<rect x="{left}" y="{height - 76}" width="{plot_w}" height="44" rx="10" fill="#f8faf9" stroke="#e5eaee"/>')
    parts.extend(svg_text_lines(left + 14, height - 56, glossary, "gloss", 16))

    parts.append("</svg>")
    Path(path).write_text("\n".join(parts), encoding="utf-8")


def main():
    args = parse_args()
    rows = load_rows(args.summary_json)
    row_by_id = by_id(rows)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    tool_skill_ids = [
        ("tools-focused-3-direct", "Focused\n3 tools"),
        ("tools-overloaded-14-flat", "Flat\n14 tools"),
        ("tools-layered-router-4", "Router\n4 tools"),
        ("skills-contract-with-tools", "Skill\n1+4 tools"),
    ]
    tool_skill_rows = [row_by_id[item[0]] for item in tool_skill_ids if item[0] in row_by_id]
    line_chart(
        out_dir / "minimax-r7-tool-skill-quality.svg",
        "Figure 1. Tool-Surface Ablation Signals",
        "Question: does adding tools or a procedural skill improve usable agent behavior?",
        "MiniMax M2.7 High, r7 pilot, n=7 per cell. Strict deployment pass@k was 0, so the chart reports partial-credit submetrics.",
        [item[1] for item in tool_skill_ids if item[0] in row_by_id],
        [
            {"name": "Task score", "values": [value(row, "avg_evaluation_score") for row in tool_skill_rows]},
            {"name": "Tool precision", "values": [value(row, "tool_precision_proxy") for row in tool_skill_rows]},
            {"name": "Required-tool coverage", "values": [value(row, "required_tool_coverage") for row in tool_skill_rows]},
            {"name": "Output schema adherence", "values": [value(row, "json_contract_pass_rate") for row in tool_skill_rows]},
        ],
        [
            "Task score = mean fraction of evaluator checks passed. Tool precision = required-tool calls / all tool calls.",
            "Required-tool coverage = required tools reached. Output schema adherence = parseable JSON contract success.",
        ],
    )

    return_ids = [
        ("tool-profile-short-structured-renewal", "Short\nJSON"),
        ("tool-profile-long-verbose-renewal", "Long\nverbose"),
        ("tool-profile-noisy-conflict-feature-rollback", "Conflicting\nevidence"),
        ("tool-profile-router-compressed-release-gate", "Router\nbundle"),
        ("tool-profile-permission-denied-hr-request", "Permission\n403"),
        ("tool-profile-large-log-artifact-release-blocker", "Large\nlog"),
    ]
    return_rows = [row_by_id[item[0]] for item in return_ids if item[0] in row_by_id]
    line_chart(
        out_dir / "minimax-r7-tool-return-quality.svg",
        "Figure 2. Tool-Return Profile Signals",
        "Question: how does tool-result shape affect extraction, schema stability, and evidence use?",
        "MiniMax M2.7 High, r7 pilot, n=7 per cell. Long/noisy returns include generated payloads with buried critical facts.",
        [item[1] for item in return_ids if item[0] in row_by_id],
        [
            {"name": "Task score", "values": [value(row, "avg_evaluation_score") for row in return_rows]},
            {"name": "Tool precision", "values": [value(row, "tool_precision_proxy") for row in return_rows]},
            {"name": "Required-tool coverage", "values": [value(row, "required_tool_coverage") for row in return_rows]},
            {"name": "Output schema adherence", "values": [value(row, "json_contract_pass_rate") for row in return_rows]},
        ],
        [
            "Return shape is a controlled mock-MCP variable, not a live external-system score.",
            "Use this figure to decide when to compress, route, summarize, or require citations from tool results.",
        ],
    )

    behavior_rows = [
        row
        for row in rows
        if row.get("category") == "rigor" and row.get("metadata", {}).get("personality_profile", {}).get("trait")
    ]
    behavior_rows = sorted(behavior_rows, key=lambda row: row["metadata"]["personality_profile"]["trait"])
    line_chart(
        out_dir / "minimax-r7-behavior-passk.svg",
        "Figure 3. Behavior Reliability Under Retry",
        "Question: which behavior traits recover with retry, and which require stronger harness constraints?",
        "MiniMax M2.7 High, r7 pilot. pass@k is an estimated probability that at least one of k attempts passes.",
        ["@1", "@3", "@5", "@7"],
        [
            {
                "name": row["metadata"]["personality_profile"]["trait"].replace("_", " ")[:22],
                "values": [pass_at(row, k) for k in [1, 3, 5, 7]],
            }
            for row in behavior_rows[:6]
        ],
        [
            "pass@k is useful for diagnosing recoverability, not for justifying autonomous high-risk actions.",
            "A steep pass@k curve implies verifier/repair dependence; flat low curves imply prompt or task redesign.",
        ],
        y_label="Estimated pass@k",
    )


if __name__ == "__main__":
    main()
