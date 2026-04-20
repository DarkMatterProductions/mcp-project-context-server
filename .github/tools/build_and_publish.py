#!/usr/bin/env python3
"""
Semantic Versioning Script for Git Repositories
Supports conventional commits: feat:, fix:, and BREAKING CHANGE
"""
import subprocess
import os
import re
import argparse
import sys
import platform
from pathlib import Path
from typing import Tuple, List, Optional

# Use 'git.exe' on Windows, 'git' on all other platforms
GIT_CMD = 'git.exe' if platform.system() == 'Windows' else 'git'


def get_distance_from_main() -> int:
    """Get the number of commits the current branch is ahead of main."""
    try:
        result = subprocess.run(
            [GIT_CMD, 'rev-list', '--count', 'main..HEAD'],
            capture_output=True,
            text=True,
            check=True
        )
        return int(result.stdout.strip())
    except subprocess.CalledProcessError as e:
        print(f"Error getting distance from main: {e}")
        if e.stdout:
            print(f"stdout: {e.stdout.strip()}")
        if e.stderr:
            print(f"stderr: {e.stderr.strip()}")
        return 0
    except Exception as e:
        print(f"Error getting distance from main: {e}")
        return 0


def get_current_git_hash() -> str:
    """Get the shortened git hash of the current HEAD."""
    try:
        result = subprocess.run(
            [GIT_CMD, 'rev-parse', '--short', 'HEAD'],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error getting git hash: {e}")
        if e.stdout:
            print(f"stdout: {e.stdout.strip()}")
        if e.stderr:
            print(f"stderr: {e.stderr.strip()}")
        return 'unknown'
    except Exception as e:
        print(f"Error getting git hash: {e}")
        return 'unknown'


def get_last_version() -> str:
    """Get the last semantic version tag, or return 0.0.0 if none exist."""
    try:
        # Get current branch name
        branch_result = subprocess.run(
            [GIT_CMD, 'branch', '--show-current'],
            capture_output=True,
            text=True,
            check=True
        )
        current_branch = branch_result.stdout.strip()

        # Get tags merged into current branch
        result = subprocess.run(
            [GIT_CMD, 'tag', '--merged', current_branch],
            capture_output=True,
            text=True,
            check=True
        )
        tags = result.stdout.strip().split('\n')
        # Filter to only semantic version tags (e.g., 1.0.0)
        version_tags = [tag for tag in tags if tag and re.match(r'^\d+\.\d+\.\d+$', tag)]

        if not version_tags:
            return '0.0.0'

        # Sort by version number and return the highest
        version_tags.sort(key=lambda v: tuple(map(int, v.split('.'))))
        return version_tags[-1]
    except subprocess.CalledProcessError as e:
        print(f"Error getting last version: {e}")
        if e.stdout:
            print(f"stdout: {e.stdout.strip()}")
        if e.stderr:
            print(f"stderr: {e.stderr.strip()}")
        return '0.0.0'
    except Exception as e:
        print(f"Error getting last version: {e}")
        return '0.0.0'


def get_commits_since_tag(tag: str) -> List[str]:
    """Get commit hashes since the given tag."""
    try:
        if tag == '0.0.0':
            # Get all commits if no tags exist
            result = subprocess.run(
                [GIT_CMD, 'rev-list', 'HEAD'],
                capture_output=True,
                text=True,
                check=True
            )
        else:
            # Get commits since the tag
            result = subprocess.run(
                [GIT_CMD, 'rev-list', f'{tag}..HEAD'],
                capture_output=True,
                text=True,
                check=True
            )

        commits = [c.strip() for c in result.stdout.strip().split('\n') if c.strip()]
        return commits
    except subprocess.CalledProcessError as e:
        print(f"Error getting commits: {e}")
        if e.stdout:
            print(f"stdout: {e.stdout.strip()}")
        if e.stderr:
            print(f"stderr: {e.stderr.strip()}")
        return []
    except Exception as e:
        print(f"Error getting commits: {e}")
        return []


def get_commit_message(commit_hash: str) -> Tuple[str, str]:
    """Get commit subject and body."""
    try:
        result = subprocess.run(
            [GIT_CMD, 'show', '-s', '--format=%s%n%b', commit_hash],
            capture_output=True,
            text=True,
            check=True
        )
        lines = result.stdout.split('\n', 1)
        subject = lines[0] if lines else ''
        body = lines[1] if len(lines) > 1 else ''
        return subject, body
    except subprocess.CalledProcessError as e:
        print(f"Error getting commit message for {commit_hash}: {e}")
        if e.stdout:
            print(f"stdout: {e.stdout.strip()}")
        if e.stderr:
            print(f"stderr: {e.stderr.strip()}")
        return '', ''
    except Exception as e:
        print(f"Error getting commit message for {commit_hash}: {e}")
        return '', ''


COMMIT_TYPES = {
    'breaking':  'A backwards incompatible change to the API or Tools',
    'rewrite':   'Complete rewrites / architectural overhauls',
    'milestone': 'Significant feature milestones / stable releases',
    'deprecate': 'Major deprecation cleanups',
    'eos':       'End of support for a runtime/platform',
    'license':   'License changes',
    'security':  'Security-mandated incompatible changes',
    'feature':   'A new feature or capability',
    'fix':       'A bug fix',
    'test':      'Adding or updating tests',
    'docs':      'Documentation changes only',
    'refactor':  'Code restructuring with no behaviour change',
    'chore':     'Build system, tooling, or dependency changes',
    'adrs':      'Adding or updating an Architecture Decision Record',
    'adr':       'Adding or updating an Architecture Decision Record',
}


def determine_bump(commits: List[str]) -> str:
    """
    Determine the semantic version bump based on commits.
    Returns 'major', 'minor', or 'patch'
    """
    has_major = False
    has_minor = False
    has_patch = False
    __bump = 'none'

    for commit_hash in commits:
        subject, body = get_commit_message(commit_hash)

        major_bump_check = re.findall(r'^(breaking|rewrite|milestone|deprecate|eos|license|security)\(.*\):', subject)
        if major_bump_check:
            commit_type = major_bump_check[0]
            print(f"Commit flagged as {commit_type} ({COMMIT_TYPES.get(commit_type, '')}). Incrementing major version.")
            has_major = True
            break

        major_bump_check = re.findall(r'^(feature|fix)!\(.*\):', subject)
        if major_bump_check:
            commit_type = major_bump_check[0]
            print(f"Commit flagged as {commit_type} ({COMMIT_TYPES.get(commit_type, '')}). Incrementing major version.")
            has_major = True
            break

        minor_bump_check = re.findall(r'^(feature|license)\(.*\):', subject)
        if minor_bump_check:
            commit_type = minor_bump_check[0]
            print(f"Commit flagged as {commit_type} ({COMMIT_TYPES.get(commit_type, '')}). Incrementing minor version.")
            has_minor = True

        patch_bump_check = re.findall(r'^(fix|test|refactor|adr[s]*)\(.*\):', subject)
        if patch_bump_check:
            commit_type = patch_bump_check[0]
            print(f"Commit flagged as {commit_type} ({COMMIT_TYPES.get(commit_type, '')}). Incrementing patch version.")
            has_patch = True

        chore_or_doc_check = re.findall(r'^(docs|chore)\(.*\):', subject)
        if chore_or_doc_check:
            commit_type = chore_or_doc_check[0]
            print(f"Commit flagged as {commit_type} ({COMMIT_TYPES.get(commit_type, '')}). Not building a release.")

    # fix: defaults to patch, so we don't need to explicitly check

    if has_major:
        __bump = 'major'
    elif has_minor:
        __bump = 'minor'
    elif has_patch:
        __bump = 'patch'
    else:
        raise ValueError(f"Unknown Increment Type: {__bump}")

    print(f"Determined bump type: {__bump}")
    return __bump

def increment_version(version: str, bump: str) -> str:
    """Increment the version based on bump type."""
    major, minor, patch = map(int, version.split('.'))

    if bump == 'major':
        major += 1
        minor = 0
        patch = 0
    elif bump == 'minor':
        minor += 1
        patch = 0
    elif bump == 'patch':
        patch += 1
    else:
        raise ValueError(f"Unknown Increment Type: {bump}")

    return f'{major}.{minor}.{patch}'


def determine_new_version(current_version: str, commits: List[str], force_bump: Optional[str] = None) -> Optional[str]:
    """
    Determine the new version based on current version and commits.

    Args:
        current_version: The current semantic version string (e.g. '1.2.3').
        commits: List of commit hashes since the last version tag.
        force_bump: Optional override for bump type ('major', 'minor', or 'patch').
                    When provided, skips commit analysis and uses this bump type directly.
    """
    if not commits and not force_bump:
        print("No new commits since last version")
        return None

    if current_version == '0.0.0':
        # Apply forced bump from initial version, or default to 0.0.1
        bump = force_bump or 'patch'
        first_version = increment_version(current_version, bump)
        if force_bump:
            print(f"No previous version found. Setting first version to {first_version} (forced {force_bump})")
        else:
            print(f"No previous version found. Setting first version to {first_version}")
        return first_version

    # Use forced bump if provided, otherwise analyse commits
    if force_bump:
        bump = force_bump
        print(f"Using forced bump type: {bump}")
    else:
        bump = determine_bump(commits)

    new_version = increment_version(current_version, bump)
    return new_version


def build_artifacts(new_version: str, verbose: bool = False) -> List[Path]:
    """Run python -m build and return the list of generated artifact paths."""
    print("Running python -m build...")

    # Run build, capturing stdout/stderr and optionally echoing to the console
    process = subprocess.Popen(
        [sys.executable, '-m', 'build'],
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
        subprocess.run([GIT_CMD, 'tag', version], check=True)
        subprocess.run([GIT_CMD, 'push', 'origin', version], check=True)
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
    if dry_run:
        print(f"[DRY-RUN] Would create GitHub release for {version} with artifacts:")
        for artifact in artifacts:
            print(f"  {artifact}")
        return

    process = subprocess.Popen(
        [
            'gh', 'release', 'create', version,
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
    # Setup argument parser
    parser = argparse.ArgumentParser(
        description='Semantic Versioning Script for Git Repositories'
    )
    version_increment = parser.add_mutually_exclusive_group(required=False)
    version_increment.add_argument('--major', action='store_true',
                                   help='Increment the major version (X.0.0)')
    version_increment.add_argument('--minor', action='store_true',
                                   help='Increment the minor version (X.Y.0)')
    version_increment.add_argument('--patch', action='store_true',
                                   help='Increment the patch version (X.Y.Z)')
    parser.add_argument('--build', action='store_true',
                        help='Build distribution artifacts using python -m build')
    parser.add_argument('--publish', action='store_true',
                        help='Publish a GitHub release with built artifacts (requires --build)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Perform a dry run without creating tags, builds, or releases')
    parser.add_argument('--verbose', action='store_true',
                        help='Stream build output to the console during python -m build')

    args = parser.parse_args()

    if args.publish and not args.build:
        print("Error: --publish requires --build")
        sys.exit(1)

    print("=== Semantic Versioning Script ===\n")

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
    print(f"Found {len(commits)} new commits\n")

    # Step 3: Resolve forced bump type from CLI flags (overrides commit analysis)
    if args.major:
        force_bump = 'major'
    elif args.minor:
        force_bump = 'minor'
    elif args.patch:
        force_bump = 'patch'
    else:
        force_bump = None

    # Step 4: Determine new base version
    new_version = determine_new_version(current_version, commits, force_bump)
    if new_version is None:
        print("Cannot determine new version")
        sys.exit(1)

    # Output version for GitHub Actions
    github_output = os.environ.get('GITHUB_OUTPUT', None)
    if github_output:
        with open(github_output, 'a') as f:
            f.write(f'version={new_version}\n')

    # Step 5: Build artifacts
    artifacts = []
    if args.build:
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

    # Step 6: Create git tag
    if args.dry_run:
        print("[DRY-RUN] Would create git tag:", new_version)
    else:
        print("Creating git tag...")
        create_git_tag(new_version)

    # Step 7: Publish GitHub release
    if args.publish:
        print("\nCreating GitHub release...")
        create_github_release(new_version, artifacts, dry_run=args.dry_run)

    print("\n=== Versioning Complete ===")


if __name__ == '__main__':
    main()







