from antlr4 import *
from messages import *


class QueryVisitor(ParseTreeVisitor):
    Q2DM = {
        "!=": "ne",
        "<=": "le",
        ">=": "ge",
        "<": "lt",
        ">": "gt",
        "=": "eq"
    }

    def visitComparison(self, ctx):
        q = Query()
        q["cmp"] = Comparison()
        q["cmp"]["op"] = self.Q2DM[str(ctx.OP())]
        q["cmp"]["value"] = Value()
        q["cmp"]["value"][str(ctx.FIELD())] = str(ctx.VALUE())

        return q

    def visitOr(self, ctx):
        q = Query()
        q["log"] = Logical()
        q["log"]["op"] = "or"
        q["log"]["l"] = self.visit(ctx.expr(0))
        q["log"]["r"] = self.visit(ctx.expr(1))

        return q

    def visitAnd(self, ctx):
        q = Query()
        q["log"] = Logical()
        q["log"]["op"] = "and"
        q["log"]["l"] = self.visit(ctx.expr(0))
        q["log"]["r"] = self.visit(ctx.expr(1))

        return q

    def visitParenthesis(self, ctx):
        return self.visit(ctx.expr())
