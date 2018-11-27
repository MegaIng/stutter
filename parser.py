import lark
from lark import Transformer
from lark.indenter import Indenter
from lark.tree import pydot__tree_to_png

from stutter_ast import CallInto, Variable, Let, LetFrom, String, Call, Block, ForEach, Number, Type, Cast

indenter = Indenter()
indenter.NL_type = "_NEWLINE"
indenter.OPEN_PAREN_types = ()
indenter.CLOSE_PAREN_types = ()
indenter.tab_len = 1
indenter.INDENT_type = "_INDENT"
indenter.DEDENT_type = "_DEDENT"


class StutterTransformer(Transformer):
    def word(self, children):
        return Variable(children[0].value)

    def string(self, children):
        return String(children[0].value)

    def call(self, children):
        func, obj, *args = children
        assert len(args) % 2 == 0, children
        return Call(func.value, obj, {n.value: v for n, v in zip(args[::2], args[1::2])})

    def call_into(self, children):
        func, obj, *args, target = children
        assert len(args) % 2 == 0, children
        return CallInto(func.value, obj, {n.value: v for n, v in zip(args[::2], args[1::2])}, target.value)

    def let(self, children):
        if len(children) == 2:
            return Let(children[0].value, children[1])
        else:
            return Let(children[0].value, None)

    def names(self, children):
        return tuple(n.value for n in children)

    def block(self, children):
        return Block(children)

    def let_from(self, children):
        target, typ, arg = children
        return LetFrom(target.value, typ, arg)

    def for_each(self, children):
        v, n, b = children
        return ForEach(v, n, b)

    def number(self, children):
        n, = children
        return Number(n.value)

    def type(self, children):
        t, = children
        return Type(t.value)

    def cast(self, children):
        v, t = children
        return Cast(v, t)

    def combined_type(self, children):
        if len(children) == 2:
            a = children[0].value
            b = children[1].value
            if b == "Buffer":
                return Type(f"{b}[{a}]")
        raise NotImplementedError


parser = lark.Lark(open("stutter.grammar").read(), postlex=indenter, lexer="standard")
tree = parser.parse(open("test.stutter").read())
pydot__tree_to_png(tree, "test.png")
tree = StutterTransformer().transform(tree)
pydot__tree_to_png(tree, "test_transformed.png")
print("\n".join(map(str, tree.children)))
