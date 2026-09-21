#!/usr/bin/env python3
"""
Unit tests for shared_helpers.py
"""
import subprocess
import unittest
from unittest.mock import MagicMock, patch

import shared_helpers as sh


# ---------------------------------------------------------------------------
# get_distance_from_main
# ---------------------------------------------------------------------------
class TestGetDistanceFromMain(unittest.TestCase):
    @patch('shared_helpers.subprocess.run')
    def test_returns_commit_count(self, mock_run):
        mock_run.return_value = MagicMock(stdout='3\n')
        self.assertEqual(sh.get_distance_from_main(), 3)

    @patch('shared_helpers.subprocess.run')
    def test_returns_zero_and_prints_stdout_on_called_process_error_with_output(self, mock_run):
        err = subprocess.CalledProcessError(1, 'git')
        err.stdout = 'some stdout'
        err.stderr = 'some stderr'
        mock_run.side_effect = err
        with patch('builtins.print') as mock_print:
            result = sh.get_distance_from_main()
        self.assertEqual(result, 0)
        printed = ' '.join(str(c) for c in mock_print.call_args_list)
        self.assertIn('some stdout', printed)
        self.assertIn('some stderr', printed)

    @patch('shared_helpers.subprocess.run', side_effect=subprocess.CalledProcessError(1, 'git'))
    def test_returns_zero_on_called_process_error(self, _):
        self.assertEqual(sh.get_distance_from_main(), 0)

    @patch('shared_helpers.subprocess.run', side_effect=Exception('boom'))
    def test_returns_zero_on_generic_exception(self, _):
        self.assertEqual(sh.get_distance_from_main(), 0)


# ---------------------------------------------------------------------------
# get_current_git_hash
# ---------------------------------------------------------------------------
class TestGetCurrentGitHash(unittest.TestCase):
    @patch('shared_helpers.subprocess.run')
    def test_returns_hash(self, mock_run):
        mock_run.return_value = MagicMock(stdout='abc1234\n')
        self.assertEqual(sh.get_current_git_hash(), 'abc1234')

    @patch('shared_helpers.subprocess.run')
    def test_returns_unknown_and_prints_stdout_on_called_process_error_with_output(self, mock_run):
        err = subprocess.CalledProcessError(1, 'git')
        err.stdout = 'some stdout'
        err.stderr = 'some stderr'
        mock_run.side_effect = err
        with patch('builtins.print') as mock_print:
            result = sh.get_current_git_hash()
        self.assertEqual(result, 'unknown')
        printed = ' '.join(str(c) for c in mock_print.call_args_list)
        self.assertIn('some stdout', printed)
        self.assertIn('some stderr', printed)

    @patch('shared_helpers.subprocess.run', side_effect=subprocess.CalledProcessError(1, 'git'))
    def test_returns_unknown_on_called_process_error(self, _):
        self.assertEqual(sh.get_current_git_hash(), 'unknown')

    @patch('shared_helpers.subprocess.run', side_effect=Exception('boom'))
    def test_returns_unknown_on_generic_exception(self, _):
        self.assertEqual(sh.get_current_git_hash(), 'unknown')


# ---------------------------------------------------------------------------
# get_commit_message
# ---------------------------------------------------------------------------
class TestGetCommitMessage(unittest.TestCase):
    @patch('shared_helpers.subprocess.run')
    def test_returns_subject_and_body(self, mock_run):
        mock_run.return_value = MagicMock(stdout='fix(scope): something\nbody text\n')
        message = sh.get_commit_message('abc123')
        self.assertEqual(message['subject'], 'fix(scope): something')
        self.assertIn('body text', message['body'])

    @patch('shared_helpers.subprocess.run')
    def test_returns_subject_only_when_no_body(self, mock_run):
        mock_run.return_value = MagicMock(stdout='fix(scope): something')
        message = sh.get_commit_message('abc123')
        self.assertEqual(message['subject'], 'fix(scope): something')
        self.assertEqual(message['body'], '')

    @patch('shared_helpers.subprocess.run', side_effect=subprocess.CalledProcessError(1, 'git'))
    def test_returns_empty_strings_on_called_process_error(self, _):
        self.assertEqual(sh.get_commit_message('abc123'), {'subject': '', 'body': ''})

    @patch('shared_helpers.subprocess.run')
    def test_returns_empty_strings_and_prints_stdout_on_called_process_error_with_output(self, mock_run):
        err = subprocess.CalledProcessError(1, 'git')
        err.stdout = 'some stdout'
        err.stderr = 'some stderr'
        mock_run.side_effect = err
        with patch('builtins.print') as mock_print:
            result = sh.get_commit_message('abc123')
        self.assertEqual(result, {'subject': '', 'body': ''})
        printed = ' '.join(str(c) for c in mock_print.call_args_list)
        self.assertIn('some stdout', printed)
        self.assertIn('some stderr', printed)

    @patch('shared_helpers.subprocess.run', side_effect=Exception('boom'))
    def test_returns_empty_strings_on_generic_exception(self, _):
        self.assertEqual(sh.get_commit_message('abc123'), {'subject': '', 'body': ''})


