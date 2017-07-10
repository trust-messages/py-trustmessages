# Generated from Query.g4 by ANTLR 4.6
# encoding: utf-8
from __future__ import print_function

from io import StringIO

from antlr4 import *


def serializedATN():
    with StringIO() as buf:
        buf.write(u"\3\u0430\ud6d1\u8206\uad2d\u4417\uaef1\u8d80\uaadd\3")
        buf.write(u"\n\32\4\2\t\2\3\2\3\2\3\2\3\2\3\2\3\2\3\2\3\2\5\2\r\n")
        buf.write(u"\2\3\2\3\2\3\2\3\2\3\2\3\2\7\2\25\n\2\f\2\16\2\30\13")
        buf.write(u"\2\3\2\2\3\2\3\2\2\2\33\2\f\3\2\2\2\4\5\b\2\1\2\5\6\7")
        buf.write(u"\7\2\2\6\7\7\b\2\2\7\r\7\t\2\2\b\t\7\3\2\2\t\n\5\2\2")
        buf.write(u"\2\n\13\7\4\2\2\13\r\3\2\2\2\f\4\3\2\2\2\f\b\3\2\2\2")
        buf.write(u"\r\26\3\2\2\2\16\17\f\4\2\2\17\20\7\5\2\2\20\25\5\2\2")
        buf.write(u"\5\21\22\f\3\2\2\22\23\7\6\2\2\23\25\5\2\2\4\24\16\3")
        buf.write(u"\2\2\2\24\21\3\2\2\2\25\30\3\2\2\2\26\24\3\2\2\2\26\27")
        buf.write(u"\3\2\2\2\27\3\3\2\2\2\30\26\3\2\2\2\5\f\24\26")
        return buf.getvalue()


