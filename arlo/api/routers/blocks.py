"""
FastAPI router for Leadership Blocks.
"""

from typing import List, Dict
from datetime import datetime
from fastapi import APIRouter, HTTPException
from arlo.core.models import Block, BlockType, BlockVersion
from arlo.core.database import get_db_connection
from arlo.features.activity_capture import update_block, get_block_history
from arlo.api.schemas import BlockUpdate

router = APIRouter(prefix="/blocks", tags=["blocks"])


@router.put("/project/{project_id}/{block_type}")
def api_update_block(project_id: int, block_type: BlockType, block_in: BlockUpdate):
    try:
        update_block(project_id, block_type, block_in.new_content)
        return {"status": "success", "message": f"Block {block_type.value} updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update block: {e}")


@router.get("/project/{project_id}/{block_type}/history", response_model=List[BlockVersion])
def api_get_block_history(project_id: int, block_type: BlockType, limit: int = 5):
    try:
        return get_block_history(project_id, block_type, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch block history: {e}")


@router.get("/project/{project_id}", response_model=Dict[str, Block])
def api_get_project_blocks(project_id: int):
    """Retrieves all current blocks for a project."""
    try:
        with get_db_connection() as conn:
            rows = conn.execute(
                "SELECT block_type, current_content, updated_at FROM blocks WHERE project_id = ?;",
                (project_id,)
            ).fetchall()
            
            blocks_dict = {}
            for r in rows:
                bt = r["block_type"]
                blocks_dict[bt] = Block(
                    project_id=project_id,
                    block_type=BlockType(bt),
                    current_content=r["current_content"] or "",
                    updated_at=datetime.fromisoformat(r["updated_at"])
                )
            
            # Fill in any missing block types
            for bt in BlockType:
                if bt.value not in blocks_dict:
                    blocks_dict[bt.value] = Block(
                        project_id=project_id,
                        block_type=bt,
                        current_content="",
                        updated_at=datetime.utcnow()
                    )
            return blocks_dict
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch project blocks: {e}")
