"""
Example TMS.
"""
from __future__ import absolute_import, print_function

import sys
from builtins import input
from functools import partial
from random import randint

from pyasn1.codec.ber import decoder, encoder
from pyasn1.type import univ

from trustmessages import trustsocket
from trustmessages.messages import (Assessment, AssessmentRequest,
                                    AssessmentResponse, FormatRequest,
                                    FormatResponse, Message, Trust,
                                    TrustRequest, TrustResponse)
from trustmessages.trustdatabase import QtmDb, SLDb
from trustmessages.trustutils import create_predicate, create_query, pp


def simple_tms(ts, address, port, data, db, provider):
    try:
        message, remaining = decoder.decode(data, asn1Spec=Message())
        assert remaining == b"", "Message did not fully decode: %s" % remaining
        component = message.getComponent()
        type_ = message.getName()

        print("(%s, %d): %s [size=%dB]" % (address, port, type_, len(data)))

        if type_ == "assessment-request":
            print(pp(component))
            predicate = create_predicate(component["query"])
            hits = filter(predicate, db.ASSESSMENT_DB)
            reply = AssessmentResponse()
            reply["provider"] = provider
            reply["format"] = db.TMS
            reply["rid"] = component["rid"]
            reply["response"] = univ.SequenceOf(componentType=Assessment())
            reply["response"].setComponents(*hits)
            ts.send(address, port, encoder.encode(reply))
        elif type_ == "assessment-response":
            print("%d hits: %s" % (len(component["response"]), pp(component)))
        elif type_ == "trust-request":
            print(pp(component))
            predicate = create_predicate(component["query"])
            hits = filter(predicate, db.TRUST_DB)
            reply = TrustResponse()
            reply["provider"] = provider
            reply["format"] = db.TMS
            reply["rid"] = component["rid"]
            reply["response"] = univ.SequenceOf(componentType=Trust())
            reply["response"].setComponents(*hits)
            ts.send(address, port, encoder.encode(reply))
        elif type_ == "trust-response":
            print("%d hits: %s" % (len(component["response"]), pp(component)))
        elif type_ == "format-request":
            print(pp(component))
            reply = FormatResponse()
            reply["assessment"] = db.TRUST_SCHEMA
            reply["trust"] = db.ASSESSMENT_SCHEMA
            reply["format"] = db.TMS
            ts.send(address, port, encoder.encode(reply))
        elif type_ == "format-response":
            print(component.prettyPrint())
    except Exception as e:
        print("(%s, %d): Error while parsing (size=%dB) [%s]: %s" % (
            address, port, len(data), type(e), e))


def main(address, port, database, provider):
    handler = partial(simple_tms, db=QtmDb() if database ==
                      'qtm' else SLDb(), provider=provider)
    ts = trustsocket.TrustSocket(address, port, handler)
    ts.start()

    while True:
        try:
            user_input = input().strip()
            split = user_input.split(" ", 3)

            if len(split) == 3:
                address, port, verb = split
                q = None
            elif len(split) > 3:
                address, port, verb, q = split
            else:
                print("Invalid command: %s" % user_input)
                continue
            port = int(port)

            if verb == "connect":
                ts.connect(address, port)
            elif verb == "disconnect":
                ts.disconnect(address, port)
            elif verb == "areq":
                req = AssessmentRequest()
                req["rid"] = randint(-32700, 32700)
                req["query"] = create_query(q)
                ts.send(address, port, encoder.encode(req))
            elif verb == "treq":
                req = TrustRequest()
                req["rid"] = randint(-32700, 32700)
                req["query"] = create_query(q)
                ts.send(address, port, encoder.encode(req))
            elif verb == "freq":
                ts.send(address, port, encoder.encode(FormatRequest()))
            else:
                print("Unknown verb: %s" % verb)
        except KeyboardInterrupt:
            print("Forcing shutdown.")
            break
        except Exception as e:
            print("Error (%s) %s" % (type(e), e))

    print("Shutting down.")


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Provide a port number, a database type and a name for this TMS")
        sys.exit(1)

    if sys.argv[2] not in ("qtm", "sl"):
        print("Choose either a 'qtm' or a 'sl' database")
        sys.exit(1)

    main("", int(sys.argv[1]), sys.argv[2], sys.argv[3])
