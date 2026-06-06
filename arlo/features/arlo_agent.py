"""
Arlo Agent — central intent routing and orchestration (FR-C / §8).
Classifies user messages, routes to feature handlers, returns structured responses.
Works with or without LLM (graceful degradation).
"""

import logging
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List

from arlo.core.prompts import PROMPTS

logger = logging.getLogger(__name__)

# --------------------------------------------------------------------------- #
#  Response types
# --------------------------------------------------------------------------- #

@dataclass
class SuggestionCardData:
    action_type: str          # e.g. "UPDATE_BLOCK", "CREATE_ACTIVITY"
    project_name: str
    previous_text: str
    suggested_text: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentResponse:
    message: str
    suggestion_card: Optional[SuggestionCardData] = None
    clarification_question: Optional[str] = None
    clarification_options: List[str] = field(default_factory=list)
    intent: str = "unknown"
    action_taken: bool = False


# --------------------------------------------------------------------------- #
#  Main entry point
# --------------------------------------------------------------------------- #

def process_message(
    user_message: str,
    current_screen: str = "dashboard",
    active_project_id: Optional[int] = None,
    active_project_name: str = "",
    llm=None,
) -> AgentResponse:
    """
    Full Arlo agent pipeline:
      1. Classify intent via LLM P-01 (or keyword fallback)
      2. Route to handler
      3. Return AgentResponse with message and optional suggestion card
    """
    # Step 1: Classify intent
    intent_data = _classify_intent(
        user_message, current_screen, active_project_name, llm
    )
    intent = intent_data.get("intent", "unknown")
    entities = intent_data.get("entities", {})
    clarification_needed = intent_data.get("clarification_needed", False)
    clarification_question = intent_data.get("clarification_question", "")

    # Step 2: Ask clarification if needed (before any action)
    if clarification_needed and clarification_question:
        options = _build_clarification_options(intent, active_project_id)
        return AgentResponse(
            message=clarification_question,
            clarification_question=clarification_question,
            clarification_options=options,
            intent=intent,
        )

    # Step 3: Route intent → handler
    return _route_intent(
        intent=intent,
        entities=entities,
        user_message=user_message,
        active_project_id=active_project_id,
        active_project_name=active_project_name,
        llm=llm,
    )


# --------------------------------------------------------------------------- #
#  Intent classification
# --------------------------------------------------------------------------- #

def _classify_intent(
    user_message: str,
    current_screen: str,
    project_name: str,
    llm,
) -> Dict[str, Any]:
    """Uses LLM P-01 or keyword fallback to classify the message."""
    if llm is not None and getattr(llm, "is_loaded", False):
        try:
            prompt = PROMPTS["P-01"]["v1"]
            user_prompt = prompt["user"].format(
                user_message=user_message,
                current_screen=current_screen,
                project_name=project_name or "None",
            )
            result = llm.generate_json(prompt["system"], user_prompt)
            return result
        except Exception as e:
            logger.warning(f"LLM intent classification failed: {e}. Using keyword fallback.")

    return _keyword_classify(user_message)


def _keyword_classify(message: str) -> Dict[str, Any]:
    """Simple keyword-based intent fallback when LLM is unavailable."""
    msg = message.lower()
    if any(k in msg for k in ["create project", "new project"]):
        return {"intent": "create_project", "entities": {}, "clarification_needed": False}
    if any(k in msg for k in ["log activity", "completed", "finished", "i did"]):
        return {"intent": "log_activity", "entities": {"text": message}, "clarification_needed": True, "clarification_question": "Which project is this for?"}
    if any(k in msg for k in ["update progress", "update block", "update focus", "update risk", "update support"]):
        return {"intent": "update_block", "entities": {"text": message}, "clarification_needed": True, "clarification_question": "Which block and project should I update?"}
    if any(k in msg for k in ["log risk", "risk:", "blocker"]):
        return {"intent": "log_risk", "entities": {"text": message}, "clarification_needed": True, "clarification_question": "Which project is this risk for?"}
    if any(k in msg for k in ["unblocked", "helped", "unblock"]):
        return {"intent": "log_unblocking", "entities": {"text": message}, "clarification_needed": True, "clarification_question": "Who did you unblock and how many hours were saved?"}
    if any(k in msg for k in ["feedback", "manager said", "peer said"]):
        return {"intent": "capture_feedback", "entities": {"text": message}, "clarification_needed": False}
    if any(k in msg for k in ["intention", "priority", "today i want", "my goals"]):
        return {"intent": "set_intentions", "entities": {"text": message}, "clarification_needed": False}
    if any(k in msg for k in ["mark intention", "complete intention", "done intention"]):
        return {"intent": "complete_intention", "entities": {}, "clarification_needed": True, "clarification_question": "Which intention number should I mark complete?"}
    if any(k in msg for k in ["delete intention", "remove intention"]):
        return {"intent": "delete_intention", "entities": {}, "clarification_needed": True, "clarification_question": "Which intention number should I delete?"}
    if any(k in msg for k in ["carry over", "carry intention"]):
        return {"intent": "carry_intention", "entities": {}, "clarification_needed": True, "clarification_question": "Which intention should I carry over to tomorrow?"}
    if any(k in msg for k in ["generate", "write", "draft", "status update", "write a"]):
        return {"intent": "generate_draft", "entities": {"text": message}, "clarification_needed": True, "clarification_question": "Which project should I generate a draft for?"}
    if any(k in msg for k in ["what are", "show me", "list", "open risks", "query"]):
        return {"intent": "query_context", "entities": {"text": message}, "clarification_needed": False}
    if any(k in msg for k in ["morning brief", "start brief", "morning"]):
        return {"intent": "start_morning_brief", "entities": {}, "clarification_needed": False}
    return {"intent": "unknown", "entities": {}, "clarification_needed": False}


