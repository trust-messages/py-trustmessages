from QueryLexer import QueryLexer
from QueryParser import QueryParser
from QueryVisitor import QueryVisitor
import antlr4
import os
import itertools


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

    if query.getName() == "log":
        left_predicate = create_predicate(component["l"])
        right_predicate = create_predicate(component["r"])

        if component["op"] == 0:  # and
            return lambda item: left_predicate(item) and right_predicate(item)
        else:
            return lambda item: left_predicate(item) or right_predicate(item)
    else:
        value = component["value"].getComponent()
        field = component["value"].getName()

        if component["op"] == 0:  # eq
            return lambda item: item[field] == value
        elif component["op"] == 1:  # ne
            return lambda item: item[field] != value
        elif component["op"] == 2:  # lt
            return lambda item: item[field] < value
        elif component["op"] == 3:  # le
            return lambda item: item[field] <= value
        elif component["op"] == 4:  # gt
            return lambda item: item[field] > value
        else:  # ge
            return lambda item: item[field] >= value


def create_sql(query):
    """Takes a query message and returns an SQL query statement"""

    component = query.getComponent()

    if query.getName() == "log":
        left_sql = create_sql(component["l"])
        right_sql = create_sql(component["r"])

        if component["op"] == 0:
            return "%s AND %s" % (left_sql, right_sql)
        else:
            return "%s OR %s" % (left_sql, right_sql)
    else:
        value = component["value"].getComponent()
        field = component["value"].getName()

        if component["op"] == 0:  # eq
            return "%s = %s" % (field, value)
        elif component["op"] == 1:  # ne
            return "%s != %s" % (field, value)
        elif component["op"] == 2:  # lt
            return "%s < %s" % (field, value)
        elif component["op"] == 3:  # le
            return "%s <= %s" % (field, value)
        elif component["op"] == 4:  # gt
            return "%s > %s" % (field, value)
        else:  # ge
            return "%s >= %s" % (field, value)


def create_mongo(query):
    """Takes a query message and returns a mongo query"""

    component = query.getComponent()

    if query.getName() == "log":
        left_mq = create_mongo(component["l"])
        right_mq = create_mongo(component["r"])

        if component["op"] == 0:
            return {"$and": [left_mq, right_mq]}
        else:
            return {"$or": [left_mq, right_mq]}
    else:
        field = component["value"].getName()
        if field == "date":
            value = int(component["value"].getComponent())
        else:
            value = str(component["value"].getComponent())

        if component["op"] == 0:  # eq
            return {field: {"$eq": value}}
        elif component["op"] == 1:  # ne
            return {field: {"$ne": value}}
        elif component["op"] == 2:  # lt
            return {field: {"$lt": value}}
        elif component["op"] == 3:  # le
            return {field: {"$lte": value}}
        elif component["op"] == 4:  # gt
            return {field: {"$gt": value}}
        else:  # ge
            return {field: {"$gte": value}}


def pp(m):
    """Removes empty lines from prettyPrint()"""
    return os.linesep.join(itertools.ifilter(None, m.prettyPrint().splitlines()))
