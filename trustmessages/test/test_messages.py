from __future__ import absolute_import, print_function

import base64
import unittest
from itertools import cycle

from pyasn1.codec.ber import decoder, encoder
from pyasn1.type import char, univ

from .. import (Rating, DataRequest, DataResponse, Constraint, Fault, Format,
                FormatRequest, FormatResponse, Expression, Message, QtmDb, Query,
                Value, trustutils)


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
        r = Rating()
        r["source"] = next(self.users)
        r["target"] = next(self.users)
        r["service"] = next(self.services)
        r["date"] = 100
        val = next(self.quantitative)
        r["value"] = encoder.encode(univ.Integer(val))

        decoded, _ = decoder.decode(encoder.encode(r), asn1Spec=Rating())

        assert (r == decoded)
        assert (r.prettyPrint() == decoded.prettyPrint())
        assert (decoder.decode(decoded["value"],
                               asn1Spec=univ.Integer())[0] == val)

    def test_assessment_qualitative(self):
        r = Rating()
        r["source"] = next(self.users)
        r["target"] = next(self.users)
        r["service"] = next(self.services)
        r["date"] = 100
        val = next(self.qualitative)
        r["value"] = encoder.encode(char.IA5String(val))

        decoded, _ = decoder.decode(encoder.encode(r), asn1Spec=Rating())

        assert (r == decoded)
        assert (r.prettyPrint() == decoded.prettyPrint())
        assert (str(decoder.decode(decoded["value"], asn1Spec=char.IA5String())[0]) == val)

    def test_assessment_request(self):
        a_req = DataRequest()
        a_req["rid"] = 1
        a_req["type"] = "assessment"
        sq = Query()
        sq["con"] = Constraint()
        sq["con"]["operator"] = "ge"
        sq["con"]["value"] = Value()
        sq["con"]["value"]["date"] = 80
        a_req["query"] = sq

        original = Message()
        original["version"] = 1
        original["payload"] = a_req
        decoded, _ = decoder.decode(encoder.encode(original), asn1Spec=Message())

        assert (decoded == original)
        assert (decoded["payload"].getComponent() == a_req)
        assert (decoded["payload"].getComponent().prettyPrint() == a_req.prettyPrint())

    def test_assessment_response(self):
        a_res = DataResponse()
        a_res["provider"] = "ebay"
        a_res["type"] = "assessment"
        a_res["format"] = Format((1, 1, 1))
        a_res["rid"] = 1
        a_res["response"] = univ.SequenceOf(componentType=Rating())

        for i in range(2):
            a = Rating()
            a["source"] = next(self.users)
            a["target"] = next(self.users)
            a["service"] = next(self.services)
            a["date"] = 1000
            a["value"] = encoder.encode(univ.Integer(5))
            a_res["response"].setComponentByPosition(i, a)

        original = Message()
        original["version"] = 1
        original["payload"] = a_res
        decoded, _ = decoder.decode(encoder.encode(original), asn1Spec=Message())

        assert (decoded == original)
        assert (decoded["payload"].getComponent() == a_res)
        assert (decoded["payload"].getComponent().prettyPrint() == a_res.prettyPrint())

    def test_trust_request(self):
        t_req = DataRequest()
        t_req["rid"] = 5000
        t_req["type"] = "trust"
        sq = Query()
        sq["con"] = Constraint()
        sq["con"]["operator"] = "ge"
        sq["con"]["value"] = Value()
        sq["con"]["value"]["date"] = 80
        t_req["query"] = sq

        original = Message()
        original["version"] = 1
        original["payload"] = t_req
        decoded, _ = decoder.decode(encoder.encode(original), asn1Spec=Message())

        assert (decoded == original)
        assert (decoded["payload"].getComponent() == t_req)
        assert (decoded["payload"].getComponent().prettyPrint() == t_req.prettyPrint())

    def test_trust_response(self):
        t_res = DataResponse()
        t_res["provider"] = "ebay"
        t_res["format"] = univ.ObjectIdentifier((1, 1, 1))
        t_res["rid"] = 70000
        t_res["type"] = "trust"
        t_res["response"] = univ.SequenceOf(componentType=Rating())

        for i in range(2):
            t = Rating()
            t["source"] = next(self.users)
            t["target"] = next(self.users)
            t["service"] = next(self.services)
            t["date"] = 2000
            t["value"] = encoder.encode(
                char.IA5String(next(self.qualitative)))
            t_res["response"].setComponentByPosition(i, t)

        original = Message()
        original["version"] = 1
        original["payload"] = t_res
        decoded, _ = decoder.decode(encoder.encode(original), asn1Spec=Message())

        assert (decoded == original)
        assert (decoded["payload"].getComponent() == t_res)
        assert (decoded["payload"].getComponent().prettyPrint() == t_res.prettyPrint())

    def test_format_request(self):
        f_req = FormatRequest(10)
        original = Message()
        original["version"] = 1
        original["payload"] = f_req
        decoded, _ = decoder.decode(encoder.encode(original), asn1Spec=Message())

        assert (decoded == original)
        assert (decoded["payload"].getComponent() == f_req)
        assert (decoded["payload"].getComponent().prettyPrint() == f_req.prettyPrint())

    def test_format_response(self):
        f_res = FormatResponse()
        f_res["rid"] = 10
        f_res["assessment-id"] = Format((1, 2, 3))
        f_res["assessment-def"] = char.IA5String(
            "Here be an ASN.1 spec for assessment values")
        f_res["trust-id"] = Format((1, 2, 3))
        f_res["trust-def"] = char.IA5String(
            "Here be an ASN.1 spec for trust values")

        original = Message()
        original["version"] = 1
        original["payload"] = f_res
        decoded, _ = decoder.decode(encoder.encode(original), asn1Spec=Message())

        assert (decoded == original)
        assert (decoded["payload"].getComponent() == f_res)
        assert (decoded["payload"].getComponent().prettyPrint() == f_res.prettyPrint())

    def test_fault(self):
        e = Fault()
        e["rid"] = 10
        e["message"] = "something went wrong!"

        original = Message()
        original["version"] = 1
        original["payload"] = e
        decoded, _ = decoder.decode(encoder.encode(original), asn1Spec=Message())

        assert (decoded == original)
        assert (decoded["payload"].getComponent() == e)
        assert (decoded["payload"].getComponent().prettyPrint() == e.prettyPrint())