# ---------------------------------------------------------------------------
# determine_bump
# ---------------------------------------------------------------------------
class TestDetermineBump(unittest.TestCase):
    @patch('shared_helpers.get_commit_message')
    def test_major_bump_on_breaking_type(self, mock_msg):
        mock_msg.return_value = {'subject': 'breaking(api): remove endpoint', 'body': ''}
        self.assertEqual(sh.determine_bump(['abc']), 'major')

    @patch('shared_helpers.get_commit_message')
    def test_major_bump_on_rewrite_type(self, mock_msg):
        mock_msg.return_value = {'subject': 'rewrite(core): full overhaul', 'body': ''}
        self.assertEqual(sh.determine_bump(['abc']), 'major')

    @patch('shared_helpers.get_commit_message')
    def test_major_bump_on_feature_bang(self, mock_msg):
        mock_msg.return_value = {'subject': 'feature!(scope): new breaking feature', 'body': ''}
        self.assertEqual(sh.determine_bump(['abc']), 'major')

    @patch('shared_helpers.get_commit_message')
    def test_major_bump_on_fix_bang(self, mock_msg):
        mock_msg.return_value = {'subject': 'fix!(scope): breaking fix', 'body': ''}
        self.assertEqual(sh.determine_bump(['abc']), 'major')

    @patch('shared_helpers.get_commit_message')
    def test_minor_bump_on_feature_type(self, mock_msg):
        mock_msg.return_value = {'subject': 'feature(scope): new feature', 'body': ''}
        self.assertEqual(sh.determine_bump(['abc']), 'minor')

    @patch('shared_helpers.get_commit_message')
    def test_patch_bump_on_fix_type(self, mock_msg):
        mock_msg.return_value = {'subject': 'fix(scope): correct a bug', 'body': ''}
        self.assertEqual(sh.determine_bump(['abc']), 'patch')

    @patch('shared_helpers.get_commit_message')
    def test_returns_none_on_test_type(self, mock_msg):
        mock_msg.return_value = {'subject': 'test(scope): add unit tests', 'body': ''}
        self.assertEqual(sh.determine_bump(['abc']), 'none')

    @patch('shared_helpers.get_commit_message')
    def test_minor_bump_on_refactor_type(self, mock_msg):
        mock_msg.return_value = {'subject': 'refactor(scope): restructure module', 'body': ''}
        self.assertEqual(sh.determine_bump(['abc']), 'minor')

    @patch('shared_helpers.get_commit_message')
    def test_minor_bump_on_adr_type_prefix_matching_adrs(self, mock_msg):
        # There is no dedicated 'adr' entry in COMMIT_TYPES (only 'adrs'), so
        # this exercises key_id_lookup's startswith() prefix-matching fallback,
        # which should resolve 'adr' against the 'adrs' entry and use its
        # bump_type ('minor').
        mock_msg.return_value = {'subject': 'adr(process): accept decision', 'body': ''}
        self.assertEqual(sh.determine_bump(['abc']), 'minor')

    @patch('shared_helpers.get_commit_message')
    def test_minor_bump_on_adrs_type(self, mock_msg):
        mock_msg.return_value = {'subject': 'adrs(process): update decisions', 'body': ''}
        self.assertEqual(sh.determine_bump(['abc']), 'minor')

    @patch('shared_helpers.get_commit_message')
    def test_override_scope_forces_none_despite_adr_prefix_match(self, mock_msg):
        # Even though 'adr' prefix-matches 'adrs' (bump_type 'minor'), an
        # override scope (e.g. 'ci') must still force bump_type to 'none' -
        # override precedence must survive the startswith() fallback path.
        mock_msg.return_value = {'subject': 'adr(ci): accept decision', 'body': ''}
        self.assertEqual(sh.determine_bump(['abc']), 'none')

    @patch('shared_helpers.get_commit_message')
    def test_returns_none_on_chore_only(self, mock_msg):
        mock_msg.return_value = {'subject': 'chore(ci): update pipeline', 'body': ''}
        self.assertEqual(sh.determine_bump(['abc']), 'none')

    @patch('shared_helpers.get_commit_message')
    def test_returns_none_on_docs_only(self, mock_msg):
        mock_msg.return_value = {'subject': 'docs(readme): update readme', 'body': ''}
        self.assertEqual(sh.determine_bump(['abc']), 'none')

    @patch('shared_helpers.get_commit_message')
    def test_returns_invalid_on_unrecognized_type_with_non_override_scope(self, mock_msg):
        # No COMMIT_TYPES key starts with 'unknown', so key_id_lookup's
        # startswith() fallback finds no match and returns the hardcoded
        # {'bump_type': 'invalid', ...} dict instead of crashing.
        mock_msg.return_value = {'subject': 'unknown(scope): something', 'body': ''}
        self.assertEqual(sh.determine_bump(['abc']), 'invalid')

    @patch('shared_helpers.get_commit_message')
    def test_major_wins_over_minor_across_commits(self, mock_msg):
        mock_msg.side_effect = [
            {'subject': 'feature(scope): new feature', 'body': ''},
            {'subject': 'breaking(api): remove endpoint', 'body': ''},
        ]
        self.assertEqual(sh.determine_bump(['abc', 'def']), 'major')

    @patch('shared_helpers.get_commit_message')
    def test_returns_none_on_ci_scope_overrides_fix(self, mock_msg):
        mock_msg.return_value = {'subject': 'fix(ci): update pipeline config', 'body': ''}
        self.assertEqual(sh.determine_bump(['abc']), 'none')

    @patch('shared_helpers.get_commit_message')
    def test_returns_none_on_tools_scope_overrides_feature(self, mock_msg):
        mock_msg.return_value = {'subject': 'feature(tools): add new build script', 'body': ''}
        self.assertEqual(sh.determine_bump(['abc']), 'none')

    @patch('shared_helpers.get_commit_message')
    def test_no_release_scope_does_not_block_other_commits(self, mock_msg):
        mock_msg.side_effect = [
            {'subject': 'fix(ci): update pipeline', 'body': ''},
            {'subject': 'fix(scope): correct a bug', 'body': ''},
        ]
        self.assertEqual(sh.determine_bump(['abc', 'def']), 'patch')

    @patch('shared_helpers.get_commit_message')
    def test_returns_none_when_all_commits_are_no_release_scope(self, mock_msg):
        mock_msg.side_effect = [
            {'subject': 'fix(ci): update pipeline', 'body': ''},
            {'subject': 'chore(tools): update build script', 'body': ''},
            {'subject': 'docs(ci): update workflow readme', 'body': ''},
        ]
        self.assertEqual(sh.determine_bump(['abc', 'def', 'ghi']), 'none')

    @patch('shared_helpers.get_commit_message')
    def test_treats_merge_commit_subject_as_no_release(self, mock_msg):
        mock_msg.return_value = {'subject': 'Merge branch \'main\' into feature/x', 'body': ''}
        self.assertEqual(sh.determine_bump(['abc']), 'none')


