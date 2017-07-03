"""
Example TMS.
"""
from __future__ import absolute_import, print_function

import sys
from functools import partial
from random import randint

from builtins import input
from pyasn1.codec.ber import decoder, encoder
from pyasn1.type import univ

from trustmessages import trustsocket
from trustmessages.messages import (Rating, DataRequest, DataResponse,
                                    FormatRequest, FormatResponse, Message)
from trustmessages.trustdatabase import QtmDb, SLDb
from trustmessages.trustutils import create_predicate, create_query, pp


def simple_tms(trust_socket, address, port, data, db, provider):
    try:
        message, remaining = decoder.decode(data, asn1Spec=Message())
        assert remaining == b"", "Message did not fully decode: %s" % remaining
        component = message.getComponent()
        type_ = message.getName()

        print("(%s, %d): %s [size=%dB]" % (address, port, type_, len(data)))

        if type_ == "data-request":
            print(pp(component))
            predicate = create_predicate(component["query"])
            hits = filter(predicate,
                          db.trust_db if component["type"] == "trust" else db.assessment_db)
            reply = DataResponse()
            reply["provider"] = provider
            reply["format"] = db.tms_trust if component["type"] == 0 else db.tms_assessment
            reply["rid"] = component["rid"]
            reply["type"] = component["type"]
            reply["response"] = univ.SequenceOf(componentType=Rating())
            reply["response"].setComponents(*hits)
            trust_socket.send(address, port, encoder.encode(reply))
        elif type_ == "data-response":
            print("%d hits: %s" % (len(component["response"]), pp(component)))
        elif type_ == "format-request":
            print(pp(component))
            reply = FormatResponse()
            reply["rid"] = int(component)
            reply["assessment-id"] = db.tms_assessment
            reply["assessment-def"] = db.assessment_schema
            reply["trust-id"] = db.tms_trust
            reply["trust-def"] = db.trust_schema
            trust_socket.send(address, port, encoder.encode(reply))
        elif type_ == "format-response":
            print(component.prettyPrint())
    except Exception as excp:
        print("(%s, %d): Error while parsing (size=%dB) [%s]: %s" % (
            address, port, len(data), type(excp), excp))


def main(address, port, database, provider):
    handler = partial(simple_tms, db=QtmDb() if database == 'qtm' else SLDb(),
                      provider=provider)
    trust_socket = trustsocket.TrustSocket(address, port, handler)
    trust_socket.start()

    while True:
        try:
            user_input = input().strip()
            split = user_input.split(" ", 3)

            if len(split) == 3:
                address, port, verb = split
                query = None
            elif len(split) > 3:
                address, port, verb, query = split
            else:
                print("Invalid command: %s" % user_input)
                continue
            port = int(port)

            if verb == "connect":
                trust_socket.connect(address, port)
            elif verb == "disconnect":
                trust_socket.disconnect(address, port)
            elif verb in ("areq", "treq"):
                req = DataRequest()
                req["rid"] = randint(-32700, 32700)
                req["type"] = "assessment" if verb == "areq" else "trust"
                req["query"] = create_query(query)
                trust_socket.send(address, port, encoder.encode(req))
            elif verb == "freq":
                trust_socket.send(
                    address, port, encoder.encode(FormatRequest(randint(0, 1000))))
            else:
                print("Unknown verb: %s" % verb)
        except KeyboardInterrupt:
            print("Forcing shutdown.")
            break
        except Exception as excp:
            print("Error (%s): %s" % (type(excp), excp))

    print("Shutting down.")


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Provide a port number, a database type and a name for this TMS")
        sys.exit(1)

    if sys.argv[2] not in ("qtm", "sl"):
        print("Choose either a 'qtm' or a 'sl' database")
        sys.exit(1)

    main("", int(sys.argv[1]), sys.argv[2], sys.argv[3])
