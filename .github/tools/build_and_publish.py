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
from collections import defaultdict
from pathlib import Path
from typing import Tuple, List, Optional, Dict, Any

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


def get_commit_message(commit_hash: str) -> Dict[str, str]:
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
        return {
            "subject": subject,
            "body": body
        }
    except subprocess.CalledProcessError as e:
        print(f"Error getting commit message for {commit_hash}: {e}")
        if e.stdout:
            print(f"stdout: {e.stdout.strip()}")
        if e.stderr:
            print(f"stderr: {e.stderr.strip()}")
        return {
            "subject": "",
            "body": ""
        }
    except Exception as e:
        print(f"Error getting commit message for {commit_hash}: {e}")
        return {
            "subject": "",
            "body": ""
        }


COMMIT_TYPES = {
    'breaking': {'name': 'breaking', 'description': 'A backwards incompatible change to the API or Tools', 'bump_type': 'major'},
    'rewrite': {'name': 'rewrite', 'description': 'Complete rewrites / architectural overhauls', 'bump_type': 'major'},
    'milestone': {'name': 'milestone', 'description': 'Significant feature milestones / stable releases', 'bump_type': 'major'},
    'deprecate': {'name': 'deprecate', 'description': 'Major deprecation cleanups', 'bump_type': 'major'},
    'eos': {'name': 'eos', 'description': 'End of support for a runtime/platform', 'bump_type': 'major'},
    'license': {'name': 'license', 'description': 'License changes', 'bump_type': 'major'},
    'security': {'name': 'security', 'description': 'Security-mandated incompatible changes', 'bump_type': 'major'},
    'feature': {'name': 'feature', 'description': 'A new feature or capability', 'bump_type': 'minor'},
    'fix': {'name': 'fix', 'description': 'A bug fix', 'bump_type': 'minor'},
    'test': {'name': 'test', 'description': 'Adding or updating tests', 'bump_type': 'none'},
    'docs': {'name': 'docs', 'description': 'Documentation changes only', 'bump_type': 'none'},
    'refactor': {'name': 'refactor', 'description': 'Code restructuring with no behaviour change', 'bump_type': 'minor'},
    'chore': {'name': 'chore', 'description': 'Build system, tooling, or dependency changes', 'bump_type': 'none'},
    'adrs': {'name': 'adrs', 'description': 'Adding or updating an Architecture Decision Record', 'bump_type': 'minor'},
}


INCREMENT_BUMP_TYPE_MESSAGES = {
    'major': 'Incrementing major version.',
    'minor': 'Incrementing minor version.',
    'patch': 'Incrementing patch version.',
    'none': 'No version change.',
}


RELEASE_OVERRIDE_SCOPES = {
    'ci': {'name': 'ci', 'description': 'Changes to CI configuration files and scripts', 'bump_type': 'none'},
    'tools': {'name': 'tools', 'description': 'Changes to build, release, or dependency tools', 'bump_type': 'none'},
    'packaging': {'name': 'packaging', 'description': 'Changes to packaging configuration files and scripts', 'bump_type': 'none'},
}


def key_id_lookup(_type_scope_match: str, mapping: dict) -> dict[str, str | bool]:
    __type_id = _type_scope_match.group("type") if _type_scope_match else None
    __force_major = _type_scope_match.group("force_major") if _type_scope_match else False
    __scope_skip_version = _type_scope_match.group("scope") if _type_scope_match else False
    key_ids = [key_id for key_id in mapping.keys() if key_id is not None and (key_id.startswith(__type_id) if __type_id else False)]
    for key_id in key_ids:
        type_id = mapping[key_id].copy()
        type_id["force_major"] = __force_major
        type_id["skip_version"] = __scope_skip_version
        return type_id
    return {'name': 'invalid', 'description': 'Invalid Type', 'bump_type': 'invalid', 'force_major': False, 'skip_version': False}


