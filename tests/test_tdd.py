from src.server import MAX_MESSAGE_LENGTH, check_message

# ============================================================================
# TEST-DRIVEN DEVELOPMENT (TDD) - Ciclo Rojo-Verde-Refactor
# ============================================================================
# Metodologia que primero escribe las pruebas, luego implementa codigo
# que las hace pasar, y finalmente optimiza la solucion.

# FASE ROJA (Red): Escribir pruebas que fallan inicialmente
# El objetivo es validar comportamientos esperados
def test_valid_message_returns_true():
    ok, reason = check_message("Hola")
    assert ok is True
    assert reason == ""

# Rojo: mensaje vacío rechazado
def test_empty_message_returns_false():
    ok, reason = check_message("")
    assert ok is False
    assert reason != ""

# Rojo: mensaje largo rechazado
def test_long_message_returns_false():
    ok, reason = check_message("x" * (MAX_MESSAGE_LENGTH + 1))
    assert ok is False

# FASE VERDE (Green): Escribir codigo minimo para hacer pasar las pruebas
# Se anaden casos adicionales para validar el comportamiento
def test_only_spaces_is_empty():
    ok, _ = check_message("    \t  ")
    assert ok is False

# Verde: mensaje en límite exacto es válido
def test_exact_limit_is_valid():
    ok, _ = check_message("a" * MAX_MESSAGE_LENGTH)
    assert ok is True

# FASE REFACTOR: Optimizar el codigo manteniendo las pruebas pasando
# Se verifica que los mensajes de error sean descriptivos y claros
def test_reason_contains_description():
    _, reason = check_message("")
    assert "vacio" in reason.lower()

    _, reason = check_message("x" * (MAX_MESSAGE_LENGTH + 1))
    assert "excede" in reason.lower()

