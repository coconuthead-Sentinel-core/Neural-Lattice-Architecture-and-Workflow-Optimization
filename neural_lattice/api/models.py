"""Pydantic models for API request/response validation."""

from __future__ import annotations

import re

from pydantic import BaseModel, Field, field_validator


class DocumentCreate(BaseModel):
    doc_id: str = Field(..., pattern=r"^[A-Z]{3,4}-[A-Z]{3,6}-[0-9]{3}$")
    title: str = Field(..., min_length=1, max_length=200)
    cognitive_load: int = Field(..., ge=1, le=10)
    artifact_type: str = "note"
    protocol: str = "Onset_Omega_1"
    status: str = "DRAFT"
    dependencies: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    content: str = ""
    zone: str | None = None

    @field_validator("tags", mode="before")
    @classmethod
    def validate_tags(cls, v: list[str]) -> list[str]:
        for tag in v:
            if not re.match(r"^[a-z][a-z0-9_]*$", tag):
                raise ValueError(f"Invalid tag: {tag}")
        return v


class DocumentUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=200)
    cognitive_load: int | None = Field(None, ge=1, le=10)
    artifact_type: str | None = None
    protocol: str | None = None
    status: str | None = None
    dependencies: list[str] | None = None
    tags: list[str] | None = None
    content: str | None = None
    version: str | None = None

    @field_validator("tags", mode="before")
    @classmethod
    def validate_tags(cls, v: list[str] | None) -> list[str] | None:
        if v is None:
            return v
        for tag in v:
            if not re.match(r"^[a-z][a-z0-9_]*$", tag):
                raise ValueError(f"Invalid tag: {tag}")
        return v


class ZoneMigrateRequest(BaseModel):
    doc_id: str
    target_zone: str = Field(..., pattern=r"^(GREEN|YELLOW|RED)$")
    cognitive_load: int = Field(..., ge=1, le=10)
    status: str = "ACTIVE"
    version: str = "0.1"
    revision_needed: bool = False
    scope_change_approved: bool = False


class ClassifyRequest(BaseModel):
    cognitive_load: int = Field(..., ge=1, le=10)


class ValidateRequest(BaseModel):
    doc_id: str
    title: str
    zone: str
    protocol: str
    artifact_type: str
    cognitive_load: int
    timestamp: str
    dependencies: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    status: str


class SessionCreateRequest(BaseModel):
    session_id: str | None = None


class WorkEndRequest(BaseModel):
    cognitive_load: int | None = Field(None, ge=1, le=10)
    notes: str = ""


class CognitiveLoadRequest(BaseModel):
    cognitive_load: int = Field(..., ge=1, le=10)


class ReflectRequest(BaseModel):
    insight: str = Field(..., min_length=1, max_length=1000)
    cognitive_load_after: int | None = Field(None, ge=1, le=10)
    carry_forward: str = ""
