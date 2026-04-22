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
    'breaking':  ('major_bump', 'A backwards incompatible change to the API or Tools'),
    'rewrite':   ('major_bump', 'A significant rewrite of a major component or subsystem'),
    'milestone': ('major_bump', 'A significant milestone or achievement, such as a major feature completion or project phase'),
    'deprecate': ('major_bump', 'Deprecation of a major feature or API, signaling that it will be removed in a future release'),
    'eos':       ('major_bump', 'End of support for a major version or platform'),
    'security':  ('major_bump', 'A security fix that addresses a critical vulnerability'),
    'license':   ('major_bump', 'Changes to licensing or legal documentation'),
    'feature':   ('minor_bump', 'A new feature or enhancement to existing functionality'),
    'fix':       ('patch_bump', 'A bug fix or patch that addresses a specific issue'),
    'refactor':  ('patch_bump', 'A code change that improves internal structure or readability without changing external behavior'),
    'docs':      ('no_release', 'Documentation changes, including updates to README, docstrings, or other non-code content'),
    'test':      ('no_release', 'Changes to test code or test coverage, without affecting production code'),
    'chore':     ('no_release', 'General maintenance tasks, such as build scripts, CI configuration, or other non-feature, non-fix changes'),
}

COMMIT_OUTPUT_MESSAGE = {
    'no_bump': "Commit flagged as {commit_type}({scope}) ({description}). Not building a release.",
    'patch_bump': "Commit flagged as {commit_type} ({description}). Incrementing patch version.",
    'minor_bump': "Commit flagged as {commit_type} ({description}). Incrementing minor version.",
    'major_bump': "Commit flagged as {commit_type} ({description}). Incrementing major version.",
}

# Scopes that suppress version bumping regardless of commit type.
NO_RELEASE_SCOPES = {'ci', 'tools'}


def determine_bump(commits: List[str]) -> str:
    """
    Determine the semantic version bump based on commits.
    Returns 'major', 'minor', 'patch', or 'none' when all commits are docs/test/chore-only
    or scoped to a no-release scope (e.g. 'ci', 'tools').
    """
    has_major = False
    has_minor = False
    has_patch = False
    has_none = False

    for commit_hash in commits:
        subject, body = get_commit_message(commit_hash)

        bump_check_result = re.match(r'^([a-zA-Z0-9]+)\((.*)\)([*!]*):', subject)
        bump_check_metadata = bump_check_result.groups() if bump_check_result else None
        if bump_check_metadata:
            if bump_check_metadata is None:
                continue
            commit_type_match = bump_check_metadata[0]
            commit_scope_match = bump_check_metadata[1]
            override_flag_match = bump_check_metadata[2]
            commit_type = COMMIT_TYPES.get(commit_type_match, '')
            bump_action = commit_type[0] if commit_type else 'unknown'
            commit_response_msg = COMMIT_OUTPUT_MESSAGE.get(commit_type[0], None)
            if commit_response_msg is None:
                raise ValueError(f"Unknown commit type {commit_type_match}")

            if override_flag_match and override_flag_match == "!":
                print("** Breaking Change Escalation Override Enabled **")
                has_major = True
            elif override_flag_match and override_flag_match == "*":
                print("** Breaking Change Downgrading Exception Override Enabled **")
                has_minor = True
            elif bump_action == 'no_release':
                has_none = True
            elif bump_action == 'patch_bump':
                has_patch = True
            elif bump_action == 'minor_bump':
                has_minor = True
            elif bump_action == 'major_bump':
                print(commit_response_msg.format(commit_type=commit_type_match, scope=commit_scope_match, description=commit_type[1]))
                has_major = True
            else:
                raise ValueError(f"Unknown bump action {bump_action} for commit type {commit_type_match}")
            print(commit_response_msg.format(commit_type=commit_type_match, scope=commit_scope_match, description=commit_type[1]))
            break
        else:
            ValueError(f"Commit {commit_hash} does not match expected format. Cannot determine bump type.")

    if has_major:
        bump = 'major'
    elif has_minor:
        bump = 'minor'
    elif has_patch:
        bump = 'patch'
    elif has_none:
        bump = 'none'
    else:
        raise ValueError(f"No recognised commit type found in {len(commits)} commit(s). Cannot determine bump type.")

    print(f"Determined bump type: {bump}")
    return bump

def increment_version(version: str, bump: str) -> Optional[str]:
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
    elif bump == 'none':
        pass  # No version change
    else:
        raise ValueError(f"Unknown Increment Type: {bump}")

    if bump == 'none':
        return None
    else:
        return f'{major}.{minor}.{patch}'


def determine_new_version(current_version: str, commits: List[str], force_bump: Optional[str] = None) -> Tuple[Optional[str], str]:
    """
    Determine the new version based on current version and commits.

    Args:
        current_version: The current semantic version string (e.g. '1.2.3').
        commits: List of commit hashes since the last version tag.
        force_bump: Optional override for bump type ('major', 'minor', or 'patch').
                    When provided, skips commit analysis and uses this bump type directly.

    Returns:
        A tuple of (new_version, bump_used). new_version is None when there is nothing
        to version. bump_used is 'none' when all commits are docs/test/chore-only or
        when there are no commits and no force_bump.
    """
    if not commits and not force_bump:
        print("No new commits since last version")
        return None, 'none'

    if current_version == '0.0.0':
        # Apply forced bump from initial version, or default to 0.0.1
        bump = force_bump or 'patch'
        first_version = increment_version(current_version, bump)
        if force_bump:
            print(f"No previous version found. Setting first version to {first_version} (forced {force_bump})")
        else:
            print(f"No previous version found. Setting first version to {first_version}")
        return first_version, bump

    # Use forced bump if provided, otherwise analyse commits
    if force_bump:
        bump = force_bump
        print(f"Using forced bump type: {bump}")
    else:
        bump = determine_bump(commits)

    if bump == 'none':
        print("No version-bumping commits found. Skipping release.")
        return None, 'none'

    new_version = increment_version(current_version, bump)
    return new_version, bump


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
    new_version, bump_used = determine_new_version(current_version, commits, force_bump)

    # Output version and bump type for GitHub Actions
    github_output = os.environ.get('GITHUB_OUTPUT', None)
    if github_output:
        with open(github_output, 'a') as f:
            f.write(f'version={new_version}\n')
            f.write(f'bump={bump_used}\n')

    if bump_used == 'none':
        print("No release needed based on commit analysis. Exiting.")
        sys.exit(0)
    elif new_version is None:
        print("Cannot determine new version")
        sys.exit(1)

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
