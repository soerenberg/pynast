"""Expression node for ASTs."""
from __future__ import annotations

import abc
from typing import Any


class Expr:
    """Base class for expressions."""

    # pylint: disable=too-few-public-methods

    @abc.abstractmethod
    def accept(self, visitor: Visitor) -> Any:
        """Accept method for the visitor pattern."""


class Visitor:
    """Visitor for Expr types."""
