"""
nexus.engines.notifications.application.quiet_hours - Quiet Hours Evaluator.
"""

from __future__ import annotations

from nexus.engines.notifications.application.dtos import QuietHoursWindow


class QuietHoursEvaluator:
    """
    Evaluates whether the current local time falls within customer or branch quiet hours.
    """

    @classmethod
    def is_in_quiet_hours(cls, window: QuietHoursWindow, current_minute: int) -> bool:
        """
        Determines if current_minute (0-1439) falls inside the quiet window.
        Handles overnight periods (e.g. 22:00 to 08:00 -> 1320 to 480).
        """
        if not window.enabled:
            return False

        start = window.start_minute
        end = window.end_minute

        # Case 1: Overnight wrap (start > end, e.g. 22:00 -> 08:00)
        if start > end:
            return current_minute >= start or current_minute < end

        # Case 2: Same-day window (start <= end)
        return start <= current_minute < end
