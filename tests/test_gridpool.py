# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Tests for the frequenz.gridpool package."""
import pytest

from frequenz.gridpool import delete_me


def test_gridpool_succeeds() -> None:  # TODO(cookiecutter): Remove
    """Test that the delete_me function succeeds."""
    assert delete_me() is True


def test_gridpool_fails() -> None:  # TODO(cookiecutter): Remove
    """Test that the delete_me function fails."""
    with pytest.raises(RuntimeError, match="This function should be removed!"):
        delete_me(blow_up=True)
