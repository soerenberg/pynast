"""Function for reporting errors."""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import scanner


def throw_at(line: int, column: int, message: str):
    """Report error to std out, raise RuntimeError."""
    message = f"[line {line}, column {column}]: {message}"
    print(message)
    raise RuntimeError(message)


def throw_token(token: "scanner.Token", message: str) -> None:
    """Report error to std out, raise RuntimeError."""
    throw_at(token.line, token.column, message)