# --------------------------------------------------------------------------- #
#  Intent routing
# --------------------------------------------------------------------------- #

def _route_intent(
    intent: str,
    entities: Dict[str, Any],
    user_message: str,
    active_project_id: Optional[int],
    active_project_name: str,
    llm,
) -> AgentResponse:
    """Dispatches to the appropriate handler for each intent."""

    if intent == "create_project":
        return AgentResponse(
            message="Sure! Let me open the project creation form for you. Fill in the 5 clarity questions and I'll register your project.",
            intent=intent,
            action_taken=False,
        )

    elif intent == "log_activity":
        activity_text = entities.get("text", user_message)
        if not active_project_id:
            return _needs_project(intent)
        try:
            from arlo.features.activity_capture import log_activity
            activity = log_activity(active_project_id, activity_text)
            # Try to suggest a block update
            suggestion = _suggest_block_update(active_project_id, active_project_name, activity_text, llm)
            return AgentResponse(
                message=f"✅ Activity logged for **{active_project_name}**.",
                suggestion_card=suggestion,
                intent=intent,
                action_taken=True,
            )
        except Exception as e:
            logger.error(f"log_activity failed: {e}")
            return AgentResponse(message=f"❌ Failed to log activity: {e}", intent=intent)

    elif intent == "update_block":
        if not active_project_id:
            return _needs_project(intent)
        suggested_text = entities.get("text", user_message)
        block_type = entities.get("block", "progress")
        card = SuggestionCardData(
            action_type="UPDATE_BLOCK",
            project_name=active_project_name,
            previous_text=_get_current_block(active_project_id, block_type),
            suggested_text=suggested_text,
            metadata={"project_id": active_project_id, "block_type": block_type},
        )
        return AgentResponse(
            message=f"Here's my suggested update for the **{block_type}** block:",
            suggestion_card=card,
            intent=intent,
        )

    elif intent == "log_risk":
        if not active_project_id:
            return _needs_project(intent)
        return AgentResponse(
            message="To log this risk, please use the **📝 Log Activity** form on the Project Detail screen and select 'Risk Logged'. I'll suggest a block update after you save.",
            intent=intent,
        )

    elif intent == "log_unblocking":
        return AgentResponse(
            message="Head to **Team Tracker → Log Unblocking** to record who you unblocked and the impact. This is key evidence for your promotion case.",
            intent=intent,
        )

    elif intent == "capture_feedback":
        return AgentResponse(
            message="Go to **Team Tracker → Log Feedback** to capture this. I'll extract sentiment and topics once you save it.",
            intent=intent,
        )

    elif intent == "set_intentions":
        return AgentResponse(
            message="Head to **Daily Flow → Morning Brief** to set today's intentions. You can also type them here: just list your top 3 priorities.",
            intent=intent,
        )

    elif intent in ("complete_intention", "delete_intention", "carry_intention"):
        action_map = {
            "complete_intention": ("complete", "✅"),
            "delete_intention": ("delete", "🗑️"),
            "carry_intention": ("carry over to tomorrow", "↩"),
        }
        action_label, icon = action_map[intent]
        return AgentResponse(
            message=f"{icon} Open **Daily Flow** to {action_label} intentions. Each intention has action buttons you can click directly.",
            intent=intent,
        )

    elif intent == "generate_draft":
        if not active_project_id:
            return _needs_project(intent)
        return AgentResponse(
            message=f"Generating a communication draft for **{active_project_name}**... Head to **Communications** once it's ready. (Full LLM generation available when model is loaded.)",
            intent=intent,
        )

    elif intent == "query_context":
        query_text = entities.get("text", user_message)
        if active_project_id:
            return _answer_context_query(active_project_id, active_project_name, query_text)
        return AgentResponse(
            message="Which project would you like to query? Open a project first and then ask me again.",
            intent=intent,
        )

    elif intent == "start_morning_brief":
        return AgentResponse(
            message="☀️ Let's start your morning brief! Navigate to **Daily Flow → Morning Brief** to begin the 5-step flow.",
            intent=intent,
            action_taken=True,
        )

    else:
        return AgentResponse(
            message=(
                "I'm not sure what you'd like to do. Here are some things you can ask me:\n\n"
                "- *\"Create a new project called X\"*\n"
                "- *\"Log that I completed model validation on Project A\"*\n"
                "- *\"Generate a status update for Project B\"*\n"
                "- *\"Start my morning brief\"*\n"
                "- *\"What are the open risks on Project A?\"*"
            ),
            intent="unknown",
        )


