from __future__ import absolute_import, print_function

import base64
from itertools import cycle
import unittest

from pyasn1.codec.ber import decoder, encoder
from pyasn1.type import char, univ

from .. import (Data, DataRequest, DataResponse, Comparison, Entity,
                Fault, Format, FormatRequest, FormatResponse, Logical,
                Message, QtmDb, Query, Value, trustutils)


class AbstractTests(unittest.TestCase):
    users = cycle(["a@x.com", "b@x.com", "c@x.com"])
    services = cycle(["buyer", "seller", "letter", "renter"])
    quantitative = cycle(range(1, 6))
    qualitative = cycle(["distrust", "neutral", "trust"])
    qtm = QtmDb()

    def encode(self, m):
        return base64.b64encode(encoder.encode(m))

    def decode(self, m):
        return base64.b64decode(m)

    def to_bytes(self, s):
        return ":".join("{:02x}".format(ord(c)) for c in s)


class TestMessages(AbstractTests):

    def test_assessment_quantitative(self):
        r = Data()
        r["source"] = next(self.users)
        r["target"] = next(self.users)
        r["service"] = next(self.services)
        r["date"] = 100
        val = next(self.quantitative)
        r["value"] = encoder.encode(univ.Integer(val))
        decoded, _ = decoder.decode(encoder.encode(r), asn1Spec=Data())

        assert(r.prettyPrint() == decoded.prettyPrint())
        assert(decoder.decode(decoded["value"],
                              asn1Spec=univ.Integer())[0] == val)

    def test_assessment_qualitative(self):
        r = Data()
        r["source"] = next(self.users)
        r["target"] = next(self.users)
        r["service"] = next(self.services)
        r["date"] = 100
        val = next(self.qualitative)
        r["value"] = encoder.encode(char.PrintableString(val))

        decoded, _ = decoder.decode(encoder.encode(r), asn1Spec=Data())
        assert(r.prettyPrint() == decoded.prettyPrint())
        assert(str(decoder.decode(decoded["value"], asn1Spec=char.PrintableString())[0]) == val)

    def test_assessment_request(self):
        a_req = DataRequest()
        a_req["rid"] = 1
        a_req["type"] = "assessment"
        sq = Query()
        sq["cmp"] = Comparison()
        sq["cmp"]["op"] = "ge"
        sq["cmp"]["value"] = Value()
        sq["cmp"]["value"]["date"] = 80
        a_req["query"] = sq
        decoded, _ = decoder.decode(encoder.encode(a_req), asn1Spec=Message())
        assert(a_req.prettyPrint() == decoded.getComponent().prettyPrint())

    def test_assessment_response(self):
        a_res = DataResponse()
        a_res["provider"] = "ebay"
        a_res["type"] = "assessment"
        a_res["format"] = Format((1, 1, 1))
        a_res["rid"] = 1
        a_res["response"] = univ.SequenceOf(componentType=Data())

        for i in range(2):
            a = Data()
            a["source"] = next(self.users)
            a["target"] = next(self.users)
            a["service"] = next(self.services)
            a["date"] = 1000
            a["value"] = encoder.encode(univ.Integer(5))
            a_res["response"].setComponentByPosition(i, a)

        data, _ = decoder.decode(encoder.encode(a_res), asn1Spec=Message())
        assert(data.getComponent() == a_res)
        assert(data.getComponent().prettyPrint() == a_res.prettyPrint())

    def test_trust_request(self):
        t_req = DataRequest()
        t_req["rid"] = 5000
        t_req["type"] = "trust"
        sq = Query()
        sq["cmp"] = Comparison()
        sq["cmp"]["op"] = "ge"
        sq["cmp"]["value"] = Value()
        sq["cmp"]["value"]["date"] = 80
        t_req["query"] = sq
        data, _ = decoder.decode(encoder.encode(t_req), asn1Spec=Message())
        assert(data.getComponent() == t_req)
        assert(data.getComponent().prettyPrint() == t_req.prettyPrint())

    def test_trust_response(self):
        t_res = DataResponse()
        t_res["provider"] = "ebay"
        t_res["format"] = univ.ObjectIdentifier((1, 1, 1))
        t_res["rid"] = 70000
        t_res["type"] = "trust"
        t_res["response"] = univ.SequenceOf(componentType=Data())

        for i in range(2):
            t = Data()
            t["source"] = next(self.users)
            t["target"] = next(self.users)
            t["service"] = next(self.services)
            t["date"] = 2000
            t["value"] = encoder.encode(
                char.PrintableString(next(self.qualitative)))
            t_res["response"].setComponentByPosition(i, t)

        data, _ = decoder.decode(encoder.encode(t_res), asn1Spec=Message())

        assert(data.getComponent() == t_res)
        assert(data.getComponent().prettyPrint() == t_res.prettyPrint())

    def test_format_request(self):
        f_req = FormatRequest()
        data, _ = decoder.decode(encoder.encode(f_req), asn1Spec=Message())
        assert(data.getComponent() == f_req)
        assert(data.getComponent().prettyPrint() == f_req.prettyPrint())

    def test_format_response(self):
        f_res = FormatResponse()
        f_res["format"] = Format((1, 2, 3))
        f_res["assessment"] = char.PrintableString(
            "Here be an ASN.1 spec for assessment values")
        f_res["trust"] = char.PrintableString(
            "Here be an ASN.1 spec for trust values")

        data, _ = decoder.decode(encoder.encode(f_res), asn1Spec=Message())
        assert(data.getComponent() == f_res)
        assert(data.getComponent().prettyPrint() == f_res.prettyPrint())

    def test_fault(self):
        e = Fault()
        e["value"] = "invalid-parameters"
        e["message"] = "something went wrong!"

        data, _ = decoder.decode(encoder.encode(e), asn1Spec=Message())

        assert(data.getComponent() == e)
        assert(data.getComponent().prettyPrint() == e.prettyPrint())


