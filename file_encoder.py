import itertools
import random
import string

from pyasn1.codec.ber import encoder, decoder
from pyasn1.type import univ, char

from trustmessages import DataRequest, Message, FormatRequest, DataResponse, Format, Rating, QtmDb, FormatResponse
from trustmessages.trustutils import create_query, pp

# users = itertools.cycle(["aaaaaa@xxxxxx.com", "bbbbbb@xxxxxx.com", "cccccc@xxxxxx.com"])
users = itertools.cycle(["a"*15, "b"*15, "c"*15])
services = itertools.cycle(["buyera", "seller", "letter", "renter"])


def decode(filename, asn_type):
    with open(filename, "rb") as h:
        data = h.read()

    decoded, _ = decoder.decode(data, asn1Spec=asn_type())

    print(pp(decoded))


def encode(filename, pdu, debug=True):
    with open(filename, "wb") as h:
        h.write(encoder.encode(pdu))

    if debug:
        print(pp(pdu))
    print("Saved to: '%s'" % filename)


def enc_data_request(destination="../message-data-request.ber"):
    dr = DataRequest()
    dr["rid"] = 42
    dr["type"] = "assessment"
    dr["query"] = create_query("service = renter AND (target = alice OR target = bob)")
    request = Message()
    request["version"] = 1
    request["payload"] = dr
    encode(destination, request)


def enc_format_request(destination="../message-format-request.ber"):
    request = Message()
    request["version"] = 1
    request["payload"] = FormatRequest(73)
    encode(destination, request)


def enc_data_response(destination="../message-data-response.ber"):
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

    encode(destination, response)


def enc_format_response(destination="../message-format-response.ber"):
    f_res = FormatResponse()
    f_res["rid"] = 100
    f_res["assessment-id"] = Format((1, 2, 3))
    f_res["trust-id"] = Format((1, 2, 3))
    f_res["assessment-def"] = char.PrintableString("Here be an ASN.1 spec for assessment values")
    f_res["trust-def"] = char.PrintableString("Here be an ASN.1 spec for trust values")

    m = Message()
    m["version"] = 1
    m["payload"] = f_res
    encode(destination, m)


def enc_format_response_length(destination="../message-format-response-long.ber", length=100):
    f_res = FormatResponse()
    f_res["rid"] = 1
    f_res["assessment-id"] = Format((1, 2, 3))
    f_res["trust-id"] = Format((1, 2, 3))
    f_res["assessment-def"] = char.PrintableString(generate_text(length))
    f_res["trust-def"] = char.PrintableString(generate_text(length))

    m = Message()
    m["version"] = 1
    m["payload"] = f_res
    encode(destination, m, False)


def generate_text(length=100):
    return ''.join(random.choice(string.ascii_letters + " ") for x in range(length))


def generate_constraints(length=10):
    fields = itertools.cycle(("source", "target", "service", "date"))
    comparisons = itertools.cycle(("=", "<=", "<", ">", ">="))

    generated = []
    for _ in range(length):
        field = next(fields)

        if field in ("source", "target"):
            value = next(users)
            comparison = "="
        elif field == "service":
            value = next(services)
            comparison = "="
        else:  # date
            value = 1538666307
            comparison = next(comparisons)

        generated.append("%s %s %s" % (field, comparison, value))

    return generated


def generate_query(length=10):
    operators = ("AND", "OR")
    query, *rest = generate_constraints(length)

    for con in rest:
        operator = random.choice(operators)
        query += " %s %s" % (operator, con)

    return query


def enc_data_request_length(destination="../message-data-request.ber", length=10):
    dr = DataRequest()
    dr["rid"] = 1
    dr["type"] = "assessment"
    dr["query"] = create_query(generate_query(length))
    request = Message()
    request["version"] = 1
    request["payload"] = dr
    encode(destination, request, False)


def enc_data_response_length(destination, length):
    a_res = DataResponse()
    a_res["provider"] = "ebay"
    a_res["format"] = Format((1, 1, 1))
    a_res["type"] = "assessment"
    a_res["rid"] = 1
    a_res["response"] = univ.SequenceOf(componentType=Rating())

    qtm = QtmDb().AssessmentClass("very-good")

    for i in range(length):
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

    encode(destination, response, False)


if __name__ == '__main__':
    # enc_format_request()
    # enc_format_response()
    # enc_data_request()
    # enc_data_response()
    # decode("../c-dr.ber", Message)
    # enc_format_response_length("../long-message-format-response.ber", 2**20)
    # enc_data_request_length("../long-message-data-request.ber", 100)
    for i in range(10):
        num = (i + 1) * 100
        enc_data_response_length("../message-data-response-%d.ber" % num, num)
        # enc_data_request_length("../message-data-request-%d.ber" % num, num)
    # decode("../long-message-data-request.ber", Message)
