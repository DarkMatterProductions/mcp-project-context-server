#!/usr/bin/env python3
"""
Semantic Versioning Script for Git Repositories
Supports conventional commits: feat:, fix:, and BREAKING CHANGE
"""
import subprocess
import os
import re
import argparse
import shutil
import sys
import platform
import tarfile
import tempfile
import zipfile
from collections import defaultdict
from pathlib import Path
from typing import Tuple, List, Optional, Dict, Any
from shared_helpers import key_id_lookup, GH_CMD, INSTALL_DIR, GH_API_URL, GIT_CMD, get_last_version, \
    get_commits_since_tag, determine_new_version
from constants import COMMIT_TYPES, INCREMENT_BUMP_TYPE_MESSAGES, RELEASE_OVERRIDE_SCOPES

import requests


# ── Helpers ──────────────────────────────────────────────────────────────────

def get_installed_version() -> str | None:
    """Return the installed gh version string (e.g. '2.50.0'), or None."""
    gh_path = shutil.which(GH_CMD) or INSTALL_DIR / GH_CMD
    try:
        result = subprocess.run(
            [str(gh_path), "--version"],
            capture_output=True, text=True, check=True
        )
        # Output: "gh version 2.50.0 (2024-05-01)"
        return result.stdout.split()[2]
    except (subprocess.CalledProcessError, FileNotFoundError, IndexError):
        return None


def get_latest_release() -> tuple[str, str]:
    """Return (version, download_url) for the current platform from the GitHub API."""
    system = platform.system()   # 'Linux', 'Darwin', 'Windows'
    machine = platform.machine() # 'x86_64', 'arm64', 'AMD64', etc.

    # Normalise OS label to match GitHub asset naming
    os_map = {"Linux": "linux", "Darwin": "macOS", "Windows": "windows"}
    os_label = os_map.get(system, system.lower())

    # Normalise arch label
    arch_map = {"x86_64": "amd64", "AMD64": "amd64", "aarch64": "arm64", "arm64": "arm64"}
    arch_label = arch_map.get(machine, machine.lower())

    response = requests.get(GH_API_URL, timeout=10)
    response.raise_for_status()
    data = response.json()

    version = data["tag_name"].lstrip("v")  # e.g. '2.50.0'

    # Asset names look like: gh_2.50.0_linux_amd64.tar.gz / gh_2.50.0_windows_amd64.zip
    ext = "zip" if system == "Windows" else "tar.gz"
    expected_name = f"gh_{version}_{os_label}_{arch_label}.{ext}"

    for asset in data["assets"]:
        if asset["name"] == expected_name:
            return version, asset["browser_download_url"]

    raise RuntimeError(
        f"No matching asset found for {os_label}/{arch_label}. "
        f"Looked for: {expected_name}"
    )


def version_tuple(v: str) -> tuple[int, ...]:
    return tuple(int(x) for x in v.split("."))


