import asyncio
from datetime import datetime, time
from sqlalchemy.orm import Session
from app.crud import reminder as crud_reminder
from app.models.reminder import Reminder
from typing import List
import logging

logger = logging.getLogger(__name__)


class ReminderService:
    def __init__(self):
        self.running = False

    async def start_reminder_checker(self, db: Session):
        """
        WHAT THIS DOES:
        - Runs in background every minute
        - Checks all active reminders
        - Sends notifications when it's time
        - Like a clock that never stops checking
        """
        self.running = True
        while self.running:
            try:
                await self.check_reminders(db)
                await asyncio.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Error in reminder checker: {e}")
                await asyncio.sleep(60)

                # app/services/reminder_service.py
    async def check_reminders(self, db: Session):
        """Check if it's time to send reminders"""
        current_time = datetime.now().strftime("%H:%M")
        current_weekday = datetime.now().weekday() + 1  # 1=Monday, 7=Sunday
        current_day = datetime.now().day  # Day of month (1-31)

        # ADD DEBUG LOGGING
        print(f" Checking reminders at {current_time}, weekday: {current_weekday}, day: {current_day}")

        # Get all active reminders
        all_reminders = db.query(Reminder).filter(Reminder.is_active == True).all()
        print(f"📋 Found {len(all_reminders)} active reminders")

        for reminder in all_reminders:
            try:
                should_send = self.should_send_reminder(reminder, current_time, current_weekday,
                                                        current_day)
                print(
                    f" Reminder '{reminder.name}' at {reminder.time} ({reminder.frequency}): {'✅ SEND' if should_send else '❌ Skip'}")

                if should_send:
                    await self.send_reminder(reminder)
            except Exception as e:
                logger.error(f"Error checking reminder {reminder.id}: {e}")


    # async def check_reminders(self, db: Session):
    #     """
    #     WHAT THIS DOES:
    #     - Gets current time (e.g., 22:00)
    #     - Gets current day of week (e.g., Monday = 1)
    #     - Gets current day of month (e.g., 15th)
    #     - Checks each reminder to see if it's time
    #     """
    #     current_time = datetime.now().strftime("%H:%M")
    #     current_weekday = datetime.now().weekday() + 1  # 1=Monday, 7=Sunday
    #     current_day = datetime.now().day  # Day of month (1-31)
    #
    #     # Get all active reminders
    #     all_reminders = db.query(Reminder).filter(Reminder.is_active == True).all()
    #
    #     for reminder in all_reminders:
    #         try:
    #             if self.should_send_reminder(reminder, current_time, current_weekday, current_day):
    #                 await self.send_reminder(reminder)
    #         except Exception as e:
    #             logger.error(f"Error checking reminder {reminder.id}: {e}")

    def should_send_reminder(self, reminder, current_time: str, current_weekday: int, current_day: int) -> bool:
        """
        WHAT THIS DOES:
        - Checks if it's time to send this reminder
        - For daily: always send at the time
        - For weekly: send if today is in selected_days
        - For monthly: send if today is in selected_days
        """
        # Check if time matches
        if reminder.time != current_time:
            return False

        # Check frequency
        if reminder.frequency == "daily":
            return True
        elif reminder.frequency == "weekly":
            if not reminder.selected_days:
                return False
            # Parse selected days: "1,3,5" -> [1, 3, 5] (Mon, Wed, Fri)
            selected_days = [int(day.strip()) for day in reminder.selected_days.split(",")]
            return current_weekday in selected_days
        elif reminder.frequency == "monthly":
            if not reminder.selected_days:
                return False
            # Parse selected days: "1,15,30" -> [1, 15, 30]
            selected_days = [int(day.strip()) for day in reminder.selected_days.split(",")]
            return current_day in selected_days

        return False

    async def send_reminder(self, reminder):
        """
        WHAT THIS DOES:
        - Sends notification to user's phone
        - Like WhatsApp message or alarm
        - User gets notification even if app is closed
        """
        message = f"Time for: {reminder.name}"
        logger.info(f"REMINDER: {message}")

        # TODO: Add actual push notification here
        # await self.send_push_notification(reminder.user_id, message)

    def stop(self):
        """Stop the reminder checker"""
        self.running = False


# Global reminder service
reminder_service = ReminderService()