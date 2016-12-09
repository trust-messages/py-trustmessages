# Generated from Query.g4 by ANTLR 4.5.3
# encoding: utf-8
from __future__ import print_function
from antlr4 import *
from io import StringIO


def serializedATN():
    with StringIO() as buf:
        buf.write(u"\3\u0430\ud6d1\u8206\uad2d\u4417\uaef1\u8d80\uaadd\2")
        buf.write(u"\nL\b\1\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\4\7\t")
        buf.write(u"\7\4\b\t\b\4\t\t\t\3\2\3\2\3\3\3\3\3\4\3\4\3\4\3\4\3")
        buf.write(u"\5\3\5\3\5\3\6\3\6\3\6\3\6\3\6\3\6\3\6\3\6\3\6\3\6\3")
        buf.write(u"\6\3\6\3\6\3\6\3\6\3\6\3\6\3\6\3\6\3\6\3\6\3\6\3\6\5")
        buf.write(u"\6\66\n\6\3\7\3\7\3\7\3\7\3\7\3\7\3\7\5\7?\n\7\3\b\6")
        buf.write(u"\bB\n\b\r\b\16\bC\3\t\6\tG\n\t\r\t\16\tH\3\t\3\t\2\2")
        buf.write(u"\n\3\3\5\4\7\5\t\6\13\7\r\b\17\t\21\n\3\2\4\7\2\60\60")
        buf.write(u"\62;B\\^^c|\5\2\13\f\17\17\"\"S\2\3\3\2\2\2\2\5\3\2\2")
        buf.write(u"\2\2\7\3\2\2\2\2\t\3\2\2\2\2\13\3\2\2\2\2\r\3\2\2\2\2")
        buf.write(u"\17\3\2\2\2\2\21\3\2\2\2\3\23\3\2\2\2\5\25\3\2\2\2\7")
        buf.write(u"\27\3\2\2\2\t\33\3\2\2\2\13\65\3\2\2\2\r>\3\2\2\2\17")
        buf.write(u"A\3\2\2\2\21F\3\2\2\2\23\24\7*\2\2\24\4\3\2\2\2\25\26")
        buf.write(u"\7+\2\2\26\6\3\2\2\2\27\30\7C\2\2\30\31\7P\2\2\31\32")
        buf.write(u"\7F\2\2\32\b\3\2\2\2\33\34\7Q\2\2\34\35\7T\2\2\35\n\3")
        buf.write(u"\2\2\2\36\37\7u\2\2\37 \7q\2\2 !\7w\2\2!\"\7t\2\2\"#")
        buf.write(u"\7e\2\2#\66\7g\2\2$%\7v\2\2%&\7c\2\2&\'\7t\2\2\'(\7i")
        buf.write(u"\2\2()\7g\2\2)\66\7v\2\2*+\7u\2\2+,\7g\2\2,-\7t\2\2-")
        buf.write(u".\7x\2\2./\7k\2\2/\60\7e\2\2\60\66\7g\2\2\61\62\7f\2")
        buf.write(u"\2\62\63\7c\2\2\63\64\7v\2\2\64\66\7g\2\2\65\36\3\2\2")
        buf.write(u"\2\65$\3\2\2\2\65*\3\2\2\2\65\61\3\2\2\2\66\f\3\2\2\2")
        buf.write(u"\678\7#\2\28?\7?\2\29:\7>\2\2:?\7?\2\2;<\7@\2\2<?\7?")
        buf.write(u"\2\2=?\4>@\2>\67\3\2\2\2>9\3\2\2\2>;\3\2\2\2>=\3\2\2")
        buf.write(u"\2?\16\3\2\2\2@B\t\2\2\2A@\3\2\2\2BC\3\2\2\2CA\3\2\2")
        buf.write(u"\2CD\3\2\2\2D\20\3\2\2\2EG\t\3\2\2FE\3\2\2\2GH\3\2\2")
        buf.write(u"\2HF\3\2\2\2HI\3\2\2\2IJ\3\2\2\2JK\b\t\2\2K\22\3\2\2")
        buf.write(u"\2\7\2\65>CH\3\b\2\2")
        return buf.getvalue()


class QueryLexer(Lexer):

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]


    T__0 = 1
    T__1 = 2
    T__2 = 3
    T__3 = 4
    FIELD = 5
    OP = 6
    VALUE = 7
    WS = 8

    modeNames = [ u"DEFAULT_MODE" ]

    literalNames = [ u"<INVALID>",
            u"'('", u"')'", u"'AND'", u"'OR'" ]

    symbolicNames = [ u"<INVALID>",
            u"FIELD", u"OP", u"VALUE", u"WS" ]

    ruleNames = [ u"T__0", u"T__1", u"T__2", u"T__3", u"FIELD", u"OP", u"VALUE", 
                  u"WS" ]

    grammarFileName = u"Query.g4"

    def __init__(self, input=None):
        super(QueryLexer, self).__init__(input)
        self.checkVersion("4.5.3")
        self._interp = LexerATNSimulator(self, self.atn, self.decisionsToDFA, PredictionContextCache())
        self._actions = None
        self._predicates = None


