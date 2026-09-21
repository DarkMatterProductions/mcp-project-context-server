#!/usr/bin/env python3
"""
Unit tests for build_and_publish.py
"""
import subprocess
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import build_and_publish as bap


# ---------------------------------------------------------------------------
# get_last_version
# ---------------------------------------------------------------------------
class TestGetLastVersion(unittest.TestCase):
    @patch('build_and_publish.subprocess.run')
    def test_returns_highest_version_tag(self, mock_run):
        mock_run.return_value = MagicMock(stdout='1.0.0\n2.0.0\n1.5.0\n')
        self.assertEqual(bap.get_last_version(), '2.0.0')
        mock_run.assert_called_once_with(
            [bap.GIT_CMD, 'tag', '--merged', 'HEAD'],
            capture_output=True,
            text=True,
            check=True,
        )

    @patch('build_and_publish.subprocess.run')
    def test_returns_zero_when_no_version_tags(self, mock_run):
        mock_run.return_value = MagicMock(stdout='some-non-version-tag\n')
        self.assertEqual(bap.get_last_version(), '0.0.0')

    @patch('build_and_publish.subprocess.run')
    def test_returns_zero_when_tags_empty(self, mock_run):
        mock_run.return_value = MagicMock(stdout='\n')
        self.assertEqual(bap.get_last_version(), '0.0.0')

    @patch('build_and_publish.subprocess.run', side_effect=subprocess.CalledProcessError(1, 'git'))
    def test_returns_zero_on_called_process_error(self, _):
        self.assertEqual(bap.get_last_version(), '0.0.0')

    @patch('build_and_publish.subprocess.run')
    def test_returns_zero_and_prints_stdout_on_called_process_error_with_output(self, mock_run):
        err = subprocess.CalledProcessError(1, 'git')
        err.stdout = 'some stdout'
        err.stderr = 'some stderr'
        mock_run.side_effect = err
        with patch('builtins.print') as mock_print:
            result = bap.get_last_version()
        self.assertEqual(result, '0.0.0')
        printed = ' '.join(str(c) for c in mock_print.call_args_list)
        self.assertIn('some stdout', printed)
        self.assertIn('some stderr', printed)

    @patch('build_and_publish.subprocess.run', side_effect=Exception('boom'))
    def test_returns_zero_on_generic_exception(self, _):
        self.assertEqual(bap.get_last_version(), '0.0.0')


# ---------------------------------------------------------------------------
# get_commits_since_tag
# ---------------------------------------------------------------------------
class TestGetCommitsSinceTag(unittest.TestCase):
    @patch('build_and_publish.subprocess.run')
    def test_uses_rev_list_head_when_tag_is_zero(self, mock_run):
        mock_run.return_value = MagicMock(stdout='abc\ndef\n')
        commits = bap.get_commits_since_tag('0.0.0')
        self.assertEqual(commits, ['abc', 'def'])
        mock_run.assert_called_once()
        self.assertIn('HEAD', mock_run.call_args[0][0])

    @patch('build_and_publish.subprocess.run')
    def test_uses_tag_range_for_real_tag(self, mock_run):
        mock_run.return_value = MagicMock(stdout='abc\n')
        commits = bap.get_commits_since_tag('1.2.3')
        self.assertEqual(commits, ['abc'])
        self.assertIn('1.2.3..HEAD', mock_run.call_args[0][0])

    @patch('build_and_publish.subprocess.run')
    def test_returns_empty_list_on_empty_output(self, mock_run):
        mock_run.return_value = MagicMock(stdout='\n')
        self.assertEqual(bap.get_commits_since_tag('1.0.0'), [])

    @patch('build_and_publish.subprocess.run', side_effect=subprocess.CalledProcessError(1, 'git'))
    def test_returns_empty_list_on_called_process_error(self, _):
        self.assertEqual(bap.get_commits_since_tag('1.0.0'), [])

    @patch('build_and_publish.subprocess.run')
    def test_returns_empty_list_and_prints_stdout_on_called_process_error_with_output(self, mock_run):
        err = subprocess.CalledProcessError(1, 'git')
        err.stdout = 'some stdout'
        err.stderr = 'some stderr'
        mock_run.side_effect = err
        with patch('builtins.print') as mock_print:
            result = bap.get_commits_since_tag('1.0.0')
        self.assertEqual(result, [])
        printed = ' '.join(str(c) for c in mock_print.call_args_list)
        self.assertIn('some stdout', printed)
        self.assertIn('some stderr', printed)

    @patch('build_and_publish.subprocess.run', side_effect=Exception('boom'))
    def test_returns_empty_list_on_generic_exception(self, _):
        self.assertEqual(bap.get_commits_since_tag('1.0.0'), [])


