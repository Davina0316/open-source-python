from .main import Notifier


def test_notifier():
    notifier = Notifier(threshold=10)
    notifier.notify(15)
    assert notifier.get_notifications() == ["Alert: Result 15 exceeds threshold 10"]
