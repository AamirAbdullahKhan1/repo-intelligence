"""Schema for the /capabilities endpoint response."""

from __future__ import annotations

from typing import List, Literal

from pydantic import BaseModel


class Capability(BaseModel):
    id: str
    name: str
    description: str
    status: Literal["implemented", "planned"]


class CapabilitiesResponse(BaseModel):
    service: str
    capabilities: List[Capability]
