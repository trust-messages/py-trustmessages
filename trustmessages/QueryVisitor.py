from __future__ import absolute_import

from antlr4 import ParseTreeVisitor

from .messages import Constraint, Expression, Query, Value


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
        q["con"] = Constraint()
        q["con"]["operator"] = self.Q2DM[str(ctx.OP())]
        q["con"]["value"] = Value()
        q["con"]["value"][str(ctx.FIELD())] = str(ctx.VALUE())

        return q

    def visitOr(self, ctx):
        q = Query()
        q["exp"] = Expression()
        q["exp"]["operator"] = "or"
        q["exp"]["left"] = self.visit(ctx.expr(0))
        q["exp"]["right"] = self.visit(ctx.expr(1))

        return q

    def visitAnd(self, ctx):
        q = Query()
        q["exp"] = Expression()
        q["exp"]["operator"] = "and"
        q["exp"]["left"] = self.visit(ctx.expr(0))
        q["exp"]["right"] = self.visit(ctx.expr(1))

        return q

    def visitParenthesis(self, ctx):
        return self.visit(ctx.expr())
