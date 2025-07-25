# Copyright notice.

import pytest

from libs.dashboard import KeyboardNavigationManager, NavigationContext
from libs.dashboard.keyboard_navigation import KeyModifier

# Copyright (c) 2024 Yesman Claude Project
# Licensed under the MIT License


class TestKeyboardNavigation:
    """Tests for keyboard navigation system."""

    @pytest.fixture
    @staticmethod
    def keyboard_manager() -> KeyboardNavigationManager:
        """Create KeyboardNavigationManager instance.

        Returns:
        KeyboardNavigationManager: Description of return value.
        """
        manager = KeyboardNavigationManager()
        yield manager
        # Cleanup
        manager.actions.clear()
        manager.bindings.clear()

    @staticmethod
    def test_keyboard_navigation(keyboard_manager: KeyboardNavigationManager) -> None:
        """Test 4: Keyboard navigation system."""
        # Test action registration
        test_called = False

        def test_action() -> None:
            nonlocal test_called
            test_called = True

        keyboard_manager.register_action("test_action", test_action)
        assert "test_action" in keyboard_manager.actions

        # Test key binding
        keyboard_manager.register_binding(
            "t",
            [KeyModifier.CTRL],
            "test_action",
            "Test action",
        )

        # Test key event handling
        handled = keyboard_manager.handle_key_event("t", [KeyModifier.CTRL])
        assert handled is True
        assert test_called is True

        # Test focus management
        keyboard_manager.add_focusable_element("element1", "button", 0)
        keyboard_manager.add_focusable_element("element2", "input", 1)

        assert len(keyboard_manager.focusable_elements) == 2

        # Test context switching
        keyboard_manager.set_context(NavigationContext.DASHBOARD)
        assert keyboard_manager.current_context == NavigationContext.DASHBOARD
