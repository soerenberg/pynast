"""Statement nodes for ASTs."""
from __future__ import annotations
import abc
from typing import Any, List, Optional

from nast import expr
from nast import tokens


class Stmt:
    """Statement base class."""

    # pylint: disable=too-few-public-methods

    @abc.abstractmethod
    def accept(self, visitor: Visitor) -> Any:
        """Accept method for the visitor pattern."""


class Program(Stmt):
    """Stan program."""

    # pylint: disable=too-few-public-methods

    def __init__(self, functions: Block, data: Block, transformed_data: Block,
                 parameters: Block, transformed_parameters: Block,
                 model: Block, generated_quantities: Block):
        # pylint: disable=too-many-arguments
        self.functions = functions
        self.data = data
        self.transformed_data = transformed_data
        self.parameters = parameters
        self.transformed_parameters = transformed_parameters
        self.model = model
        self.generated_quantities = generated_quantities

    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_program(self)


class Declaration(Stmt):
    """Variable declaration statement."""

    # pylint: disable=too-few-public-methods

    def __init__(self,
                 dtype: tokens.Token,
                 identifier: tokens.Token,
                 type_dims: Optional[List[expr.Expr]] = None,
                 lower: Optional[expr.Expr] = None,
                 upper: Optional[expr.Expr] = None,
                 offset: Optional[expr.Expr] = None,
                 multiplier: Optional[expr.Expr] = None,
                 array_dims: Optional[List[expr.Expr]] = None,
                 initializer: Optional[expr.Expr] = None):
        # pylint: disable=too-many-arguments
        self.dtype = dtype
        self.identifier = identifier
        self.type_dims = type_dims or []
        self.lower = lower
        self.upper = upper
        self.offset = offset
        self.multiplier = multiplier
        self.array_dims = array_dims or []
        self.initializer = initializer

    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_declaration(self)

    def __eq__(self, other):
        return (isinstance(other, Declaration) and self.dtype == other.dtype
                and self.identifier == other.identifier
                and self.type_dims == other.type_dims
                and self.lower == other.lower and self.upper == other.upper
                and self.offset == other.offset
                and self.multiplier == other.multiplier
                and self.initializer == other.initializer)


class ArgumentDeclaration(Stmt):
    """Argument declaration for custom functions."""

    def __init__(self, dtype: tokens.TokenType, n_dims: int,
                 identifier: tokens.Token):
        self.dtype = dtype
        self.n_dims = n_dims
        self.identifier = identifier

    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_argument_declaration(self)

    def __eq__(self, other):
        return (isinstance(other, ArgumentDeclaration)
                and self.dtype == other.dtype and self.n_dims == other.n_dims
                and self.identifier == other.identifier)


class Assign(Stmt):
    """Assignment statement."""

    def __init__(self, lhs: expr.Expr, assignment_op: tokens.Token,
                 value: expr.Expr):
        self.lhs = lhs
        self.assignment_op = assignment_op
        self.value = value

    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_assign(self)

    def __eq__(self, other):
        return (isinstance(other, Assign) and self.lhs == other.lhs
                and self.assignment_op == other.assignment_op
                and self.value == other.value)


class Tilde(Stmt):
    """Tilde statement to increase log probability."""

    def __init__(self, lhs: expr.Expr, identifier: tokens.Token,
                 args: List[expr.Expr]):
        self.lhs = lhs
        self.identifier = identifier
        self.args = args

    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_tilde(self)

    def __eq__(self, other):
        return (isinstance(other, Tilde) and self.lhs == other.lhs
                and self.identifier == other.identifier
                and self.args == other.args)


class IncrementLogProb(Stmt):
    """increment_log_prob statement, deprecated in Stan 3."""

    def __init__(self, keyword: tokens.Token, value: expr.Expr):
        self.keyword = keyword
        self.value = value

    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_increment_log_prob(self)

    def __eq__(self, other):
        return (isinstance(other, IncrementLogProb)
                and self.keyword == other.keyword
                and self.value == other.value)


class Break(Stmt):
    """break statement."""

    def __init__(self, keyword: tokens.Token):
        self.keyword = keyword

    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_break(self)

    def __eq__(self, other):
        return isinstance(other, Break) and self.keyword == other.keyword


class Continue(Stmt):
    """continue statement."""

    def __init__(self, keyword: tokens.Token):
        self.keyword = keyword

    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_continue(self)

    def __eq__(self, other):
        return isinstance(other, Continue) and self.keyword == other.keyword


