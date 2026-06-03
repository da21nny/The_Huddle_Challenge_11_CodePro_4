from src.server import MAX_MESSAGE_LENGTH, check_message

# Pruebas TDD - Ciclo Rojo-Verde-Refactor

# Rojo: mensaje válido
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

# Verde: solo espacios se considera vacío
def test_only_spaces_is_empty():
    ok, _ = check_message("    \t  ")
    assert ok is False

# Verde: mensaje en límite exacto es válido
def test_exact_limit_is_valid():
    ok, _ = check_message("a" * MAX_MESSAGE_LENGTH)
    assert ok is True

# Refactor: razón contiene descripción clara
def test_reason_contains_description():
    _, reason = check_message("")
    assert "vacio" in reason.lower()

    _, reason = check_message("x" * (MAX_MESSAGE_LENGTH + 1))
    assert "excede" in reason.lower()

