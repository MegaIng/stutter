from dataclasses import dataclass
from textwrap import indent
from typing import Dict, List, TYPE_CHECKING, Optional, Tuple


class AST:
    def __str__(self):
        raise NotImplementedError


class Value(AST):
    def __str__(self):
        raise NotImplementedError


@dataclass
class Number(Value):
    content: str

    def __str__(self):
        return self.content


@dataclass
class Variable(Value):
    name: str

    def __str__(self):
        return self.name


@dataclass
class String(Value):
    raw: str

    def __str__(self):
        return self.raw


@dataclass
class Collection(Value):
    content: List[Value]

    def __str__(self):
        return f"({', '.join(str(v) for v in self.content)})"


@dataclass
class Call(AST):
    func: str
    obj: Value
    arguments: Dict[str, Value]

    def __str__(self):
        arguments = ", ".join(f'{n}={v}' for n, v in self.arguments.items())
        return f"{self.obj}.{self.func}({arguments})"


@dataclass
class CallInto(Call):
    target: str
    if TYPE_CHECKING:
        def __init__(self, func: str, obj: Value, arguments: Dict[str, Value], target: str): ...

    def __str__(self):
        return f"{self.target} = {super().__str__()}"


@dataclass
class Let(AST):
    target: str
    type: Optional[str]

    def __str__(self):
        return f"{self.target}: {self.type or 'Any'}"


@dataclass
class LetSet(Let):
    value: Value
    if TYPE_CHECKING:
        def __init__(self, target: str, type: str, value: Value): ...

    def __str__(self):
        return super().__str__() + f" = {self.value}"


@dataclass
class LetFrom(Let):
    argument: Value
    if TYPE_CHECKING:
        def __init__(self, target: str, type: str, value: Value): ...

    def __str__(self):
        return super().__str__() + f" = {self.type}({self.argument})"


@dataclass
class Block(AST):
    content: List[AST]

    def __str__(self):
        return indent("\n".join(map(str, self.content)), '    ')


@dataclass
class ForEach(AST):
    obj: Value
    names: Tuple[str, ...]
    block: Block

    def __str__(self):
        return f"for {', '.join(self.names)} in {self.obj}.__each__({len(self.names)}):\n{self.block}"


@dataclass
class Type(AST):
    data: str

    def __str__(self):
        return self.data


@dataclass
class Cast(Value):
    value: Value
    type: Type

    def __str__(self):
        return f"{self.type}({self.value})"
