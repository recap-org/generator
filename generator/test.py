#!/usr/bin/env python3
"""Test generated templates by running them in dev containers."""

import subprocess
import sys
import yaml
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "templates.yaml"
OUT = ROOT / "out"
LOGS = ROOT / "logs"


def run_command(cmd, log_file, cwd=None):
    """Run a command and write output to log file. Return exit code."""
    print(f"  Running: {' '.join(cmd)}")

    with open(log_file, "a") as log:
        log.write(f"\n{'='*80}\n")
        log.write(f"Command: {' '.join(cmd)}\n")
        log.write(f"{'='*80}\n\n")

        result = subprocess.run(
            cmd,
            cwd=cwd,
            stdout=log,
            stderr=subprocess.STDOUT,
            text=True
        )

        log.write(f"\n\nExit code: {result.returncode}\n")

    return result.returncode


def test_template(template_id, setup_cmd, run_cmd):
    """Test a single template in its dev container."""
    template_dir = OUT / template_id
    log_file = LOGS / f"test-{template_id}.log"

    print(f"\n{'='*80}")
    print(f"Testing template: {template_id}")
    print(f"{'='*80}")

    # Create log file
    log_file.parent.mkdir(parents=True, exist_ok=True)
    log_file.write_text(f"Test log for template: {template_id}\n")

    # Step 1: Build/start the dev container
    print(f"→ Building dev container...")
    exit_code = run_command(
        ["devcontainer", "up", "--workspace-folder", str(template_dir)],
        log_file
    )

    if exit_code != 0:
        print(f"✗ Failed to build dev container for {template_id}")
        print(f"  See log: {log_file}")
        return False

    # Step 2: Run setup command
    print(f"→ Running setup command: {setup_cmd}")
    exit_code = run_command(
        ["devcontainer", "exec", "--workspace-folder", str(template_dir),
         "bash", "-c", setup_cmd],
        log_file
    )

    if exit_code != 0:
        print(f"✗ Setup command failed for {template_id}")
        print(f"  See log: {log_file}")
        return False

    # Step 3: Run the main command
    print(f"→ Running main command: {run_cmd}")
    exit_code = run_command(
        ["devcontainer", "exec", "--workspace-folder", str(template_dir),
         "bash", "-c", run_cmd],
        log_file
    )

    if exit_code != 0:
        print(f"✗ Run command failed for {template_id}")
        print(f"  See log: {log_file}")
        return False

    print(f"✓ Template {template_id} passed all tests")
    return True


def main():
    # Load templates
    with open(MANIFEST, "r") as f:
        templates = yaml.safe_load(f)

    print(f"Testing {len(templates)} templates...")

    # Test each template
    failed_templates = []
    for spec in templates:
        template_id = spec["id"]
        setup_cmd = spec["setup"]
        run_cmd = spec["run"]

        success = test_template(template_id, setup_cmd, run_cmd)

        if not success:
            failed_templates.append(template_id)

    # Summary
    print(f"\n{'='*80}")
    print(f"TEST RESULTS")
    print(f"{'='*80}")

    if failed_templates:
        print(f"✗ {len(failed_templates)} template(s) failed:")
        for template_id in failed_templates:
            print(f"  - {template_id}")
        print(f"\nLogs are in: {LOGS}/")
        sys.exit(1)
    else:
        print(f"✓ All {len(templates)} templates passed!")
        print(f"\nLogs are in: {LOGS}/")
        sys.exit(0)


if __name__ == "__main__":
    main()
