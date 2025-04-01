"""
The `notifier_component` package provides a Notifier class that sends alerts
when a result exceeds a specified threshold. This helps in tracking important
events and receiving notifications for results that are significant.

Usage:
    from notifier_component import Notifier

    notifier = Notifier(threshold=10)
    notifier.notify(12)
    alerts = notifier.get_notifications()
"""

from .main import Notifier

__all__ = ["Notifier"]