class QueryParser(Parser):
    grammarFileName = "Query.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [DFA(ds, i) for i, ds in enumerate(atn.decisionToState)]

    sharedContextCache = PredictionContextCache()

    literalNames = [u"<INVALID>", u"'('", u"')'", u"'AND'", u"'OR'"]

    symbolicNames = [u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>",
                     u"<INVALID>", u"FIELD", u"OP", u"VALUE", u"WS"]

    RULE_expr = 0

    ruleNames = [u"expr"]

    EOF = Token.EOF
    T__0 = 1
    T__1 = 2
    T__2 = 3
    T__3 = 4
    FIELD = 5
    OP = 6
    VALUE = 7
    WS = 8

    def __init__(self, input):
        super(QueryParser, self).__init__(input)
        self.checkVersion("4.6")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None

    class ExprContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(QueryParser.ExprContext, self).__init__(parent, invokingState)
            self.parser = parser

        def getRuleIndex(self):
            return QueryParser.RULE_expr

        def copyFrom(self, ctx):
            super(QueryParser.ExprContext, self).copyFrom(ctx)

    class OrContext(ExprContext):

        def __init__(self, parser, ctx):  # actually a QueryParser.ExprContext)
            super(QueryParser.OrContext, self).__init__(parser)
            self.copyFrom(ctx)

        def expr(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(QueryParser.ExprContext)
            else:
                return self.getTypedRuleContext(QueryParser.ExprContext, i)

        def accept(self, visitor):
            if hasattr(visitor, "visitOr"):
                return visitor.visitOr(self)
            else:
                return visitor.visitChildren(self)

    class AndContext(ExprContext):

        def __init__(self, parser, ctx):  # actually a QueryParser.ExprContext)
            super(QueryParser.AndContext, self).__init__(parser)
            self.copyFrom(ctx)

        def expr(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(QueryParser.ExprContext)
            else:
                return self.getTypedRuleContext(QueryParser.ExprContext, i)

        def accept(self, visitor):
            if hasattr(visitor, "visitAnd"):
                return visitor.visitAnd(self)
            else:
                return visitor.visitChildren(self)

    class ConstraintContext(ExprContext):

        def __init__(self, parser, ctx):  # actually a QueryParser.ExprContext)
            super(QueryParser.ConstraintContext, self).__init__(parser)
            self.copyFrom(ctx)

        def FIELD(self):
            return self.getToken(QueryParser.FIELD, 0)

        def OP(self):
            return self.getToken(QueryParser.OP, 0)

        def VALUE(self):
            return self.getToken(QueryParser.VALUE, 0)

        def accept(self, visitor):
            if hasattr(visitor, "visitConstraint"):
                return visitor.visitConstraint(self)
            else:
                return visitor.visitChildren(self)

    class ParenthesisContext(ExprContext):

        def __init__(self, parser, ctx):  # actually a QueryParser.ExprContext)
            super(QueryParser.ParenthesisContext, self).__init__(parser)
            self.copyFrom(ctx)

        def expr(self):
            return self.getTypedRuleContext(QueryParser.ExprContext, 0)

        def accept(self, visitor):
            if hasattr(visitor, "visitParenthesis"):
                return visitor.visitParenthesis(self)
            else:
                return visitor.visitChildren(self)

    def expr(self, _p=0):
        _parentctx = self._ctx
        _parentState = self.state
        localctx = QueryParser.ExprContext(self, self._ctx, _parentState)
        _prevctx = localctx
        _startState = 0
        self.enterRecursionRule(localctx, 0, self.RULE_expr, _p)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 10
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [QueryParser.FIELD]:
                localctx = QueryParser.ConstraintContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx

                self.state = 3
                self.match(QueryParser.FIELD)
                self.state = 4
                self.match(QueryParser.OP)
                self.state = 5
                self.match(QueryParser.VALUE)
                pass
            elif token in [QueryParser.T__0]:
                localctx = QueryParser.ParenthesisContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx
                self.state = 6
                self.match(QueryParser.T__0)
                self.state = 7
                self.expr(0)
                self.state = 8
                self.match(QueryParser.T__1)
                pass
            else:
                raise NoViableAltException(self)

            self._ctx.stop = self._input.LT(-1)
            self.state = 20
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input, 2, self._ctx)
            while _alt != 2 and _alt != ATN.INVALID_ALT_NUMBER:
                if _alt == 1:
                    if self._parseListeners is not None:
                        self.triggerExitRuleEvent()
                    _prevctx = localctx
                    self.state = 18
                    self._errHandler.sync(self)
                    la_ = self._interp.adaptivePredict(self._input, 1, self._ctx)
                    if la_ == 1:
                        localctx = QueryParser.AndContext(self, QueryParser.ExprContext(self, _parentctx, _parentState))
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expr)
                        self.state = 12
                        if not self.precpred(self._ctx, 2):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 2)")
                        self.state = 13
                        self.match(QueryParser.T__2)
                        self.state = 14
                        self.expr(3)
                        pass

                    elif la_ == 2:
                        localctx = QueryParser.OrContext(self, QueryParser.ExprContext(self, _parentctx, _parentState))
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expr)
                        self.state = 15
                        if not self.precpred(self._ctx, 1):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 1)")
                        self.state = 16
                        self.match(QueryParser.T__3)
                        self.state = 17
                        self.expr(2)
                        pass

                self.state = 22
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input, 2, self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.unrollRecursionContexts(_parentctx)
        return localctx

    def sempred(self, localctx, ruleIndex, predIndex):
        if self._predicates == None:
            self._predicates = dict()
        self._predicates[0] = self.expr_sempred
        pred = self._predicates.get(ruleIndex, None)
        if pred is None:
            raise Exception("No predicate with index:" + str(ruleIndex))
        else:
            return pred(localctx, predIndex)

    def expr_sempred(self, localctx, predIndex):
        if predIndex == 0:
            return self.precpred(self._ctx, 2)

        if predIndex == 1:
            return self.precpred(self._ctx, 1)