# ---------------------------------------------------------------------------
# COMMIT_TYPES dictionary
# ---------------------------------------------------------------------------
class TestCommitTypesDictionary(unittest.TestCase):
    def test_all_major_types_present(self):
        for t in ('breaking', 'rewrite', 'milestone', 'deprecate', 'eos', 'license', 'security'):
            self.assertIn(t, bap.COMMIT_TYPES)

    def test_all_minor_types_present(self):
        for t in ('feature', 'refactor', 'adrs'):
            self.assertIn(t, bap.COMMIT_TYPES)

    def test_all_patch_types_present(self):
        for t in ('fix',):
            self.assertIn(t, bap.COMMIT_TYPES)

    def test_all_no_release_types_present(self):
        for t in ('docs', 'chore', 'test', 'merge'):
            self.assertIn(t, bap.COMMIT_TYPES)

    def test_descriptions_are_non_empty_strings(self):
        for key, value in bap.COMMIT_TYPES.items():
            self.assertIsInstance(value['description'], str, msg=f"COMMIT_TYPES['{key}']['description'] is not a string")
            self.assertTrue(len(value['description']) > 0, msg=f"COMMIT_TYPES['{key}']['description'] is empty")


# ---------------------------------------------------------------------------
# RELEASE_OVERRIDE_SCOPES constant
# ---------------------------------------------------------------------------
class TestReleaseOverrideScopesConstant(unittest.TestCase):
    def test_ci_scope_is_present(self):
        self.assertIn('ci', bap.RELEASE_OVERRIDE_SCOPES)

    def test_tools_scope_is_present(self):
        self.assertIn('tools', bap.RELEASE_OVERRIDE_SCOPES)

    def test_is_a_dict(self):
        self.assertIsInstance(bap.RELEASE_OVERRIDE_SCOPES, dict)

    def test_all_scopes_force_none_bump(self):
        for scope, entry in bap.RELEASE_OVERRIDE_SCOPES.items():
            self.assertEqual(entry['bump_type'], 'none', msg=f"RELEASE_OVERRIDE_SCOPES['{scope}'] should force a 'none' bump")


# ---------------------------------------------------------------------------
# determine_new_version
# ---------------------------------------------------------------------------
class TestDetermineNewVersion(unittest.TestCase):
    def test_returns_none_when_no_commits_and_no_force(self):
        new_version, bump_used = bap.determine_new_version('1.0.0', [])
        self.assertIsNone(new_version)
        self.assertEqual(bump_used, 'none')

    def test_first_version_defaults_to_patch_from_zero(self):
        new_version, bump_used = bap.determine_new_version('0.0.0', ['abc'])
        self.assertEqual(new_version, '0.0.1')
        self.assertEqual(bump_used, 'patch')

    def test_first_version_respects_force_bump(self):
        new_version, bump_used = bap.determine_new_version('0.0.0', [], force_bump='minor')
        self.assertEqual(new_version, '0.1.0')
        self.assertEqual(bump_used, 'minor')

    def test_force_bump_overrides_commit_analysis(self):
        new_version, bump_used = bap.determine_new_version('1.2.3', ['abc'], force_bump='major')
        self.assertEqual(new_version, '2.0.0')
        self.assertEqual(bump_used, 'major')


# ---------------------------------------------------------------------------
# get_repository_name
# ---------------------------------------------------------------------------
class TestGetRepositoryName(unittest.TestCase):
    @patch('build_and_publish.subprocess.run')
    def test_returns_directory_name(self, mock_run):
        mock_run.return_value = MagicMock(stdout='/home/user/my-repo\n')
        self.assertEqual(bap.get_repository_name(), 'my-repo')

    @patch('build_and_publish.subprocess.run')
    def test_returns_empty_string_and_prints_stdout_on_called_process_error_with_output(self, mock_run):
        err = subprocess.CalledProcessError(1, 'git')
        err.stdout = 'some stdout'
        err.stderr = 'some stderr'
        mock_run.side_effect = err
        with patch('builtins.print') as mock_print:
            result = bap.get_repository_name()
        self.assertEqual(result, '')
        printed = ' '.join(str(c) for c in mock_print.call_args_list)
        self.assertIn('some stdout', printed)
        self.assertIn('some stderr', printed)

    @patch('build_and_publish.subprocess.run', side_effect=subprocess.CalledProcessError(1, 'git'))
    def test_returns_empty_string_on_called_process_error(self, _):
        self.assertEqual(bap.get_repository_name(), '')

    @patch('build_and_publish.subprocess.run', side_effect=Exception('boom'))
    def test_returns_empty_string_on_generic_exception(self, _):
        self.assertEqual(bap.get_repository_name(), '')


