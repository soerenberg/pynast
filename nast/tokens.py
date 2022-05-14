"""Stan tokens."""
from enum import auto, Enum
from typing import Any, NamedTuple


class TokenType(Enum):
    """Token type for Stan."""
    NEWLINE = auto()
    SPACE = auto()

    # Program blocks
    FUNCTIONBLOCK = auto()  # functions
    DATABLOCK = auto()  # data
    TRANSFORMEDDATABLOCK = auto()  # transformed data
    PARAMETERSBLOCK = auto()  # parameters
    TRANSFORMEDPARAMETERSBLOCK = auto()  # transformed parameters
    MODELBLOCK = auto()  # model
    GENERATEDQUANTITIESBLOCK = auto()  # generated quantities

    # Punctuation
    LBRACE = auto()  # {
    RBRACE = auto()  # }
    LPAREN = auto()  # (
    RPAREN = auto()  # )
    LBRACK = auto()  # [
    RBRACK = auto()  # ]
    LABRACK = auto()  # <
    RABRACK = auto()  # >
    COMMA = auto()  # ,
    SEMICOLON = auto()  # ;
    BAR = auto()  # |

    # Control flow keywords
    RETURN = auto()  # return
    IF = auto()  # if
    ELSE = auto()  # else
    WHILE = auto()  # while
    PROFILE = auto()  # profile
    FOR = auto()  # for
    IN = auto()  # in
    BREAK = auto()  # break
    CONTINUE = auto()  # continue

    # Types
    VOID = auto()  # void
    INT = auto()  # int
    REAL = auto()  # real
    COMPLEX = auto()  # complex
    VECTOR = auto()  # vector
    ROWVECTOR = auto()  # row_vector
    ARRAY = auto()  # array
    MATRIX = auto()  # matrix
    ORDERED = auto()  # ordered
    POSITIVEORDERED = auto()  # positive_ordered
    SIMPLEX = auto()  # simplex
    UNITVECTOR = auto()  # unit_vector
    CHOLESKYFACTORCORR = auto()  # cholesky_factor_corr
    CHOLESKYFACTORCOV = auto()  # cholesky_factor_cov
    CORRMATRIX = auto()  # corr_matrix
    COVMATRIX = auto()  # cov_matrix

    # Transformation keywords
    LOWER = auto()  # lower
    UPPER = auto()  # upper
    OFFSET = auto()  # offset
    MULTIPLIER = auto()  # multiplier

    # Operators
    QMARK = auto()  # ?
    COLON = auto()  # :
    BANG = auto()  # !
    MINUS = auto()  # -
    PLUS = auto()  # +
    HAT = auto()  # ^
    TRANSPOSE = auto()  # '
    TIMES = auto()  # *
    DIVIDE = auto()  # /
    MODULO = auto()  # %
    IDIVIDE = auto()  # %/%
    LDIVIDE = auto()  # \
    ELTTIMES = auto()  # .*
    ELTPOW = auto()  # .^
    ELTDIVIDE = auto()  # ./
    OR = auto()  # ||
    AND = auto()  # &&
    EQUALS = auto()  # ==
    NEQUALS = auto()  # !=
    LEQ = auto()  # <=
    GEQ = auto()  # >=
    TILDE = auto()  # ~

    # Assignments
    ASSIGN = auto()  # =
    PLUSASSIGN = auto()  # +=
    MINUSASSIGN = auto()  # -=
    TIMESASSIGN = auto()  # *=
    DIVIDEASSIGN = auto()  # /=
    ELTTIMESASSIGN = auto()  # .*=
    ELTDIVIDEASSIGN = auto()  # ./=
    ARROWASSIGN = auto()  # <-
    INCREMENTLOGPROB = auto()  # increment_log_prob

    # Effects
    PRINT = auto()  # print
    REJECT = auto()  # reject
    TRUNCATE = auto()  # T (note: this needs context)

    STRING = auto()
    INTNUMERAL = auto()
    REALNUMERAL = auto()
    IMAGNUMERAL = auto()

    IDENTIFIER = auto()

    EOF = auto()


class Token(NamedTuple):
    """Token.

    Attributes:
        ttype: type of token
        line: line the token was scanned on
        column: horizontal position the token was scanned on
        lexeme: string as the token was scanned
        literal: literal value, only used for literals.
    """
    ttype: TokenType
    line: int
    column: int
    lexeme: str = ""
    literal: Any = None


class RealValue(NamedTuple):
    """Datatype for parsed real literals."""
    integer_part: int
    non_integer_part: int = 0
    exponent: int = 0


class ComplexValue(NamedTuple):
    """Datatype for parsed imaginary literals."""
    imag: RealValue