class Return(Stmt):
    """return statement."""

    def __init__(self,
                 keyword: tokens.Token,
                 value: Optional[expr.Expr] = None):
        self.keyword = keyword
        self.value = value

    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_return(self)

    def __eq__(self, other):
        return (isinstance(other, Return) and self.keyword == other.keyword
                and self.value == other.value)


class Empty(Stmt):
    """Empty statement, i.e., just a semicolon."""

    def __init__(self, semicolon: tokens.Token):
        self.semicolon = semicolon

    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_empty(self)

    def __eq__(self, other):
        return isinstance(other, Empty) and self.semicolon == other.semicolon


class IfElse(Stmt):
    """if/else statement."""

    def __init__(self,
                 condition: expr.Expr,
                 consequent: Stmt,
                 alternative: Optional[Stmt] = None):
        self.condition = condition
        self.consequent = consequent
        self.alternative = alternative

    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_if_else(self)

    def __eq__(self, other):
        return (isinstance(other, IfElse) and self.condition == other.condition
                and self.consequent == other.consequent
                and self.alternative == other.alternative)


class While(Stmt):
    """while statement."""

    def __init__(self, condition: expr.Expr, body: Stmt):
        self.condition = condition
        self.body = body

    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_while(self)

    def __eq__(self, other):
        return (isinstance(other, While) and self.condition == other.condition
                and self.body == other.body)


class Print(Stmt):
    """print statement."""

    def __init__(self, expressions: List[expr.Expr]):
        self.expressions = expressions

    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_print(self)

    def __eq__(self, other):
        return (isinstance(other, Print)
                and self.expressions == other.expressions)


class Reject(Stmt):
    """reject statement."""

    def __init__(self, expressions: List[expr.Expr]):
        self.expressions = expressions

    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_reject(self)

    def __eq__(self, other):
        return (isinstance(other, Reject)
                and self.expressions == other.expressions)


class TargetPlusAssign(Stmt):
    """target += ...; statement."""

    def __init__(self, value: expr.Expr):
        self.value = value

    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_target_plus_assign(self)

    def __eq__(self, other):
        return (isinstance(other, TargetPlusAssign)
                and self.value == other.value)


class Block(Stmt):
    """Block statement, i.e.,

    '{'  var_declaration* statement+ '}' .
    """

    def __init__(self, declarations: List[Declaration],
                 statements: List[Stmt]):
        self.declarations = declarations
        self.statements = statements

    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_block(self)

    def __eq__(self, other):
        return (isinstance(other, Block)
                and self.declarations == other.declarations
                and self.statements == other.statements)


class Visitor:
    """Visitor for Stmt types."""

    # pylint: disable=too-few-public-methods

    @abc.abstractmethod
    def visit_program(self, statement: Program) -> Any:
        """Visit Program."""

    @abc.abstractmethod
    def visit_declaration(self, statement: Declaration) -> Any:
        """Visit Declaration."""

    @abc.abstractmethod
    def visit_argument_declaration(self,
                                   statement: ArgumentDeclaration) -> Any:
        """Visit ArgumentDeclaration."""

    @abc.abstractmethod
    def visit_assign(self, statement: Assign) -> Any:
        """Visit Assign."""

    @abc.abstractmethod
    def visit_tilde(self, statement: Tilde) -> Any:
        """Visit Tilde."""

    @abc.abstractmethod
    def visit_increment_log_prob(self, statement: IncrementLogProb) -> Any:
        """Visit IncrementLogProb."""

    @abc.abstractmethod
    def visit_break(self, statement: Break) -> Any:
        """Visit Break."""

    @abc.abstractmethod
    def visit_continue(self, statement: Continue) -> Any:
        """Visit Continue."""

    @abc.abstractmethod
    def visit_return(self, statement: Return) -> Any:
        """Visit Return."""

    @abc.abstractmethod
    def visit_empty(self, statement: Empty) -> Any:
        """Visit Empty."""

    @abc.abstractmethod
    def visit_if_else(self, statement: IfElse) -> Any:
        """Visit IfElse."""

    @abc.abstractmethod
    def visit_while(self, statement: While) -> Any:
        """Visit While."""

    @abc.abstractmethod
    def visit_print(self, statement: Print) -> Any:
        """Visit Print."""

    @abc.abstractmethod
    def visit_reject(self, statement: Reject) -> Any:
        """Visit Reject."""

    @abc.abstractmethod
    def visit_target_plus_assign(self, statement: TargetPlusAssign) -> Any:
        """Visit TargetPlusAssign."""

    @abc.abstractmethod
    def visit_block(self, statement: Block) -> Any:
        """Visit Block."""
