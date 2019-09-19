import ast
import inspect


class Backwards:
    def visit(self, node):
        if isinstance(node, list):
            for n in node:
                self.visit(n)
            return
        if node is None:
            return
        if isinstance(node, (str, bool, int, float)):
            return
        try:
            method = getattr(self, "visit_" + node.__class__.__name__)
        except AttributeError:
            self.generic_visit(node)
        else:
            method(node)

    def generic_visit(self, node):
        for f in node._fields:
            self.visit(getattr(node, f))

    def visit_FunctionDef(self, node):
        self.generic_visit(node)
        node.body.reverse()

    def visit_If(self, node):
        self.generic_visit(node)
        node.body.reverse()
        node.orelse.reverse()
        node.body, node.orelse = node.orelse, node.body
        node.test = ast.UnaryOp(ast.Not(), node.test)

    def visit_While(self, node):
        self.generic_visit(node)
        node.body.reverse()
        node.orelse.reverse()

    def visit_For(self, node):
        self.generic_visit(node)
        node.body.reverse()
        node.orelse.reverse()
        node.iter = ast.Call(ast.Name("reversed", ctx=ast.Load()), [ast.Call(ast.Name("list", ctx=ast.Load()), [node.iter], [])], [])


def backwards(f):
    code = ast.parse(inspect.getsource(f))
    del code.body[0].decorator_list[0]
    Backwards().visit(code)
    locs = {}
    ast.fix_missing_locations(code)
    exec(compile(code, filename="<ast>", mode="exec"), globals(), locs)
    v, = locs.values()
    return v


@backwards
def f():
    print("BOOM")
    for i in range(10):
        print("%s..." % i)
    print("Goodbye")

    print("And x is", x)
    x = y + y

    if y % 2 == 0:
        print("y is odd")
    else:
        print("y is even")

    print("The value of y is", y)
    y = 1

    print("Hello")


f()
