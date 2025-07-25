import logging
from collections.abc import Callable

from .claude_monitor import ClaudeMonitor
from .claude_process_controller import ClaudeProcessController
from .claude_session_manager import ClaudeSessionManager
from .claude_status_manager import ClaudeStatusManager
from .prompt_detector import PromptInfo

# Copyright notice.
# Copyright (c) 2024 Yesman Claude Project
# Licensed under the MIT License

"""Claude manager for dashboard integration - Refactored.""" ""


class DashboardController:
    """Main controller that orchestrates Claude session management, process control, and monitoring."""

    def __init__(self, session_name: str, pane_id: str | None = None) -> None:
        """Initialize the dashboard controller."""
        self.session_name = session_name
        self.pane_id = pane_id

        # Initialize component managers
        self.session_manager = ClaudeSessionManager(session_name, pane_id)
        self.status_manager = ClaudeStatusManager(session_name)
        self.process_controller = ClaudeProcessController(
            self.session_manager,
            self.status_manager,
        )
        self.monitor = ClaudeMonitor(
            self.session_manager,
            self.process_controller,
            self.status_manager,
        )

        self.logger = logging.getLogger(f"yesman.dashboard.controller.{session_name}")

        # Try to initialize session, but don't fail if session doesn't exist
        if not self.session_manager.initialize_session():
            self.status_manager.update_status(
                f"[yellow]Session '{session_name}' not found[/]",
            )

    @property
    def claude_pane(self) -> object:
        """Get the Claude pane (for backward compatibility).

        Returns:
        object: Description of return value.
        """
        return self.session_manager.get_claude_pane()

    @property
    def is_running(self) -> bool:
        """Check if monitoring is running.

        Returns:
        bool: Description of return value.
        """
        return self.monitor.is_running

    @property
    def is_auto_next_enabled(self) -> bool:
        """Check if auto-next is enabled.

        Returns:
        bool: Description of return value.
        """
        return self.monitor.is_auto_next_enabled

    @property
    def selected_model(self) -> str:
        """Get selected model.

        Returns:
        str: Description of return value.
        """
        return self.process_controller.selected_model

    def set_status_callback(self, callback: Callable) -> None:
        """Set callback for status updates."""
        self.status_manager.set_status_callback(callback)

    def set_activity_callback(self, callback: Callable) -> None:
        """Set callback for activity updates."""
        self.status_manager.set_activity_callback(callback)

    def start(self) -> bool:
        """Start the controller.

        Returns:
        bool: Description of return value.
        """
        # Re-initialize in case session was created after initialization
        if not self.claude_pane and not self.session_manager.initialize_session():
            self.logger.error(f"Failed to initialize session '{self.session_name}'")  # noqa: G004
            return False

        if not self.claude_pane:
            self.logger.error(
                "No Claude pane found in session '%s'. Make sure the session is running and Claude Code is started.",
                self.session_name,
            )
            return False

        return self.monitor.start_monitoring()

    def stop(self) -> bool:
        """Stop the controller.

        Returns:
        bool: Description of return value.
        """
        return self.monitor.stop_monitoring()

    def restart_claude_pane(self) -> bool:
        """Restart Claude pane.

        Returns:
        bool: Description of return value.
        """
        return self.process_controller.restart_claude_pane()

    def set_model(self, model: str) -> None:
        """Set the selected model."""
        self.process_controller.set_model(model)

    def set_auto_next(self, enabled: bool) -> None:  # noqa: FBT001
        """Enable or disable auto-next responses."""
        self.monitor.set_auto_next(enabled)

    def set_mode_yn(self, mode: str, response: str) -> None:
        """Set manual override for Y/N prompts."""
        self.monitor.set_mode_yn(mode, response)

    def set_mode_12(self, mode: str, response: str) -> None:
        """Set manual override for 1/2 prompts."""
        self.monitor.set_mode_12(mode, response)

    def set_mode_123(self, mode: str, response: str) -> None:
        """Set manual override for 1/2/3 prompts."""
        self.monitor.set_mode_123(mode, response)

    def capture_pane_content(self, lines: int = 50) -> str:
        """Capture content from Claude pane.

        Returns:
        str: Description of return value.
        """
        content = self.session_manager.capture_pane_content(lines)
        if content:
            # Save capture to file
            self.status_manager.save_capture_to_file(content, self.pane_id)
        return content

    def send_input(self, text: str) -> None:
        """Send input to Claude pane."""
        self.process_controller.send_input(text)

    def is_waiting_for_input(self) -> bool:
        """Check if Claude is currently waiting for user input.

        Returns:
        bool: Description of return value.
        """
        return self.monitor.is_waiting_for_input()

    def get_current_prompt(self) -> PromptInfo | None:
        """Get the current prompt information.

        Returns:
        object: Description of return value.
        """
        return self.monitor.get_current_prompt()

    def get_response_history(self) -> list:
        """Get the response history.

        Returns:
        list: Description of return value.
        """
        return self.status_manager.get_response_history()

    def get_collection_stats(self) -> dict:
        """Get content collection statistics.

        Returns:
        dict: Description of return value.
        """
        return self.monitor.get_collection_stats()

    def cleanup_old_collections(self, days_to_keep: int = 7) -> int:
        """Clean up old collection files.

        Returns:
        int: Description of return value.
        """
        return self.monitor.cleanup_old_collections(days_to_keep)

    # Adaptive response system methods
    def get_adaptive_statistics(self) -> dict:
        """Get statistics from the adaptive response system.

        Returns:
        dict: Description of return value.
        """
        return self.monitor.get_adaptive_statistics()

    def set_adaptive_confidence_threshold(self, threshold: float) -> None:
        """Adjust the confidence threshold for adaptive responses."""
        self.monitor.set_adaptive_confidence_threshold(threshold)

    def enable_adaptive_response(self, enabled: bool = True) -> None:  # noqa: FBT001
        """Enable or disable adaptive response functionality."""
        self.monitor.enable_adaptive_response(enabled)

    def enable_adaptive_learning(self, enabled: bool = True) -> None:  # noqa: FBT001
        """Enable or disable adaptive learning functionality."""
        self.monitor.enable_adaptive_learning(enabled)

    def export_adaptive_data(self, output_path: str) -> bool:
        """Export adaptive learning data for analysis.

        Returns:
        bool: Description of return value.
        """
        return self.monitor.export_adaptive_data(output_path)

    def learn_from_user_input(
        self,
        prompt_text: str,
        user_response: str,
        context: str = "",
    ) -> None:
        """Learn from manual user input for future improvements.

        Returns:
        None: Description of return value.
        """
        self.monitor.learn_from_user_input(prompt_text, user_response, context)

    # Context-aware automation methods
    async def start_automation_monitoring(self, monitor_interval: int = 10) -> bool:
        """Start context-aware automation monitoring."""
        return await self.monitor.start_automation_monitoring(monitor_interval)

    async def stop_automation_monitoring(self) -> bool:
        """Stop context-aware automation monitoring."""
        return await self.monitor.stop_automation_monitoring()

    def get_automation_status(self) -> dict:
        """Get automation system status.

        Returns:
        dict: Description of return value.
        """
        return self.monitor.get_automation_status()

    def register_automation_workflow(self, workflow: object) -> None:
        """Register a custom automation workflow."""
        self.monitor.register_automation_workflow(workflow)

    async def test_automation(self, context_type_name: str) -> dict:
        """Test automation with simulated context."""
        return await self.monitor.test_automation(context_type_name)

    def get_automation_execution_history(self, limit: int = 10) -> list:
        """Get recent automation execution history.

        Returns:
        list: Description of return value.
        """
        return self.monitor.get_automation_execution_history(limit)

    def save_automation_config(self) -> None:
        """Save automation configuration."""
        self.monitor.save_automation_config()

    def load_automation_config(self) -> None:
        """Load automation configuration."""
        self.monitor.load_automation_config()

    # Project health monitoring methods
    async def calculate_project_health(self, force_refresh: bool = False) -> dict:  # noqa: FBT001
        """Calculate comprehensive project health."""
        return await self.monitor.calculate_project_health(force_refresh)

    def get_health_summary(self) -> dict:
        """Get a quick health summary.

        Returns:
        dict: Description of return value.
        """
        return self.monitor.get_health_summary()

    # Asynchronous logging methods
    async def start_async_monitoring(self) -> bool:
        """Start monitoring with async logging enabled."""
        return await self.monitor.start_async_monitoring()

    async def stop_async_monitoring(self) -> bool:
        """Stop monitoring and async logging."""
        return await self.monitor.stop_async_monitoring()

    def get_async_logging_stats(self) -> dict:
        """Get async logging statistics.

        Returns:
        dict: Description of return value.
        """
        return self.monitor.get_async_logging_stats()

    async def flush_async_logs(self) -> None:
        """Force flush all pending async logs."""
        await self.monitor.flush_async_logs()

    # Legacy compatibility methods (deprecated but kept for backward compatibility)
    def detect_trust_prompt(self, content: str) -> bool:
        """Detect trust prompt in content (deprecated - use monitor methods).

        Returns:
        bool: Description of return value.
        """
        return self.monitor._detect_trust_prompt(content)

    def auto_trust_if_needed(self) -> bool:
        """Auto-respond to trust prompts if detected (deprecated - use monitor methods).

        Returns:
        bool: Description of return value.
        """
        return self.monitor._auto_trust_if_needed()

    def auto_respond_to_selection(self, prompt_info: PromptInfo) -> bool:
        """Auto-respond to selection prompts (deprecated - use monitor methods).

        Returns:
        bool: Description of return value.
        """
        return self.monitor._auto_respond_to_selection(prompt_info)

    def check_for_prompt(self, content: str) -> PromptInfo | None:
        """Check if content contains a prompt waiting for input (deprecated - use monitor methods).

        Returns:
        object: Description of return value.
        """
        return self.monitor._check_for_prompt(content)

    def clear_prompt_state(self) -> None:
        """Clear prompt state (deprecated - use monitor methods)."""
        self.monitor._clear_prompt_state()


class ClaudeManager:
    """Manages multiple DashboardController instances, one for each session."""

    def __init__(self) -> None:
        """Initialize the Claude manager."""
        self.controllers: dict[str, DashboardController] = {}
        self.logger = logging.getLogger("yesman.dashboard.claude_manager")

    def get_controller(
        self,
        session_name: str,
        pane_id: str | None = None,
    ) -> DashboardController:
        """Get or create controller for session.

        Returns:
            Dashboardcontroller object the requested data.


        """
        if session_name not in self.controllers:
            self.controllers[session_name] = DashboardController(session_name, pane_id)
        return self.controllers[session_name]

    def remove_controller(self, session_name: str) -> None:
        """Remove controller for session."""
        if session_name in self.controllers:
            controller = self.controllers[session_name]
            controller.stop()
            del self.controllers[session_name]

    def stop_all(self) -> None:
        """Stop all controllers."""
        for controller in self.controllers.values():
            controller.stop()
        self.controllers.clear()
