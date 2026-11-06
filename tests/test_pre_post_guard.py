import json
from unittest import mock

import pytest

from slack_cli.client import SlackApiError, SlackClient
from slack_cli import config


@pytest.mark.parametrize('method', ['chat.postMessage', 'chat.scheduleMessage', 'chat.update'])
def test_guard_hold_stops_all_message_writers_before_http(method):
    client = SlackClient('test-token', pre_post_guard=['guard', 'check'])
    with mock.patch('slack_cli.client.subprocess.run', return_value=mock.Mock(returncode=4, stdout='{"verdict":"HOLD"}')) as guard, \
            mock.patch.object(client, '_request') as request:
        with pytest.raises(SlackApiError, match='pre_post_guard_hold'):
            client.call(method, {'channel': 'CSTUDENTS01', 'text': 'final text'})
    request.assert_not_called()
    payload = json.loads(guard.call_args.kwargs['input'])
    assert payload == {'method': method, 'params': {'channel': 'CSTUDENTS01', 'text': 'final text'}}


@pytest.mark.parametrize('stdout,returncode', [('not json', 0), ('{}', 0), ('{"verdict":"PASS"}', 4)])
def test_guard_requires_exit_zero_and_exact_pass(stdout, returncode):
    client = SlackClient('test-token', pre_post_guard=['guard'])
    with mock.patch('slack_cli.client.subprocess.run', return_value=mock.Mock(returncode=returncode, stdout=stdout)), \
            mock.patch.object(client, '_request') as request:
        with pytest.raises(SlackApiError, match='pre_post_guard_'):
            client.call('chat.scheduleMessage', {'text': 'final text'})
    request.assert_not_called()


def test_success_runs_guard_then_http_and_does_not_put_credentials_in_payload():
    client = SlackClient('test-private-token', pre_post_guard=['guard'])
    with mock.patch('slack_cli.client.subprocess.run', return_value=mock.Mock(returncode=0, stdout='{"verdict":"PASS"}')) as guard, \
            mock.patch.object(client, '_request', return_value={'ok': True}) as request:
        assert client.call('chat.postMessage', {'text': 'final text'})['ok']
    request.assert_called_once()
    assert 'test-private-token' not in guard.call_args.kwargs['input']


def test_reads_and_unconfigured_profiles_are_unchanged():
    for configured, method in [(None, 'chat.postMessage'), (['guard'], 'chat.scheduledMessages.list')]:
        client = SlackClient('test-token', pre_post_guard=configured)
        with mock.patch('slack_cli.client.subprocess.run') as guard, \
                mock.patch.object(client, '_request', return_value={'ok': True}):
            client.call(method)
        guard.assert_not_called()


def test_missing_guard_executable_fails_closed():
    client = SlackClient('test-token', pre_post_guard=['missing-guard'])
    with mock.patch('slack_cli.client.subprocess.run', side_effect=OSError), mock.patch.object(client, '_request') as request:
        with pytest.raises(SlackApiError, match='pre_post_guard_unavailable'):
            client.call('chat.postMessage', {'text': 'final text'})
    request.assert_not_called()


def test_profile_retains_guard_command_without_auth_changes():
    data = {'profiles': {'guarded': {'bot_token': 'test-token', 'pre_post_guard': ['guard']}}, 'default_profile': 'guarded'}
    with mock.patch.object(config, 'load_config', return_value=data):
        profile = config.get_profile('guarded')
    assert profile['pre_post_guard'] == ['guard']
    assert profile['bot_token'] == 'test-token'