# ---------------------------------------------------------------------------
# create_git_tag
# ---------------------------------------------------------------------------
class TestCreateGitTag(unittest.TestCase):
    @patch('build_and_publish.subprocess.run')
    def test_creates_and_pushes_tag(self, mock_run):
        bap.create_git_tag('1.2.3')
        calls = mock_run.call_args_list
        self.assertEqual(len(calls), 2)
        self.assertIn('tag', calls[0][0][0])
        self.assertIn('1.2.3', calls[0][0][0])
        self.assertIn('push', calls[1][0][0])
        self.assertIn('1.2.3', calls[1][0][0])

    @patch('build_and_publish.subprocess.run', side_effect=subprocess.CalledProcessError(1, 'git'))
    def test_re_raises_called_process_error(self, _):
        with self.assertRaises(subprocess.CalledProcessError):
            bap.create_git_tag('1.2.3')


# ---------------------------------------------------------------------------
# create_github_release
# ---------------------------------------------------------------------------
class TestCreateGithubRelease(unittest.TestCase):
    @patch('build_and_publish.ensure_gh_cli')
    def test_dry_run_does_not_call_gh(self, mock_ensure_gh_cli):
        with patch('build_and_publish.subprocess.Popen') as mock_popen:
            bap.create_github_release('1.0.0', ['artifact.whl'], dry_run=True)
            mock_popen.assert_not_called()
        mock_ensure_gh_cli.assert_called_once_with(True)

    @patch('build_and_publish.ensure_gh_cli')
    @patch('build_and_publish.subprocess.Popen')
    def test_live_run_calls_gh_release_create(self, mock_popen, mock_ensure_gh_cli):
        mock_process = MagicMock()
        mock_process.stdout = iter(['line1\n'])
        mock_process.wait.return_value = None
        mock_process.returncode = 0
        mock_popen.return_value = mock_process

        bap.create_github_release('1.0.0', [Path('artifact.whl')])
        args = mock_popen.call_args[0][0]
        self.assertIn('gh', args)
        self.assertIn('release', args)
        self.assertIn('create', args)
        self.assertIn('1.0.0', args)

    @patch('build_and_publish.ensure_gh_cli')
    @patch('build_and_publish.subprocess.Popen')
    def test_raises_on_non_zero_exit(self, mock_popen, mock_ensure_gh_cli):
        mock_process = MagicMock()
        mock_process.stdout = iter([])
        mock_process.wait.return_value = None
        mock_process.returncode = 1
        mock_popen.return_value = mock_process

        with self.assertRaises(subprocess.CalledProcessError):
            bap.create_github_release('1.0.0', [])


