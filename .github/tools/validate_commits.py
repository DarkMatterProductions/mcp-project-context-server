import platform
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from typing import List, Any, Dict, Literal
from shared_helpers import key_id_lookup, get_last_version, analyze_commits, determine_new_version
from constants import COMMIT_TYPES, RELEASE_OVERRIDE_SCOPES
from regex_patterns import TYPE_COPE_REGEX

# ── Constants ────────────────────────────────────────────────────────────────
GH_CMD = "gh.exe" if platform.system() == "Windows" else "gh"
GH_API_URL = "https://api.github.com/repos/cli/cli/releases/latest"
INSTALL_DIR = Path.home() / "bin"
GIT_CMD = 'git.exe' if platform.system() == 'Windows' else 'git'


def get_commits_since_branch_head(source: str = "HEAD", destination:str = "main") -> List[str]:
    """Get commit hashes since the given tag."""
    try:
        # Get commits since the tag
        result = subprocess.run(
            [GIT_CMD, 'rev-list', f'{source}...{destination}'],
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

def validate_commit_messages(commits: List[str]) -> Dict[str, Dict[str, List[Dict[str, str | Dict[str, str]]] | int]]:
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
        if commit_ids[commit_hash]["type_id"]["force_major"] and not commit_ids[commit_hash]["type_id"]["skip_version"]:
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

    invalid_commits = [commit_ids[commit_hash] for commit_hash in commits if commit_ids[commit_hash]["type_id"] is None or commit_ids[commit_hash]["type_id"]["bump_type"] == "invalid"]
    valid_commits = [commit_ids[commit_hash] for commit_hash in commits if commit_ids[commit_hash]["type_id"] is not None and commit_ids[commit_hash]["type_id"]["bump_type"] != "invalid"]
    analyzed_commits: Dict[Literal["invalid", "valid"], Dict[Literal["commits", "count"], List[Dict[str, str | Dict[str, str]]] | int]] = {
        "invalid": {
            "commits": invalid_commits,
            "count": len(invalid_commits),
        },
        "valid": {
            "commits": valid_commits,
            "count": len(valid_commits),
        }
    }

    if has_major:
        bump = ("major", "X.0.0")
    elif has_minor:
        bump = ("minor", "0.X.0")
    elif has_patch:
        bump = ("patch", "0.0.X")
    elif has_none:
        bump = ("none", "N.N.N")
    elif has_invalid:
        bump = ("invalid", None)
    else:
        print("\nNo valid commits found to determine bump.")
        bump = None

    if bump is not None:
        print(f"\nBump type: {bump[0]} ({bump[1]})")

    return analyzed_commits, bump

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Validate commit messages")
    parser.add_argument("-s", "--source", default="HEAD",  action="store", help="Name of source branch to validate")
    parser.add_argument("-d", "--destination", default="main", action="store", help="Name of source branch to validate")
    args = parser.parse_args()

    print("Validating commit messages...")

    unvalidated_commits = get_commits_since_branch_head(args.source, args.destination)
    validated_commits, bump = validate_commit_messages(unvalidated_commits)

    print("Valid Commits:")
    if validated_commits["valid"]["commits"]:
        for commit_hash in validated_commits["valid"]["commits"]:
            scope_skip_versioning = f" (Scope Enforced Skip Version Increment)" if commit_hash["type_id"]["skip_version"] else f""
            _scope_id = commit_hash['type_id']['scope_id'] if 'scope_id' in commit_hash['type_id'].keys() else "ci"
            print(f"    Commit {commit_hash['hash']} has recognized commit type (Type: {COMMIT_TYPES[commit_hash['type_id']['name']]['name']} - Scope: {_scope_id} / Bump: {commit_hash['type_id']['bump_type']}{scope_skip_versioning}) in subject: '{commit_hash['subject']}'")
    else:
        print("    No valid commits found.")

    if validated_commits["invalid"]["count"] > 0:
        print("\nInvalid commit details -")
        for commit_hash in validated_commits["invalid"]["commits"]:
            print(f"    Commit {commit_hash['hash']} has no recognized type in subject: '{commit_hash['subject']}'")
        print(f"Unrecognized 'type(scope):' header identified in {validated_commits['invalid']['count']} commit(s) subject line(s)."
              f" All headers must adhere to the pattern '{TYPE_COPE_REGEX}'  Exiting process.")
        sys.exit(-1)

    current_version = get_last_version()
    print(f"Current version: {current_version}")
    print()
    new_version, bump_used = determine_new_version(current_version, unvalidated_commits, None, False, False)
    print(f"New version: {new_version} Enforced Bump Type: {bump_used}")
    print()