#!/usr/bin/env python3
"""
Unit tests for validate_commits.py
"""
import subprocess
import unittest
from unittest.mock import MagicMock, patch

import validate_commits as vc


# ---------------------------------------------------------------------------
# get_commits_since_branch_head
# ---------------------------------------------------------------------------
class TestGetCommitsSinceBranchHead(unittest.TestCase):
    @patch('validate_commits.subprocess.run')
    def test_returns_commit_list(self, mock_run):
        mock_run.return_value = MagicMock(stdout='abc\ndef\n')
        commits = vc.get_commits_since_branch_head()
        self.assertEqual(commits, ['abc', 'def'])

    @patch('validate_commits.subprocess.run')
    def test_uses_source_and_destination_range(self, mock_run):
        mock_run.return_value = MagicMock(stdout='abc\n')
        vc.get_commits_since_branch_head(source='feature/x', destination='main')
        self.assertIn('feature/x...main', mock_run.call_args[0][0])

    @patch('validate_commits.subprocess.run')
    def test_defaults_to_head_and_main(self, mock_run):
        mock_run.return_value = MagicMock(stdout='abc\n')
        vc.get_commits_since_branch_head()
        self.assertIn('HEAD...main', mock_run.call_args[0][0])

    @patch('validate_commits.subprocess.run')
    def test_returns_empty_list_on_empty_output(self, mock_run):
        mock_run.return_value = MagicMock(stdout='\n')
        self.assertEqual(vc.get_commits_since_branch_head(), [])

    @patch('validate_commits.subprocess.run', side_effect=subprocess.CalledProcessError(1, 'git'))
    def test_returns_empty_list_on_called_process_error(self, _):
        self.assertEqual(vc.get_commits_since_branch_head(), [])

    @patch('validate_commits.subprocess.run')
    def test_returns_empty_list_and_prints_stdout_on_called_process_error_with_output(self, mock_run):
        err = subprocess.CalledProcessError(1, 'git')
        err.stdout = 'some stdout'
        err.stderr = 'some stderr'
        mock_run.side_effect = err
        with patch('builtins.print') as mock_print:
            result = vc.get_commits_since_branch_head()
        self.assertEqual(result, [])
        printed = ' '.join(str(c) for c in mock_print.call_args_list)
        self.assertIn('some stdout', printed)
        self.assertIn('some stderr', printed)

    @patch('validate_commits.subprocess.run', side_effect=Exception('boom'))
    def test_returns_empty_list_on_generic_exception(self, _):
        self.assertEqual(vc.get_commits_since_branch_head(), [])


