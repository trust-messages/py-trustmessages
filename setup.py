import sys
from setuptools import setup


VERSION = "0.1"
AUTHOR = "David Jelenc, University of Ljubljana"
EMAIL = "david.jelenc@fri.uni-lj.si"

setup(
    name='trustmessages',
    version=VERSION,
    description='Python ASN.1 trust messages',
    url='http://github.com/trust-messages/py-trust-messages',
    author=AUTHOR,
    author_email=EMAIL,
    packages=['trustmessages'],
    install_requires=[
        "pyasn1",
        "antlr4-python%d-runtime" % sys.version_info.major,
        "asn1ate",
        "future"
    ],
    test_suite='nose.collector',
    tests_require=['nose'],
    include_package_data=True,
    zip_safe=False)
