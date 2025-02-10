
class Logger:
    """Logs operations performed by the calculator."""

    def __init__(self) -> None:
        """Doc string."""
        self.logs = []

    def log(self, operation: str, result: float) -> None:
        """Log an operation with its result."""
        entry = f"{operation} = {result}"
        self.logs.append(entry)

    def get_logs(self) -> list:
        """Return all logs."""
        return self.logs
