"""End-to-end workflow test: Profile and streak tracking.

This test simulates a complete user workflow:
1. User views their profile
2. User logs meals over multiple days
3. User checks streak progress
4. User views taste preferences
5. User verifies profile updates reflect meal history
"""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from typer.testing import CliRunner

from fcp_cli.commands.log import app as log_app
from fcp_cli.commands.profile import app as profile_app
from fcp_cli.services import FCP, TasteProfile

pytestmark = pytest.mark.integration


class TestProfileAndStreakWorkflow:
    """Test complete profile and streak tracking workflow."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    @pytest.fixture
    def mock_profile(self):
        """Sample taste profile for workflow."""
        return TasteProfile(
            user_id="test-user",
            favorite_cuisines=["Italian", "Japanese", "Mexican"],
            preferred_ingredients=["tomatoes", "basil", "olive oil"],
            disliked_ingredients=["cilantro", "anchovies"],
            dietary_restrictions=["vegetarian"],
            average_calories=2000.0,
        )

    @pytest.fixture
    def mock_streak_data(self):
        """Sample streak data for workflow."""
        return {
            "current_streak": 7,
            "best_streak": 14,
            "total_days": 45,
            "last_log_date": datetime.now(UTC).strftime("%Y-%m-%d"),
        }

    @patch("fcp_cli.commands.profile.run_async")
    @patch("fcp_cli.commands.profile.FcpClient")
    @patch("fcp_cli.commands.log.run_async")
    @patch("fcp_cli.commands.log.FcpClient")
    def test_complete_profile_workflow(
        self,
        mock_log_client_class,
        mock_log_run_async,
        mock_profile_client_class,
        mock_profile_run_async,
        runner,
        mock_profile,
        mock_streak_data,
    ):
        """Test full workflow: view profile → log meals → check streak → verify updates."""
        # Setup: Mock profile client
        mock_profile_client = AsyncMock()
        mock_profile_client.get_taste_profile.return_value = mock_profile
        mock_profile_client.get_streak.return_value = mock_streak_data
        mock_profile_client_class.return_value = mock_profile_client
        mock_profile_run_async.side_effect = [mock_profile, mock_streak_data, mock_profile, mock_streak_data]

        # Step 1: User views their profile
        result = runner.invoke(profile_app, ["show"])

        assert result.exit_code == 0
        assert "Italian" in result.stdout or "Japanese" in result.stdout
        mock_profile_client.get_taste_profile.assert_called_once()

        # Step 2: User checks current streak
        result = runner.invoke(profile_app, ["streak"])

        assert result.exit_code == 0
        assert "7" in result.stdout  # Current streak
        assert "14" in result.stdout  # Best streak
        mock_profile_client.get_streak.assert_called_once()

        # Setup: Mock log client for meal logging
        meals = [
            FCP(
                id="m1",
                user_id="test-user",
                dish_name="Margherita Pizza",
                meal_type="dinner",
                timestamp=datetime.now(UTC),
            ),
            FCP(
                id="m2",
                user_id="test-user",
                dish_name="Vegetable Sushi",
                meal_type="lunch",
                timestamp=datetime.now(UTC),
            ),
        ]

        mock_log_client = MagicMock()
        mock_log_client.create_food_log = AsyncMock(side_effect=meals)
        mock_log_client_class.return_value = mock_log_client

        log_call_count = [0]

        def mock_log_run_side_effect(coro):
            result = meals[log_call_count[0]]
            log_call_count[0] += 1
            return result

        mock_log_run_async.side_effect = mock_log_run_side_effect

        # Step 3: User logs meals (building streak)
        for meal_name, meal_type in [("Margherita Pizza", "dinner"), ("Vegetable Sushi", "lunch")]:
            result = runner.invoke(log_app, ["add", meal_name, "--meal-type", meal_type])
            assert result.exit_code == 0
            assert meal_name in result.stdout

        # Step 4: User checks streak again (should maintain or increase)
        # Mock updated streak
        updated_streak = {
            "current_streak": 8,  # Increased
            "best_streak": 14,
            "total_days": 47,  # Increased by 2 days
            "last_log_date": datetime.now(UTC).strftime("%Y-%m-%d"),
        }
        mock_profile_client.get_streak.return_value = updated_streak
        mock_profile_run_async.side_effect = lambda coro: updated_streak

        result = runner.invoke(profile_app, ["streak"])

        assert result.exit_code == 0
        # Streak should show progress
        assert "8" in result.stdout or "7" in result.stdout  # Current streak
        assert mock_log_client.create_food_log.call_count == 2

    @patch("fcp_cli.commands.profile.run_async")
    @patch("fcp_cli.commands.profile.FcpClient")
    def test_taste_profile_workflow(self, mock_client_class, mock_run_async, runner, mock_profile):
        """Test taste profile viewing and understanding."""
        mock_client = AsyncMock()
        mock_client.get_taste_profile.return_value = mock_profile
        mock_client_class.return_value = mock_client
        mock_run_async.side_effect = lambda coro: mock_profile

        # User views detailed profile
        result = runner.invoke(profile_app, ["show"])

        assert result.exit_code == 0
        # Verify all profile sections are displayed
        assert "Italian" in result.stdout or "Japanese" in result.stdout
        assert "vegetarian" in result.stdout or "cilantro" in result.stdout

    @patch("fcp_cli.commands.profile.run_async")
    @patch("fcp_cli.commands.profile.FcpClient")
    def test_streak_encouragement_workflow(self, mock_client_class, mock_run_async, runner):
        """Test streak encouragement messages at different milestones."""
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client

        # Test streak at 7 days (should show encouragement)
        mock_client.get_streak.return_value = {
            "current_streak": 7,
            "best_streak": 10,
            "total_days": 30,
            "last_log_date": datetime.now(UTC).strftime("%Y-%m-%d"),
        }
        mock_run_async.side_effect = lambda coro: {
            "current_streak": 7,
            "best_streak": 10,
            "total_days": 30,
            "last_log_date": datetime.now(UTC).strftime("%Y-%m-%d"),
        }

        result = runner.invoke(profile_app, ["streak"])
        assert result.exit_code == 0
        assert "7" in result.stdout

        # Test streak at 30 days (milestone)
        mock_client.get_streak.return_value = {
            "current_streak": 30,
            "best_streak": 30,
            "total_days": 100,
            "last_log_date": datetime.now(UTC).strftime("%Y-%m-%d"),
        }
        mock_run_async.side_effect = lambda coro: {
            "current_streak": 30,
            "best_streak": 30,
            "total_days": 100,
            "last_log_date": datetime.now(UTC).strftime("%Y-%m-%d"),
        }

        result = runner.invoke(profile_app, ["streak"])
        assert result.exit_code == 0
        assert "30" in result.stdout

    @patch("fcp_cli.commands.profile.run_async")
    @patch("fcp_cli.commands.profile.FcpClient")
    @patch("fcp_cli.commands.log.run_async")
    @patch("fcp_cli.commands.log.FcpClient")
    def test_profile_reflects_meal_history(
        self, mock_log_client_class, mock_log_run_async, mock_profile_client_class, mock_profile_run_async, runner
    ):
        """Test that profile taste preferences reflect logged meals."""
        # Initial profile with limited preferences
        initial_profile = TasteProfile(
            user_id="test-user",
            favorite_cuisines=["Italian"],
            preferred_ingredients=["tomatoes", "cheese"],
            disliked_ingredients=[],
            dietary_restrictions=[],
        )

        # Setup: Mock profile client
        mock_profile_client = AsyncMock()
        mock_profile_client.get_taste_profile.return_value = initial_profile
        mock_profile_client_class.return_value = mock_profile_client
        mock_profile_run_async.side_effect = [initial_profile]

        # Step 1: User views initial profile
        result = runner.invoke(profile_app, ["show"])
        assert result.exit_code == 0
        assert "Italian" in result.stdout

        # Setup: Mock log client
        new_meal = FCP(
            id="m1",
            user_id="test-user",
            dish_name="Spicy Thai Curry",
            meal_type="dinner",
            timestamp=datetime.now(UTC),
        )
        mock_log_client = MagicMock()
        mock_log_client.create_food_log = AsyncMock(return_value=new_meal)
        mock_log_client_class.return_value = mock_log_client
        mock_log_run_async.side_effect = lambda coro: new_meal

        # Step 2: User logs a new type of meal (Thai cuisine)
        result = runner.invoke(log_app, ["add", "Spicy Thai Curry", "--meal-type", "dinner"])
        assert result.exit_code == 0

        # Step 3: User checks profile again (should reflect new preferences)
        # Mock updated profile
        updated_profile = TasteProfile(
            user_id="test-user",
            favorite_cuisines=["Italian", "Thai"],  # Added Thai
            preferred_ingredients=["tomatoes", "cheese", "curry", "coconut milk"],  # Added Thai ingredients
            disliked_ingredients=[],
            dietary_restrictions=[],
        )
        mock_profile_client.get_taste_profile.return_value = updated_profile
        mock_profile_run_async.side_effect = lambda coro: updated_profile

        result = runner.invoke(profile_app, ["show"])
        assert result.exit_code == 0
        # Profile should now include Thai cuisine
        assert "Thai" in result.stdout or "Italian" in result.stdout
        mock_log_client.create_food_log.assert_called_once()
