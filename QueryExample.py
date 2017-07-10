from __future__ import absolute_import, print_function

from antlr4 import InputStream, CommonTokenStream

from trustmessages.QueryLexer import QueryLexer
from trustmessages.QueryParser import QueryParser
from trustmessages.QueryVisitor import QueryVisitor
from trustmessages.trustutils import pp

if __name__ == '__main__':
    input_ = InputStream(
        "service = renter AND (target = alice OR target = bob)")
    lexer = QueryLexer(input_)
    stream = CommonTokenStream(lexer)
    parser = QueryParser(stream)
    tree = parser.expr()
    visitor = QueryVisitor()
    result = visitor.visit(tree)

    if result is not None:
        print(pp(result))
