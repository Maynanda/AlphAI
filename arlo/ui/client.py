"""
HTTP client for the Streamlit UI to communicate with the FastAPI backend.
"""

import os
import logging
from typing import List, Dict, Any, Optional
import httpx

logger = logging.getLogger(__name__)

# Base API configuration
API_BASE_URL = os.environ.get("ARLO_API_BASE_URL", "http://127.0.0.1:8000")


class ArloAPIClient:
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url
        self.timeout = 30.0 # Setup a generous timeout for LLM synthesis calls

    def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        url = f"{self.base_url}{path}"
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(url, params=params)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error on GET {url}: {e.response.text}")
            raise RuntimeError(e.response.json().get("detail", str(e)))
        except Exception as e:
            logger.error(f"Connection error on GET {url}: {e}")
            raise RuntimeError(f"Could not connect to Arlo API backend: {e}")

    def _post(self, path: str, json_data: Optional[Dict[str, Any]] = None, data: Optional[Dict[str, Any]] = None, files: Optional[Dict[str, Any]] = None) -> Any:
        url = f"{self.base_url}{path}"
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(url, json=json_data, data=data, files=files)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error on POST {url}: {e.response.text}")
            raise RuntimeError(e.response.json().get("detail", str(e)))
        except Exception as e:
            logger.error(f"Connection error on POST {url}: {e}")
            raise RuntimeError(f"Could not connect to Arlo API backend: {e}")

    def _put(self, path: str, json_data: Optional[Dict[str, Any]] = None, params: Optional[Dict[str, Any]] = None) -> Any:
        url = f"{self.base_url}{path}"
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.put(url, json=json_data, params=params)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error on PUT {url}: {e.response.text}")
            raise RuntimeError(e.response.json().get("detail", str(e)))
        except Exception as e:
            logger.error(f"Connection error on PUT {url}: {e}")
            raise RuntimeError(f"Could not connect to Arlo API backend: {e}")

    def _delete(self, path: str) -> Any:
        url = f"{self.base_url}{path}"
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.delete(url)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error on DELETE {url}: {e.response.text}")
            raise RuntimeError(e.response.json().get("detail", str(e)))
        except Exception as e:
            logger.error(f"Connection error on DELETE {url}: {e}")
            raise RuntimeError(f"Could not connect to Arlo API backend: {e}")

    # --- Project Registry ---

    def list_projects(self, include_archived: bool = False) -> List[Dict[str, Any]]:
        return self._get("/projects/", params={"include_archived": include_archived})

    def get_project(self, project_id: int) -> Dict[str, Any]:
        return self._get(f"/projects/{project_id}")

    def create_project(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        return self._post("/projects/", json_data=project_data)

    def archive_project(self, project_id: int) -> Dict[str, Any]:
        return self._post(f"/projects/{project_id}/archive")

    # --- Activities ---

    def list_activities(self, project_id: int) -> List[Dict[str, Any]]:
        return self._get(f"/activities/project/{project_id}")

    def log_activity(self, project_id: int, content: str) -> Dict[str, Any]:
        return self._post("/activities/", json_data={"project_id": project_id, "content": content})

    def edit_activity(self, activity_id: int, content: str) -> Dict[str, Any]:
        return self._put(f"/activities/{activity_id}", params={"content": content})

    # --- Blocks ---

    def get_project_blocks(self, project_id: int) -> Dict[str, Any]:
        return self._get(f"/blocks/project/{project_id}")

    def update_block(self, project_id: int, block_type: str, content: str) -> Dict[str, Any]:
        return self._put(f"/blocks/project/{project_id}/{block_type}", json_data={"new_content": content})

    def get_block_history(self, project_id: int, block_type: str, limit: int = 5) -> List[Dict[str, Any]]:
        return self._get(f"/blocks/project/{project_id}/{block_type}/history", params={"limit": limit})

    # --- Daily Intentions ---

    def get_intentions(self, date_str: str) -> Dict[str, Any]:
        return self._get(f"/intentions/daily/{date_str}")

    def save_intentions(self, date_str: str, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        return self._post(f"/intentions/daily/{date_str}", json_data={"items": items})

    def update_intention_status(self, date_str: str, index: int, status: str) -> Dict[str, Any]:
        return self._put(f"/intentions/daily/{date_str}/{index}/status", json_data={"status": status})

    def confirm_eod(self, date_str: str) -> Dict[str, Any]:
        return self._post(f"/intentions/daily/{date_str}/confirm_eod")

    def carry_intention(self, date_str: str, index: int, to_date_str: str) -> Dict[str, Any]:
        return self._post(f"/intentions/daily/{date_str}/{index}/carry", json_data={"to_date_str": to_date_str, "index": index})

    def get_overdue_count(self, current_date_str: str) -> int:
        return self._get("/intentions/overdue", params={"current_date_str": current_date_str})

    # --- Team Tracker ---

    def log_unblocking_action(self, action_data: Dict[str, Any], project_id: Optional[int] = None) -> Dict[str, Any]:
        path = "/team/unblock"
        if project_id is not None:
            path += f"?project_id={project_id}"
        return self._post(path, json_data=action_data)

    def list_unblocking_actions(self, project_id: Optional[int] = None, limit: int = 20) -> List[Dict[str, Any]]:
        params = {"limit": limit}
        if project_id is not None:
            params["project_id"] = project_id
        return self._get("/team/unblock", params=params)

    def capture_feedback(self, feedback_data: Dict[str, Any], project_id: Optional[int] = None) -> Dict[str, Any]:
        path = "/team/feedback"
        if project_id is not None:
            path += f"?project_id={project_id}"
        return self._post(path, json_data=feedback_data)

    def list_feedback(self, project_id: Optional[int] = None, limit: int = 20) -> List[Dict[str, Any]]:
        params = {"limit": limit}
        if project_id is not None:
            params["project_id"] = project_id
        return self._get("/team/feedback", params=params)

    # --- Communications ---

    def list_communications(self, project_id: Optional[int] = None, status: Optional[str] = None) -> List[Dict[str, Any]]:
        params = {}
        if project_id is not None:
            params["project_id"] = project_id
        if status is not None:
            params["status"] = status
        return self._get("/communications/", params=params)

    def create_communication_draft(self, comm_data: Dict[str, Any]) -> Dict[str, Any]:
        return self._post("/communications/", json_data=comm_data)

    def get_communication(self, comm_id: int) -> Dict[str, Any]:
        return self._get(f"/communications/{comm_id}")

    def mark_communication_reviewed(self, comm_id: int) -> Dict[str, Any]:
        return self._post(f"/communications/{comm_id}/review")

    def archive_communication(self, comm_id: int) -> Dict[str, Any]:
        return self._post(f"/communications/{comm_id}/archive")

    def update_communication_body(self, comm_id: int, body: str) -> Dict[str, Any]:
        return self._put(f"/communications/{comm_id}/body", params={"body": body})

    def log_communication_copied(self, comm_id: int) -> Dict[str, Any]:
        return self._post(f"/communications/{comm_id}/copied")

    def get_communication_history(self, comm_id: int) -> List[Dict[str, Any]]:
        return self._get(f"/communications/{comm_id}/history")

    # --- Weekly Reports ---

    def compile_report(self, project_id: int, start_date_str: str) -> Dict[str, Any]:
        return self._get(f"/reports/weekly/{project_id}", params={"start_date_str": start_date_str})

    def synthesize_report(self, project_id: int, start_date_str: str) -> Dict[str, Any]:
        return self._post(f"/reports/weekly/{project_id}/synthesize", json_data={"start_date_str": start_date_str})

    def get_pdf_report_url(self, project_id: int, start_date_str: str) -> str:
        return f"{self.base_url}/reports/weekly/{project_id}/pdf?start_date_str={start_date_str}"

    # --- Document Manager ---

    def list_documents(self, project_id: int) -> List[Dict[str, Any]]:
        return self._get(f"/documents/project/{project_id}")

    def upload_document(self, project_id: int, doc_type: str, filename: str, file_content: bytes) -> Dict[str, Any]:
        files = {"file": (filename, file_content)}
        data = {"doc_type": doc_type}
        return self._post(f"/documents/project/{project_id}", data=data, files=files)

    def delete_document(self, project_id: int, document_id: int) -> Dict[str, Any]:
        return self._delete(f"/documents/project/{project_id}/{document_id}")

    def list_fragments(self, project_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        return self._get(f"/documents/project/{project_id}/fragments", params={"limit": limit})

    def save_fragment(self, project_id: int, content: str, source: str) -> Dict[str, Any]:
        data = {"content": content, "source": source}
        return self._post(f"/documents/project/{project_id}/fragment", data=data)


    # --- Settings & Streaks ---

    def get_settings(self) -> Dict[str, Any]:
        return self._get("/settings/")

    def update_settings(self, settings_dict: Dict[str, Any]) -> Dict[str, Any]:
        return self._put("/settings/", json_data=settings_dict)

    def get_streak(self) -> Dict[str, Any]:
        return self._get("/settings/streak")

    def check_streak(self, date_str: str) -> Dict[str, Any]:
        return self._post("/settings/streak/check", params={"date_str": date_str})

    # --- Email ---

    def send_email(self, to_email: str, subject: str, body_text: str, body_html: Optional[str] = None) -> Dict[str, Any]:
        payload = {"to_email": to_email, "subject": subject, "body_text": body_text}
        if body_html:
            payload["body_html"] = body_html
        return self._post("/email/send", json_data=payload)

    # --- Chat Agent ---

    def send_chat_message(self, message: str, current_screen: str = "dashboard", active_project_id: Optional[int] = None, active_project_name: str = "") -> Dict[str, Any]:
        payload = {
            "message": message,
            "current_screen": current_screen,
            "active_project_id": active_project_id,
            "active_project_name": active_project_name
        }
        return self._post("/chat/", json_data=payload)
