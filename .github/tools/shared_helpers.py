import re

from constants import RELEASE_OVERRIDE_SCOPES, COMMIT_TYPES


def key_id_lookup(_type_scope_match: re.Match, mapping: dict) -> dict[str, str | bool]:
    __type_id = _type_scope_match.group("type") if _type_scope_match.group("type") != '' else None
    __scope_id = _type_scope_match.group("scope") if _type_scope_match.group("scope") != '' else None
    __force_major = True if _type_scope_match.group("force_major") != '' else False
    __bump_type = (COMMIT_TYPES[_type_scope_match.group("type")]["bump_type"] if _type_scope_match.group("scope") not in RELEASE_OVERRIDE_SCOPES else RELEASE_OVERRIDE_SCOPES[_type_scope_match.group("scope")]["bump_type"]) if _type_scope_match.group("type") != '' else None
    __scope_skip_version = True if _type_scope_match.group("scope") in RELEASE_OVERRIDE_SCOPES else False
    key_ids = [key_id for key_id in mapping.keys() if key_id is not None and (key_id.startswith(__type_id) if __type_id else False)]
    for key_id in key_ids:
        type_id = mapping[key_id].copy()
        type_id["force_major"] = __force_major
        type_id["scope_id"] = __scope_id
        type_id["skip_version"] = __scope_skip_version
        type_id["bump_type"] = __bump_type
        return type_id
    return {'name': 'invalid', 'description': 'Invalid Type', 'bump_type': 'invalid', 'force_major': False,  'skip_version': False}