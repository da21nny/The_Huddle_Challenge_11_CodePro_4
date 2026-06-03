"""
TDD Demonstration — Red-Green-Refactor Cycle.

Chosen functionality: message validation (check_message).

This file documents the TDD process as it happened:

  RED      → Tests are written FIRST. The check_message function
             does not exist yet, so tests fail.
  GREEN    → Implement check_message with MINIMAL code to
             make tests pass.
  REFACTOR → Clean up code (names, docstrings) without altering
             behavior. Tests continue to pass.
"""

from src.server import MAX_MESSAGE_LENGTH, check_message


# ===================================================================
# RED PHASE — Tests written BEFORE implementation
# ===================================================================
# These tests were written first. Since check_message did not exist,
# execution failed with ImportError → RED ✗
#
# GREEN PHASE — Minimal implementation
# check_message was implemented in server.py with:
#   if not msg or not msg.strip(): return (False, "...")
#   if len(msg) > MAX_MESSAGE_LENGTH: return (False, "...")
#   return (True, "")
# Result: all tests pass → GREEN ✓
#
# REFACTOR PHASE — Cleanup
# Improved readability (docstring, clear names) without changing logic.
# Result: tests continue to pass → REFACTOR ✓
# ===================================================================


class TestCheckMessageTDD:
    """Complete TDD cycle for check_message."""

    # --- 🔴 RED: these tests were written first ---

    def test_red_valid_message_returns_true(self):
        """RED → expects a normal message to be valid."""
        ok, reason = check_message("Hola")
        assert ok is True
        assert reason == ""

    def test_red_empty_message_returns_false(self):
        """RED → expects an empty message to be rejected."""
        ok, reason = check_message("")
        assert ok is False
        assert reason != ""

    def test_red_long_message_returns_false(self):
        """RED → expects a very long message to be rejected."""
        ok, reason = check_message("x" * (MAX_MESSAGE_LENGTH + 1))
        assert ok is False

    # --- 🟢 GREEN: minimal implementation made these tests pass ---

    def test_green_only_spaces_is_empty(self):
        """GREEN → whitespace is treated as empty."""
        ok, _ = check_message("    \t  ")
        assert ok is False

    def test_green_exact_limit_is_valid(self):
        """GREEN → message with exactly 500 characters is valid."""
        ok, _ = check_message("a" * MAX_MESSAGE_LENGTH)
        assert ok is True

    # --- 🔵 REFACTOR: same tests, cleaner code ---

    def test_refactor_reason_contains_description(self):
        """REFACTOR → error messages are descriptive."""
        _, reason = check_message("")
        assert "vacio" in reason.lower()

        _, reason = check_message("x" * (MAX_MESSAGE_LENGTH + 1))
        assert "excede" in reason.lower()
