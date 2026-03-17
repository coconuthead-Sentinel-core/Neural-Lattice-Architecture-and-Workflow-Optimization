"""Metadata schema definitions matching Charter Section 3.3."""

from __future__ import annotations

import re
from enum import Enum
from typing import Any


class ZoneEnum(str, Enum):
    GREEN = "GREEN"
    YELLOW = "YELLOW"
    RED = "RED"


class StatusEnum(str, Enum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    TESTING = "TESTING"
    ARCHIVED = "ARCHIVED"
    REFERENCE = "REFERENCE"


class ProtocolEnum(str, Enum):
    ONSET_OMEGA_1 = "Onset_Omega_1"
    JOY_PROTOCOL = "Joy_Protocol"
    COCONUT_HEAD = "Coconut_Head"
    COMBINED = "Combined"


class ArtifactType(str, Enum):
    CHARTER = "charter"
    SPEC = "spec"
    USER_STORY = "user_story"
    DESIGN = "design"
    CODE = "code"
    TEST = "test"
    RUNBOOK = "runbook"
    REPORT = "report"
    TEMPLATE = "template"
    NOTE = "note"
    LOG = "log"
    CONFIG = "config"


DOC_ID_PATTERN = re.compile(r"^[A-Z]{3,4}-[A-Z]{3,6}-[0-9]{3}$")
TAG_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")

# Cognitive load ranges per zone (Charter Section 3.2 guards)
ZONE_LOAD_RANGES: dict[ZoneEnum, tuple[int, int]] = {
    ZoneEnum.GREEN: (7, 10),
    ZoneEnum.YELLOW: (4, 6),
    ZoneEnum.RED: (1, 3),
}


def validate_doc_id(doc_id: str) -> bool:
    return bool(DOC_ID_PATTERN.match(doc_id))


def validate_tag(tag: str) -> bool:
    return bool(TAG_PATTERN.match(tag))


def validate_cognitive_load_for_zone(zone: ZoneEnum, load: int) -> bool:
    lo, hi = ZONE_LOAD_RANGES[zone]
    return lo <= load <= hi


def validate_metadata(meta: dict[str, Any]) -> list[str]:
    """Return a list of validation errors (empty = valid)."""
    errors: list[str] = []
    required = [
        "doc_id", "title", "zone", "protocol", "artifact_type",
        "cognitive_load", "timestamp", "dependencies", "tags", "status",
    ]
    for field in required:
        if field not in meta:
            errors.append(f"Missing required field: {field}")

    if "doc_id" in meta and not validate_doc_id(meta["doc_id"]):
        errors.append(f"Invalid doc_id format: {meta['doc_id']} (expected ^[A-Z]{{3,4}}-[A-Z]{{3,6}}-[0-9]{{3}}$)")

    if "title" in meta:
        title = meta["title"]
        if not isinstance(title, str) or not (1 <= len(title) <= 200):
            errors.append(f"Title must be 1-200 characters, got {len(title) if isinstance(title, str) else type(title)}")

    if "zone" in meta:
        try:
            ZoneEnum(meta["zone"])
        except ValueError:
            errors.append(f"Invalid zone: {meta['zone']}")

    if "protocol" in meta:
        try:
            ProtocolEnum(meta["protocol"])
        except ValueError:
            errors.append(f"Invalid protocol: {meta['protocol']}")

    if "artifact_type" in meta:
        try:
            ArtifactType(meta["artifact_type"])
        except ValueError:
            errors.append(f"Invalid artifact_type: {meta['artifact_type']}")

    if "cognitive_load" in meta:
        load = meta["cognitive_load"]
        if not isinstance(load, int) or not (1 <= load <= 10):
            errors.append(f"cognitive_load must be integer 1-10, got {load}")
        elif "zone" in meta:
            try:
                zone = ZoneEnum(meta["zone"])
                if not validate_cognitive_load_for_zone(zone, load):
                    lo, hi = ZONE_LOAD_RANGES[zone]
                    errors.append(
                        f"cognitive_load {load} out of range for zone {zone.value} "
                        f"(expected {lo}-{hi})"
                    )
            except ValueError:
                pass  # zone error already captured

    if "status" in meta:
        try:
            StatusEnum(meta["status"])
        except ValueError:
            errors.append(f"Invalid status: {meta['status']}")

    if "tags" in meta:
        if not isinstance(meta["tags"], list):
            errors.append("tags must be an array")
        else:
            for tag in meta["tags"]:
                if not validate_tag(tag):
                    errors.append(f"Invalid tag format: {tag} (must be lowercase_underscore)")

    if "dependencies" in meta:
        if not isinstance(meta["dependencies"], list):
            errors.append("dependencies must be an array")
        else:
            for dep in meta["dependencies"]:
                if not validate_doc_id(dep):
                    errors.append(f"Invalid dependency doc_id: {dep}")

    return errors