def determine_bump(commits: List[str], verbose: bool = False, debug: bool=False) -> str:
    """
    Determine the semantic version bump based on commits.
    Returns 'major', 'minor', 'patch', or 'none' when all commits are docs/test/chore-only
    or scoped to a no-release scope (e.g. 'ci', 'tools').
    """
    has_major = False
    has_minor = False
    has_patch = False
    has_none = False
    has_invalid = False
    type_id_entry = lambda typescope_match: key_id_lookup(typescope_match, COMMIT_TYPES)
    commit_ids: defaultdict[Any, dict[str, str | Dict[str, str]]] = defaultdict(dict)

    for commit_hash in commits:
        commit_ids[commit_hash] = get_commit_message(commit_hash)
        commit_ids[commit_hash]["hash"] = commit_hash
        commit_ids[commit_hash]["short_hash"] = commit_hash[:7]
        type_scope_match = re.match(r'(?P<type>\w+)(?P<force_major>!?)\((?P<scope>\w+)\):[ ]+', commit_ids[commit_hash]["subject"])
        commit_ids[commit_hash]["type_id"] = type_id_entry(type_scope_match)

        if commit_ids[commit_hash]["type_id"] is None:
            raise ValueError(f"\"type_id_entry()\" should not have returned None for commit {commit_ids[commit_hash]['hash']} with subject: {commit_ids[commit_hash]['subject']}")
        elif commit_ids[commit_hash]["type_id"]["force_major"] and not commit_ids[commit_hash]["type_id"]["skip_version"]:
            has_major = True
            print("** FORCE MAJOR OVERRIDE ENABLED **")
            print("  Skipping version bump analysis.")
            print()
        elif commit_ids[commit_hash]["type_id"]["bump_type"] == "major":
            has_major = True
        elif commit_ids[commit_hash]["type_id"]["bump_type"] == "minor":
            has_minor = True
        elif commit_ids[commit_hash]["type_id"]["bump_type"] == "patch":
            has_patch = True
        elif commit_ids[commit_hash]["type_id"]["bump_type"] == "none" or commit_ids[commit_hash]["type_id"]["skip_version"]:
            has_none = True
        elif commit_ids[commit_hash]["type_id"]["bump_type"] == "invalid":
            has_invalid = True


    for commit_data in commit_ids.values():
        if debug:
            if commit_data["type_id"]:
                print(f"Commit {commit_data['hash']}: ({commit_data['type_id']['name']}: {commit_data['subject']})")

    if not any([has_major, has_minor, has_patch, has_none]) or has_invalid:
        invalid_commits = [commit_ids[commit_hash] for commit_hash in commits if commit_ids[commit_hash]["type_id"] is None or commit_ids[commit_hash]["type_id"]["bump_type"] == "invalid"]
        invalid_count = len(invalid_commits)
        if invalid_count > 0:
            print("\nInvalid commit details -")
            for commit_hash in invalid_commits:
                if debug:
                    print(f"    Commit {commit_hash['hash']} has no recognized type in subject: '{commit_hash['subject']}'")
            print(f"Unrecognized types identified in {invalid_count} commit(s) subject line(s). Exiting process.")
        else:
            print("\nNo valid commits found. Exiting process.")
        sys.exit(-1)
    elif has_major:
        bump = "major"
    elif has_minor:
        bump = "minor"
    elif has_patch:
        bump = "patch"
    elif has_none:
        bump = "none"
    else:
        raise ValueError(f"Cannot determine bump type.")


    print()
    print(f"Determined bump type: {bump} ({INCREMENT_BUMP_TYPE_MESSAGES[bump]})")
    return bump

def increment_version(version: str, bump: str) -> Optional[str]:
    """Increment the version based on bump type."""
    major, minor, patch = map(int, version.split('.'))

    if bump == "major":
        major += 1
        minor = 0
        patch = 0
    elif bump == "minor":
        minor += 1
        patch = 0
    elif bump == "patch":
        patch += 1
    elif bump == "none":
        pass  # No version change
    else:
        raise ValueError(f"Unknown Increment Type: {bump}")

    if bump == "none":
        return None
    else:
        return f'{major}.{minor}.{patch}'


def determine_new_version(current_version: str, commits: List[str], force_bump: Optional[str] = None, verbose: bool = False, debug: bool = False) -> Tuple[Optional[str], str]:
    """
    Determine the new version based on current version and commits.

    Args:
        current_version: The current semantic version string (e.g. '1.2.3').
        commits: List of commit hashes since the last version tag.
        force_bump: Optional override for bump type ('major', 'minor', or 'patch').
                    When provided, skips commit analysis and uses this bump type directly.
        verbose: Whether to print verbose output.
        debug: Whether to print debug output.

    Returns:
        A tuple of (new_version, bump_used). new_version is None when there is nothing
        to version. bump_used is 'none' when all commits are docs/test/chore-only or
        when there are no commits and no force_bump.
    """
    if not commits and not force_bump:
        print("No new commits since last version")
        return None, "none"

    if current_version == '0.0.0':
        # Apply forced bump from initial version, or default to 0.0.1
        bump = force_bump or "patch"
        first_version = increment_version(current_version, bump)
        if force_bump:
            print(f"No previous version found. Setting first version to {first_version} (forced {force_bump})")
        else:
            print(f"No previous version found. Setting first version to {first_version}")
        return first_version, bump

    # Use forced bump if provided, otherwise analyze commits
    if force_bump:
        bump = force_bump
        print(f"Using forced bump type: {bump}")
    else:
        bump = determine_bump(commits, verbose, debug)

    if bump == "none":
        print("No version-bumping commits found. Skipping release.")
        return None, "none"

    new_version = increment_version(current_version, bump)
    return new_version, bump


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
    parser.add_argument('--publish', action="store_true",
                        help='Publish a GitHub release with built artifacts (requires --build)')
    parser.add_argument('--dry-run', action="store_true",
                        help='Perform a dry run without creating tags, builds, or releases')
    parser.add_argument('--verbose', action="store_true",
                        help='Enable verbose output for expanded console output')
    parser.add_argument('--debug', action="store_true",
                        help='Enable debug output')

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
        force_bump = "major"
    elif args.minor:
        force_bump = "minor"
    elif args.patch:
        force_bump = "patch"
    else:
        force_bump = None

    # Step 4: Determine new base version
    new_version, bump_used = determine_new_version(current_version, commits, force_bump, args.verbose, args.debug)

    # Output version and bump type for GitHub Actions
    github_output = os.environ.get("GITHUB_OUTPUT", None)
    if github_output:
        with open(github_output, "a") as f:
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
