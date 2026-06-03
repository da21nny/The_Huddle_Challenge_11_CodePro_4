"""
Demostración TDD — Ciclo Red-Green-Refactor.

Funcionalidad elegida: validación de mensajes.

Este archivo documenta el proceso TDD tal como ocurrió:

  RED    → Se escriben los tests PRIMERO. La función validate_message
           no existe aún, así que los tests fallan.
  GREEN  → Se implementa validate_message con el código MÍNIMO para
           que los tests pasen.
  REFACTOR → Se limpia el código (guardia temprana, mensaje descriptivo)
             sin alterar el comportamiento. Los tests siguen pasando.
"""

from src.server import MAX_MSG_LENGTH, validate_message


# ===================================================================
# FASE RED — Tests escritos ANTES de la implementación
# ===================================================================
# Estos tests se escribieron primero. Al no existir validate_message,
# la ejecución fallaba con ImportError → RED ✗
#
# FASE GREEN — Implementación mínima
# Se implementó validate_message en server.py con:
#   if not msg or not msg.strip(): return (False, "...")
#   if len(msg) > MAX_MSG_LENGTH: return (False, "...")
#   return (True, "")
# Resultado: todos los tests pasan → GREEN ✓
#
# FASE REFACTOR — Limpieza
# Se mejoró la legibilidad (docstring, type hints) sin cambiar lógica.
# Resultado: tests siguen pasando → REFACTOR ✓
# ===================================================================


class TestValidateMessageTDD:
    """Ciclo TDD completo para validate_message."""

    # --- RED: estos tests se escribieron primero ---

    def test_red_mensaje_valido_retorna_true(self):
        """RED → espera que un mensaje normal sea válido."""
        ok, reason = validate_message("Hola")
        assert ok is True
        assert reason == ""

    def test_red_mensaje_vacio_retorna_false(self):
        """RED → espera que un mensaje vacío sea rechazado."""
        ok, reason = validate_message("")
        assert ok is False
        assert reason != ""

    def test_red_mensaje_largo_retorna_false(self):
        """RED → espera que un mensaje muy largo sea rechazado."""
        ok, reason = validate_message("x" * (MAX_MSG_LENGTH + 1))
        assert ok is False

    # --- GREEN: implementación mínima hizo pasar estos tests ---

    def test_green_solo_espacios_es_vacio(self):
        """GREEN → espacios en blanco se tratan como vacío."""
        ok, _ = validate_message("    \t  ")
        assert ok is False

    def test_green_limite_exacto_es_valido(self):
        """GREEN → mensaje con exactamente MAX_MSG_LENGTH es válido."""
        ok, _ = validate_message("a" * MAX_MSG_LENGTH)
        assert ok is True

    # --- REFACTOR: mismos tests, código más limpio ---

    def test_refactor_razon_contiene_descripcion(self):
        """REFACTOR → los mensajes de error son descriptivos."""
        _, reason = validate_message("")
        assert "vacío" in reason.lower()

        _, reason = validate_message("x" * (MAX_MSG_LENGTH + 1))
        assert "excede" in reason.lower()
