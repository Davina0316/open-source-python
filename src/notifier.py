from typing import List

class Notifier:
    """Sends alerts when a result exceeds a threshold."""

    def __init__(self, threshold: float) -> None:
        """Doc string."""
        self.threshold: float = threshold
        self.notifications: List[str] = []

    def notify(self, result: float) -> None:
        """Send a notification if the result exceeds the threshold."""
        if result > self.threshold:
            message = f"Alert: Result {result} exceeds threshold {self.threshold}"
            self.notifications.append(message)

    def get_notifications(self) -> List[str]:
        """Return all notifications."""
        return self.notifications
