"""Tests for publish commands."""

from __future__ import annotations

from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from fcp_cli.commands.publish import app
from fcp_cli.services import (
    Draft,
    FcpConnectionError,
    FcpServerError,
)

pytestmark = [pytest.mark.unit, pytest.mark.cli]


class TestGenerateContentCommand:
    """Test generate content command."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    @patch("fcp_cli.commands.publish.FcpClient")
    @patch("fcp_cli.commands.publish.run_async")
    def test_generate_content_minimal(self, mock_run_async, mock_client_class, runner):
        """Test generate content with minimal arguments."""
        mock_run_async.return_value = {
            "id": "draft123",
            "title": "My Food Journey",
            "content": "This is the generated content.",
            "status": "draft",
        }

        result = runner.invoke(app, ["generate", "blog"])

        assert result.exit_code == 0
        assert "My Food Journey" in result.stdout
        assert "draft" in result.stdout
        assert "draft123" in result.stdout
        mock_run_async.assert_called_once()

    @patch("fcp_cli.commands.publish.FcpClient")
    @patch("fcp_cli.commands.publish.run_async")
    def test_generate_content_with_log_ids(self, mock_run_async, mock_client_class, runner):
        """Test generate content with log IDs."""
        mock_run_async.return_value = {
            "id": "draft456",
            "title": "Weekly Food Recap",
            "content": "Based on your recent meals...",
            "status": "draft",
        }

        result = runner.invoke(
            app,
            ["generate", "newsletter", "--log", "log1", "--log", "log2"],
        )

        assert result.exit_code == 0
        assert "Weekly Food Recap" in result.stdout

    @patch("fcp_cli.commands.publish.FcpClient")
    @patch("fcp_cli.commands.publish.run_async")
    def test_generate_content_with_body_field(self, mock_run_async, mock_client_class, runner):
        """Test generate content when response has 'body' instead of 'content'."""
        mock_run_async.return_value = {
            "id": "draft789",
            "title": "Social Post",
            "body": "Check out my amazing meal!",
            "status": "draft",
        }

        result = runner.invoke(app, ["generate", "social"])

        assert result.exit_code == 0
        assert "Social Post" in result.stdout
        assert "Check out my amazing meal!" in result.stdout

    @patch("fcp_cli.commands.publish.FcpClient")
    @patch("fcp_cli.commands.publish.run_async")
    def test_generate_content_without_id(self, mock_run_async, mock_client_class, runner):
        """Test generate content when response has no ID."""
        mock_run_async.return_value = {
            "title": "Preview Content",
            "content": "Some content",
            "status": "preview",
        }

        result = runner.invoke(app, ["generate", "blog"])

        assert result.exit_code == 0
        assert "Preview Content" in result.stdout
        assert "draft123" not in result.stdout

    @patch("fcp_cli.commands.publish.FcpClient")
    @patch("fcp_cli.commands.publish.run_async")
    def test_generate_content_connection_error(self, mock_run_async, mock_client_class, runner):
        """Test generate content with connection error."""
        mock_run_async.side_effect = FcpConnectionError("Connection failed")

        result = runner.invoke(app, ["generate", "blog"])

        assert result.exit_code == 1
        assert "Connection error" in result.stdout
        assert "FCP server running" in result.stdout

    @patch("fcp_cli.commands.publish.FcpClient")
    @patch("fcp_cli.commands.publish.run_async")
    def test_generate_content_server_error(self, mock_run_async, mock_client_class, runner):
        """Test generate content with server error."""
        mock_run_async.side_effect = FcpServerError("Server error")

        result = runner.invoke(app, ["generate", "blog"])

        assert result.exit_code == 1
        assert "Server error" in result.stdout

    @patch("fcp_cli.commands.publish.FcpClient")
    @patch("fcp_cli.commands.publish.run_async")
    def test_generate_content_default_values(self, mock_run_async, mock_client_class, runner):
        """Test generate content with minimal response."""
        mock_run_async.return_value = {}

        result = runner.invoke(app, ["generate", "blog"])

        assert result.exit_code == 0
        assert "Generated Content" in result.stdout


class TestListDraftsCommand:
    """Test list drafts command."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    @patch("fcp_cli.commands.publish.FcpClient")
    @patch("fcp_cli.commands.publish.run_async")
    def test_list_drafts_success(self, mock_run_async, mock_client_class, runner):
        """Test list drafts with multiple drafts."""
        mock_run_async.return_value = [
            {
                "id": "draft1",
                "title": "Blog Post 1",
                "content_type": "blog",
                "status": "draft",
            },
            {
                "id": "draft2",
                "title": "Newsletter",
                "type": "newsletter",
                "status": "ready",
            },
        ]

        result = runner.invoke(app, ["drafts"])

        assert result.exit_code == 0
        assert "Blog Post 1" in result.stdout
        assert "Newsletter" in result.stdout
        assert "draft1" in result.stdout
        assert "draft2" in result.stdout

    @patch("fcp_cli.commands.publish.FcpClient")
    @patch("fcp_cli.commands.publish.run_async")
    def test_list_drafts_empty(self, mock_run_async, mock_client_class, runner):
        """Test list drafts with no drafts."""
        mock_run_async.return_value = []

        result = runner.invoke(app, ["drafts"])

        assert result.exit_code == 0
        assert "No drafts yet" in result.stdout

    @patch("fcp_cli.commands.publish.FcpClient")
    @patch("fcp_cli.commands.publish.run_async")
    def test_list_drafts_missing_fields(self, mock_run_async, mock_client_class, runner):
        """Test list drafts with missing fields."""
        mock_run_async.return_value = [
            {
                # Missing most fields
            },
        ]

        result = runner.invoke(app, ["drafts"])

        assert result.exit_code == 0
        # Should show dashes for missing values
        assert "-" in result.stdout

    @patch("fcp_cli.commands.publish.FcpClient")
    @patch("fcp_cli.commands.publish.run_async")
    def test_list_drafts_connection_error(self, mock_run_async, mock_client_class, runner):
        """Test list drafts with connection error."""
        mock_run_async.side_effect = FcpConnectionError("Connection failed")

        result = runner.invoke(app, ["drafts"])

        assert result.exit_code == 1
        assert "Connection error" in result.stdout

    @patch("fcp_cli.commands.publish.FcpClient")
    @patch("fcp_cli.commands.publish.run_async")
    def test_list_drafts_server_error(self, mock_run_async, mock_client_class, runner):
        """Test list drafts with server error."""
        mock_run_async.side_effect = FcpServerError("Server error")

        result = runner.invoke(app, ["drafts"])

        assert result.exit_code == 1
        assert "Server error" in result.stdout


