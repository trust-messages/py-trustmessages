"""
Example TMS.
"""
import sys
from builtins import input
from functools import partial
from random import randint

from pyasn1.codec.ber import decoder, encoder
from pyasn1.type import univ

from trustmessages import trustsocket
from trustmessages.messages import (Rating, DataRequest, DataResponse,
                                    FormatRequest, FormatResponse, Message)
from trustmessages.trustdatabase import QtmDb, SLDb
from trustmessages.trustutils import create_predicate, create_query, pp


def simple_tms(trust_socket, address, port, data, db):
    try:
        incoming_message, remaining = decoder.decode(data, asn1Spec=Message())
        assert remaining == b"", "Message did not fully decode: %s" % remaining
        assert incoming_message["version"] == 1, "Invalid protocol version: %d" % incoming_message["version"]
        payload = incoming_message["payload"].getComponent()
        type_ = incoming_message["payload"].getName()

        print("(%s, %d): %s [size=%dB]" % (address, port, type_, len(data)))

        if type_ == "data-request":
            print(pp(payload))
            predicate = create_predicate(payload["query"])
            hits = filter(predicate,
                          db.trust_db if payload["type"] == "trust" else db.assessment_db)
            dr = DataResponse()
            dr["format"] = db.tms_trust if payload["type"] == 0 else db.tms_assessment
            dr["rid"] = payload["rid"]
            dr["type"] = payload["type"]
            dr["response"] = univ.SequenceOf(componentType=Rating())
            dr["response"].setComponents(*hits)

            response = Message()
            response["version"] = 1
            response["caller"] = incoming_message["caller"]
            response["callee"] = incoming_message["callee"]
            response["payload"] = dr
            trust_socket.send(address, port, encoder.encode(response))
        elif type_ == "data-response":
            print("%d hits: %s" % (len(payload["response"]), pp(payload)))
        elif type_ == "format-request":
            print(pp(payload))
            fr = FormatResponse()
            fr["rid"] = int(payload)
            fr["assessment-id"] = db.tms_assessment
            fr["assessment-def"] = db.assessment_schema
            fr["trust-id"] = db.tms_trust
            fr["trust-def"] = db.trust_schema
            response = Message()
            response["version"] = 1
            response["caller"] = incoming_message["caller"]
            response["callee"] = incoming_message["callee"]
            response["payload"] = fr
            trust_socket.send(address, port, encoder.encode(response))
        elif type_ == "format-response":
            print(payload.prettyPrint())
    except Exception as excp:
        print("(%s, %d): Error while parsing (size=%dB) [%s]: %s" % (
            address, port, len(data), type(excp), excp))


def main(address, port, database, provider):
    handler = partial(simple_tms, db=QtmDb() if database == 'qtm' else SLDb())
    trust_socket = trustsocket.TrustSocket(address, port, handler)
    trust_socket.start()

    while True:
        try:
            user_input = input().strip()
            split = user_input.split(" ", 4)

            query = None
            callee = None
            if len(split) == 3:
                address, port, verb = split
            elif len(split) == 4:
                address, port, verb, callee = split
            elif len(split) > 4:
                print(split)
                address, port, verb, callee, query = split
            else:
                print("Invalid command: %s" % user_input)
                continue
            port = int(port)

            if verb == "connect":
                trust_socket.connect(address, port)
            elif verb == "disconnect":
                trust_socket.disconnect(address, port)
            elif verb in ("areq", "treq"):
                dr = DataRequest()
                dr["rid"] = randint(-32700, 32700)
                dr["type"] = "assessment" if verb == "areq" else "trust"
                dr["query"] = create_query(query)
                request = Message()
                request["version"] = 1
                request["payload"] = dr
                request["caller"] = provider
                request["callee"] = callee
                trust_socket.send(address, port, encoder.encode(request))
            elif verb == "freq":
                request = Message()
                request["version"] = 1
                request["caller"] = provider
                request["callee"] = callee
                request["payload"] = FormatRequest(randint(0, 1000))
                trust_socket.send(address, port, encoder.encode(request))
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
