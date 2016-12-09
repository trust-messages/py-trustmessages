import sys
import trustsocket
import itertools
import random
from trustutils import *
from messages import *
from pyasn1.codec.ber import encoder
from pyasn1.codec.ber import decoder
from pyasn1.type import univ
from trustdatabase import QtmDb, SLDb
from functools import partial


def simple_tms(ts, address, port, data, db):
    try:
        message, remaining = decoder.decode(data, asn1Spec=Message())
        assert remaining == "", "Message did not fully decode."
        component = message.getComponent()
        type_ = message.getName()

        print("(%s, %d): %s [size=%dB]" % (address, port, type_, len(data)))

        if type_ == "assessment-request":
            print(pp(component))
            predicate = create_predicate(component["query"])
            hits = itertools.ifilter(predicate, db.ASSESSMENT_DB)
            reply = AssessmentResponse()
            reply["rid"] = component["rid"]
            reply["response"] = univ.SequenceOf(componentType=Assessment())
            reply["response"].setComponents(*hits)
            ts.send(address, port, encoder.encode(reply))
        elif type_ == "assessment-response":
            print("%d hits: %s" % (len(component["response"]), pp(component)))
        elif type_ == "trust-request":
            print(pp(component))
            predicate = create_predicate(component["query"])
            hits = itertools.ifilter(predicate, db.TRUST_DB)
            reply = TrustResponse()
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
            reply["tms"] = db.TMS
            ts.send(address, port, encoder.encode(reply))
        elif type_ == "format-response":
            print(component.prettyPrint())
    except Exception as e:
        print("(%s, %d): Error while parsing (size=%dB): %s" % (
              address, port, len(data), e))


def main(address, port, database):
    handler = partial(simple_tms, db=QtmDb() if database == 'qtm' else SLDb())
    ts = trustsocket.TrustSocket(address, port, handler)
    ts.start()

    while True:
        try:
            user_input = raw_input().strip()
            split = user_input.split(" ", 3)

            if len(split) == 3:
                address, port, verb = split
                q = None
            elif len(split) > 3:
                address, port, verb, q = split
            else:
                print "Invalid command: %s" % user_input
                continue
            port = int(port)

            if verb == "connect":
                ts.connect(address, port)
            elif verb == "disconnect":
                ts.disconnect(address, port)
            elif verb == "areq":
                req = AssessmentRequest()
                req["rid"] = random.randint(-32700, 32700)
                req["query"] = create_query(q)
                ts.send(address, port, encoder.encode(req))
            elif verb == "treq":
                req = TrustRequest()
                req["rid"] = random.randint(-32700, 32700)
                req["query"] = create_query(q)
                ts.send(address, port, encoder.encode(req))
            elif verb == "freq":
                ts.send(address, port, encoder.encode(FormatRequest()))
            else:
                print "Unknown verb: %s" % verb
        except KeyboardInterrupt:
            print("Forcing shutdown.")
            break
        except Exception as e:
            print("Parse error %s" % e)

    print("Shutting down.")


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Provide a port number and a database type")
        sys.exit(1)

    if sys.argv[2] not in ("qtm", "sl"):
        print("Choose either a 'qtm' or a 'sl' database")
        sys.exit(1)

    main("", int(sys.argv[1]), sys.argv[2])
