"""Software tests for secure Earth Engine initialization."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from src.data.gee_auth import initialize_earth_engine


def test_initialize_uses_explicit_project_without_auth_material() -> None:
    """Pass only the project ID to the SDK initializer."""
    calls: list[dict[str, str]] = []
    module = SimpleNamespace(Initialize=lambda **kwargs: calls.append(kwargs))

    result = initialize_earth_engine("public-project-id", ee_module=module)

    assert result is module
    assert calls == [{"project": "public-project-id"}]


def test_initialize_reads_project_from_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """Use the documented environment variable when no argument is passed."""
    calls: list[dict[str, str]] = []
    module = SimpleNamespace(Initialize=lambda **kwargs: calls.append(kwargs))
    monkeypatch.setenv("EE_PROJECT_ID", "configured-project")

    initialize_earth_engine(ee_module=module)

    assert calls == [{"project": "configured-project"}]


def test_initialize_requires_project_id(monkeypatch: pytest.MonkeyPatch) -> None:
    """Fail with actionable guidance when project configuration is missing."""
    monkeypatch.delenv("EE_PROJECT_ID", raising=False)

    with pytest.raises(ValueError, match="EE_PROJECT_ID"):
        initialize_earth_engine(ee_module=SimpleNamespace(Initialize=lambda **_: None))