# ---------------------------------------------------------------------------
# validate_commit_messages
#
# NOTE: validate_commit_messages() delegates entirely to shared_helpers'
# analyze_commits(), which resolves commit subjects via its own module-level
# get_commit_message() - NOT the duplicate get_commit_message() defined in
# validate_commits.py itself (that copy is dead code, unused by this
# function). So these tests must patch 'shared_helpers.get_commit_message',
# not 'validate_commits.get_commit_message'.
# ---------------------------------------------------------------------------
class TestValidateCommitMessages(unittest.TestCase):
    @patch('shared_helpers.get_commit_message')
    def test_major_bump_on_breaking_type(self, mock_msg):
        mock_msg.return_value = {'subject': 'breaking(api): remove endpoint', 'body': ''}
        analyzed, bump = vc.validate_commit_messages(['abc'])
        self.assertEqual(bump, ('major', 'X.0.0'))
        self.assertEqual(analyzed['valid']['count'], 1)
        self.assertEqual(analyzed['invalid']['count'], 0)

    @patch('shared_helpers.get_commit_message')
    def test_minor_bump_on_feature_type(self, mock_msg):
        mock_msg.return_value = {'subject': 'feature(scope): new feature', 'body': ''}
        analyzed, bump = vc.validate_commit_messages(['abc'])
        self.assertEqual(bump, ('minor', '0.X.0'))
        self.assertEqual(analyzed['valid']['count'], 1)

    @patch('shared_helpers.get_commit_message')
    def test_patch_bump_on_fix_type(self, mock_msg):
        mock_msg.return_value = {'subject': 'fix(scope): correct a bug', 'body': ''}
        analyzed, bump = vc.validate_commit_messages(['abc'])
        self.assertEqual(bump, ('patch', '0.0.X'))
        self.assertEqual(analyzed['valid']['count'], 1)

    @patch('shared_helpers.get_commit_message')
    def test_none_bump_on_docs_only(self, mock_msg):
        mock_msg.return_value = {'subject': 'docs(readme): update readme', 'body': ''}
        analyzed, bump = vc.validate_commit_messages(['abc'])
        self.assertEqual(bump, ('none', 'N.N.N'))
        self.assertEqual(analyzed['valid']['count'], 1)

    @patch('shared_helpers.get_commit_message')
    def test_major_wins_over_minor_and_patch(self, mock_msg):
        mock_msg.side_effect = [
            {'subject': 'fix(scope): correct a bug', 'body': ''},
            {'subject': 'feature(scope): new feature', 'body': ''},
            {'subject': 'breaking(api): remove endpoint', 'body': ''},
        ]
        _, bump = vc.validate_commit_messages(['abc', 'def', 'ghi'])
        self.assertEqual(bump, ('major', 'X.0.0'))

    @patch('shared_helpers.get_commit_message')
    def test_force_major_override_from_bang(self, mock_msg):
        mock_msg.return_value = {'subject': 'fix!(scope): breaking fix', 'body': ''}
        _, bump = vc.validate_commit_messages(['abc'])
        self.assertEqual(bump, ('major', 'X.0.0'))

    @patch('shared_helpers.get_commit_message')
    def test_ci_scope_override_forces_none_and_counts_as_valid(self, mock_msg):
        mock_msg.return_value = {'subject': 'fix(ci): update pipeline config', 'body': ''}
        analyzed, bump = vc.validate_commit_messages(['abc'])
        self.assertEqual(bump, ('none', 'N.N.N'))
        self.assertEqual(analyzed['valid']['count'], 1)
        self.assertEqual(analyzed['invalid']['count'], 0)

    @patch('shared_helpers.get_commit_message')
    def test_tools_scope_override_forces_none_despite_feature_type(self, mock_msg):
        mock_msg.return_value = {'subject': 'feature(tools): add new build script', 'body': ''}
        _, bump = vc.validate_commit_messages(['abc'])
        self.assertEqual(bump, ('none', 'N.N.N'))

    @patch('shared_helpers.get_commit_message')
    def test_bucket_invalid_for_unrecognized_type_without_aborting_batch(self, mock_msg):
        # No COMMIT_TYPES key starts with 'unknown', so key_id_lookup's
        # startswith() fallback resolves it to bump_type 'invalid' instead of
        # crashing - the commit is bucketed as invalid, and the other
        # (docs-type, 'none'-bump) commit in the batch is still bucketed as
        # valid. The overall bump is still 'none' here since has_none is
        # checked ahead of has_invalid in validate_commit_messages's priority
        # order - 'invalid' only wins the overall bump when no other commit
        # in the batch produced a major/minor/patch/none result.
        mock_msg.side_effect = [
            {'subject': 'docs(readme): update readme', 'body': ''},
            {'subject': 'unknown(scope): something', 'body': ''},
        ]
        analyzed, bump = vc.validate_commit_messages(['abc', 'def'])
        self.assertEqual(bump, ('none', 'N.N.N'))
        self.assertEqual(analyzed['valid']['count'], 1)
        self.assertEqual(analyzed['invalid']['count'], 1)

    @patch('shared_helpers.get_commit_message')
    def test_invalid_bump_when_only_commit_is_unrecognized_type(self, mock_msg):
        mock_msg.return_value = {'subject': 'unknown(scope): something', 'body': ''}
        analyzed, bump = vc.validate_commit_messages(['abc'])
        self.assertEqual(bump, ('invalid', None))
        self.assertEqual(analyzed['valid']['count'], 0)
        self.assertEqual(analyzed['invalid']['count'], 1)

    def test_returns_none_bump_for_empty_commit_list(self):
        analyzed, bump = vc.validate_commit_messages([])
        self.assertIsNone(bump)
        self.assertEqual(analyzed['valid']['count'], 0)
        self.assertEqual(analyzed['invalid']['count'], 0)

    @patch('shared_helpers.get_commit_message')
    def test_treats_merge_commit_subject_as_no_release(self, mock_msg):
        mock_msg.return_value = {'subject': 'Merge branch \'main\' into feature/x', 'body': ''}
        analyzed, bump = vc.validate_commit_messages(['abc'])
        self.assertEqual(bump, ('none', 'N.N.N'))
        self.assertEqual(analyzed['valid']['count'], 1)


if __name__ == '__main__':
    unittest.main()
