#!/usr/bin/env python3
"""Post-build hooks runner for templates with post commands.

This script runs after generator.py to execute post-build commands
in Docker containers for templates that specify a 'post' field.
"""

from pathlib import Path
import os
import subprocess
import yaml
import sys

from models import Manifest


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "templates.yaml"
OUT = ROOT / "out"


def load_manifest():
    """Load and validate the manifest file."""
    with open(MANIFEST, "r") as f:
        manifest_data = yaml.safe_load(f)

    try:
        return Manifest(**manifest_data)
    except Exception as e:
        print(f"✗ Invalid manifest: {e}")
        sys.exit(1)


def run_post_hook(template_id: str, language: str, release: str, post_command: str):
    """Execute post-build command in a Docker container.

    Args:
        template_id: Template identifier
        language: Programming language (e.g., 'r', 'python')
        release: Release version (e.g., '2026-q1')
        post_command: Shell command to execute
    """
    template_dir = OUT / template_id

    if not template_dir.exists():
        print(f"✗ Template directory not found: {template_dir}")
        return False

    # Construct Docker image name
    image = f"ghcr.io/recap-org/{language}:{release}"

    # Mount the template directory and run the command
    docker_cmd = [
        "docker", "run",
        "--rm",  # Remove container after execution
        # Mount template directory
        "-v", f"{template_dir.absolute()}:/workspace",
        "-w", "/workspace"
    ]

    docker_cmd.extend([
        image,
        "sh", "-c", post_command  # Execute the post command
    ])

    print(f"→ Running post-build hook for {template_id}")
    print(f"  Image: {image}")
    print(f"  Command: {post_command}")

    try:
        result = subprocess.run(
            docker_cmd,
            check=True,
            capture_output=True,
            text=True
        )

        if result.stdout:
            print(f"  Output:\n{result.stdout}")

        print(f"✓ Post-build hook completed for {template_id}")
        return True

    except subprocess.CalledProcessError as e:
        print(f"✗ Post-build hook failed for {template_id}")
        print(f"  Error: {e.stderr}")
        return False
    except FileNotFoundError:
        print(f"✗ Docker not found. Please ensure Docker is installed and available.")
        return False


def main():
    """Main entry point for post-build hooks."""
    manifest = load_manifest()

    # Find templates with post-build hooks
    templates_with_hooks = [
        template for template in manifest.templates
        if template.post is not None
    ]

    if not templates_with_hooks:
        print("No templates with post-build hooks found.")
        return

    print(
        f"Found {len(templates_with_hooks)} template(s) with post-build hooks\n")

    success_count = 0
    failure_count = 0

    for template in templates_with_hooks:
        success = run_post_hook(
            template_id=template.id,
            language=template.language,
            release=manifest.release,
            post_command=template.post
        )

        if success:
            success_count += 1
        else:
            failure_count += 1

        print()  # Blank line between templates

    # Print summary
    print("=" * 50)
    print(f"Post-build hooks summary:")
    print(f"  ✓ Success: {success_count}")
    print(f"  ✗ Failure: {failure_count}")

    if failure_count > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
