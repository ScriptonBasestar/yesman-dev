# Copyright notice.

import datetime
import logging
from collections.abc import Callable
from pathlib import Path

from libs.utils import ensure_log_directory, get_default_log_path

# Import here to avoid circular import
from libs.yesman_config import YesmanConfig

# Copyright (c) 2024 Yesman Claude Project
# Licensed under the MIT License

"""Claude status and callback management."""


class ClaudeStatusManager:
    """Manages status updates, callbacks, and response history."""

    def __init__(self, session_name: str) -> None:
        self.session_name = session_name
        self.status_callback: Callable | None = None
        self.activity_callback: Callable | None = None
        self.response_history: list[dict[str, object]] = []
        self.logger = logging.getLogger(f"yesman.claude_status.{session_name}")

    def set_status_callback(self, callback: Callable) -> None:
        """Set callback for status updates."""
        self.status_callback = callback

    def set_activity_callback(self, callback: Callable) -> None:
        """Set callback for activity updates."""
        self.activity_callback = callback

    def update_status(self, message: str) -> None:
        """Update status through callback."""
        if self.status_callback:
            self.status_callback(message)
        self.logger.info(message)

    def update_activity(self, activity: str) -> None:
        """Update activity through callback."""
        if self.activity_callback:
            self.activity_callback(activity)

    def record_response(self, prompt_type: str, response: str, content: str) -> None:
        """Record auto-response in history."""
        record = {
            "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
            "prompt_type": prompt_type,
            "response": response,
            "content_snippet": content[-200:],  # Last 200 chars for context
        }
        self.response_history.append(record)
        self.logger.info(f"Auto-response recorded: {prompt_type} -> {response}")  # noqa: G004

        # Keep only last 100 responses
        if len(self.response_history) > 100:
            self.response_history = self.response_history[-100:]

    def get_response_history(self) -> list[dict[str, object]]:
        """Get the response history.

        Returns:
        Dict containing the requested data.
        """
        return self.response_history

    def save_capture_to_file(self, content: str, pane_id: str | None = None) -> str:
        """Save captured content to file and return file path.

        Returns:
        String containing.
        """
        try:
            config = YesmanConfig()
            log_base = config.get("log_path", str(get_default_log_path()))
            log_path = ensure_log_directory(Path(log_base))
            capture_dir = ensure_log_directory(log_path / "captures")

            ts = datetime.datetime.now(datetime.UTC).strftime("%Y%m%d_%H%M%S")
            pane_id = pane_id or "unknown"
            filename = f"capture_{self.session_name}_{pane_id}_{ts}.txt"
            file_path = capture_dir / filename

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

            self.logger.info(f"Saved pane capture to {file_path}")  # noqa: G004
            return str(file_path)

        except Exception as e:
            self.logger.exception("Error saving capture to file")  # noqa: G004
            return ""
