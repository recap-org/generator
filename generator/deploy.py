#!/usr/bin/env python3
"""Deploy generated templates to GitHub repositories."""

import subprocess
import sys
import yaml
import shutil
import tempfile
from pathlib import Path
from datetime import datetime

from models import Manifest


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "templates.yaml"
OUT = ROOT / "out"


def run_git_command(cmd, cwd):
    """Run a git command and return exit code."""
    print(f"  $ {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"  Error: {result.stderr}")

    return result.returncode, result.stdout, result.stderr


def get_current_commit_sha():
    """Get the current git commit SHA of the generator repo."""
    result = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"],
        cwd=ROOT,
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        return result.stdout.strip()
    return "unknown"


def sync_directory(src, dst):
    """Sync all files from src to dst, removing files that don't exist in src."""
    # Remove all files in dst except .git
    for item in dst.iterdir():
        if item.name == ".git":
            continue
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()

    # Copy all files from src to dst
    for item in src.iterdir():
        if item.is_dir():
            shutil.copytree(item, dst / item.name)
        else:
            shutil.copy2(item, dst / item.name)


def deploy_template(template_id):
    """Deploy a single template to its GitHub repository."""
    template_dir = OUT / template_id
    repo_url = f"git@github.com:recap-org/template-{template_id}.git"

    print(f"\n{'='*80}")
    print(f"Deploying template: {template_id}")
    print(f"Repository: {repo_url}")
    print(f"{'='*80}")

    # Create temporary directory for the repo
    with tempfile.TemporaryDirectory(prefix=f"deploy-{template_id}-") as tmpdir:
        repo_dir = Path(tmpdir) / template_id

        # Clone or check if repo exists
        print(f"→ Cloning repository...")
        exit_code, stdout, stderr = run_git_command(
            ["git", "clone", repo_url, str(repo_dir)],
            cwd=tmpdir
        )

        if exit_code != 0:
            print(f"✗ Failed to clone repository for {template_id}")
            return False

        # Sync files
        print(f"→ Syncing files from {template_dir}...")
        sync_directory(template_dir, repo_dir)

        # Check for changes
        print(f"→ Checking for changes...")
        exit_code, stdout, stderr = run_git_command(
            ["git", "status", "--porcelain"],
            cwd=repo_dir
        )

        if exit_code != 0:
            print(f"✗ Failed to check git status for {template_id}")
            return False

        if not stdout.strip():
            print(f"→ No changes detected, skipping push")
            print(f"✓ Template {template_id} is up to date")
            return True

        # Stage all changes
        print(f"→ Staging changes...")
        exit_code, stdout, stderr = run_git_command(
            ["git", "add", "-A"],
            cwd=repo_dir
        )

        if exit_code != 0:
            print(f"✗ Failed to stage changes for {template_id}")
            return False

        # Create commit
        commit_sha = get_current_commit_sha()
        timestamp = datetime.now().strftime("%Y-%m-%d")
        commit_message = f"Update from generator@{commit_sha} on {timestamp}"

        print(f"→ Creating commit: {commit_message}")
        exit_code, stdout, stderr = run_git_command(
            ["git", "commit", "-m", commit_message],
            cwd=repo_dir
        )

        if exit_code != 0:
            print(f"✗ Failed to create commit for {template_id}")
            return False

        # Push to GitHub
        print(f"→ Pushing to GitHub...")
        exit_code, stdout, stderr = run_git_command(
            ["git", "push", "origin", "main"],
            cwd=repo_dir
        )

        if exit_code != 0:
            print(f"✗ Failed to push to GitHub for {template_id}")
            return False

        print(f"✓ Successfully deployed {template_id}")
        return True


def main():
    # Load and validate templates
    with open(MANIFEST, "r") as f:
        manifest_data = yaml.safe_load(f)

    try:
        manifest = Manifest(**manifest_data)
    except Exception as e:
        print(f"✗ Invalid manifest: {e}")
        sys.exit(1)

    print(f"Deploying {len(manifest.templates)} templates...")

    # Deploy each template
    failed_templates = []
    templates = manifest.templates
    for spec in templates:
        success = deploy_template(spec.id)

        if not success:
            failed_templates.append(spec.id)
            # Fail fast - exit on first failure
            print(f"\n{'='*80}")
            print(f"DEPLOYMENT FAILED")
            print(f"{'='*80}")
            print(f"✗ Failed to deploy template: {spec.id}")
            print(f"  Aborting deployment process")
            sys.exit(1)

    # Summary
    print(f"\n{'='*80}")
    print(f"DEPLOYMENT COMPLETE")
    print(f"{'='*80}")
    print(f"✓ Successfully deployed all {len(templates)} templates!")
    sys.exit(0)


if __name__ == "__main__":
    main()
