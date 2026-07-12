"""Motor de fórmulas: tokenizer, parser y evaluador con resolución de dependencias.

Soporta referencias de celda (A1), rangos (A1:B2), operadores aritméticos y de
comparación, y un set de funciones estilo Excel/Google Sheets (nombres en
inglés y en español).
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from .coords import a1_to_coord, coord_to_a1

CELL_RE = re.compile(r"^[A-Za-z]+\d+$")


class FormulaError(Exception):
    """Carries an Excel-style error code, e.g. #DIV/0!, #REF!, #CIRC!, #NAME?, #VALUE!."""

    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


# ---------------------------------------------------------------------------
# Tokenizer
# ---------------------------------------------------------------------------

TOKEN_SPEC = [
    ("NUMBER", r"\d+\.\d+|\d+"),
    ("STRING", r'"(?:[^"\\]|\\.)*"'),
    ("RANGE", r"[A-Za-z]+\d+:[A-Za-z]+\d+"),
    ("CELL", r"[A-Za-z]+\d+"),
    ("ID", r"[A-Za-z_][A-Za-z0-9_.]*"),
    ("OP", r"<=|>=|<>|[+\-*/^&=<>(),:]"),
    ("SKIP", r"[ \t]+"),
    ("MISMATCH", r"."),
]
TOKEN_RE = re.compile("|".join(f"(?P<{name}>{pattern})" for name, pattern in TOKEN_SPEC))


@dataclass
class Token:
    kind: str
    value: str


def tokenize(expr: str) -> list[Token]:
    tokens = []
    for match in TOKEN_RE.finditer(expr):
        kind = match.lastgroup
        value = match.group()
        if kind == "SKIP":
            continue
        if kind == "MISMATCH":
            raise FormulaError("#NAME?")
        tokens.append(Token(kind, value))
    return tokens


# ---------------------------------------------------------------------------
# AST
# ---------------------------------------------------------------------------


class Node:
    pass


@dataclass
class NumberNode(Node):
    value: float


@dataclass
class StringNode(Node):
    value: str


@dataclass
class CellNode(Node):
    ref: str


@dataclass
class RangeNode(Node):
    start: str
    end: str


@dataclass
class UnaryOpNode(Node):
    op: str
    operand: Node


@dataclass
class BinOpNode(Node):
    op: str
    left: Node
    right: Node


@dataclass
class FuncCallNode(Node):
    name: str
    args: list[Node]


# ---------------------------------------------------------------------------
# Parser (recursive descent)
# ---------------------------------------------------------------------------


class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.pos = 0

    def peek(self) -> Token | None:
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def advance(self) -> Token:
        tok = self.tokens[self.pos]
        self.pos += 1
        return tok

    def expect(self, value: str) -> Token:
        tok = self.peek()
        if tok is None or tok.value != value:
            raise FormulaError("#NAME?")
        return self.advance()

    def parse(self) -> Node:
        node = self.parse_comparison()
        if self.peek() is not None:
            raise FormulaError("#NAME?")
        return node

    def parse_comparison(self) -> Node:
        node = self.parse_concat()
        while self.peek() and self.peek().value in ("=", "<>", "<", ">", "<=", ">="):
            op = self.advance().value
            node = BinOpNode(op, node, self.parse_concat())
        return node

    def parse_concat(self) -> Node:
        node = self.parse_additive()
        while self.peek() and self.peek().value == "&":
            self.advance()
            node = BinOpNode("&", node, self.parse_additive())
        return node

    def parse_additive(self) -> Node:
        node = self.parse_multiplicative()
        while self.peek() and self.peek().value in ("+", "-"):
            op = self.advance().value
            node = BinOpNode(op, node, self.parse_multiplicative())
        return node

    def parse_multiplicative(self) -> Node:
        node = self.parse_power()
        while self.peek() and self.peek().value in ("*", "/"):
            op = self.advance().value
            node = BinOpNode(op, node, self.parse_power())
        return node

    def parse_power(self) -> Node:
        node = self.parse_unary()
        if self.peek() and self.peek().value == "^":
            self.advance()
            node = BinOpNode("^", node, self.parse_power())
        return node

    def parse_unary(self) -> Node:
        tok = self.peek()
        if tok and tok.value in ("+", "-"):
            self.advance()
            return UnaryOpNode(tok.value, self.parse_unary())
        return self.parse_primary()

    def parse_primary(self) -> Node:
        tok = self.peek()
        if tok is None:
            raise FormulaError("#NAME?")

        if tok.kind == "NUMBER":
            self.advance()
            return NumberNode(float(tok.value))

        if tok.kind == "STRING":
            self.advance()
            return StringNode(tok.value[1:-1].replace('\\"', '"'))

        if tok.kind == "RANGE":
            self.advance()
            start, end = tok.value.split(":")
            return RangeNode(start, end)

        if tok.kind == "CELL":
            self.advance()
            return CellNode(tok.value)

        if tok.value == "(":
            self.advance()
            node = self.parse_comparison()
            self.expect(")")
            return node

        if tok.kind == "ID":
            self.advance()
            name = tok.value
            self.expect("(")
            args = []
            if self.peek() and self.peek().value != ")":
                args.append(self.parse_comparison())
                while self.peek() and self.peek().value == ",":
                    self.advance()
                    args.append(self.parse_comparison())
            self.expect(")")
            return FuncCallNode(name.upper(), args)

        raise FormulaError("#NAME?")


