# Auto-generated by asn1ate on 2020-06-23 12:54:56.755261
from pyasn1.type import univ, char, namedtype, namedval, tag


class Format(univ.ObjectIdentifier):
    pass


class FormatResponse(univ.Sequence):
    pass


FormatResponse.tagSet = univ.Sequence.tagSet.tagImplicitly(
    tag.Tag(tag.tagClassApplication, tag.tagFormatConstructed, 1))
FormatResponse.componentType = namedtype.NamedTypes(
    namedtype.NamedType('rid', univ.Integer()),
    namedtype.NamedType('assessment-id', Format()),
    namedtype.NamedType('assessment-def', char.IA5String()),
    namedtype.NamedType('trust-id', Format()),
    namedtype.NamedType('trust-def', char.IA5String())
)


class Fault(univ.Sequence):
    pass


Fault.tagSet = univ.Sequence.tagSet.tagImplicitly(tag.Tag(tag.tagClassApplication, tag.tagFormatConstructed, 7))
Fault.componentType = namedtype.NamedTypes(
    namedtype.NamedType('rid', univ.Integer()),
    namedtype.NamedType('message', char.IA5String())
)


class Service(char.IA5String):
    pass


class Entity(char.IA5String):
    pass


class BinaryTime(univ.Integer):
    pass


class Value(univ.Choice):
    pass


Value.componentType = namedtype.NamedTypes(
    namedtype.NamedType('source',
                        Entity().subtype(implicitTag=tag.Tag(tag.tagClassApplication, tag.tagFormatSimple, 0))),
    namedtype.NamedType('target',
                        Entity().subtype(implicitTag=tag.Tag(tag.tagClassApplication, tag.tagFormatSimple, 1))),
    namedtype.NamedType('date',
                        BinaryTime().subtype(implicitTag=tag.Tag(tag.tagClassApplication, tag.tagFormatSimple, 2))),
    namedtype.NamedType('service',
                        Service().subtype(implicitTag=tag.Tag(tag.tagClassApplication, tag.tagFormatSimple, 3)))
)


class Constraint(univ.Sequence):
    pass


Constraint.tagSet = univ.Sequence.tagSet.tagImplicitly(tag.Tag(tag.tagClassApplication, tag.tagFormatConstructed, 5))
Constraint.componentType = namedtype.NamedTypes(
    namedtype.NamedType('operator', univ.Enumerated(
        namedValues=namedval.NamedValues(('eq', 0), ('ne', 1), ('lt', 2), ('le', 3), ('gt', 4), ('ge', 5)))),
    namedtype.NamedType('value', Value())
)


class Expression(univ.Sequence):
    pass


class Query(univ.Choice):
    pass


for _ in range(100):
    Expression.tagSet = univ.Sequence.tagSet.tagImplicitly(
        tag.Tag(tag.tagClassApplication, tag.tagFormatConstructed, 6))
    Expression.componentType = namedtype.NamedTypes(
        namedtype.NamedType('operator', univ.Enumerated(namedValues=namedval.NamedValues(('and', 0), ('or', 1)))),
        namedtype.NamedType('left', Query()),
        namedtype.NamedType('right', Query())
    )
    Query.componentType = namedtype.NamedTypes(
        namedtype.NamedType('con', Constraint()),
        namedtype.NamedType('exp', Expression())
    )


class DataRequest(univ.Sequence):
    pass


DataRequest.tagSet = univ.Sequence.tagSet.tagImplicitly(tag.Tag(tag.tagClassApplication, tag.tagFormatConstructed, 2))
DataRequest.componentType = namedtype.NamedTypes(
    namedtype.NamedType('rid', univ.Integer()),
    namedtype.NamedType('type', univ.Enumerated(namedValues=namedval.NamedValues(('trust', 0), ('assessment', 1)))),
    namedtype.NamedType('query', Query())
)


class FormatRequest(univ.Integer):
    pass


FormatRequest.tagSet = univ.Integer.tagSet.tagImplicitly(tag.Tag(tag.tagClassApplication, tag.tagFormatSimple, 0))


class Rating(univ.Sequence):
    pass


Rating.tagSet = univ.Sequence.tagSet.tagImplicitly(tag.Tag(tag.tagClassApplication, tag.tagFormatConstructed, 4))
Rating.componentType = namedtype.NamedTypes(
    namedtype.NamedType('source', Entity()),
    namedtype.NamedType('target', Entity()),
    namedtype.NamedType('service', Service()),
    namedtype.NamedType('date', BinaryTime()),
    namedtype.NamedType('value', univ.OctetString())
)


class DataResponse(univ.Sequence):
    pass


DataResponse.tagSet = univ.Sequence.tagSet.tagImplicitly(tag.Tag(tag.tagClassApplication, tag.tagFormatConstructed, 3))
DataResponse.componentType = namedtype.NamedTypes(
    namedtype.NamedType('rid', univ.Integer()),
    namedtype.NamedType('format', Format()),
    namedtype.NamedType('type', univ.Enumerated(namedValues=namedval.NamedValues(('trust', 0), ('assessment', 1)))),
    namedtype.NamedType('response', univ.SequenceOf(componentType=Rating()))
)


class Message(univ.Sequence):
    pass


Message.componentType = namedtype.NamedTypes(
    namedtype.NamedType('version', univ.Integer()),
    namedtype.NamedType('caller', Entity()),
    namedtype.NamedType('callee', Entity()),
    namedtype.NamedType('payload', univ.Choice(componentType=namedtype.NamedTypes(
        namedtype.NamedType('data-request', DataRequest()),
        namedtype.NamedType('data-response', DataResponse()),
        namedtype.NamedType('format-request', FormatRequest()),
        namedtype.NamedType('format-response', FormatResponse()),
        namedtype.NamedType('fault', Fault())
    ))
                        )
)
