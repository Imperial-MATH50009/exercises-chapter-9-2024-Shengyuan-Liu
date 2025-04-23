"""."""
from numbers import Number as NumType
from functools import singledispatch


def make_expr(x):
    """."""
    if isinstance(x, Expression):
        return x
    elif isinstance(x, NumType):
        return Number(x)
    elif isinstance(x, str):
        return Symbol(x)
    else:
        raise TypeError(f"Cannot convert {x!r} to an Expression")


class Expression():
    """."""

    def __init__(self, *operands):
        """."""
        self.operands = operands

    def __add__(self, other):
        """."""
        return Add(self, make_expr(other))

    def __sub__(self, other):
        """."""
        return Sub(self, make_expr(other))

    def __mul__(self, other):
        """."""
        return Mul(self, make_expr(other))

    def __truediv__(self, other):
        """."""
        return Div(self, make_expr(other))

    def __pow__(self, other):
        """."""
        return Pow(self, make_expr(other))

    def __radd__(self, other):
        """."""
        return Add(make_expr(other), self)

    def __rsub__(self, other):
        """."""
        return Sub(make_expr(other), self)

    def __rmul__(self, other):
        """."""
        return Mul(make_expr(other), self)

    def __rtruediv__(self, other):
        """."""
        return Div(make_expr(other), self)

    def __rpow__(self, other):
        """."""
        return Pow(make_expr(other), self)


class Operator(Expression):
    """."""

    symbol = "?"
    precedence = 10

    def __str__(self):
        """."""
        def format_arg(arg):
            """."""
            s = str(arg)
            if isinstance(arg, Operator) and arg.precedence < self.precedence:
                return f"({s})"
            return s
        return f" {self.symbol} ".join(format_arg(op) for op in self.operands)

    def __repr__(self):
        """."""
        return type(self).__name__ + repr(self.operands)


class Add(Operator):
    """."""

    symbol = "+"
    precedence = 1


class Sub(Operator):
    """."""

    symbol = "-"
    precedence = 1


class Mul(Operator):
    """."""

    symbol = "*"
    precedence = 2


class Div(Operator):
    """."""

    symbol = "/"
    precedence = 2


class Pow(Operator):
    """."""

    symbol = "^"
    precedence = 3


class Terminal(Expression):
    """."""

    def __init__(self, value):
        """."""
        super().__init__()
        self.value = value

    def __repr__(self):
        """."""
        return repr(self.value)

    def __str__(self):
        """."""
        return str(self.value)


class Number(Terminal):
    """."""

    def __init__(self, value):
        """."""
        if not isinstance(value, NumType):
            raise TypeError("Number value must be numeric")
        super().__init__(value)


class Symbol(Terminal):
    """."""

    def __init__(self, value):
        """."""
        if not isinstance(value, str):
            raise TypeError("Symbol value must be a string")
        super().__init__(value)


def postvisitor(expr, fn, **kwargs):
    """."""
    stack = [expr]
    visited = {}

    while stack:
        e = stack.pop()
        unvisited_children = []
        for o in e.operands:
            if o not in visited:
                unvisited_children.append(o)

        if unvisited_children:
            stack.append(e)
            stack.extend(unvisited_children)
        else:
            visited[e] = fn(e, *(visited.get(o, o) for o in e.operands),
                            **kwargs)

    return visited[expr]


@singledispatch
def differentiate(expr, *o, var=None):
    """."""
    raise NotImplementedError(
        f"No differentiation rule for {type(expr).__name__}"
    )


@differentiate.register
def _(expr: Number, *o, var=None):
    return Number(0)


@differentiate.register
def _(expr: Symbol, *o, var=None):
    return Number(1) if expr.value == var else Number(0)


@differentiate.register
def _(expr: Add, *o, var=None):
    return Add(*o)


@differentiate.register
def _(expr: Sub, *o, var=None):
    return Sub(*o)


@differentiate.register
def _(expr: Mul, *o, var=None):
    u, v = expr.operands
    du, dv = o
    return Add(Mul(du, v), Mul(u, dv))


@differentiate.register
def _(expr: Div, *o, var=None):
    u, v = expr.operands
    du, dv = o
    return Div(Sub(Mul(du, v), Mul(u, dv)), Pow(v, Number(2)))


@differentiate.register
def _(expr: Pow, *o, var=None):
    base, exponent = expr.operands
    dbase, dexp = o
    if isinstance(exponent, Number):
        return Mul(Mul(exponent, Pow(base, Number(exponent.value - 1))), dbase)
    else:
        raise NotImplementedError(
            "Differentiation where variable is in exponent not supported."
        )
