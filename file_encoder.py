import itertools

from pyasn1.codec.ber import encoder, decoder
from pyasn1.type import univ, char

from trustmessages import DataRequest, Message, FormatRequest, DataResponse, Format, Rating, QtmDb, FormatResponse
from trustmessages.trustutils import create_query, pp

users = itertools.cycle(["a@x.com", "b@x.com", "c@x.com"])
services = itertools.cycle(["buyer", "seller", "letter", "renter"])


def decode(filename, asn_type):
    with open(filename, "rb") as h:
        data = h.read()

    decoded, _ = decoder.decode(data, asn1Spec=asn_type())

    print(pp(decoded))


def encode(filename, pdu):
    with open(filename, "wb") as h:
        h.write(encoder.encode(pdu))

    print(pp(pdu))
    print("Saved to: '%s'" % filename)


def enc_data_request():
    dr = DataRequest()
    dr["rid"] = 42
    dr["type"] = "assessment"
    dr["query"] = create_query("service = renter AND (target = alice OR target = bob)")
    request = Message()
    request["version"] = 1
    request["payload"] = dr
    encode("../message-data-request.ber", request)


def enc_format_request():
    request = Message()
    request["version"] = 1
    request["payload"] = FormatRequest(73)
    encode("../message-format-request.ber", request)


def enc_data_response():
    a_res = DataResponse()
    a_res["provider"] = "ebay"
    a_res["format"] = Format((1, 1, 1))
    a_res["type"] = "assessment"
    a_res["rid"] = 1
    a_res["response"] = univ.SequenceOf(componentType=Rating())

    for i in range(2):
        qtm = QtmDb().AssessmentClass("very-good")

        a = Rating()
        a["source"] = next(users)
        a["target"] = next(users)
        a["service"] = next(services)
        a["date"] = 1000
        a["value"] = encoder.encode(qtm)
        a_res["response"].setComponentByPosition(i, a)

    response = Message()
    response["version"] = 1
    response["payload"] = a_res

    encode("../message-data-response.ber", response)


def enc_format_response():
    f_res = FormatResponse()
    f_res["rid"] = 100
    f_res["assessment-id"] = Format((1, 2, 3))
    f_res["trust-id"] = Format((1, 2, 3))
    f_res["assessment-def"] = char.PrintableString("Here be an ASN.1 spec for assessment values")
    f_res["trust-def"] = char.PrintableString("Here be an ASN.1 spec for trust values")

    m = Message()
    m["version"] = 1
    m["payload"] = f_res
    encode("../message-format-response.ber", m)


if __name__ == '__main__':
    enc_format_request()
    enc_format_response()
    enc_data_request()
    enc_data_response()

    # decode("../message-format-response.ber", Message)