# ---------------------------------------------------------------------------
# build_artifacts
# ---------------------------------------------------------------------------
class TestBuildArtifacts(unittest.TestCase):
    def _make_process(self, output_lines, returncode=0):
        mock_process = MagicMock()
        mock_process.stdout = iter(output_lines)
        mock_process.wait.return_value = None
        mock_process.returncode = returncode
        return mock_process

    @patch('build_and_publish.subprocess.Popen')
    def test_returns_single_artifact(self, mock_popen):
        mock_popen.return_value = self._make_process([
            'building...\n',
            'Successfully built mypackage-1.0.0.tar.gz\n',
        ])
        result = bap.build_artifacts('1.0.0')
        self.assertEqual(result, [Path('mypackage-1.0.0.tar.gz')])

    @patch('build_and_publish.subprocess.Popen')
    def test_returns_multiple_artifacts(self, mock_popen):
        mock_popen.return_value = self._make_process([
            'Successfully built mypackage-1.0.0.tar.gz and mypackage-1.0.0-py3-none-any.whl\n',
        ])
        result = bap.build_artifacts('1.0.0')
        self.assertEqual(result, [
            Path('mypackage-1.0.0.tar.gz'),
            Path('mypackage-1.0.0-py3-none-any.whl'),
        ])

    @patch('build_and_publish.subprocess.Popen')
    def test_verbose_prints_lines(self, mock_popen):
        mock_popen.return_value = self._make_process([
            'build output line\n',
            'Successfully built pkg-1.0.0.tar.gz\n',
        ])
        with patch('builtins.print') as mock_print:
            bap.build_artifacts('1.0.0', verbose=True)
        printed = ' '.join(str(c) for c in mock_print.call_args_list)
        self.assertIn('build output line', printed)

    @patch('build_and_publish.subprocess.Popen')
    def test_exits_on_non_zero_returncode(self, mock_popen):
        mock_popen.return_value = self._make_process(['error output\n'], returncode=1)
        with self.assertRaises(SystemExit):
            bap.build_artifacts('1.0.0')

    @patch('build_and_publish.subprocess.Popen')
    def test_exits_when_no_artifacts_found(self, mock_popen):
        mock_popen.return_value = self._make_process(['no success line here\n'])
        with self.assertRaises(SystemExit):
            bap.build_artifacts('1.0.0')

    @patch('build_and_publish.subprocess.Popen')
    def test_non_zero_exit_prints_output_when_not_verbose(self, mock_popen):
        mock_popen.return_value = self._make_process(['error output\n'], returncode=1)
        with patch('builtins.print') as mock_print:
            with self.assertRaises(SystemExit):
                bap.build_artifacts('1.0.0', verbose=False)
        printed = ' '.join(str(c) for c in mock_print.call_args_list)
        self.assertIn('error output', printed)


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
class TestMain(unittest.TestCase):
    def _run_main(self, argv, env=None, **mock_overrides):
        """Helper: patch argv + all external calls and invoke main()."""
        defaults = dict(
            get_repository_name=MagicMock(return_value='my-repo'),
            get_last_version=MagicMock(return_value='1.0.0'),
            get_commits_since_tag=MagicMock(return_value=['abc']),
            determine_new_version=MagicMock(return_value=('1.0.1', 'patch')),
            create_git_tag=MagicMock(),
            build_artifacts=MagicMock(return_value=[Path('my-repo-1.0.1.tar.gz')]),
            create_github_release=MagicMock(),
        )
        defaults.update(mock_overrides)
        patches = [patch(f'build_and_publish.{k}', v) for k, v in defaults.items()]
        with patch('sys.argv', ['build_and_publish.py'] + argv):
            with patch.dict('os.environ', env or {}, clear=False):
                for p in patches:
                    p.start()
                try:
                    bap.main()
                finally:
                    for p in patches:
                        p.stop()
        return defaults

    def test_basic_run_without_publish_does_not_create_tag(self):
        mocks = self._run_main([])
        mocks['create_git_tag'].assert_not_called()

    def test_publish_without_build_exits(self):
        with patch('sys.argv', ['build_and_publish.py', '--publish']):
            with self.assertRaises(SystemExit):
                bap.main()

    def test_dry_run_skips_tag_creation(self):
        mocks = self._run_main(['--dry-run'])
        mocks['create_git_tag'].assert_not_called()

    def test_force_major_bump(self):
        mocks = self._run_main(['--major'])
        mocks['determine_new_version'].assert_called_once()
        _, kwargs = mocks['determine_new_version'].call_args
        self.assertEqual(kwargs.get('force_bump') or mocks['determine_new_version'].call_args[0][2], 'major')

    def test_force_minor_bump(self):
        mocks = self._run_main(['--minor'])
        args = mocks['determine_new_version'].call_args[0]
        self.assertEqual(args[2], 'minor')

    def test_force_patch_bump(self):
        mocks = self._run_main(['--patch'])
        args = mocks['determine_new_version'].call_args[0]
        self.assertEqual(args[2], 'patch')

    def test_build_flag_calls_build_artifacts(self):
        mocks = self._run_main(['--build'])
        mocks['build_artifacts'].assert_called_once_with(new_version='1.0.1', verbose=False)

    def test_build_verbose_flag(self):
        mocks = self._run_main(['--build', '--verbose'])
        mocks['build_artifacts'].assert_called_once_with(new_version='1.0.1', verbose=True)

    def test_dry_run_build_does_not_call_build_artifacts(self):
        mocks = self._run_main(['--build', '--dry-run'])
        mocks['build_artifacts'].assert_not_called()

    def test_publish_calls_create_github_release(self):
        mocks = self._run_main(['--build', '--publish'])
        mocks['create_github_release'].assert_called_once()

    def test_dry_run_publish_does_not_call_create_github_release(self):
        mocks = self._run_main(['--build', '--publish', '--dry-run'])
        mocks['create_github_release'].assert_not_called()

    def test_none_version_exits(self):
        with self.assertRaises(SystemExit):
            self._run_main([], determine_new_version=MagicMock(return_value=(None, 'none')))

    def test_github_output_env_writes_version_and_bump(self):
        tmp = Path('/tmp/gh_output_test.txt')
        tmp.write_text('')
        try:
            self._run_main([], env={'GITHUB_OUTPUT': str(tmp)})
            content = tmp.read_text()
            self.assertIn('version=1.0.1', content)
            self.assertIn('bump=patch', content)
        finally:
            tmp.unlink(missing_ok=True)

    def test_github_output_env_writes_bump_none_for_no_release_commits(self):
        tmp = Path('/tmp/gh_output_test_none.txt')
        tmp.write_text('')
        try:
            with self.assertRaises(SystemExit) as cm:
                self._run_main(
                    [],
                    env={'GITHUB_OUTPUT': str(tmp)},
                    determine_new_version=MagicMock(return_value=('1.0.0', 'none')),
                )
            self.assertEqual(cm.exception.code, 0)
        finally:
            tmp.unlink(missing_ok=True)


if __name__ == '__main__':
    unittest.main()
