---
name: slack-file-upload
description: "Upload files to Slack or download attachments for local inspection. Use when sharing reports and build artifacts, or when an agent needs to read a Slack image, document, or other attached file."
command_name: slack-cli
tags: [slack, file, upload, download, share, attachment]
---
<!-- installed by slack-cli -->

# /slack-file-upload -- Upload and Download Slack Files

Upload files to Slack channels and threads, or download Slack attachments for local inspection. Uploads use the modern V2 flow (`files.getUploadURLExternal` + `files.completeUploadExternal`) that replaced the deprecated `files.upload` endpoint. Downloads resolve the private URL through `files.info` and send bot authentication automatically.

## When to Use

- Sharing a file (PDF, image, CSV, log, etc.) to a Slack channel
- Uploading build artifacts or reports to a thread
- Attaching a file with a comment for context
- Listing or inspecting files already shared in Slack
- Downloading an image, PDF, document, log, or other attachment so an agent can read it locally

## Procedure

### Step 1: Upload a File to a Channel

Basic upload:

```bash
slack-cli files upload /path/to/report.pdf --channels <CHANNEL_ID>
```

This uploads the file and shares it to the specified channel. The `--channels` flag takes a channel ID.

### Step 2: Add a Title and Comment

```bash
slack-cli files upload /path/to/report.pdf --channels <CHANNEL_ID> --title "Q1 Revenue Report" --comment "Here is the Q1 report. Key findings on page 3."
```

- `--title` sets the file's display title in Slack (defaults to the filename if omitted)
- `--comment` adds an initial message that appears alongside the file share

### Step 3: Upload to a Thread

```bash
slack-cli files upload /path/to/screenshot.png --channels <CHANNEL_ID> --thread-ts 1712345678.123456
```

The `--thread-ts` flag shares the file as a reply within the specified thread. You still need `--channels` to identify which channel the thread is in.

### Step 4: Upload Without Sharing

If you omit `--channels`, the file is uploaded to Slack but NOT shared to any channel. It will be visible in the uploader's file list but not posted anywhere:

```bash
slack-cli files upload /path/to/draft.docx
```

You can share it later through the Slack UI or API.

## How the V2 Upload Works

The `files upload` command handles a three-step flow automatically:

1. **Get upload URL** -- calls `files.getUploadURLExternal` with the filename and file size to get a pre-signed upload URL and file ID
2. **Upload file data** -- POSTs the raw file bytes to the pre-signed URL
3. **Complete upload** -- calls `files.completeUploadExternal` to finalize the upload, set the title, share to channels, and attach the initial comment

You do not need to manage these steps manually. The command handles all three.

## File Management

### List files

List files in the workspace:

```bash
slack-cli files list
```

Filter by channel:

```bash
slack-cli files list --channel <CHANNEL_ID>
```

Filter by user:

```bash
slack-cli files list --user <USER_ID>
```

Filter by type:

```bash
slack-cli files list --types images
slack-cli files list --types pdfs
slack-cli files list --types snippets
```

Combine filters:

```bash
slack-cli files list --channel <CHANNEL_ID> --types images --count 50
```

### Get file info

```bash
slack-cli files info <FILE_ID>
```

With full JSON metadata:

```bash
slack-cli files info <FILE_ID> --json
```

Returns: file ID, name, title, type, size, uploader, creation date, download URL, and which channels it is shared in.

### Download and read an attachment

Download to the file's Slack name in the current directory:

```bash
slack-cli files download <FILE_ID>
```

Choose a local destination:

```bash
slack-cli files download <FILE_ID> --output /tmp/attachment.png
```

`slack-cli files get <FILE_ID>` is an alias. Use this command instead of copying `url_private` into `curl`: the CLI supplies `Authorization: Bearer` without exposing the token and streams large files to disk. After download, inspect the local image/document with the appropriate agent tool.

### Delete a file

```bash
slack-cli files delete <FILE_ID>
```

## Examples

### Upload a CSV report to a channel

```bash
slack-cli files upload ./data/weekly-metrics.csv --channels C0AM2BVMHRT --title "Weekly Metrics - Week 14" --comment "Attached this week's metrics. Revenue up 12%."
```

### Upload a screenshot to a thread

```bash
slack-cli files upload /tmp/screenshot.png --channels C08ACMRDC04 --thread-ts 1712345678.123456 --title "Bug Screenshot"
```

### Upload a log file for debugging

```bash
slack-cli files upload /var/log/app/error.log --channels C0AM2BVMHRT --title "Error log from production" --comment "Seeing intermittent 500s. Full log attached."
```

### List recent images in a channel

```bash
slack-cli files list --channel C0AM2BVMHRT --types images --count 10 --json
```

### Download an image attachment for inspection

```bash
slack-cli files download F0FILEID --output /tmp/slack-image.png
file /tmp/slack-image.png
```

### Upload without sharing, then check it exists

```bash
slack-cli files upload ./draft-proposal.pdf --json
# Capture file_id from the response

slack-cli files info <FILE_ID>
```

## Supported File Types

Slack accepts virtually any file type. Common ones:

| Type | Extensions | `--types` filter |
|------|-----------|-----------------|
| Images | .png, .jpg, .gif, .svg | `images` |
| PDFs | .pdf | `pdfs` |
| Documents | .docx, .doc, .pages | `gdocs` |
| Spreadsheets | .xlsx, .csv | `spaces` |
| Code snippets | .py, .js, .sh, .json | `snippets` |
| Archives | .zip, .tar.gz | `zips` |
| Videos | .mp4, .mov | N/A |
| Audio | .mp3, .m4a, .ogg | N/A |

The file size limit depends on the workspace plan (free: 5 GB total, paid: larger per-file limits).

## Tips

- The file path must be a local file that exists on disk. The command validates this before uploading.
- If `--title` is omitted, the filename (e.g., `report.pdf`) is used as the title.
- The `--channels` flag takes a single channel ID. To share to multiple channels after upload, use the Slack UI or the raw API.
- For large files, the upload may take a moment. The command blocks until the upload completes.
- The `--json` flag on `files upload` returns the full file object from the completeUploadExternal response, including the file ID and permalink.
- Bot tokens need the `files:write` scope for uploads and `files:read` for listing, info, and downloads. A `missing_scope` error during download means the app must be granted `files:read` and reinstalled to the workspace.
- To upload to a different workspace, use `--profile <name>`.
