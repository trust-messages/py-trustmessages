import messages
import itertools
import StringIO
import random
import os
from pyasn1.codec.ber import encoder
from pyasn1.codec.ber import decoder
from asn1ate import parser, sema, pyasn1gen


class InMemoryTrustDatabase(object):
    SYSTEMS = {}

    @staticmethod
    def pp(m):
        """Nicer prettyPrint() for values"""

        buff = StringIO.StringIO()

        for line in m.prettyPrint().splitlines():
            if line != "":
                hit = line.find("value=0x")

                if hit > -1:
                    v, _ = decoder.decode(m["value"], asn1Spec=InMemoryTrustDatabase.SYSTEMS[m["format"]]["trust"]())
                    buff.write(line[:hit + 6])
                    buff.write(v.prettyPrint())
                else:
                    buff.write(line)

                buff.write(os.linesep)

        return buff.getvalue().strip()

    def _define_value_class(self, schema):
        _parse_tree = parser.parse_asn1(schema)
        _modules = sema.build_semantic_model(_parse_tree)
        _clazz_stream = StringIO.StringIO()
        pyasn1gen.generate_pyasn1(_modules[0], _clazz_stream)
        _clazz = _clazz_stream.getvalue()
        _clazz_stream.close()
        exec(_clazz)
        return ValueFormat

    def __init__(self, tms, assessment_schema, trust_schema=None):
        self.USERS = ["alice", "bob", "charlie", "david", "eve"]
        self.SERVICES = ["buyer", "seller", "letter", "renter"]
        self.TRUST_DB = []
        self.ASSESSMENT_DB = []

        self.TMS = tms
        self.ASSESSMENT_SCHEMA = assessment_schema
        self.TRUST_SCHEMA = trust_schema if trust_schema is not None else assessment_schema

        # time generators
        self.assess_time_generator = itertools.count(0)
        self.trust_time_generator = itertools.count(0)

        # define Value classes
        self.AssessmentClass = self._define_value_class(assessment_schema)
        if trust_schema is None:
            # Are they the same?
            self.TrustClass = self.AssessmentClass
        else:
            self.TrustClass = self._define_value_class(trust_schema)

        self.SYSTEMS[tms] = {"assessment": self.AssessmentClass, "trust": self.TrustClass}

    def create_trust(self, target, service, date, value):
        t = messages.Trust()
        t["target"] = target
        t["service"] = service
        t["date"] = date
        t["value"] = encoder.encode(value)
        return t

    def create_assessment(self, source, target, service, date, value):
        a = messages.Assessment()
        a["source"] = source
        a["target"] = target
        a["service"] = service
        a["date"] = date
        a["value"] = encoder.encode(value)
        return a


class QtmDb(InMemoryTrustDatabase):

    def __init__(self):
        schema = ("ValueFormat DEFINITIONS ::= BEGIN "
                  "ValueFormat ::= ENUMERATED { "
                  "very-bad (0), bad (1), neutral (2), good (3), very-good (4)"
                  "} END")
        super(QtmDb, self).__init__((1, 1, 1), schema)

        self.values_generator = itertools.cycle(self.TrustClass().getNamedValues())

        self.TRUST_DB = [self.create_trust(
            target, service, self.trust_time_generator.next(),
            self.TrustClass(self.values_generator.next()[0]))
            for target in self.USERS
            for service in self.SERVICES]

        self.ASSESSMENT_DB = [self.create_assessment(
            source, target, service, self.assess_time_generator.next(),
            self.AssessmentClass(self.values_generator.next()[0]))
            for source in self.USERS
            for target in self.USERS
            for service in self.SERVICES if source != target]


class SLDb(InMemoryTrustDatabase):

    def values_generator(self):
        while True:
            v = self.TrustClass()
            v["b"] = random.uniform(0, 1)
            v["d"] = random.uniform(0, 1.0 - v["b"])
            v["u"] = 1.0 - v["b"] - v["d"]

            yield v

    def __init__(self):
        schema = ("ValueFormat DEFINITIONS ::= BEGIN "
                  "ValueFormat ::= SEQUENCE { b REAL, d REAL, u REAL } "
                  "END")
        super(SLDb, self).__init__((2, 2, 2), schema)

        self.AssessmentClass.prettyPrint = lambda v: "<b=%.2f, d=%.2f, u=%.2f>" % (
            (v["b"], v["d"], v["u"]) if None not in v else (0, 0, 0))
        self.TrustClass.prettyPrint = self.AssessmentClass.prettyPrint

        self.TRUST_DB = [self.create_trust(
            target, service, next(self.trust_time_generator), next(self.values_generator()))
            for target in self.USERS
            for service in self.SERVICES]

        self.ASSESSMENT_DB = [self.create_assessment(
            source, target, service, next(self.assess_time_generator),
            next(self.values_generator()))
            for source in self.USERS
            for target in self.USERS
            for service in self.SERVICES if source != target]
