"""Examples of two trust management systems: QTM and SL"""
from __future__ import absolute_import, print_function

import itertools
import os
import random
import sys

from asn1ate import parser, pyasn1gen, sema
from pyasn1.codec.ber import decoder, encoder

from . import messages

if sys.version_info.major == 3:
    from io import StringIO as BytesIO
else:
    from io import BytesIO


class InMemoryTrustDatabase(object):
    """An abstract trust database that keeps values in memory."""
    SYSTEMS = {}
    USERS = ["alice", "bob", "charlie", "david", "eve"]
    SERVICES = ["buyer", "seller", "letter", "renter"]

    @staticmethod
    def pp(m):
        """Nicer prettyPrint() for values"""

        buff = BytesIO()

        for line in m.prettyPrint().splitlines():
            if line != "":
                hit = line.find("value=0x")

                if hit > -1:
                    spec = InMemoryTrustDatabase.SYSTEMS[
                        m["format"]]["trust"]()
                    value, _ = decoder.decode(m["value"], asn1Spec=spec)
                    buff.write(line[:hit + 6])
                    buff.write(value.prettyPrint())
                else:
                    buff.write(line)

                buff.write(os.linesep)

        return buff.getvalue().strip()

    def _define_value_class(self, schema):
        _parse_tree = parser.parse_asn1(schema)
        _modules = sema.build_semantic_model(_parse_tree)
        _clazz_stream = BytesIO()
        pyasn1gen.generate_pyasn1(_modules[0], _clazz_stream)
        _clazz = _clazz_stream.getvalue()
        _clazz_stream.close()
        exec(_clazz, locals())
        return locals()["ValueFormat"]

    def __init__(self, tms_trust, tms_assessment, assessment_schema, trust_schema):
        self.trust_db = []
        self.assessment_db = []

        self.tms_trust = tms_trust
        self.tms_assessment = tms_assessment

        self.assessment_schema = assessment_schema
        self.trust_schema = trust_schema

        # time generators
        self.assess_time_generator = itertools.count(0)
        self.trust_time_generator = itertools.count(0)

        # define Value classes
        self.AssessmentClass = self._define_value_class(assessment_schema)
        self.TrustClass = self._define_value_class(trust_schema)

        self.SYSTEMS[tms_trust] = {
            "assessment": self.AssessmentClass, "trust": self.TrustClass}


def create_data(source, target, service, date, value):
    """Creates a data instance"""
    data = messages.Rating()
    data["source"] = source
    data["target"] = target
    data["service"] = service
    data["date"] = date
    data["value"] = encoder.encode(value)
    return data


class QtmDb(InMemoryTrustDatabase):
    """Example trust database: Qualitative Trust Model"""

    def __init__(self):
        schema = ("ValueFormat DEFINITIONS ::= BEGIN "
                  "ValueFormat ::= ENUMERATED { "
                  "very-bad (0), bad (1), neutral (2), good (3), very-good (4)"
                  "} END")
        super(QtmDb, self).__init__((1, 1, 1), (1, 1, 1), schema, schema)

        self.values_generator = itertools.cycle(self.TrustClass().getNamedValues())

        self.trust_db = [create_data(
            source, target, service, next(self.trust_time_generator),
            self.AssessmentClass(next(self.values_generator)[0]))
            for source in self.USERS
            for target in self.USERS
            for service in self.SERVICES if source != target]

        self.assessment_db = [create_data(
            source, target, service, next(self.assess_time_generator),
            self.AssessmentClass(next(self.values_generator)[0]))
            for source in self.USERS
            for target in self.USERS
            for service in self.SERVICES if source != target]


class SLDb(InMemoryTrustDatabase):
    """An example TMS: Subjective Logic."""

    def values_generator(self):
        """Generates belief, disbelief and uncertainty (b, d, u) triplets"""
        while True:
            value = self.TrustClass()
            value["b"] = random.uniform(0, 1)
            value["d"] = random.uniform(0, 1.0 - value["b"])
            value["u"] = 1.0 - value["b"] - value["d"]
            yield value

    def __init__(self):
        schema = ("ValueFormat DEFINITIONS ::= BEGIN "
                  "ValueFormat ::= SEQUENCE { b REAL, d REAL, u REAL } "
                  "END")
        super(SLDb, self).__init__((2, 2, 2), (2, 2, 2), schema, schema)

        self.AssessmentClass.prettyPrint = lambda v: "<b=%.2f, d=%.2f, u=%.2f>" % (
            (v["b"], v["d"], v["u"]) if None not in v else (0, 0, 0))
        self.TrustClass.prettyPrint = self.AssessmentClass.prettyPrint

        self.trust_db = [create_data(
            source, target, service, next(self.trust_time_generator),
            next(self.values_generator()))
            for source in self.USERS
            for target in self.USERS
            for service in self.SERVICES if source != target]

        self.assessment_db = [create_data(
            source, target, service, next(self.assess_time_generator),
            next(self.values_generator()))
            for source in self.USERS
            for target in self.USERS
            for service in self.SERVICES if source != target]
