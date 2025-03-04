
class Notifier:
    """Sends alerts when a result exceeds a threshold."""

    def __init__(self, threshold: float) -> None:
        """Doc string"""
        self.threshold = threshold
        self.notifications:list[str] = []

    def notify(self, result: float) -> None:
        """Send a notification if the result exceeds the threshold."""
        if result > self.threshold:
            message = f"Alert: Result {result} exceeds threshold {self.threshold}"
            self.notifications.append(message)

    def get_notifications(self) -> list[str]:
        """Returns all notifications."""
        return self.notifications
