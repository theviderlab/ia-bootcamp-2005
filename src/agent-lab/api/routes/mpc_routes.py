"""
MPC (Model Context Protocol) management API routes.

Endpoints for:
- Creating MPC server instances
- Stopping instances
- Querying instance status
- Listing all instances
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


class CreateInstanceRequest(BaseModel):
    """Request model for creating an MPC instance."""

    instance_id: str
    host: str = "localhost"
    port: int


class InstanceResponse(BaseModel):
    """Response model for instance information."""

    instance_id: str
    status: str
    host: str
    port: int
    created_at: str


@router.post("/instances", response_model=InstanceResponse)
async def create_instance(request: CreateInstanceRequest):
    """
    Create and start a new MPC server instance.

    Args:
        request: Instance creation parameters.

    Returns:
        Information about the created instance.
    """
    # Implementation to be added in future iterations
    raise HTTPException(
        status_code=501, detail="Instance creation not implemented yet"
    )


@router.delete("/instances/{instance_id}")
async def stop_instance(instance_id: str):
    """
    Stop a running MPC server instance.

    Args:
        instance_id: Instance identifier to stop.

    Returns:
        Status of the operation.
    """
    raise HTTPException(status_code=501, detail="Instance stop not implemented yet")


@router.get("/instances/{instance_id}", response_model=InstanceResponse)
async def get_instance_status(instance_id: str):
    """
    Get status information for an MPC instance.

    Args:
        instance_id: Instance identifier.

    Returns:
        Current instance information.
    """
    raise HTTPException(status_code=501, detail="Status query not implemented yet")


@router.get("/instances", response_model=list[InstanceResponse])
async def list_instances():
    """
    List all managed MPC instances.

    Returns:
        List of all instance information.
    """
    raise HTTPException(status_code=501, detail="Instance listing not implemented yet")
