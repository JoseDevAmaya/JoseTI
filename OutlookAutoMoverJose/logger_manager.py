import logging
from pathlib import Path


class LoggerManager:
    """Builds and exposes a reusable local file logger."""

    def __init__(self, log_file: str = "outlook_auto_mover.log") -> None:
        self.log_path = Path(log_file).resolve()
        self._logger = logging.getLogger("OutlookAutoMoverJose")
        self._logger.setLevel(logging.INFO)
        self._configure_once()

    def _configure_once(self) -> None:
        if self._logger.handlers:
            return

        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        )
        file_handler = logging.FileHandler(self.log_path, encoding="utf-8")
        file_handler.setFormatter(formatter)
        self._logger.addHandler(file_handler)

    @property
    def logger(self) -> logging.Logger:
        return self._logger
