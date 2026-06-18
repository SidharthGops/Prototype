"""
Shared base types every module's schemas should extend or reuse.

Rule: this file holds concepts common to MULTIPLE modules only.
A field specific to one module's pipeline belongs in that module's
own schemas/schemas.py, not here.
"""

from enum import Enum
from typing import Optional, Any, Dict
from pydantic import BaseModel


class JobStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ImageReference(BaseModel):
    """Points at an image rather than embedding raw bytes in every payload."""
    url: Optional[str] = None
    base64: Optional[str] = None
    storage_key: Optional[str] = None


class JobRequest(BaseModel):
    """Base shape for any request that triggers a module pipeline.
    Module-specific request schemas should extend this."""
    job_id: Optional[str] = None
    metadata: Dict[str, Any] = {}


class JobResponse(BaseModel):
    """Base shape for any module's result. Module-specific response
    schemas should extend this with their own output fields."""
    job_id: Optional[str] = None
    status: JobStatus
    metadata: Dict[str, Any] = {}


class ErrorResponse(BaseModel):
    error_code: str
    message: str