class TestQueries(AbstractTests):

    def test_simple_query1(self):
        sq1 = Query()
        sq1["cmp"] = Comparison()
        sq1["cmp"]["op"] = "lt"
        sq1["cmp"]["value"] = Value()
        sq1["cmp"]["value"]["date"] = 50

        assert(all(t["date"] < 50
                   for t in filter(trustutils.create_predicate(sq1), self.qtm.assessment_db)))

    def test_simple_query2(self):
        sq2 = Query()
        sq2["log"] = Logical()
        sq2["log"]["op"] = "and"
        sq2["log"]["l"] = Query()
        sq2["log"]["l"]["cmp"] = Comparison()
        sq2["log"]["l"]["cmp"]["op"] = "eq"
        sq2["log"]["l"]["cmp"]["value"] = Value()
        sq2["log"]["l"]["cmp"]["value"]["source"] = "alice"
        sq2["log"]["r"] = Query()
        sq2["log"]["r"]["cmp"] = Comparison()
        sq2["log"]["r"]["cmp"]["op"] = "eq"
        sq2["log"]["r"]["cmp"]["value"] = Value()
        sq2["log"]["r"]["cmp"]["value"]["target"] = "bob"

        assert(all(str(t["source"]) == "alice" and str(t["target"]) == "bob"
                   for t in filter(trustutils.create_predicate(sq2), self.qtm.assessment_db)))

    def test_simple_query3(self):
        q = Query()
        q["log"] = Logical()
        q["log"]["l"] = Query()
        q["log"]["l"]["cmp"] = Comparison()
        q["log"]["l"]["cmp"]["op"] = "eq"
        q["log"]["l"]["cmp"]["value"] = Value()
        q["log"]["l"]["cmp"]["value"]["service"] = "seller"
        q["log"]["op"] = "and"
        q["log"]["r"] = Query()
        q["log"]["r"]["log"] = Logical()
        q["log"]["r"]["log"]["op"] = "or"
        q["log"]["r"]["log"]["l"] = Query()
        q["log"]["r"]["log"]["l"]["cmp"] = Comparison()
        q["log"]["r"]["log"]["l"]["cmp"]["op"] = "eq"
        q["log"]["r"]["log"]["l"]["cmp"]["value"] = Value()
        q["log"]["r"]["log"]["l"]["cmp"]["value"]["source"] = "charlie"
        q["log"]["r"]["log"]["r"] = Query()
        q["log"]["r"]["log"]["r"]["cmp"] = Comparison()
        q["log"]["r"]["log"]["r"]["cmp"]["op"] = "eq"
        q["log"]["r"]["log"]["r"]["cmp"]["value"] = Value()
        q["log"]["r"]["log"]["r"]["cmp"]["value"]["source"] = "david"

        assert(all(str(t["service"]) == "seller" and (str(t["source"]) == "charlie" or str(t["source"]) == "david")
                   for t in filter(trustutils.create_predicate(q), self.qtm.assessment_db)))
        substrate = encoder.encode(q)
        d, e = decoder.decode(substrate, asn1Spec=Query())
        assert(d == q)
        assert(q.prettyPrint() == d.prettyPrint())


class TestPrinting(AbstractTests):

    def test_assessment_quantitative(self):
        r = Data()
        r["source"] = "djelenc@gmail.com"
        r["target"] = "david.jelenc@fri.uni-lj.si"
        r["service"] = "seller"
        r["date"] = 1
        r["value"] = encoder.encode(self.qtm.AssessmentClass("very-good"))

        decoded, _ = decoder.decode(encoder.encode(r), asn1Spec=Data())
        assert(r.prettyPrint() == decoded.prettyPrint())
        v, _ = decoder.decode(
            decoded["value"], asn1Spec=self.qtm.AssessmentClass())

    def test_decode_java_query(self):
        bytez = base64.b64decode(b"Y4IBBRMHc29tZXRtcwYCKQEKAQECAQEwge9kOhMDY" \
                                 b"m9iEwVhbGljZRMGc2VsbGVyAgF0MCEJCYDLBeIczX" \
                                 b"+yvwkJgMcctowL4EVJCQmAzQYUnpxwkjtkOhMDYm9" \
                                 b"iEwVhbGljZRMGbGV0dGVyAgF1MCEJCYDLH1N4dOm8" \
                                 b"twkJgMsSbilzxAGFCQnAzQRwaHorb49kOhMDYm9iE" \
                                 b"wVhbGljZRMGcmVudGVyAgF2MCEJCYDLFNENqpjKOw" \
                                 b"kJgMoauqtkEgqPCQnAygRcxrlDnwVkORMDYm9iEwV" \
                                 b"hbGljZRMFYnV5ZXICAXcwIQkJgM0HzNy1KNkzCQmA" \
                                 b"zgLy3GwqO1cJCcDNBbKVjX1P4Q==")
        m, _ = decoder.decode(bytez, asn1Spec=Message())