def parse_formula(expr: str) -> Node:
    body = expr[1:] if expr.startswith("=") else expr
    tokens = tokenize(body)
    if not tokens:
        raise FormulaError("#NAME?")
    return Parser(tokens).parse()


# ---------------------------------------------------------------------------
# Functions
# ---------------------------------------------------------------------------


def _to_number(value) -> float:
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            raise FormulaError("#VALUE!")
    if value is None or value == "":
        return 0.0
    raise FormulaError("#VALUE!")


def _flatten(args) -> list:
    out = []
    for a in args:
        if isinstance(a, list):
            out.extend(_flatten(a))
        else:
            out.append(a)
    return out


def fn_sum(args):
    return sum(_to_number(v) for v in _flatten(args) if v not in ("", None))


def fn_average(args):
    nums = [_to_number(v) for v in _flatten(args) if v not in ("", None)]
    if not nums:
        raise FormulaError("#DIV/0!")
    return sum(nums) / len(nums)


def fn_count(args):
    return sum(1 for v in _flatten(args) if isinstance(v, (int, float)) and not isinstance(v, bool))


def fn_counta(args):
    return sum(1 for v in _flatten(args) if v not in ("", None))


def fn_max(args):
    nums = [_to_number(v) for v in _flatten(args) if v not in ("", None)]
    return max(nums) if nums else 0.0


def fn_min(args):
    nums = [_to_number(v) for v in _flatten(args) if v not in ("", None)]
    return min(nums) if nums else 0.0


def fn_if(args):
    if len(args) < 2:
        raise FormulaError("#VALUE!")
    cond, then_val = args[0], args[1]
    else_val = args[2] if len(args) > 2 else False
    return then_val if bool(cond) else else_val


def fn_and(args):
    return all(bool(v) for v in _flatten(args))


def fn_or(args):
    return any(bool(v) for v in _flatten(args))


def fn_vlookup(args):
    if len(args) < 3:
        raise FormulaError("#VALUE!")
    lookup, table, col_index = args[0], args[1], int(_to_number(args[2]))
    if not isinstance(table, list) or not table or not isinstance(table[0], list):
        raise FormulaError("#REF!")
    for row in table:
        if row and row[0] == lookup:
            if col_index < 1 or col_index > len(row):
                raise FormulaError("#REF!")
            return row[col_index - 1]
    raise FormulaError("#N/A")


def fn_concat(args):
    return "".join(_cell_str(v) for v in _flatten(args))


def _cell_str(v) -> str:
    if v is None:
        return ""
    if isinstance(v, float) and v == int(v):
        return str(int(v))
    return str(v)


def fn_iferror(args):
    if len(args) < 2:
        raise FormulaError("#VALUE!")
    value, fallback = args[0], args[1]
    if isinstance(value, FormulaError):
        return fallback
    return value


def fn_abs(args):
    if len(args) != 1:
        raise FormulaError("#VALUE!")
    return abs(_to_number(args[0]))


def fn_round(args):
    if len(args) not in (1, 2):
        raise FormulaError("#VALUE!")
    num = _to_number(args[0])
    digits = int(_to_number(args[1])) if len(args) == 2 else 0
    return round(num, digits)


FUNCTIONS = {
    "SUM": fn_sum,
    "SUMA": fn_sum,
    "AVERAGE": fn_average,
    "PROMEDIO": fn_average,
    "COUNT": fn_count,
    "CONTAR": fn_count,
    "COUNTA": fn_counta,
    "CONTARA": fn_counta,
    "MAX": fn_max,
    "MIN": fn_min,
    "IF": fn_if,
    "SI": fn_if,
    "AND": fn_and,
    "Y": fn_and,
    "OR": fn_or,
    "O": fn_or,
    "VLOOKUP": fn_vlookup,
    "BUSCARV": fn_vlookup,
    "CONCAT": fn_concat,
    "CONCATENAR": fn_concat,
    "IFERROR": fn_iferror,
    "SI.ERROR": fn_iferror,
    "ABS": fn_abs,
    "ROUND": fn_round,
    "REDONDEAR": fn_round,
}


