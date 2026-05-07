#!/usr/bin/env python3

import argparse
import datetime as dt
import json
import shlex
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def parse_args():
    parser = argparse.ArgumentParser(description="Plan or execute a long-running Agent Peak Bench campaign.")
    parser.add_argument("campaign", help="Path to campaign JSON, for example evals/campaigns/harness_engineering_campaign_v1.json")
    parser.add_argument("--batch", action="append", help="Batch id to run. Defaults to all batches in order.")
    parser.add_argument("--execute", action="store_true", help="Actually run commands. Default only prints commands.")
    parser.add_argument("--out-dir", default="", help="Output directory. Defaults to results/<campaign_id>/")
    parser.add_argument("--runner", default="scripts/run_minimax_evals.py", help="Runner script path.")
    return parser.parse_args()


def shell_join(command: list) -> str:
    if hasattr(shlex, "join"):
        return shlex.join(command)
    return " ".join(shlex.quote(item) for item in command)


def build_command(runner: Path, campaign: dict, batch: dict, out_dir: Path) -> list:
    timestamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    campaign_id = campaign["campaign_id"]
    batch_id = batch["id"]
    out_file = out_dir / f"{campaign_id}-{batch_id}-{timestamp}.json"
    command = [
        "python3",
        str(runner),
        "--campaign-id",
        campaign_id,
        "--run-notes",
        batch_id,
        "--force-repeat",
        str(batch["force_repeat"]),
        "--pass-k",
        batch["pass_k"],
        "--out",
        str(out_file),
    ]
    for suite in batch["suites"]:
        command.extend(["--suite", suite])
    return command


def main():
    args = parse_args()
    campaign_path = Path(args.campaign).resolve()
    campaign = json.loads(campaign_path.read_text(encoding="utf-8"))
    runner = Path(args.runner)
    runner_path = runner if runner.is_absolute() else ROOT / runner
    if not runner_path.exists():
        raise SystemExit(f"Runner not found: {runner}")
    out_dir = Path(args.out_dir) if args.out_dir else Path("results") / campaign["campaign_id"]
    out_dir_path = out_dir if out_dir.is_absolute() else ROOT / out_dir
    out_dir_path.mkdir(parents=True, exist_ok=True)

    selected = set(args.batch or [])
    batches = [
        batch
        for batch in campaign.get("campaign_batches", [])
        if not selected or batch["id"] in selected
    ]
    missing = selected - {batch["id"] for batch in batches}
    if missing:
        raise SystemExit(f"Unknown batch id(s): {', '.join(sorted(missing))}")

    commands = [build_command(runner, campaign, batch, out_dir) for batch in batches]
    for command in commands:
        print(shell_join(command))

    if not args.execute:
        print("\nDry run only. Add --execute to run. Provider credentials must be supplied through MODEL_* env vars.")
        return 0

    for command in commands:
        subprocess.run(command, cwd=ROOT, check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
