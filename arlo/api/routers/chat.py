"""
FastAPI router for Arlo Chat Agent.
"""

import logging
from fastapi import APIRouter, HTTPException, Depends
from arlo.api.schemas import ChatRequest, ChatResponse, SuggestionCardDataSchema
from arlo.features.arlo_agent import process_message, AgentResponse
from arlo.api.deps import get_llm

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/", response_model=ChatResponse)
def api_chat(payload: ChatRequest, llm=Depends(get_llm)):
    try:
        # Call features/arlo_agent.py process_message
        agent_resp: AgentResponse = process_message(
            user_message=payload.message,
            current_screen=payload.current_screen,
            active_project_id=payload.active_project_id,
            active_project_name=payload.active_project_name,
            llm=llm
        )
        
        # Serialize/Map to ChatResponse schema
        card_schema = None
        if agent_resp.suggestion_card:
            card_schema = SuggestionCardDataSchema(
                action_type=agent_resp.suggestion_card.action_type,
                project_name=agent_resp.suggestion_card.project_name,
                previous_text=agent_resp.suggestion_card.previous_text,
                suggested_text=agent_resp.suggestion_card.suggested_text,
                metadata=agent_resp.suggestion_card.metadata or {}
            )
            
        return ChatResponse(
            message=agent_resp.message,
            suggestion_card=card_schema,
            clarification_question=agent_resp.clarification_question,
            clarification_options=agent_resp.clarification_options or [],
            intent=agent_resp.intent,
            action_taken=agent_resp.action_taken
        )
    except Exception as e:
        logger.error(f"Chat execution failed: {e}")
        raise HTTPException(status_code=500, detail=f"Agent failed to process message: {e}")