# --------------------------------------------------------------------------- #
#  Helpers
# --------------------------------------------------------------------------- #

def _needs_project(intent: str) -> AgentResponse:
    return AgentResponse(
        message="Which project is this for? Open a project from the **Dashboard** and then ask me again.",
        clarification_question="Which project?",
        intent=intent,
    )


def _get_current_block(project_id: int, block_type: str) -> str:
    try:
        from arlo.core.database import get_db_connection
        with get_db_connection() as conn:
            row = conn.execute(
                "SELECT current_content FROM blocks WHERE project_id = ? AND block_type = ?;",
                (project_id, block_type)
            ).fetchone()
            return row["current_content"] if row and row["current_content"] else ""
    except Exception:
        return ""


def _suggest_block_update(
    project_id: int,
    project_name: str,
    activity_text: str,
    llm,
) -> Optional[SuggestionCardData]:
    """Uses LLM P-02 to suggest a block update after an activity is logged."""
    if llm is None or not getattr(llm, "is_loaded", False):
        return None
    try:
        current_progress = _get_current_block(project_id, "progress")
        prompt = PROMPTS["P-02"]["v1"]
        user_prompt = prompt["user"].format(
            activity_text=activity_text,
            block_name="progress",
            current_block_text=current_progress or "(empty)",
            rag_chunks="",
        )
        result = llm.generate_json(prompt["system"], user_prompt)
        suggested_text = result.get("suggested_text", "")
        block = result.get("block", "progress")
        if suggested_text:
            return SuggestionCardData(
                action_type="UPDATE_BLOCK",
                project_name=project_name,
                previous_text=_get_current_block(project_id, block),
                suggested_text=suggested_text,
                metadata={"project_id": project_id, "block_type": block},
            )
    except Exception as e:
        logger.warning(f"Block suggestion failed: {e}")
    return None


def _answer_context_query(
    project_id: int,
    project_name: str,
    query: str,
) -> AgentResponse:
    """Answers a context query by reading the current DB state."""
    try:
        from arlo.core.database import get_db_connection
        lines = [f"Here's what I know about **{project_name}**:\n"]
        with get_db_connection() as conn:
            # Fetch blocks
            rows = conn.execute(
                "SELECT block_type, current_content FROM blocks WHERE project_id = ?;",
                (project_id,)
            ).fetchall()
            for row in rows:
                if row["current_content"]:
                    label = row["block_type"].replace("_", " ").title()
                    lines.append(f"**{label}:** {row['current_content']}")

            # Recent activities
            acts = conn.execute(
                "SELECT content FROM activities WHERE project_id = ? ORDER BY created_at DESC LIMIT 5;",
                (project_id,)
            ).fetchall()
            if acts:
                lines.append("\n**Recent Activities:**")
                for a in acts:
                    lines.append(f"- {a['content']}")

        return AgentResponse(
            message="\n".join(lines) if len(lines) > 1 else f"No data found for {project_name} yet.",
            intent="query_context",
            action_taken=False,
        )
    except Exception as e:
        return AgentResponse(message=f"Query failed: {e}", intent="query_context")


def _build_clarification_options(intent: str, active_project_id: Optional[int]) -> List[str]:
    """Builds quick-reply option buttons for clarification."""
    try:
        from arlo.features.project_registry import list_projects
        projects = list_projects()
        return [p.name for p in projects[:5]]
    except Exception:
        return []