# ---------------------------------------------------------------------------
# increment_version
# ---------------------------------------------------------------------------
class TestIncrementVersion(unittest.TestCase):
    def test_major_increment(self):
        self.assertEqual(sh.increment_version('1.2.3', 'major'), '2.0.0')

    def test_minor_increment(self):
        self.assertEqual(sh.increment_version('1.2.3', 'minor'), '1.3.0')

    def test_patch_increment(self):
        self.assertEqual(sh.increment_version('1.2.3', 'patch'), '1.2.4')

    def test_none_bump_leaves_version_unchanged(self):
        self.assertEqual(sh.increment_version('1.2.3', 'none'), '1.2.3')

    def test_raises_on_unknown_bump(self):
        with self.assertRaises(ValueError):
            sh.increment_version('1.2.3', 'unknown')


# ---------------------------------------------------------------------------
# determine_new_version delegation to determine_bump
# ---------------------------------------------------------------------------
class TestDetermineNewVersionDelegation(unittest.TestCase):
    @patch('shared_helpers.determine_bump', return_value='patch')
    def test_delegates_to_determine_bump_when_no_force(self, mock_bump):
        new_version, bump_used = sh.determine_new_version('1.2.3', ['abc'])
        self.assertEqual(new_version, '1.2.4')
        self.assertEqual(bump_used, 'patch')
        mock_bump.assert_called_once_with(['abc'], False, False)

    @patch('shared_helpers.determine_bump', return_value='none')
    def test_leaves_version_unchanged_when_bump_is_none(self, mock_bump):
        # increment_version('none') returns the version unchanged, not None;
        # main() relies on this by comparing new_version == current_version
        # to detect a no-release run.
        new_version, bump_used = sh.determine_new_version('1.2.3', ['abc'])
        self.assertEqual(new_version, '1.2.3')
        self.assertEqual(bump_used, 'none')


if __name__ == '__main__':
    unittest.main()
