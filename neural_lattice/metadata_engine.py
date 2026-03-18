"""Metadata Engine — auto-generates YAML frontmatter with 10 required fields.

Implements Charter Section 3.3 metadata schema.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import yaml

from neural_lattice.meta.schemas import (
    ArtifactType,
    ProtocolEnum,
    StatusEnum,
    ZoneEnum,
    validate_metadata,
)
from neural_lattice.zone_engine import ZoneEngine


class MetadataEngine:
    """Generates and validates YAML frontmatter for documents."""

    @staticmethod
    def generate(
        doc_id: str,
        title: str,
        cognitive_load: int,
        artifact_type: str | ArtifactType = ArtifactType.NOTE,
        protocol: str | ProtocolEnum = ProtocolEnum.ONSET_OMEGA_1,
        status: str | StatusEnum = StatusEnum.DRAFT,
        dependencies: list[str] | None = None,
        tags: list[str] | None = None,
        zone: str | ZoneEnum | None = None,
    ) -> dict[str, Any]:
        """Generate a complete metadata block with all 10 required fields."""
        if isinstance(artifact_type, ArtifactType):
            artifact_type = artifact_type.value
        if isinstance(protocol, ProtocolEnum):
            protocol = protocol.value
        if isinstance(status, StatusEnum):
            status = status.value

        # Auto-classify zone from cognitive_load if not given
        if zone is None:
            resolved_zone = ZoneEngine.classify_zone(cognitive_load)
        elif isinstance(zone, ZoneEnum):
            resolved_zone = zone
        else:
            resolved_zone = ZoneEnum(zone)

        meta: dict[str, Any] = {
            "doc_id": doc_id,
            "title": title,
            "zone": resolved_zone.value,
            "protocol": protocol,
            "artifact_type": artifact_type,
            "cognitive_load": cognitive_load,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "dependencies": dependencies or [],
            "tags": tags or [],
            "status": status,
        }
        return meta

    @staticmethod
    def validate(meta: dict[str, Any]) -> list[str]:
        """Validate a metadata block. Returns list of errors (empty = valid)."""
        return validate_metadata(meta)

    @staticmethod
    def to_yaml(meta: dict[str, Any]) -> str:
        """Serialize metadata to YAML frontmatter string."""
        return yaml.dump(meta, default_flow_style=False, sort_keys=False)

    @staticmethod
    def from_yaml(yaml_str: str) -> dict[str, Any]:
        """Parse YAML frontmatter string to metadata dict."""
        return yaml.safe_load(yaml_str)

    @staticmethod
    def to_frontmatter(meta: dict[str, Any]) -> str:
        """Wrap metadata in YAML frontmatter delimiters (---)."""
        return f"---\n{MetadataEngine.to_yaml(meta)}---\n"

    @staticmethod
    def extract_frontmatter(content: str) -> tuple[dict[str, Any] | None, str]:
        """Extract YAML frontmatter from document content.

        Returns (metadata_dict, remaining_content). If no frontmatter
        found, returns (None, original_content).
        """
        if not content.startswith("---"):
            return None, content
        parts = content.split("---", 2)
        if len(parts) < 3:
            return None, content
        meta = yaml.safe_load(parts[1])
        body = parts[2].lstrip("\n")
        return meta, body
