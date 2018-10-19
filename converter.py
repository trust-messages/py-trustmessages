import copy
import glob

import asn1tools

OUTPUT_FORMATS = ('ber', 'xer', 'per', 'jer', 'uper', 'gser')
msg_spec = asn1tools.parse_files("../asn1-trustmessages/messages.asn")
fmt_spec = asn1tools.parse_files("../asn1-trustmessages/formats.asn")
codecs = {
    "msg": {f: asn1tools.compile_dict(msg_spec, f) for f in OUTPUT_FORMATS},
    "fmt": {f: asn1tools.compile_dict(fmt_spec, f) for f in OUTPUT_FORMATS}
}
messages = asn1tools.compile_files("../asn1-trustmessages/messages.asn", 'ber')
formats = asn1tools.compile_files("../asn1-trustmessages/formats.asn", 'ber')


def determine_target(m):
    if m['payload'][1]['format'] == "1.1.1":
        return 'QTM'
    elif m['payload'][1]['format'] == "2.2.2":
        return 'SL'
    else:
        raise ValueError("Unknown format")


def decode(data, codecs, enc):
    m = codecs["msg"][enc].decode('Message', data)

    if 'payload' in m and 'data-response' in m['payload']:
        target = determine_target(m)

        for item in m["payload"][1]["response"]:
            item["value"] = formats.decode(target, item["value"])
    return m


def encode(message, codecs, enc):
    if 'payload' in message and 'data-response' in message['payload']:
        m = copy.deepcopy(message)
        target = determine_target(m)
        for item in m["payload"][1]["response"]:
            item["value"] = codecs["fmt"][enc].encode(target, item["value"])
    else:
        m = message

    return codecs["msg"][enc].encode('Message', m)


if __name__ == '__main__':
    files = glob.iglob("../*.ber")
    for filename in files:
        enc = filename.split(".")[-1]
        name = filename.rsplit(".", 1)[:-1][0]

        with open(filename, "rb") as handle:
            data = handle.read()

        message = decode(data, codecs, enc)

        for codec_name in OUTPUT_FORMATS:
            if enc == codec_name:
                print("Skipping", codec_name, "for", filename)
                continue

            new_file = name + "." + codec_name
            with open(new_file, "wb") as handle:
                print("Writing", new_file)
                encoded = encode(message, codecs, codec_name)
                handle.write(encoded)