class TestShowDraftCommand:
    """Test show draft command."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    @patch("fcp_cli.commands.publish.FcpClient")
    @patch("fcp_cli.commands.publish.run_async")
    def test_show_draft_full_details(self, mock_run_async, mock_client_class, runner):
        """Test show draft with all details."""
        mock_draft = Draft(
            id="draft123",
            title="My Blog Post",
            content="This is the full content of my blog post.",
            content_type="blog",
            status="draft",
            platforms=["medium", "dev.to"],
        )
        mock_run_async.return_value = mock_draft

        result = runner.invoke(app, ["show", "draft123"])

        assert result.exit_code == 0
        assert "My Blog Post" in result.stdout
        assert "This is the full content" in result.stdout
        assert "Type: blog" in result.stdout
        assert "Status: draft" in result.stdout
        assert "Platforms: medium, dev.to" in result.stdout
        assert "ID: draft123" in result.stdout

    @patch("fcp_cli.commands.publish.FcpClient")
    @patch("fcp_cli.commands.publish.run_async")
    def test_show_draft_minimal(self, mock_run_async, mock_client_class, runner):
        """Test show draft with minimal details."""
        mock_draft = Draft(
            id="draft456",
            title="Minimal Draft",
            content=None,
            content_type=None,
            status=None,
            platforms=None,
        )
        mock_run_async.return_value = mock_draft

        result = runner.invoke(app, ["show", "draft456"])

        assert result.exit_code == 0
        assert "Minimal Draft" in result.stdout
        assert "ID: draft456" in result.stdout

    @patch("fcp_cli.commands.publish.FcpClient")
    @patch("fcp_cli.commands.publish.run_async")
    def test_show_draft_with_content_only(self, mock_run_async, mock_client_class, runner):
        """Test show draft with only content."""
        mock_draft = Draft(
            id="draft789",
            title="Content Only",
            content="Just some content",
            content_type=None,
            status=None,
            platforms=None,
        )
        mock_run_async.return_value = mock_draft

        result = runner.invoke(app, ["show", "draft789"])

        assert result.exit_code == 0
        assert "Just some content" in result.stdout

    @patch("fcp_cli.commands.publish.FcpClient")
    @patch("fcp_cli.commands.publish.run_async")
    def test_show_draft_connection_error(self, mock_run_async, mock_client_class, runner):
        """Test show draft with connection error."""
        mock_run_async.side_effect = FcpConnectionError("Connection failed")

        result = runner.invoke(app, ["show", "draft123"])

        assert result.exit_code == 1
        assert "Connection error" in result.stdout

    @patch("fcp_cli.commands.publish.FcpClient")
    @patch("fcp_cli.commands.publish.run_async")
    def test_show_draft_server_error(self, mock_run_async, mock_client_class, runner):
        """Test show draft with server error."""
        mock_run_async.side_effect = FcpServerError("Server error")

        result = runner.invoke(app, ["show", "draft123"])

        assert result.exit_code == 1
        assert "Server error" in result.stdout


class TestEditDraftCommand:
    """Test edit draft command."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    @patch("fcp_cli.commands.publish.FcpClient")
    @patch("fcp_cli.commands.publish.run_async")
    def test_edit_draft_title(self, mock_run_async, mock_client_class, runner):
        """Test edit draft title."""
        mock_draft = Draft(
            id="draft123",
            title="Updated Title",
            content="Content",
        )
        mock_run_async.return_value = mock_draft

        result = runner.invoke(app, ["edit", "draft123", "--title", "Updated Title"])

        assert result.exit_code == 0
        assert "Draft Updated" in result.stdout
        assert "Updated Title" in result.stdout
        assert "draft123" in result.stdout

    @patch("fcp_cli.commands.publish.FcpClient")
    @patch("fcp_cli.commands.publish.run_async")
    def test_edit_draft_content(self, mock_run_async, mock_client_class, runner):
        """Test edit draft content."""
        mock_draft = Draft(
            id="draft456",
            title="My Draft",
            content="New content",
        )
        mock_run_async.return_value = mock_draft

        result = runner.invoke(app, ["edit", "draft456", "--content", "New content"])

        assert result.exit_code == 0
        assert "Draft Updated" in result.stdout

    @patch("fcp_cli.commands.publish.FcpClient")
    @patch("fcp_cli.commands.publish.run_async")
    def test_edit_draft_status(self, mock_run_async, mock_client_class, runner):
        """Test edit draft status."""
        mock_draft = Draft(
            id="draft789",
            title="My Draft",
            status="ready",
        )
        mock_run_async.return_value = mock_draft

        result = runner.invoke(app, ["edit", "draft789", "--status", "ready"])

        assert result.exit_code == 0
        assert "Draft Updated" in result.stdout

    @patch("fcp_cli.commands.publish.FcpClient")
    @patch("fcp_cli.commands.publish.run_async")
    def test_edit_draft_all_fields(self, mock_run_async, mock_client_class, runner):
        """Test edit draft with all fields."""
        mock_draft = Draft(
            id="draft999",
            title="Complete Update",
            content="New content",
            status="ready",
        )
        mock_run_async.return_value = mock_draft

        result = runner.invoke(
            app,
            [
                "edit",
                "draft999",
                "--title",
                "Complete Update",
                "--content",
                "New content",
                "--status",
                "ready",
            ],
        )

        assert result.exit_code == 0
        assert "Draft Updated" in result.stdout

    @patch("fcp_cli.commands.publish.FcpClient")
    @patch("fcp_cli.commands.publish.run_async")
    def test_edit_draft_no_changes(self, mock_run_async, mock_client_class, runner):
        """Test edit draft with no changes specified."""
        result = runner.invoke(app, ["edit", "draft123"])

        assert result.exit_code == 0
        assert "No changes specified" in result.stdout
        mock_run_async.assert_not_called()

    @patch("fcp_cli.commands.publish.FcpClient")
    @patch("fcp_cli.commands.publish.run_async")
    def test_edit_draft_connection_error(self, mock_run_async, mock_client_class, runner):
        """Test edit draft with connection error."""
        mock_run_async.side_effect = FcpConnectionError("Connection failed")

        result = runner.invoke(app, ["edit", "draft123", "--title", "New Title"])

        assert result.exit_code == 1
        assert "Connection error" in result.stdout

    @patch("fcp_cli.commands.publish.FcpClient")
    @patch("fcp_cli.commands.publish.run_async")
    def test_edit_draft_server_error(self, mock_run_async, mock_client_class, runner):
        """Test edit draft with server error."""
        mock_run_async.side_effect = FcpServerError("Server error")

        result = runner.invoke(app, ["edit", "draft123", "--title", "New Title"])

        assert result.exit_code == 1
        assert "Server error" in result.stdout


