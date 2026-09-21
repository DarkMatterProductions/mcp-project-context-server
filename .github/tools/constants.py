COMMIT_TYPES = {
    'breaking': {'name': 'breaking', 'description': 'A backwards incompatible change to the API or Tools', 'bump_type': 'major'},
    'rewrite': {'name': 'rewrite', 'description': 'Complete rewrites / architectural overhauls', 'bump_type': 'major'},
    'milestone': {'name': 'milestone', 'description': 'Significant feature milestones / stable releases', 'bump_type': 'major'},
    'deprecate': {'name': 'deprecate', 'description': 'Major deprecation cleanups', 'bump_type': 'major'},
    'eos': {'name': 'eos', 'description': 'End of support for a runtime/platform', 'bump_type': 'major'},
    'license': {'name': 'license', 'description': 'License changes', 'bump_type': 'major'},
    'security': {'name': 'security', 'description': 'Security-mandated incompatible changes', 'bump_type': 'major'},
    'feature': {'name': 'feature', 'description': 'A new feature or capability', 'bump_type': 'minor'},
    'fix': {'name': 'fix', 'description': 'A bug fix', 'bump_type': 'patch'},
    'test': {'name': 'test', 'description': 'Adding or updating tests', 'bump_type': 'none'},
    'docs': {'name': 'docs', 'description': 'Documentation changes only', 'bump_type': 'none'},
    'refactor': {'name': 'refactor', 'description': 'Code restructuring with no behaviour change', 'bump_type': 'minor'},
    'chore': {'name': 'chore', 'description': 'Build system, tooling, or dependency changes', 'bump_type': 'none'},
    'adrs': {'name': 'adrs', 'description': 'Adding or updating an Architecture Decision Record', 'bump_type': 'minor'},
    'merge': {'name': 'merge', 'description': 'Merge commits (e.g. branch updates)', 'bump_type': 'none'},
}

INCREMENT_BUMP_TYPE_MESSAGES = {
    'major': 'Incrementing major version',
    'minor': 'Incrementing minor version',
    'patch': 'Incrementing patch versio.',
    'none': 'Skip building and publishing artifacts',
}

RELEASE_OVERRIDE_SCOPES = {
    'ci': {'name': 'ci', 'description': 'Changes to CI configuration files and scripts', 'bump_type': 'none'},
    'tools': {'name': 'tools', 'description': 'Changes to build, release, or dependency tools', 'bump_type': 'none'},
    'changelog': {'name': 'changelog', 'description': 'Changes to CHANGELOG.md', 'bump_type': 'none'},
    'packaging': {'name': 'packaging', 'description': 'Changes to packaging configuration files and scripts', 'bump_type': 'none'},
}