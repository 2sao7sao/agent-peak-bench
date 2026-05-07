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


def line_chart(path, title, subtitle, labels, series, y_label="score", y_max=1.0):
    width, height = 1120, 620
    left, right, top, bottom = 96, 60, 120, 118
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
        ".title{font:800 32px Georgia,'Times New Roman',serif;fill:#172026}.sub{font:500 14px -apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;fill:#5f6c73}.axis{font:650 12px -apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;fill:#5f6c73}.tick{font:600 11px -apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;fill:#5f6c73}.legend{font:650 12px -apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;fill:#172026}.label{font:650 12px -apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;fill:#172026}",
        "</style>",
        "</defs>",
        '<rect width="1120" height="620" rx="28" fill="url(#bg)"/>',
        '<rect x="34" y="34" width="1052" height="552" rx="24" fill="#fff" stroke="#cfd7dc"/>',
        f'<text x="66" y="82" class="title">{html.escape(title)}</text>',
        f'<text x="66" y="110" class="sub">{html.escape(subtitle)}</text>',
    ]

    for i in range(6):
        y = top + i * plot_h / 5
        score = y_max - i * y_max / 5
        parts.append(f'<line x1="{left}" y1="{y:.1f}" x2="{left + plot_w}" y2="{y:.1f}" stroke="#e5eaee"/>')
        parts.append(f'<text x="{left - 42}" y="{y + 4:.1f}" class="tick">{score:.1f}</text>')

    parts.append(f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top + plot_h}" stroke="#94a3ad"/>')
    parts.append(f'<line x1="{left}" y1="{top + plot_h}" x2="{left + plot_w}" y2="{top + plot_h}" stroke="#94a3ad"/>')
    parts.append(f'<text x="{left}" y="{top - 16}" class="axis">{html.escape(y_label)}</text>')

    for index, label in enumerate(labels):
        x = x_pos(index)
        parts.append(f'<line x1="{x:.1f}" y1="{top + plot_h}" x2="{x:.1f}" y2="{top + plot_h + 6}" stroke="#94a3ad"/>')
        parts.append(f'<text x="{x:.1f}" y="{top + plot_h + 28}" text-anchor="middle" class="tick">{html.escape(label)}</text>')

    legend_x = left
    legend_y = height - 50
    for s_index, item in enumerate(series):
        color = COLORS[s_index % len(COLORS)]
        points = [(x_pos(i), y_pos(v)) for i, v in enumerate(item["values"])]
        point_text = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
        parts.append(f'<polyline points="{point_text}" fill="none" stroke="{color}" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"/>')
        for x, y in points:
            parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.5" fill="#fff" stroke="{color}" stroke-width="2.5"/>')
        lx = legend_x + s_index * 178
        parts.append(f'<line x1="{lx}" y1="{legend_y}" x2="{lx + 24}" y2="{legend_y}" stroke="{color}" stroke-width="3.2"/>')
        parts.append(f'<text x="{lx + 32}" y="{legend_y + 4}" class="legend">{html.escape(item["name"])}</text>')

    parts.append("</svg>")
    Path(path).write_text("\n".join(parts), encoding="utf-8")


def main():
    args = parse_args()
    rows = load_rows(args.summary_json)
    row_by_id = by_id(rows)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    tool_skill_ids = [
        ("tools-focused-3-direct", "3 focused"),
        ("tools-overloaded-14-flat", "14 flat"),
        ("tools-layered-router-4", "router 4"),
        ("skills-contract-with-tools", "skill+4"),
    ]
    tool_skill_rows = [row_by_id[item[0]] for item in tool_skill_ids if item[0] in row_by_id]
    line_chart(
        out_dir / "minimax-r7-tool-skill-quality.svg",
        "Tools / Skills Quality Curves",
        "MiniMax M2.7 High, r7 pilot. Strict pass@k remains zero; submetrics expose the engineering boundary.",
        [item[1] for item in tool_skill_ids if item[0] in row_by_id],
        [
            {"name": "eval score", "values": [value(row, "avg_evaluation_score") for row in tool_skill_rows]},
            {"name": "tool precision", "values": [value(row, "tool_precision_proxy") for row in tool_skill_rows]},
            {"name": "tool coverage", "values": [value(row, "required_tool_coverage") for row in tool_skill_rows]},
            {"name": "JSON contract", "values": [value(row, "json_contract_pass_rate") for row in tool_skill_rows]},
        ],
    )

    return_ids = [
        ("tool-profile-short-structured-renewal", "short JSON"),
        ("tool-profile-long-verbose-renewal", "long text"),
        ("tool-profile-noisy-conflict-feature-rollback", "conflict"),
        ("tool-profile-router-compressed-release-gate", "router"),
        ("tool-profile-permission-denied-hr-request", "403 error"),
        ("tool-profile-large-log-artifact-release-blocker", "large log"),
    ]
    return_rows = [row_by_id[item[0]] for item in return_ids if item[0] in row_by_id]
    line_chart(
        out_dir / "minimax-r7-tool-return-quality.svg",
        "Tool Return Profile Curves",
        "MiniMax M2.7 High, r7 pilot. Long returns can preserve structure but increase context and latency costs.",
        [item[1] for item in return_ids if item[0] in row_by_id],
        [
            {"name": "eval score", "values": [value(row, "avg_evaluation_score") for row in return_rows]},
            {"name": "tool precision", "values": [value(row, "tool_precision_proxy") for row in return_rows]},
            {"name": "tool coverage", "values": [value(row, "required_tool_coverage") for row in return_rows]},
            {"name": "JSON contract", "values": [value(row, "json_contract_pass_rate") for row in return_rows]},
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
        "Behavior / Personality pass@k Curves",
        "MiniMax M2.7 High, r7 pilot. Some traits improve sharply with retry, which implies verifier/repair dependence.",
        ["@1", "@3", "@5", "@7"],
        [
            {
                "name": row["metadata"]["personality_profile"]["trait"].replace("_", " ")[:22],
                "values": [pass_at(row, k) for k in [1, 3, 5, 7]],
            }
            for row in behavior_rows[:6]
        ],
    )


if __name__ == "__main__":
    main()
