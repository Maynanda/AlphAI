"""
Reminder Engine feature. Handles scheduling and triggering of reminders (in-app and email).
Uses APScheduler in a background thread.
"""

import logging
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class ReminderEngine:
    def __init__(self, email_service):
        self.email_service = email_service
        self.scheduler = BackgroundScheduler()
        self.in_app_queue = []

    def start(self) -> None:
        """Starts the background scheduler thread."""
        try:
            if not self.scheduler.running:
                self.scheduler.start()
                logger.info("Reminder Engine background scheduler started.")
                self.setup_default_reminders()
        except Exception as e:
            logger.error(f"Failed to start reminder scheduler: {e}")

    def stop(self) -> None:
        """Stops the background scheduler thread."""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Reminder Engine background scheduler stopped.")

    def setup_default_reminders(self) -> None:
        """Registers default cron triggers for daily morning, EOD, and Friday reports."""
        # Clean existing jobs
        self.scheduler.remove_all_jobs()

        # Morning Brief (9:00 AM daily)
        self.scheduler.add_job(
            self._trigger_morning_brief,
            'cron',
            hour=9,
            minute=0,
            id='morning_brief'
        )

        # Team Check (2:00 PM daily)
        self.scheduler.add_job(
            self._trigger_team_check,
            'cron',
            hour=14,
            minute=0,
            id='team_check'
        )

        # EOD Review (5:00 PM daily)
        self.scheduler.add_job(
            self._trigger_eod_review,
            'cron',
            hour=17,
            minute=0,
            id='eod_review'
        )

        # Weekly Report (Friday 3:00 PM)
        self.scheduler.add_job(
            self._trigger_weekly_report_reminder,
            'cron',
            day_of_week='fri',
            hour=15,
            minute=0,
            id='weekly_report'
        )

    def _trigger_morning_brief(self) -> None:
        logger.info("Triggering morning brief reminders.")
        self.queue_in_app_notification("Good morning. Time for your morning brief.", "/?screen=daily_flow&step=1")
        # Optional: Send email via self.email_service

    def _trigger_team_check(self) -> None:
        logger.info("Triggering team unblocking check reminders.")
        self.queue_in_app_notification("Quick check: anyone blocked on your team?", "/?screen=team_tracker")

    def _trigger_eod_review(self) -> None:
        logger.info("Triggering end-of-day review reminders.")
        self.queue_in_app_notification("Time for your end-of-day review.", "/?screen=daily_flow&section=eod")

    def _trigger_weekly_report_reminder(self) -> None:
        logger.info("Triggering weekly report reminder.")
        self.queue_in_app_notification("Your weekly report is ready to review.", "/?screen=reports")

    def queue_in_app_notification(self, message: str, deep_link: str) -> None:
        """Appends notification to list for polling by Streamlit UI."""
        self.in_app_queue.append({
            "message": message,
            "deep_link": deep_link,
            "timestamp": datetime.datetime.utcnow().isoformat()
        })

    def fetch_in_app_notifications(self) -> List[Dict[str, Any]]:
        """Retrieves and clears the queued in-app notifications."""
        notifications = self.in_app_queue.copy()
        self.in_app_queue.clear()
        return notifications