# ---------------------------------------------------------------------------
# Evaluator with dependency resolution + cycle detection
# ---------------------------------------------------------------------------


class Engine:
    """Evaluates formula cells across a workbook, memoized per (sheet, coord).

    Cell resolution is lazy and recursive: evaluating a formula that refers to
    another formula cell triggers evaluation of that cell first. A `visiting`
    set detects circular references (#CIRC!).
    """

    def __init__(self, workbook):
        self.workbook = workbook
        self._memo: dict[tuple[str, int, int], object] = {}
        self._visiting: set[tuple[str, int, int]] = set()

    def recalculate(self) -> None:
        self._memo.clear()
        for sheet in self.workbook.sheets:
            for row, col, cell in list(sheet.iter_cells()):
                self._evaluate_cell(sheet, row, col, cell)

    def _evaluate_cell(self, sheet, row: int, col: int, cell) -> None:
        key = (sheet.name, row, col)
        if key in self._memo:
            return
        cell.error = None
        if not cell.is_formula:
            cell.value = self._literal(cell.raw)
            self._memo[key] = cell.value
            return
        if key in self._visiting:
            cell.error = "#CIRC!"
            cell.value = None
            self._memo[key] = None
            return
        self._visiting.add(key)
        try:
            ast = parse_formula(cell.raw)
            value = self._eval(ast, sheet)
            cell.value = value
            self._memo[key] = value
        except FormulaError as exc:
            cell.error = exc.code
            cell.value = None
            self._memo[key] = None
        finally:
            self._visiting.discard(key)

    @staticmethod
    def _literal(raw: str):
        if raw == "":
            return ""
        try:
            if "." in raw:
                return float(raw)
            return int(raw)
        except ValueError:
            return raw

    def _resolve_cell(self, sheet, ref: str):
        row, col = a1_to_coord(ref)
        cell = sheet.get_cell(row, col)
        key = (sheet.name, row, col)
        if key not in self._memo:
            self._evaluate_cell(sheet, row, col, cell)
        if cell.error:
            raise FormulaError(cell.error)
        return self._memo.get(key)

    def _resolve_range(self, sheet, start: str, end: str) -> list[list]:
        r1, c1 = a1_to_coord(start)
        r2, c2 = a1_to_coord(end)
        rows = range(min(r1, r2), max(r1, r2) + 1)
        cols = range(min(c1, c2), max(c1, c2) + 1)
        out = []
        for r in rows:
            row_vals = []
            for c in cols:
                row_vals.append(self._resolve_cell(sheet, coord_to_a1(r, c)))
            out.append(row_vals)
        return out

    def _eval(self, node: Node, sheet):
        if isinstance(node, NumberNode):
            return node.value
        if isinstance(node, StringNode):
            return node.value
        if isinstance(node, CellNode):
            return self._resolve_cell(sheet, node.ref)
        if isinstance(node, RangeNode):
            return self._resolve_range(sheet, node.start, node.end)
        if isinstance(node, UnaryOpNode):
            val = _to_number(self._eval(node.operand, sheet))
            return -val if node.op == "-" else val
        if isinstance(node, BinOpNode):
            return self._eval_binop(node, sheet)
        if isinstance(node, FuncCallNode):
            fn = FUNCTIONS.get(node.name)
            if fn is None:
                raise FormulaError("#NAME?")
            args = [self._eval(a, sheet) for a in node.args]
            return fn(args)
        raise FormulaError("#VALUE!")

    def _eval_binop(self, node: BinOpNode, sheet):
        left = self._eval(node.left, sheet)
        right = self._eval(node.right, sheet)
        op = node.op

        if op == "&":
            return _cell_str(left) + _cell_str(right)

        if op in ("=", "<>", "<", ">", "<=", ">="):
            try:
                lv = _to_number(left) if not isinstance(left, str) or op in ("=", "<>") else left
                rv = _to_number(right) if not isinstance(right, str) or op in ("=", "<>") else right
                if isinstance(lv, str) or isinstance(rv, str):
                    lv, rv = str(left), str(right)
            except FormulaError:
                lv, rv = str(left), str(right)
            return {
                "=": lv == rv,
                "<>": lv != rv,
                "<": lv < rv,
                ">": lv > rv,
                "<=": lv <= rv,
                ">=": lv >= rv,
            }[op]

        lv, rv = _to_number(left), _to_number(right)
        if op == "+":
            return lv + rv
        if op == "-":
            return lv - rv
        if op == "*":
            return lv * rv
        if op == "/":
            if rv == 0:
                raise FormulaError("#DIV/0!")
            return lv / rv
        if op == "^":
            return lv**rv
        raise FormulaError("#VALUE!")
