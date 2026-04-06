"""Storage helpers for Draw.io files."""

from __future__ import annotations

import base64
from dataclasses import dataclass
import os
from pathlib import Path
from shutil import copyfile
import tempfile

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import ALLOWED_DIAGRAM_SUFFIXES, BUNDLED_SAMPLE_RELATIVE_PATHS, CONF_STORAGE_PATH


@dataclass(slots=True, frozen=True)
class ResolvedDiagramPaths:
    """Resolved paths for a diagram and its sibling PNG export."""

    storage_root: Path
    relative_path: str
    diagram_path: Path
    png_path: Path


def resolve_diagram_paths(
    hass: HomeAssistant, entry: ConfigEntry, relative_path: str
) -> ResolvedDiagramPaths:
    """Resolve a relative diagram path inside the configured storage root."""
    normalized_relative = relative_path.strip().replace("\\", "/")
    if not normalized_relative:
        raise ValueError("invalid_relative_path")
    if normalized_relative.startswith("/"):
        raise ValueError("invalid_relative_path")

    path_like = Path(normalized_relative)
    if path_like.is_absolute() or any(part in {"", ".", ".."} for part in path_like.parts):
        raise ValueError("invalid_relative_path")

    storage_root = Path(hass.config.path(entry.data[CONF_STORAGE_PATH])).resolve()
    diagram_path = (storage_root / path_like).resolve()

    if storage_root not in diagram_path.parents and diagram_path != storage_root:
        raise ValueError("invalid_relative_path")

    if diagram_path.suffix.lower() not in ALLOWED_DIAGRAM_SUFFIXES:
        raise ValueError("unsupported_extension")

    return ResolvedDiagramPaths(
        storage_root=storage_root,
        relative_path=path_like.as_posix(),
        diagram_path=diagram_path,
        png_path=diagram_path.with_suffix(".png"),
    )


def provision_bundled_samples(hass: HomeAssistant, entry: ConfigEntry) -> list[str]:
    """Copy bundled sample diagrams into the configured storage root."""
    storage_root = Path(hass.config.path(entry.data[CONF_STORAGE_PATH])).resolve()
    package_root = Path(__file__).resolve().parent
    copied_paths: list[str] = []

    for relative_path in BUNDLED_SAMPLE_RELATIVE_PATHS:
        source_path = package_root / relative_path
        destination_path = storage_root / relative_path

        if not source_path.exists() or destination_path.exists():
            continue

        destination_path.parent.mkdir(parents=True, exist_ok=True)
        _atomic_copy_file(source_path, destination_path)
        copied_paths.append(relative_path)

    return copied_paths


def _ensure_bundled_sample_available(
    hass: HomeAssistant, entry: ConfigEntry, relative_path: str
) -> None:
    """Copy a bundled sample to storage on demand when it is requested."""
    if relative_path not in BUNDLED_SAMPLE_RELATIVE_PATHS:
        return

    storage_root = Path(hass.config.path(entry.data[CONF_STORAGE_PATH])).resolve()
    destination_path = storage_root / relative_path
    if destination_path.exists():
        return

    package_root = Path(__file__).resolve().parent
    source_path = package_root / relative_path
    if not source_path.exists():
        return

    destination_path.parent.mkdir(parents=True, exist_ok=True)
    _atomic_copy_file(source_path, destination_path)


def read_diagram(hass: HomeAssistant, entry: ConfigEntry, relative_path: str) -> dict[str, str | bool]:
    """Read a diagram file and expose sibling PNG metadata."""
    resolved = resolve_diagram_paths(hass, entry, relative_path)
    _ensure_bundled_sample_available(hass, entry, resolved.relative_path)
    if not resolved.diagram_path.exists():
        raise FileNotFoundError(resolved.relative_path)

    xml_content = resolved.diagram_path.read_text(encoding="utf-8")

    return {
        "path": resolved.relative_path,
        "xml": xml_content,
        "png_path": resolved.png_path.relative_to(resolved.storage_root).as_posix(),
        "png_exists": resolved.png_path.exists(),
    }


def save_diagram(
    hass: HomeAssistant,
    entry: ConfigEntry,
    relative_path: str,
    xml_content: str,
    png_data_uri: str | None,
) -> dict[str, str | bool]:
    """Write the diagram XML and optional PNG sibling file."""
    resolved = resolve_diagram_paths(hass, entry, relative_path)
    resolved.diagram_path.parent.mkdir(parents=True, exist_ok=True)

    png_bytes = decode_png_data_uri(png_data_uri) if png_data_uri else None

    _atomic_write_bytes(resolved.diagram_path, xml_content.encode("utf-8"))

    if png_bytes is not None:
        _atomic_write_bytes(resolved.png_path, png_bytes)

    return {
        "path": resolved.relative_path,
        "png_path": resolved.png_path.relative_to(resolved.storage_root).as_posix(),
        "png_written": png_bytes is not None,
    }


def decode_png_data_uri(data_uri: str) -> bytes:
    """Decode a PNG data URI returned by diagrams.net export."""
    if not data_uri.startswith("data:image/png;base64,"):
        raise ValueError("invalid_png_data")

    encoded_bytes = data_uri.split(",", 1)[1]
    try:
        return base64.b64decode(encoded_bytes, validate=True)
    except (base64.binascii.Error, ValueError) as err:
        raise ValueError("invalid_png_data") from err


def _atomic_write_bytes(path: Path, content: bytes) -> None:
    """Write a file atomically within the target directory."""
    file_descriptor, temporary_path = tempfile.mkstemp(
        dir=str(path.parent),
        prefix=f".{path.name}.",
        suffix=".tmp",
    )

    try:
        with os.fdopen(file_descriptor, "wb") as temporary_file:
            temporary_file.write(content)
            temporary_file.flush()
            os.fsync(temporary_file.fileno())

        os.replace(temporary_path, path)
    except Exception:
        try:
            os.unlink(temporary_path)
        except FileNotFoundError:
            pass
        raise


def _atomic_copy_file(source_path: Path, destination_path: Path) -> None:
    """Copy a file atomically within the target directory."""
    file_descriptor, temporary_path = tempfile.mkstemp(
        dir=str(destination_path.parent),
        prefix=f".{destination_path.name}.",
        suffix=".tmp",
    )

    os.close(file_descriptor)

    try:
        copyfile(source_path, temporary_path)
        os.replace(temporary_path, destination_path)
    except Exception:
        try:
            os.unlink(temporary_path)
        except FileNotFoundError:
            pass
        raise
