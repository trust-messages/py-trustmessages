from __future__ import absolute_import, print_function

from antlr4 import InputStream, CommonTokenStream

from .QueryLexer import QueryLexer
from .QueryParser import QueryParser
from .QueryVisitor import QueryVisitor
from .trustutils import pp

if __name__ == '__main__':
    # input_ = InputStream("service = renter")
    # input_ = InputStream("service = renter AND target = david@fri.si")
    input_ = InputStream(
        "service = renter AND (target = david@fri.si OR target = aleks@fri.si)")
    lexer = QueryLexer(input_)
    stream = CommonTokenStream(lexer)
    parser = QueryParser(stream)
    tree = parser.expr()
    visitor = QueryVisitor()
    result = visitor.visit(tree)

    if result is not None:
        print(pp(result))
