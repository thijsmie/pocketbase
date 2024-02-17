
_ValueType = "_Field" | bool | int | float | None
def _str_value(value: _Field | str | bool | int | float | None) -> str:
    if isinstance(value, (_Field, int, float)):
        return str(value)
    elif isinstance(value, str):
        return f"'{value}'"
    elif isinstance(value, bool):
        return 'true' if value else 'false'
    elif value is None:
        return 'null'
    raise TypeError(f"Don't know how to stringify value {value}")


class _Base:
    def __str__(self) -> str:
        pass


class _Field(_Base):
    def __lt__(self, other: "_Field" | str | bool | int | float | None) -> "_Expr":
        return _Expr(self, '<', other)

    def __le__(self, other: "_Field" | str | bool | int | float | None) -> "_Expr":
        return _Expr(self, '<=', other)

    def __gt__(self, other: "_Field" | str) -> "_Expr":
        return _Expr(self, '>', other)

    def __ge__(self, other: "_Field" | str) -> "_Expr":
        return _Expr(self, '>=', other)

    def __eq__(self, other: "_Field" | str) -> "_Expr":
        return _Expr(self, '=', other)

    def __ne__(self, other: "_Field" | str) -> "_Expr":
        return _Expr(self, '!=', other)

    def __contains__(self, other: "_Field" | str) -> "_Expr":
        return _Expr(self, '~', other)


class _ListSome(_Field):
    def __init__(self, sub: _Item):
        self._sub = sub
    
    def __str__(self) -> str:
        return str(self._sub)


class _ListEach(_Field):
    def __init__(self, sub: _Item):
        self._sub = sub
    
    def __str__(self) -> str:
        return f"{self._sub}:each"


class _ListLen(_Field):
    def __init__(self, sub: _Item):
        self._sub = sub
    
    def __str__(self) -> str:
        return f"{self._sub}:length"


class _ListIsSet(_Field):
    def __init__(self, sub: _Item):
        self._sub = sub
    
    def __str__(self) -> str:
        return f"{self._sub}:isset"


class _Logical(_Base):
    def __and__(self, other: _Logical) -> "_LogicalExpr":
        return _LogicalExpr(self, '&&', other)

    def __or__(self, other: _Logical) -> "_LogicalExpr":
        return _LogicalExpr(self, '||', other)


class _LogicalExpr(_Logical):
    def __init__(self, left: _Expr | _LogicalExpr, op: str, right: _LogicalExpr | _LogicalExpr) -> None:
        self.left, self.op, self.right = left, op, right
    
    def __str__(self) -> str:
        left = str(self.left)
        right = str(self.right)
        op = self.op
    
        return f"({left}{self.op}{right})"


class _Expr(_Logical):
    def __init__(self, left: _Field | str, op: str, right: _Field | str) -> None:
        self.left, self.op, self.right = left, op, right

    def __str__(self) -> str:
        left = _str_value(self.left)
        right = _str_value(self.right)
        op = self.op
    
        if isinstance(self.left, _ListSome):
            op = f"?{op}"
    
        return f"{left}{self.op}{right}"

    def __invert__(self) -> _Expr:
        match self.op:
            case '<': return _Expr(self.left, '>=', self.right)
            case '<=': return _Expr(self.left, '>', self.right)
            case '>': return _Expr(self.left, '<=', self.right)
            case '>=': return _Expr(self.left, '<', self.right)
            case '=': return _Expr(self.left, '!=', self.right)
            case '!=': return _Expr(self.left, '=', self.right)
            case '~': return _Expr(self.left, '!~', self.right)


class Table(_Field):
    def __init__(self, name: str):
        self._name = name

    def __getattr__(self, prop: str) -> "Table":
        return Table(f"{self._name}.{prop}")

    @property
    def name(self) -> str:
        return self._name

    def __str__(self) -> str:
        return self._name

    @property
    def some(self) -> _ListSome:
        return _ListSome(self)

    @property
    def each(self) -> _ListEach:
        return _ListEach(self)

    @property
    def is_set(self) -> _ListIsSet:
        return _ListIsSet(self)

    def __len__(self) -> _ListLen:
        return _ListLen(self)


class _Request(Table):
    method = Table("@request.method")
    headers = Table("@request.headers")
    query = Table("@request.query")
    data = Table("@request.data")
    auth = Table("@request.auth")


class _Datetime:
    now = Table("@now")
    second = Table("@second")
    minute = Table("@minute")
    hour = Table("@hour")
    weekday = Table("@weekday")
    day = Table("@day")
    month = Table("@month")
    year = Table("@year")
    today_start = Table("@todayStart")
    today_end = Table("@todayEnd")
    month_start = Table("@monthStart")
    month_end = Table("@monthEnd")
    year_start = Table("@yearStart")
    year_end = Table("@yearEnd")


request = _Request('@request')
collection = Table('@collection')
