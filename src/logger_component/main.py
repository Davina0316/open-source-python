
class Logger:
    """Logs operations performed by the calculator."""

    def __init__(self) -> None:
        """Doc string"""
        self.logs:list[str] = []

    def log(self, operation: str, result: float) -> None:
        """Logs an operation with its result."""
        entry = f"{operation} = {result}"
        self.logs.append(entry)

    def get_logs(self) -> list[str]:
        """Returns all logs."""
        return self.logs
