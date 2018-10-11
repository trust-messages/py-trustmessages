import sys
import time

from pyasn1.codec.ber import encoder, decoder

from trustmessages import Message


def measure_decode(files):
    print("Filename, Average, Total, Bytes")

    for f in files:
        message_decode(f)


def message_decode(filename, iterations=1000):
    with open(filename, "rb") as h:
        data = h.read()

    total = 0
    for _ in range(iterations):
        start = time.time()
        decoded, remaining = decoder.decode(data, asn1Spec=Message())
        end = time.time()
        assert len(remaining) == 0
        total += end - start

    print("%s, %Lf, %Lf, %ld" % (filename, total / iterations, total, len(data)))


def measure_encode(files):
    print("Filename, Average, Total, Bytes")

    for f in files:
        message_encode(f)


def message_encode(filename, iterations=1000):
    with open(filename, "rb") as h:
        read_bytes = h.read()

    message, remaining = decoder.decode(read_bytes, asn1Spec=Message())
    assert len(remaining) == 0

    total = 0
    for _ in range(iterations):
        start = time.time()
        encoded = encoder.encode(message)
        end = time.time()
        assert encoded == read_bytes
        total += end - start

    print("%s, %Lf, %Lf, %ld" % (filename, total / iterations, total, len(read_bytes)))


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: %s encode|decode <file.ber> ...")
        sys.exit(1)

    if sys.argv[1] == 'encode':
        measure_encode(sys.argv[2:])
    elif sys.argv[1] == 'decode':
        measure_decode(sys.argv[2:])
    else:
        print("Usage: %s encode|decode <file.ber> ...")
        sys.exit(1)
