import urllib.request

import pytest

from slack_cli.cli import build_parser, cmd_files_download
from slack_cli.client import SlackApiError, SlackClient
from slack_cli.files import download_file


class _StreamingHTTPResponse:
    def __init__(self, payload: bytes, status: int = 200):
        self.payload = payload
        self.status = status
        self.offset = 0
        self.read_sizes = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self, size=-1):
        self.read_sizes.append(size)
        if size < 0:
            raise AssertionError("Download must stream with a bounded read size")
        chunk = self.payload[self.offset : self.offset + size]
        self.offset += len(chunk)
        return chunk


def _headers(request):
    return {key.lower(): value for key, value in request.header_items()}


def test_download_request_gets_with_bearer_auth_and_streams_large_file(
    monkeypatch, tmp_path
):
    payload = b"a" * (3 * 1024 * 1024 + 17)
    response = _StreamingHTTPResponse(payload)
    captured = []

    def fake_urlopen(request, context=None, timeout=None):
        captured.append(request)
        return response

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)

    destination = tmp_path / "large.bin"
    client = SlackClient("bot-token-secret")
    total_bytes = client.download_request(
        "https://files.slack.com/files-pri/T123-F123/large.bin",
        str(destination),
        chunk_size=64 * 1024,
    )

    request = captured[0]
    assert request.get_method() == "GET"
    assert request.data is None
    assert _headers(request)["authorization"] == "Bearer bot-token-secret"
    assert destination.read_bytes() == payload
    assert total_bytes == len(payload)
    assert len(response.read_sizes) > 2
    assert set(response.read_sizes) == {64 * 1024}


def test_download_request_rejects_non_200_and_leaves_no_file(monkeypatch, tmp_path):
    response = _StreamingHTTPResponse(b"error", status=503)
    monkeypatch.setattr(
        urllib.request,
        "urlopen",
        lambda request, context=None, timeout=None: response,
    )
    destination = tmp_path / "failed.bin"

    with pytest.raises(SlackApiError, match="HTTP 503"):
        SlackClient("bot-token-secret").download_request(
            "https://files.slack.com/files-pri/T123-F123/failed.bin",
            str(destination),
        )

    assert not destination.exists()


class _RecordingDownloadClient:
    def __init__(self, file_data=None, error=None):
        self.file_data = file_data or {}
        self.error = error
        self.events = []

    def call(self, method_name, params=None):
        self.events.append(("call", method_name, params))
        if self.error:
            raise self.error
        return {"ok": True, "file": self.file_data}

    def download_request(self, url, output_path):
        self.events.append(("download_request", url, output_path))
        return 8


@pytest.mark.parametrize(
    "url_field",
    ["url_private_download", "url_private"],
)
def test_download_file_uses_private_url_and_requested_output(url_field, capsys):
    client = _RecordingDownloadClient(
        {"name": "image.png", url_field: "https://files.slack.com/private/image.png"}
    )

    download_file(client, "F123", output="/tmp/image.png")

    assert client.events == [
        ("call", "files.info", {"file": "F123"}),
        (
            "download_request",
            "https://files.slack.com/private/image.png",
            "/tmp/image.png",
        ),
    ]
    assert capsys.readouterr().out == "Downloaded: /tmp/image.png (8 bytes)\n"


def test_download_file_defaults_to_slack_filename_in_cwd():
    client = _RecordingDownloadClient(
        {
            "name": "../safe-image.png",
            "url_private_download": "https://files.slack.com/private/image.png",
        }
    )

    download_file(client, "F123")

    assert client.events[-1] == (
        "download_request",
        "https://files.slack.com/private/image.png",
        "safe-image.png",
    )


@pytest.mark.parametrize(
    ("api_error", "expected_message"),
    [
        ("file_not_found", "file_not_found: F404"),
        ("missing_scope", "files:read is required"),
    ],
)
def test_download_file_explains_common_files_info_errors(api_error, expected_message):
    client = _RecordingDownloadClient(error=SlackApiError(api_error))

    with pytest.raises(SlackApiError, match=expected_message):
        download_file(client, "F404")


def test_files_download_parser_supports_get_alias_and_output():
    parser = build_parser()

    for command in ("download", "get"):
        args = parser.parse_args(["files", command, "F123", "--output", "image.png"])
        assert args.func is cmd_files_download
        assert args.file_id == "F123"
        assert args.output == "image.png"
