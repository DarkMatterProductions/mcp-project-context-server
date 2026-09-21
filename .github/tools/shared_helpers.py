import platform
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from constants import RELEASE_OVERRIDE_SCOPES, COMMIT_TYPES
from regex_patterns import MERGE_REGEX, TYPE_COPE_REGEX

GH_CMD = "gh.exe" if platform.system() == "Windows" else "gh"
GH_API_URL = "https://api.github.com/repos/cli/cli/releases/latest"
INSTALL_DIR = Path.home() / "bin"
GIT_CMD = 'git.exe' if platform.system() == 'Windows' else 'git'


def key_id_lookup(_type_scope_match: re.Match, mapping: dict) -> dict[str, str | bool]:
    if _type_scope_match is not None:
        __type_id = _type_scope_match.group("type") if _type_scope_match.group("type") != '' else None
        __scope_id = _type_scope_match.group("scope") if _type_scope_match.group("scope") != '' else None
        __force_major = True if _type_scope_match.group("force_major") != '' else False
        __scope_skip_version = True if _type_scope_match.group("scope") in RELEASE_OVERRIDE_SCOPES else False
        key_ids = [key_id for key_id in mapping.keys() if key_id is not None and (key_id.startswith(__type_id) if __type_id else False)]
        for key_id in key_ids:
            type_id = mapping[key_id].copy()
            type_id["force_major"] = __force_major
            type_id["scope_id"] = __scope_id
            type_id["skip_version"] = __scope_skip_version
            type_id["bump_type"] = (
                RELEASE_OVERRIDE_SCOPES[_type_scope_match.group("scope")]["bump_type"]
                if __scope_skip_version
                else type_id["bump_type"]
            )
            return type_id
    return {'name': 'invalid', 'description': 'Invalid Type', 'bump_type': 'invalid', 'force_major': False,  'skip_version': False}


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


def get_last_version() -> str:
    """Get the last semantic version tag, or return 0.0.0 if none exist."""
    try:
        # Get tags merged into the current commit (HEAD resolves correctly
        # even in a detached-HEAD checkout, e.g. in CI)
        result = subprocess.run(
            [GIT_CMD, 'tag', '--merged', 'HEAD'],
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


def analyze_commits(commits: List[str]) -> defaultdict[Any, Dict[str, str | Dict[str, str]]]:
    type_id_entry = lambda typescope_match: key_id_lookup(typescope_match, COMMIT_TYPES)
    commit_ids: defaultdict[Any, Dict[str, str | Dict[str, str]]] = defaultdict(Dict)

    for commit_hash in commits:
        commit_ids[commit_hash] = get_commit_message(commit_hash)
        commit_ids[commit_hash]["hash"] = commit_hash
        commit_ids[commit_hash]["short_hash"] = commit_hash[:7]
        if re.match(MERGE_REGEX, commit_ids[commit_hash]["subject"]):
            merge_type = COMMIT_TYPES['merge'].copy()
            merge_type["force_major"] = False
            merge_type["skip_version"] = False
            commit_ids[commit_hash]["type_id"] = merge_type
        else:
            type_scope_match = re.match(TYPE_COPE_REGEX, commit_ids[commit_hash]["subject"])
            commit_ids[commit_hash]["type_id"] = type_id_entry(type_scope_match)

    return commit_ids

def determine_bump(commits: List[str], verbose: bool=False, debug: bool=False) -> Optional[str]:
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
    commit_ids: defaultdict[Any, Dict[str, str | Dict[str, str]]] = analyze_commits(commits)

    for commit_hash in commits:
        if commit_ids[commit_hash]["type_id"] is None:
            raise ValueError(f"\"type_id_entry()\" should not have returned None for commit {commit_ids[commit_hash]['hash']} with subject: {commit_ids[commit_hash]['subject']}")
        elif commit_ids[commit_hash]["type_id"]["force_major"] and not commit_ids[commit_hash]["type_id"]["skip_version"]:
            has_major = True
            print("** FORCE MAJOR OVERRIDE ENABLED **")
            print("  Skipping version bump analysis.")
            print()
        elif commit_ids[commit_hash]["type_id"]["bump_type"] == "major" and not commit_ids[commit_hash]["type_id"]["skip_version"]:
            has_major = True
        elif commit_ids[commit_hash]["type_id"]["bump_type"] == "minor" and not commit_ids[commit_hash]["type_id"]["skip_version"]:
            has_minor = True
        elif commit_ids[commit_hash]["type_id"]["bump_type"] == "patch" and not commit_ids[commit_hash]["type_id"]["skip_version"]:
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
                print(f"    Commit {commit_hash['hash']} has no recognized type in subject: '{commit_hash['subject']}'")
            print(f"Unrecognized types identified in {invalid_count} commit(s) subject line(s). Exiting process.")
        else:
            print("\nNo valid commits found.")
        return 'invalid'
    elif has_major:
        bump = "major"
    elif has_minor:
        bump = "minor"
    elif has_patch:
        bump = "patch"
    elif has_none:
        bump = "none"
    else:
        return 'invalid'
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
        return version
    else:
        return f'{major}.{minor}.{patch}'


def determine_new_version(
        current_version: str, commits: List[str], force_bump: Optional[str] = None,
        verbose: bool = False, debug: bool = False) -> Tuple[Optional[str], str]:
    """
    Determine the new version based on the current version and commits.

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

    new_version = increment_version(current_version, bump)
    return new_version, bump