"""Tests for labels commands."""

from __future__ import annotations

from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from fcp_cli.commands.labels import app
from fcp_cli.services import CottageLabel, FcpConnectionError, FcpServerError

pytestmark = [pytest.mark.unit, pytest.mark.cli]


class TestGenerateCottageLabelCommand:
    """Test labels cottage command."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    @pytest.fixture
    def full_label(self):
        """Full cottage label with all fields."""
        return CottageLabel(
            product_name="Homemade Strawberry Jam",
            ingredients=["strawberries", "sugar", "lemon juice", "pectin"],
            allergen_warnings=["May contain traces of nuts"],
            warnings=["Keep refrigerated after opening", "Consume within 30 days"],
            regulatory_notes=[
                "Made in a home kitchen not subject to state licensing or inspection",
                "Complies with California Cottage Food Law",
            ],
            weight="12 oz (340g)",
            producer_info="Jane's Kitchen, 123 Main St, Sacramento, CA 95814",
            label_text="HOMEMADE STRAWBERRY JAM\nNet Weight: 12 oz (340g)\nIngredients: strawberries, sugar, lemon juice, pectin",
        )

    @pytest.fixture
    def minimal_label(self):
        """Minimal cottage label with required fields only."""
        return CottageLabel(
            product_name="Simple Cookies",
            ingredients=["flour", "sugar", "butter", "eggs"],
            allergen_warnings=None,
            warnings=None,
            regulatory_notes=None,
            weight=None,
            producer_info=None,
            label_text=None,
        )

    @pytest.fixture
    def allergen_label(self):
        """Label with allergen warnings."""
        return CottageLabel(
            product_name="Peanut Butter Cookies",
            ingredients=["peanut butter", "flour", "sugar", "eggs"],
            allergen_warnings=["Contains peanuts", "Contains gluten", "Contains eggs"],
            warnings=["Not suitable for those with nut allergies"],
            regulatory_notes=["Made in a facility that also processes tree nuts"],
            weight="8 oz (227g)",
            producer_info="Bob's Bakery",
            label_text=None,
        )

    @patch("fcp_cli.commands.labels.FcpClient")
    @patch("fcp_cli.commands.labels.run_async")
    def test_cottage_minimal(self, mock_run_async, mock_client_class, runner, minimal_label):
        """Test cottage label with minimal arguments."""
        mock_run_async.return_value = minimal_label

        result = runner.invoke(
            app,
            ["cottage", "Simple Cookies", "flour", "sugar", "butter", "eggs"],
        )

        assert result.exit_code == 0
        assert "Simple Cookies" in result.stdout
        assert "flour" in result.stdout
        assert "sugar" in result.stdout

    @patch("fcp_cli.commands.labels.FcpClient")
    @patch("fcp_cli.commands.labels.run_async")
    def test_cottage_with_weight(self, mock_run_async, mock_client_class, runner, full_label):
        """Test cottage label with weight."""
        mock_run_async.return_value = full_label

        result = runner.invoke(
            app,
            [
                "cottage",
                "Homemade Strawberry Jam",
                "strawberries",
                "sugar",
                "lemon juice",
                "pectin",
                "--weight",
                "12 oz (340g)",
            ],
        )

        assert result.exit_code == 0
        assert "12 oz (340g)" in result.stdout

    @patch("fcp_cli.commands.labels.FcpClient")
    @patch("fcp_cli.commands.labels.run_async")
    def test_cottage_with_business_info(self, mock_run_async, mock_client_class, runner, full_label):
        """Test cottage label with business information."""
        mock_run_async.return_value = full_label

        result = runner.invoke(
            app,
            [
                "cottage",
                "Homemade Strawberry Jam",
                "strawberries",
                "sugar",
                "--business",
                "Jane's Kitchen",
                "--address",
                "123 Main St, Sacramento, CA 95814",
            ],
        )

        assert result.exit_code == 0
        assert "Jane's Kitchen" in result.stdout

    @patch("fcp_cli.commands.labels.FcpClient")
    @patch("fcp_cli.commands.labels.run_async")
    def test_cottage_refrigerated(self, mock_run_async, mock_client_class, runner, full_label):
        """Test cottage label with refrigeration flag."""
        mock_run_async.return_value = full_label

        result = runner.invoke(
            app,
            [
                "cottage",
                "Fresh Salsa",
                "tomatoes",
                "onions",
                "peppers",
                "--refrigerated",
            ],
        )

        assert result.exit_code == 0

    @patch("fcp_cli.commands.labels.FcpClient")
    @patch("fcp_cli.commands.labels.run_async")
    def test_cottage_all_options(self, mock_run_async, mock_client_class, runner, full_label):
        """Test cottage label with all options."""
        mock_run_async.return_value = full_label

        result = runner.invoke(
            app,
            [
                "cottage",
                "Homemade Strawberry Jam",
                "strawberries",
                "sugar",
                "lemon juice",
                "pectin",
                "--weight",
                "12 oz (340g)",
                "--business",
                "Jane's Kitchen",
                "--address",
                "123 Main St, Sacramento, CA 95814",
                "--refrigerated",
            ],
        )

        assert result.exit_code == 0
        assert "Homemade Strawberry Jam" in result.stdout
        assert "12 oz (340g)" in result.stdout
        assert "Jane's Kitchen" in result.stdout

    @patch("fcp_cli.commands.labels.FcpClient")
    @patch("fcp_cli.commands.labels.run_async")
    def test_cottage_displays_allergens(self, mock_run_async, mock_client_class, runner, allergen_label):
        """Test that allergen warnings are displayed."""
        mock_run_async.return_value = allergen_label

        result = runner.invoke(
            app,
            ["cottage", "Peanut Butter Cookies", "peanut butter", "flour", "sugar"],
        )

        assert result.exit_code == 0
        assert "Contains:" in result.stdout
        assert "peanuts" in result.stdout

    @patch("fcp_cli.commands.labels.FcpClient")
    @patch("fcp_cli.commands.labels.run_async")
    def test_cottage_displays_warnings(self, mock_run_async, mock_client_class, runner, full_label):
        """Test that warnings are displayed."""
        mock_run_async.return_value = full_label

        result = runner.invoke(
            app,
            ["cottage", "Strawberry Jam", "strawberries", "sugar"],
        )

        assert result.exit_code == 0
        assert "Warnings:" in result.stdout
        assert "Keep refrigerated" in result.stdout

    @patch("fcp_cli.commands.labels.FcpClient")
    @patch("fcp_cli.commands.labels.run_async")
    def test_cottage_displays_regulatory_notes(self, mock_run_async, mock_client_class, runner, full_label):
        """Test that regulatory notes are displayed."""
        mock_run_async.return_value = full_label

        result = runner.invoke(
            app,
            ["cottage", "Strawberry Jam", "strawberries", "sugar"],
        )

        assert result.exit_code == 0
        assert "Regulatory Notes:" in result.stdout
        assert "home kitchen" in result.stdout

    @patch("fcp_cli.commands.labels.FcpClient")
    @patch("fcp_cli.commands.labels.run_async")
    def test_cottage_displays_label_text(self, mock_run_async, mock_client_class, runner, full_label):
        """Test that label text is displayed."""
        mock_run_async.return_value = full_label

        result = runner.invoke(
            app,
            ["cottage", "Strawberry Jam", "strawberries", "sugar"],
        )

        assert result.exit_code == 0
        assert "HOMEMADE STRAWBERRY JAM" in result.stdout

    @patch("fcp_cli.commands.labels.FcpClient")
    @patch("fcp_cli.commands.labels.run_async")
    def test_cottage_multiple_ingredients(self, mock_run_async, mock_client_class, runner, full_label):
        """Test cottage label with multiple ingredients."""
        mock_run_async.return_value = full_label

        result = runner.invoke(
            app,
            [
                "cottage",
                "Complex Recipe",
                "ingredient1",
                "ingredient2",
                "ingredient3",
                "ingredient4",
                "ingredient5",
            ],
        )

        assert result.exit_code == 0

    @patch("fcp_cli.commands.labels.FcpClient")
    @patch("fcp_cli.commands.labels.run_async")
    def test_cottage_ingredients_list_format(self, mock_run_async, mock_client_class, runner, full_label):
        """Test ingredients are displayed as comma-separated list."""
        mock_run_async.return_value = full_label

        result = runner.invoke(
            app,
            ["cottage", "Jam", "strawberries", "sugar", "lemon juice", "pectin"],
        )

        assert result.exit_code == 0
        assert "strawberries, sugar, lemon juice, pectin" in result.stdout

    @patch("fcp_cli.commands.labels.FcpClient")
    @patch("fcp_cli.commands.labels.run_async")
    def test_cottage_producer_info_display(self, mock_run_async, mock_client_class, runner, full_label):
        """Test producer info is displayed."""
        mock_run_async.return_value = full_label

        result = runner.invoke(
            app,
            ["cottage", "Product", "ingredient1"],
        )

        assert result.exit_code == 0
        assert "Produced by:" in result.stdout
        assert "Jane's Kitchen" in result.stdout

    @patch("fcp_cli.commands.labels.FcpClient")
    @patch("fcp_cli.commands.labels.run_async")
    def test_cottage_connection_error(self, mock_run_async, mock_client_class, runner):
        """Test cottage label with connection error."""
        mock_run_async.side_effect = FcpConnectionError("Connection failed")

        result = runner.invoke(
            app,
            ["cottage", "Cookies", "flour", "sugar"],
        )

        assert result.exit_code == 1
        assert "Connection error" in result.stdout
        assert "FCP server running" in result.stdout

    @patch("fcp_cli.commands.labels.FcpClient")
    @patch("fcp_cli.commands.labels.run_async")
    def test_cottage_server_error(self, mock_run_async, mock_client_class, runner):
        """Test cottage label with server error."""
        mock_run_async.side_effect = FcpServerError("Server error")

        result = runner.invoke(
            app,
            ["cottage", "Bread", "flour", "water", "yeast"],
        )

        assert result.exit_code == 1
        assert "Server error" in result.stdout


@pytest.mark.parametrize(
    "product_name,ingredients",
    [
        ("Cookies", ["flour", "sugar", "butter"]),
        ("Jam", ["fruit", "sugar"]),
        ("Bread", ["flour", "water", "yeast", "salt"]),
        ("Granola", ["oats", "honey", "nuts", "seeds"]),
    ],
)
@patch("fcp_cli.commands.labels.FcpClient")
@patch("fcp_cli.commands.labels.run_async")
def test_cottage_various_products(mock_run_async, mock_client_class, product_name, ingredients):
    """Test generating labels for various products."""
    label = CottageLabel(
        product_name=product_name,
        ingredients=ingredients,
    )
    mock_run_async.return_value = label

    runner = CliRunner()
    result = runner.invoke(app, ["cottage", product_name] + ingredients)

    assert result.exit_code == 0
    assert product_name in result.stdout
    for ingredient in ingredients:
        assert ingredient in result.stdout


@pytest.mark.parametrize(
    "refrigerated,weight",
    [
        (True, "8 oz (227g)"),
        (False, "12 oz (340g)"),
        (True, "1 lb (454g)"),
        (False, None),
    ],
)
@patch("fcp_cli.commands.labels.FcpClient")
@patch("fcp_cli.commands.labels.run_async")
def test_cottage_refrigeration_and_weight(mock_run_async, mock_client_class, refrigerated, weight):
    """Test various refrigeration and weight combinations."""
    label = CottageLabel(
        product_name="Test Product",
        ingredients=["ingredient1", "ingredient2"],
        weight=weight,
    )
    mock_run_async.return_value = label

    runner = CliRunner()
    cmd = ["cottage", "Test Product", "ingredient1", "ingredient2"]
    if refrigerated:
        cmd.append("--refrigerated")
    if weight:
        cmd.extend(["--weight", weight])

    result = runner.invoke(app, cmd)

    assert result.exit_code == 0
    if weight:
        assert weight in result.stdout
