import os

import antlr4

from .QueryLexer import QueryLexer
from .QueryParser import QueryParser
from .QueryVisitor import QueryVisitor


def create_query(text):
    """Takes given string, converts in to a parse tree
    and converts it to a Query message"""

    lexer = QueryLexer(antlr4.InputStream(text))
    stream = antlr4.CommonTokenStream(lexer)
    parser = QueryParser(stream)
    tree = parser.expr()
    visitor = QueryVisitor()
    return visitor.visit(tree)


def create_predicate(query):
    """Takes a query message and returns a function predicate."""

    component = query.getComponent()

    if query.getName() == "con":
        value = component["value"].getComponent()
        field = component["value"].getName()

        if component["operator"] == 0:  # eq
            return lambda rating: rating[field] == value
        elif component["operator"] == 1:  # ne
            return lambda rating: rating[field] != value
        elif component["operator"] == 2:  # lt
            return lambda rating: rating[field] < value
        elif component["operator"] == 3:  # le
            return lambda rating: rating[field] <= value
        elif component["operator"] == 4:  # gt
            return lambda rating: rating[field] > value
        else:  # ge
            return lambda rating: rating[field] >= value
    else:  # exp
        left = create_predicate(component["left"])
        right = create_predicate(component["right"])

        if component["operator"] == 0:  # and
            return lambda rating: left(rating) and right(rating)
        else:
            return lambda rating: left(rating) or right(rating)


def create_sql(query):
    """Takes a query message and returns an SQL query statement"""

    component = query.getComponent()

    if query.getName() == "exp":
        left_sql = create_sql(component["left"])
        right_sql = create_sql(component["right"])

        if component["operator"] == 0:
            return "%s AND %s" % (left_sql, right_sql)
        else:
            return "%s OR %s" % (left_sql, right_sql)
    else:
        value = component["value"].getComponent()
        field = component["value"].getName()

        if component["operator"] == 0:  # eq
            return "%s = %s" % (field, value)
        elif component["operator"] == 1:  # ne
            return "%s != %s" % (field, value)
        elif component["operator"] == 2:  # lt
            return "%s < %s" % (field, value)
        elif component["operator"] == 3:  # le
            return "%s <= %s" % (field, value)
        elif component["operator"] == 4:  # gt
            return "%s > %s" % (field, value)
        else:  # ge
            return "%s >= %s" % (field, value)


def create_mongo(query):
    """Takes a query message and returns a mongo query"""

    component = query.getComponent()

    if query.getName() == "exp":
        left_mq = create_mongo(component["left"])
        right_mq = create_mongo(component["right"])

        if component["operator"] == 0:
            return {"$and": [left_mq, right_mq]}
        else:
            return {"$or": [left_mq, right_mq]}
    else:
        field = component["value"].getName()
        if field == "date":
            value = int(component["value"].getComponent())
        else:
            value = str(component["value"].getComponent())

        if component["operator"] == 0:  # eq
            return {field: {"$eq": value}}
        elif component["operator"] == 1:  # ne
            return {field: {"$ne": value}}
        elif component["operator"] == 2:  # lt
            return {field: {"$lt": value}}
        elif component["operator"] == 3:  # le
            return {field: {"$lte": value}}
        elif component["operator"] == 4:  # gt
            return {field: {"$gt": value}}
        else:  # ge
            return {field: {"$gte": value}}


def pp(message):
    """Removes empty lines from prettyPrint()"""
    return os.linesep.join(filter(None, message.prettyPrint().splitlines()))
