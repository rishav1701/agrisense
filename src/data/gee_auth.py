"""Secure initialization helpers for Google Earth Engine."""

from __future__ import annotations

import os
from collections.abc import Callable
from typing import Any


def initialize_earth_engine(
    project_id: str | None = None,
    *,
    ee_module: Any | None = None,
) -> Any:
    """Initialize Earth Engine using local credentials and an explicit project.

    Args:
        project_id: Non-secret Google Cloud project ID. Defaults to
            ``EE_PROJECT_ID`` from the environment.
        ee_module: Optional Earth Engine module, primarily for software tests.

    Returns:
        The initialized Earth Engine module.

    Raises:
        RuntimeError: If the Earth Engine package is not installed.
        ValueError: If no project ID is configured.
    """
    resolved_project = project_id or os.environ.get("EE_PROJECT_ID")
    if not resolved_project:
        raise ValueError("Set EE_PROJECT_ID to an Earth Engine-enabled Cloud project.")

    if ee_module is None:
        try:
            import ee as ee_module  # type: ignore[no-redef]
        except ImportError as exc:
            raise RuntimeError(
                "Earth Engine API is not installed; install earthengine-api in the "
                "project environment."
            ) from exc

    initializer: Callable[..., Any] = ee_module.Initialize
    initializer(project=resolved_project)
    return ee_module
