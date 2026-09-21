import platform
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from typing import List, Any, Dict, Literal
from constants import COMMIT_TYPES

# ── Constants ────────────────────────────────────────────────────────────────
GH_CMD = "gh.exe" if platform.system() == "Windows" else "gh"
GH_API_URL = "https://api.github.com/repos/cli/cli/releases/latest"
INSTALL_DIR = Path.home() / "bin"
GIT_CMD = 'git.exe' if platform.system() == 'Windows' else 'git'


def key_id_lookup(_type_scope_match: re.Match, mapping: Dict) -> Dict[str, str | bool]:
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

def validate_commit_messages(commits: List[str]) -> str:
    """
    Determine the semantic version bump based on commits.
    Returns 'major', 'minor', 'patch', or 'none' when all commits are docs/test/chore-only
    or scoped to a no-release scope (e.g. 'ci', 'tools').
    """
    type_id_entry = lambda typescope_match: key_id_lookup(typescope_match, COMMIT_TYPES)
    commit_ids: defaultdict[Any, Dict[str, str | Dict[str, str]]] = defaultdict(dict)

    for commit_hash in commits:
        commit_ids[commit_hash] = get_commit_message(commit_hash)
        commit_ids[commit_hash]["hash"] = commit_hash
        commit_ids[commit_hash]["short_hash"] = commit_hash[:7]
        subject = commit_ids[commit_hash]["subject"]
        if re.match(r'^Merge\b', subject):
            merge_type = COMMIT_TYPES['merge'].copy()
            merge_type["force_major"] = False
            merge_type["skip_version"] = False
            commit_ids[commit_hash]["type_id"] = merge_type
        else:
            type_scope_match = re.match(r'(?P<type>\w+)(?P<force_major>!?)\((?P<scope>\w+)\):[ ]+', subject)
            commit_ids[commit_hash]["type_id"] = type_id_entry(type_scope_match)

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
    return analyzed_commits

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Validate commit messages")
    parser.add_argument("-s", "--source", default="HEAD",  action="store", help="Name of source branch to validate")
    parser.add_argument("-d", "--destination", default="main", action="store", help="Name of source branch to validate")
    args = parser.parse_args()

    print("Validating commit messages...")

    unvalidated_commits = get_commits_since_branch_head(args.source, args.destination)
    validated_commits = validate_commit_messages(unvalidated_commits)


    for commit_hash in validated_commits["valid"]["commits"]:
        print(f"    Commit {commit_hash['hash']} has recognized commit type (Type: {COMMIT_TYPES[commit_hash['type_id']['name']]['name']} - Bump: {COMMIT_TYPES[commit_hash['type_id']['name']]['bump_type']}) in subject: '{commit_hash['subject']}'")

    if validated_commits["invalid"]["count"] > 0:
        print("\nInvalid commit details -")
        for commit_hash in validated_commits["invalid"]["commits"]:
            print(f"    Commit {commit_hash['hash']} has no recognized type in subject: '{commit_hash['subject']}'")
        print(f"Unrecognized types identified in {validated_commits['invalid']['count']} commit(s) subject line(s). Exiting process.")
        sys.exit(-1)