class TestDeleteDraftCommand:
    """Test delete draft command."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    @patch("fcp_cli.commands.publish.FcpClient")
    @patch("fcp_cli.commands.publish.run_async")
    def test_delete_draft_with_yes_flag(self, mock_run_async, mock_client_class, runner):
        """Test delete draft with --yes flag."""
        mock_run_async.return_value = True

        result = runner.invoke(app, ["delete", "draft123", "--yes"])

        assert result.exit_code == 0
        assert "Deleted draft draft123" in result.stdout
        mock_run_async.assert_called_once()

    @patch("fcp_cli.commands.publish.FcpClient")
    @patch("fcp_cli.commands.publish.run_async")
    def test_delete_draft_with_confirmation(self, mock_run_async, mock_client_class, runner):
        """Test delete draft with confirmation."""
        mock_run_async.return_value = True

        result = runner.invoke(app, ["delete", "draft123"], input="y\n")

        assert result.exit_code == 0
        assert "Deleted draft draft123" in result.stdout

    @patch("fcp_cli.commands.publish.FcpClient")
    @patch("fcp_cli.commands.publish.run_async")
    def test_delete_draft_cancelled(self, mock_run_async, mock_client_class, runner):
        """Test delete draft cancelled by user."""
        result = runner.invoke(app, ["delete", "draft123"], input="n\n")

        assert result.exit_code == 0
        assert "Cancelled" in result.stdout
        mock_run_async.assert_not_called()

    @patch("fcp_cli.commands.publish.FcpClient")
    @patch("fcp_cli.commands.publish.run_async")
    def test_delete_draft_connection_error(self, mock_run_async, mock_client_class, runner):
        """Test delete draft with connection error."""
        mock_run_async.side_effect = FcpConnectionError("Connection failed")

        result = runner.invoke(app, ["delete", "draft123", "--yes"])

        assert result.exit_code == 1
        assert "Connection error" in result.stdout

    @patch("fcp_cli.commands.publish.FcpClient")
    @patch("fcp_cli.commands.publish.run_async")
    def test_delete_draft_server_error(self, mock_run_async, mock_client_class, runner):
        """Test delete draft with server error."""
        mock_run_async.side_effect = FcpServerError("Server error")

        result = runner.invoke(app, ["delete", "draft123", "--yes"])

        assert result.exit_code == 1
        assert "Server error" in result.stdout


class TestPublishDraftCommand:
    """Test publish draft command."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    @patch("fcp_cli.commands.publish.FcpClient")
    @patch("fcp_cli.commands.publish.run_async")
    def test_publish_draft_minimal(self, mock_run_async, mock_client_class, runner):
        """Test publish draft without specifying platforms."""
        mock_run_async.return_value = {
            "platforms": ["medium"],
            "external_urls": {"medium": "https://medium.com/@user/post-123"},
        }

        result = runner.invoke(app, ["publish", "draft123"])

        assert result.exit_code == 0
        assert "Successfully published" in result.stdout
        assert "medium" in result.stdout
        assert "https://medium.com/@user/post-123" in result.stdout

    @patch("fcp_cli.commands.publish.FcpClient")
    @patch("fcp_cli.commands.publish.run_async")
    def test_publish_draft_with_platforms(self, mock_run_async, mock_client_class, runner):
        """Test publish draft with specific platforms."""
        mock_run_async.return_value = {
            "platforms": ["medium", "dev.to"],
            "external_urls": {
                "medium": "https://medium.com/@user/post-123",
                "dev.to": "https://dev.to/user/post-456",
            },
        }

        result = runner.invoke(
            app,
            ["publish", "draft123", "--platform", "medium", "--platform", "dev.to"],
        )

        assert result.exit_code == 0
        assert "Successfully published" in result.stdout
        assert "medium" in result.stdout
        assert "dev.to" in result.stdout

    @patch("fcp_cli.commands.publish.FcpClient")
    @patch("fcp_cli.commands.publish.run_async")
    def test_publish_draft_with_published_to_field(self, mock_run_async, mock_client_class, runner):
        """Test publish draft when response has 'published_to' instead of 'platforms'."""
        mock_run_async.return_value = {
            "published_to": ["twitter"],
            "urls": {"twitter": "https://twitter.com/user/status/123"},
        }

        result = runner.invoke(app, ["publish", "draft123"])

        assert result.exit_code == 0
        assert "Successfully published" in result.stdout
        assert "twitter" in result.stdout

    @patch("fcp_cli.commands.publish.FcpClient")
    @patch("fcp_cli.commands.publish.run_async")
    def test_publish_draft_no_urls(self, mock_run_async, mock_client_class, runner):
        """Test publish draft without URLs in response."""
        mock_run_async.return_value = {
            "platforms": ["medium"],
        }

        result = runner.invoke(app, ["publish", "draft123"])

        assert result.exit_code == 0
        assert "Successfully published" in result.stdout

    @patch("fcp_cli.commands.publish.FcpClient")
    @patch("fcp_cli.commands.publish.run_async")
    def test_publish_draft_urls_as_string(self, mock_run_async, mock_client_class, runner):
        """Test publish draft with URLs as string instead of dict."""
        mock_run_async.return_value = {
            "platforms": ["custom"],
            "urls": "https://example.com/post",
        }

        result = runner.invoke(app, ["publish", "draft123"])

        assert result.exit_code == 0
        assert "Successfully published" in result.stdout
        assert "https://example.com/post" in result.stdout

    @patch("fcp_cli.commands.publish.FcpClient")
    @patch("fcp_cli.commands.publish.run_async")
    def test_publish_draft_urls_with_none_values(self, mock_run_async, mock_client_class, runner):
        """Test publish draft with None values in URLs dict."""
        mock_run_async.return_value = {
            "platforms": ["medium", "twitter"],
            "external_urls": {
                "medium": "https://medium.com/@user/post-123",
                "twitter": None,
            },
        }

        result = runner.invoke(app, ["publish", "draft123"])

        assert result.exit_code == 0
        assert "Successfully published" in result.stdout
        assert "https://medium.com/@user/post-123" in result.stdout

    @patch("fcp_cli.commands.publish.FcpClient")
    @patch("fcp_cli.commands.publish.run_async")
    def test_publish_draft_connection_error(self, mock_run_async, mock_client_class, runner):
        """Test publish draft with connection error."""
        mock_run_async.side_effect = FcpConnectionError("Connection failed")

        result = runner.invoke(app, ["publish", "draft123"])

        assert result.exit_code == 1
        assert "Connection error" in result.stdout

    @patch("fcp_cli.commands.publish.FcpClient")
    @patch("fcp_cli.commands.publish.run_async")
    def test_publish_draft_server_error(self, mock_run_async, mock_client_class, runner):
        """Test publish draft with server error."""
        mock_run_async.side_effect = FcpServerError("Server error")

        result = runner.invoke(app, ["publish", "draft123"])

        assert result.exit_code == 1
        assert "Server error" in result.stdout