class TestQueries(AbstractTests):
    def test_simple_query1(self):
        sq1 = Query()
        sq1["con"] = Constraint()
        sq1["con"]["operator"] = "lt"
        sq1["con"]["value"] = Value()
        sq1["con"]["value"]["date"] = 50

        assert (all(t["date"] < 50
                    for t in filter(trustutils.create_predicate(sq1), self.qtm.assessment_db)))

    def test_simple_query2(self):
        sq2 = Query()
        sq2["exp"] = Expression()
        sq2["exp"]["operator"] = "and"
        sq2["exp"]["left"] = Query()
        sq2["exp"]["left"]["con"] = Constraint()
        sq2["exp"]["left"]["con"]["operator"] = "eq"
        sq2["exp"]["left"]["con"]["value"] = Value()
        sq2["exp"]["left"]["con"]["value"]["source"] = "alice"
        sq2["exp"]["right"] = Query()
        sq2["exp"]["right"]["con"] = Constraint()
        sq2["exp"]["right"]["con"]["operator"] = "eq"
        sq2["exp"]["right"]["con"]["value"] = Value()
        sq2["exp"]["right"]["con"]["value"]["target"] = "bob"

        assert (all(str(t["source"]) == "alice" and str(t["target"]) == "bob"
                    for t in filter(trustutils.create_predicate(sq2), self.qtm.assessment_db)))

    def test_simple_query3(self):
        q = Query()
        q["exp"] = Expression()
        q["exp"]["left"] = Query()
        q["exp"]["left"]["con"] = Constraint()
        q["exp"]["left"]["con"]["operator"] = "eq"
        q["exp"]["left"]["con"]["value"] = Value()
        q["exp"]["left"]["con"]["value"]["service"] = "seller"
        q["exp"]["operator"] = "and"
        q["exp"]["right"] = Query()
        q["exp"]["right"]["exp"] = Expression()
        q["exp"]["right"]["exp"]["operator"] = "or"
        q["exp"]["right"]["exp"]["left"] = Query()
        q["exp"]["right"]["exp"]["left"]["con"] = Constraint()
        q["exp"]["right"]["exp"]["left"]["con"]["operator"] = "eq"
        q["exp"]["right"]["exp"]["left"]["con"]["value"] = Value()
        q["exp"]["right"]["exp"]["left"]["con"]["value"]["source"] = "charlie"
        q["exp"]["right"]["exp"]["right"] = Query()
        q["exp"]["right"]["exp"]["right"]["con"] = Constraint()
        q["exp"]["right"]["exp"]["right"]["con"]["operator"] = "eq"
        q["exp"]["right"]["exp"]["right"]["con"]["value"] = Value()
        q["exp"]["right"]["exp"]["right"]["con"]["value"]["source"] = "david"

        assert (all(str(t["service"]) == "seller" and (str(t["source"]) == "charlie" or str(t["source"]) == "david")
                    for t in filter(trustutils.create_predicate(q), self.qtm.assessment_db)))
        substrate = encoder.encode(q)
        d, e = decoder.decode(substrate, asn1Spec=Query())
        assert (d == q)
        assert (q.prettyPrint() == d.prettyPrint())


class TestPrinting(AbstractTests):
    def test_assessment_quantitative(self):
        r = Rating()
        r["source"] = "djelenc@gmail.com"
        r["target"] = "david.jelenc@fri.uni-lj.si"
        r["service"] = "seller"
        r["date"] = 1
        r["value"] = encoder.encode(self.qtm.AssessmentClass("very-good"))

        decoded, _ = decoder.decode(encoder.encode(r), asn1Spec=Rating())
        assert (r.prettyPrint() == decoded.prettyPrint())
        v, _ = decoder.decode(
            decoded["value"], asn1Spec=self.qtm.AssessmentClass())

    def test_decode_java_query(self):
        """bytez = base64.b64decode(b"MIIBDAIBAWOCAQUCAQEGAikBCgEBEwdzb21ldG1zMI"
                                 b"HvZDoTA2JvYhMFYWxpY2UTBnNlbGxlcgIBdDAhCQmA"
                                 b"ywcWcApADU0JCYDHEQNZB1EEKwkJgM8BfZWmVK4nZD"
                                 b"oTA2JvYhMFYWxpY2UTBmxldHRlcgIBdTAhCQmAzAc+"
                                 b"TRsonxMJCYDJHlwQ2KW9fQkJgMsJ7GGThVJ7ZDoTA2"
                                 b"JvYhMFYWxpY2UTBnJlbnRlcgIBdjAhCQmAywUxkTfw"
                                 b"PesJCYDIFXEUGhJ52QkJgMwMECYiZrltZDkTA2JvYhM"
                                 b"FYWxpY2UTBWJ1eWVyAgF3MCEJCYDLFBLOKvpZ/wkJgM"
                                 b"obFgUaA0KJCQnAygM7oW/39oc=")

        m, _ = decoder.decode(bytez, asn1Spec=Message())"""
        pass