def download_and_install(url: str, version: str, dry_run: bool = False) -> None:
    """Download the release archive and extract the gh binary to INSTALL_DIR."""
    system = platform.system()
    if dry_run:
        print(f"Dry run mode. Would download and install gh {version} from {url} ...")
        return

    INSTALL_DIR.mkdir(parents=True, exist_ok=True)
    print(f"  Downloading from {url} ...")
    response = requests.get(url, stream=True, timeout=60)
    response.raise_for_status()

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        archive_path = tmp_path / ("gh_release.zip" if system == "Windows" else "gh_release.tar.gz")

        with open(archive_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        # Extract
        if system == "Windows":
            with zipfile.ZipFile(archive_path) as zf:
                zf.extractall(tmp_path)
        else:
            with tarfile.open(archive_path, "r:gz") as tf:
                tf.extractall(tmp_path)

        # Find the binary inside the extracted tree
        binary = next(tmp_path.rglob(GH_CMD), None)
        if binary is None:
            raise FileNotFoundError(f"Could not locate '{GH_CMD}' in downloaded archive.")

        dest = INSTALL_DIR / GH_CMD
        shutil.copy2(binary, dest)
        dest.chmod(0o755)  # no-op on Windows, harmless
        print(f"  Installed gh {version} → {dest}")


def ensure_gh_cli(dry_run: bool = False) -> None:
    print("Checking GitHub CLI (gh) ...")

    latest_version, download_url = get_latest_release()
    print(f"  Latest release : v{latest_version}")

    installed_version = get_installed_version()

    if installed_version is None:
        print("  gh not found. Installing ...")
        download_and_install(download_url, latest_version, dry_run)
    elif version_tuple(installed_version) < version_tuple(latest_version):
        print(f"  Installed version v{installed_version} is outdated. Upgrading ...")
        download_and_install(download_url, latest_version, dry_run)
    else:
        print(f"  gh v{installed_version} is up to date. Nothing to do.")


def build_artifacts(new_version: str, verbose: bool = False) -> List[Path]:
    """Run python -m build and return the list of generated artifact paths."""
    print("Running python -m build...")

    # Run build, capturing stdout/stderr and optionally echoing to the console
    process = subprocess.Popen(
        [sys.executable, "-m", "build"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env={
            "SETUPTOOLS_SCM_PRETEND_VERSION": new_version,
        },
        text=True,
    )

    assert process.stdout is not None
    output_lines: List[str] = []
    for line in process.stdout:
        if verbose:
            print(line, end='')
        output_lines.append(line)

    process.wait()

    if process.returncode != 0:
        if not verbose:
            print(''.join(output_lines), end='')
        print(f"Error: python -m build failed with exit code {process.returncode}")
        sys.exit(1)

    # Find the last 'Successfully built ...' line and extract filenames
    artifacts: List[Path] = []
    for line in output_lines:
        match = re.search(r'Successfully built (.+)', line)
        if match:
            raw = match.group(1).strip()
            # Handle "file1.tar.gz and file2.whl" or a single filename
            if ' and ' in raw:
                parts = [p.strip() for p in raw.split(' and ')]
            else:
                parts = [raw.strip()]
            artifacts = [Path(p) for p in parts if p]

    if not artifacts:
        print("Error: could not identify build artifacts from python -m build output")
        sys.exit(1)

    print("\nBuild artifacts:")
    for artifact in artifacts:
        print(f"  {artifact}")

    return artifacts


def create_git_tag(version: str):
    """Create and push a git tag for the new version."""
    try:
        subprocess.run([GIT_CMD, "tag", version], check=True)
        subprocess.run([GIT_CMD, "push", "origin", version], check=True)
        print(f"Created and pushed git tag: {version}")
    except subprocess.CalledProcessError as e:
        print(f"Error creating git tag: {e}")
        raise


def get_repository_name():
    """Create and push a git tag for the new version."""
    try:
        result = subprocess.run(
            [GIT_CMD, 'rev-parse', '--show-toplevel'],
            capture_output=True,
            text=True,
            check=True
        )
        lines = result.stdout.split('\n', 1)
        repository_path = Path(lines[0] if lines else '/repo/unknown')
        repository_name = repository_path.name
        return repository_name
    except subprocess.CalledProcessError as e:
        print(f"Error getting git repository root: {e}")
        if e.stdout:
            print(f"stdout: {e.stdout.strip()}")
        if e.stderr:
            print(f"stderr: {e.stderr.strip()}")
        return ''
    except Exception as e:
        print(f"Error getting git repository root: {e}")
        return ''


def create_github_release(version: str, artifacts: List, dry_run: bool = False):
    """Create a GitHub release with the provided artifacts."""
    ensure_gh_cli(dry_run)
    if dry_run:
        print(f"[DRY-RUN] Would create GitHub release for {version} with artifacts:")
        for artifact in artifacts:
            print(f"  {artifact}")
        return

    process = subprocess.Popen(
        [
            "gh", "release", "create", version,
            *[f"./dist/{str(a)}" for a in artifacts],
            '--title', f'{version}',
            '--notes', f'Automated release for {version}'
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    assert process.stdout is not None
    output_lines: List[str] = []
    for line in process.stdout:
        output_lines.append(line)

    process.wait()

    if process.returncode != 0:
        print(''.join(output_lines), end='')
        raise subprocess.CalledProcessError(process.returncode, 'gh release create')

    print(f"Created GitHub release for {version}")


def main():
    """Main versioning workflow."""
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description='Semantic Versioning Script for Git Repositories'
    )
    version_increment = parser.add_mutually_exclusive_group(required=False)
    version_increment.add_argument('--major', action="store_true",
                                   help='Increment the major version (X.0.0)')
    version_increment.add_argument('--minor', action="store_true",
                                   help='Increment the minor version (X.Y.0)')
    version_increment.add_argument('--patch', action="store_true",
                                   help='Increment the patch version (X.Y.Z)')
    parser.add_argument('--build', action="store_true",
                        help='Build distribution artifacts using python -m build')
    parser.add_argument('--rebuild', action="store_true",
                        help='Force rebuild latest tag artifacts (Overrides --build)')
    parser.add_argument('--publish', action="store_true",
                        help='Publish a GitHub release with built artifacts (requires --build)')
    parser.add_argument('--dry-run', action="store_true",
                        help='Perform a dry run without creating tags, builds, or releases')
    parser.add_argument('--verbose', action="store_true",
                        help='Enable verbose output for expanded console output')
    parser.add_argument('--debug', action="store_true",
                        help='Enable debug output')

    args = parser.parse_args()

    if args.rebuild:
        args.build = True

    if args.publish and not args.build:
        print("Error: --publish requires --build")
        sys.exit(1)

    print("=== Semantic Versioning Script ===\n")

    # Check if dry-run mode is active
    # Check if dry-run mode is active
    if args.dry_run:
        print("🔍 DRY-RUN MODE ACTIVE - No tags, releases, or artifacts will be created\n")

    # Get repository name from environment
    repo_full_name = get_repository_name()
    repo_name = repo_full_name.split('/')[-1]
    print(f"Repository: {repo_name}\n")

    # Step 1: Get current version
    current_version = get_last_version()
    print(f"Current version: {current_version}")

    # Step 2: Get commits since last version
    commits = get_commits_since_tag(current_version)

    # Step 3: Resolve forced bump type from CLI flags (overrides commit analysis)
    if args.major:
        force_bump = "major"
    elif args.minor:
        force_bump = "minor"
    elif args.patch:
        force_bump = "patch"
    else:
        force_bump = None

    # Step 4: Determine new base version
    new_version, bump_used = determine_new_version(current_version, commits, force_bump, args.verbose, args.debug)
    if args.rebuild:
        new_version = current_version
    elif new_version is None:
        print("No new commits since last version. Exiting.")
        sys.exit(0)
    print(f"New version: {new_version} ({INCREMENT_BUMP_TYPE_MESSAGES[bump_used]})")
    print(f"Found {len(commits)} new commits\n")

    # Output version and bump type for GitHub Actions
    github_output = os.environ.get("GITHUB_OUTPUT", None)
    if github_output:
        with open(github_output, "a") as f:
            f.write(f'version={new_version}\n')
            f.write(f'bump={bump_used}\n')

    if new_version == current_version and bump_used == 'none':
        print("Tagged for skipping Build & Release. Exiting.")
        sys.exit(0)

    # Step 5: Build artifacts
    artifacts = []
    if args.build or args.rebuild:
        if args.dry_run:
            print("\n[DRY-RUN] Would run python -m build")
            artifacts = [
                f"{repo_name}-{new_version}.tar.gz",
                f"{repo_name}-{new_version}-py3-none-any.whl",
            ]
            print("Would produce artifacts:")
            for artifact in artifacts:
                print(f"  {artifact}")
        else:
            print("\nBuilding artifacts...")
            artifacts = build_artifacts(
                new_version=new_version,
                verbose=args.verbose
            )
    else:
        print("Skipping build step.")

    # Step 6: Create git tag
    if args.dry_run:
        print("[DRY-RUN] Would create git tag:", new_version)
    else:
        # Step 7: Publish GitHub release
        if args.publish and not args.rebuild:
            print(f"Creating git tag: {new_version}")
            create_git_tag(new_version)
            print("\nCreating GitHub release...")
            create_github_release(new_version, artifacts, dry_run=args.dry_run)

    print("\n=== Versioning Complete ===")


if __name__ == '__main__':
    main()