class TestListPublishedCommand:
    """Test list published content command."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    @patch("fcp_cli.commands.publish.FcpClient")
    @patch("fcp_cli.commands.publish.run_async")
    def test_list_published_success(self, mock_run_async, mock_client_class, runner):
        """Test list published content with multiple items."""
        mock_run_async.return_value = [
            {
                "id": "pub1",
                "title": "Blog Post 1",
                "content_type": "blog",
                "platforms": ["medium"],
                "published_at": "2026-02-01T10:00:00Z",
            },
            {
                "id": "pub2",
                "title": "Newsletter",
                "type": "newsletter",
                "platforms": ["substack", "medium"],
                "date": "2026-02-05T14:30:00Z",
            },
        ]

        result = runner.invoke(app, ["published"])

        assert result.exit_code == 0
        assert "Blog Post 1" in result.stdout
        assert "Newsletter" in result.stdout
        assert "pub1" in result.stdout
        assert "pub2" in result.stdout
        assert "medium" in result.stdout

    @patch("fcp_cli.commands.publish.FcpClient")
    @patch("fcp_cli.commands.publish.run_async")
    def test_list_published_empty(self, mock_run_async, mock_client_class, runner):
        """Test list published content with no items."""
        mock_run_async.return_value = []

        result = runner.invoke(app, ["published"])

        assert result.exit_code == 0
        assert "No published content yet" in result.stdout

    @patch("fcp_cli.commands.publish.FcpClient")
    @patch("fcp_cli.commands.publish.run_async")
    def test_list_published_missing_fields(self, mock_run_async, mock_client_class, runner):
        """Test list published content with missing fields."""
        mock_run_async.return_value = [
            {
                # Missing most fields
            },
        ]

        result = runner.invoke(app, ["published"])

        assert result.exit_code == 0
        # Should show dashes for missing values
        assert "-" in result.stdout

    @patch("fcp_cli.commands.publish.FcpClient")
    @patch("fcp_cli.commands.publish.run_async")
    def test_list_published_no_platforms(self, mock_run_async, mock_client_class, runner):
        """Test list published content with no platforms."""
        mock_run_async.return_value = [
            {
                "id": "pub1",
                "title": "Post",
                "content_type": "blog",
                "published_at": "2026-02-01T10:00:00Z",
            },
        ]

        result = runner.invoke(app, ["published"])

        assert result.exit_code == 0
        assert "-" in result.stdout

    @patch("fcp_cli.commands.publish.FcpClient")
    @patch("fcp_cli.commands.publish.run_async")
    def test_list_published_connection_error(self, mock_run_async, mock_client_class, runner):
        """Test list published content with connection error."""
        mock_run_async.side_effect = FcpConnectionError("Connection failed")

        result = runner.invoke(app, ["published"])

        assert result.exit_code == 1
        assert "Connection error" in result.stdout

    @patch("fcp_cli.commands.publish.FcpClient")
    @patch("fcp_cli.commands.publish.run_async")
    def test_list_published_server_error(self, mock_run_async, mock_client_class, runner):
        """Test list published content with server error."""
        mock_run_async.side_effect = FcpServerError("Server error")

        result = runner.invoke(app, ["published"])

        assert result.exit_code == 1
        assert "Server error" in result.stdout


@pytest.mark.parametrize(
    "content_type,expected_in_output",
    [
        ("blog", "blog"),
        ("social", "social"),
        ("newsletter", "newsletter"),
        ("custom_type", "custom_type"),
    ],
)
@patch("fcp_cli.commands.publish.FcpClient")
@patch("fcp_cli.commands.publish.run_async")
def test_generate_various_content_types(
    mock_run_async,
    mock_client_class,
    content_type,
    expected_in_output,
):
    """Test generating various content types."""
    mock_run_async.return_value = {
        "id": "draft123",
        "title": f"{content_type.title()} Content",
        "content": "Generated content",
        "status": "draft",
    }

    runner = CliRunner()
    result = runner.invoke(app, ["generate", content_type])

    assert result.exit_code == 0
    assert expected_in_output.title() in result.stdout or "Generated Content" in result.stdout


@pytest.mark.parametrize(
    "platform_list,expected_count",
    [
        (["medium"], 1),
        (["medium", "dev.to"], 2),
        (["medium", "dev.to", "hashnode"], 3),
        ([], 0),
    ],
)
@patch("fcp_cli.commands.publish.FcpClient")
@patch("fcp_cli.commands.publish.run_async")
def test_publish_multiple_platforms(
    mock_run_async,
    mock_client_class,
    platform_list,
    expected_count,
):
    """Test publishing to multiple platforms."""
    urls = {platform: f"https://{platform}.com/post" for platform in platform_list}
    mock_run_async.return_value = {
        "platforms": platform_list,
        "external_urls": urls,
    }

    runner = CliRunner()
    args = ["publish", "draft123"]
    for platform in platform_list:
        args.extend(["--platform", platform])

    result = runner.invoke(app, args)

    assert result.exit_code == 0
    assert "Successfully published" in result.stdout


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    @patch("fcp_cli.commands.publish.FcpClient")
    @patch("fcp_cli.commands.publish.run_async")
    def test_generate_empty_response(self, mock_run_async, mock_client_class, runner):
        """Test generate with completely empty response."""
        mock_run_async.return_value = {}

        result = runner.invoke(app, ["generate", "blog"])

        assert result.exit_code == 0

    @patch("fcp_cli.commands.publish.FcpClient")
    @patch("fcp_cli.commands.publish.run_async")
    def test_show_draft_empty_platforms(self, mock_run_async, mock_client_class, runner):
        """Test show draft with empty platforms list."""
        mock_draft = Draft(
            id="draft123",
            title="Test",
            content="Content",
            platforms=[],
        )
        mock_run_async.return_value = mock_draft

        result = runner.invoke(app, ["show", "draft123"])

        assert result.exit_code == 0

    @patch("fcp_cli.commands.publish.FcpClient")
    @patch("fcp_cli.commands.publish.run_async")
    def test_publish_empty_platforms(self, mock_run_async, mock_client_class, runner):
        """Test publish with empty platforms list."""
        mock_run_async.return_value = {
            "platforms": [],
            "external_urls": {},
        }

        result = runner.invoke(app, ["publish", "draft123"])

        assert result.exit_code == 0
        assert "Successfully published" in result.stdout

    @patch("fcp_cli.commands.publish.FcpClient")
    @patch("fcp_cli.commands.publish.run_async")
    def test_edit_draft_short_option_flags(self, mock_run_async, mock_client_class, runner):
        """Test edit draft with short option flags."""
        mock_draft = Draft(
            id="draft123",
            title="New Title",
            content="New content",
            status="ready",
        )
        mock_run_async.return_value = mock_draft

        result = runner.invoke(
            app,
            ["edit", "draft123", "-t", "New Title", "-c", "New content", "-s", "ready"],
        )

        assert result.exit_code == 0
        assert "Draft Updated" in result.stdout

    @patch("fcp_cli.commands.publish.FcpClient")
    @patch("fcp_cli.commands.publish.run_async")
    def test_delete_draft_short_yes_flag(self, mock_run_async, mock_client_class, runner):
        """Test delete draft with short -y flag."""
        mock_run_async.return_value = True

        result = runner.invoke(app, ["delete", "draft123", "-y"])

        assert result.exit_code == 0
        assert "Deleted draft draft123" in result.stdout

    @patch("fcp_cli.commands.publish.FcpClient")
    @patch("fcp_cli.commands.publish.run_async")
    def test_publish_short_platform_flag(self, mock_run_async, mock_client_class, runner):
        """Test publish with short -p flag for platform."""
        mock_run_async.return_value = {
            "platforms": ["medium"],
            "external_urls": {"medium": "https://medium.com/@user/post"},
        }

        result = runner.invoke(app, ["publish", "draft123", "-p", "medium"])

        assert result.exit_code == 0
        assert "Successfully published" in result.stdout

    @patch("fcp_cli.commands.publish.FcpClient")
    @patch("fcp_cli.commands.publish.run_async")
    def test_generate_short_log_flag(self, mock_run_async, mock_client_class, runner):
        """Test generate with short -l flag for log IDs."""
        mock_run_async.return_value = {
            "id": "draft123",
            "title": "Test",
            "content": "Content",
            "status": "draft",
        }

        result = runner.invoke(app, ["generate", "blog", "-l", "log1", "-l", "log2"])

        assert result.exit_code == 0

    @patch("fcp_cli.commands.publish.FcpClient")
    @patch("fcp_cli.commands.publish.run_async")
    def test_list_drafts_with_type_fallback(self, mock_run_async, mock_client_class, runner):
        """Test list drafts using 'type' field as fallback."""
        mock_run_async.return_value = [
            {
                "id": "draft1",
                "title": "Test",
                "type": "blog",  # Using 'type' instead of 'content_type'
                "status": "draft",
            },
        ]

        result = runner.invoke(app, ["drafts"])

        assert result.exit_code == 0
        assert "blog" in result.stdout

    @patch("fcp_cli.commands.publish.FcpClient")
    @patch("fcp_cli.commands.publish.run_async")
    def test_list_published_with_type_fallback(self, mock_run_async, mock_client_class, runner):
        """Test list published using 'type' field as fallback."""
        mock_run_async.return_value = [
            {
                "id": "pub1",
                "title": "Test",
                "type": "newsletter",  # Using 'type' instead of 'content_type'
                "platforms": ["substack"],
                "date": "2026-02-01T10:00:00Z",  # Using 'date' instead of 'published_at'
            },
        ]

        result = runner.invoke(app, ["published"])

        assert result.exit_code == 0
        assert "newsletter" in result.stdout
        assert "2026-02-01T10:00:00Z" in result.stdout

    @patch("fcp_cli.commands.publish.FcpClient")
    @patch("fcp_cli.commands.publish.run_async")
    def test_show_draft_no_content(self, mock_run_async, mock_client_class, runner):
        """Test show draft when content is empty string."""
        mock_draft = Draft(
            id="draft123",
            title="Title Only",
            content="",
            content_type="blog",
            status="draft",
        )
        mock_run_async.return_value = mock_draft

        result = runner.invoke(app, ["show", "draft123"])

        assert result.exit_code == 0
        assert "Title Only" in result.stdout
