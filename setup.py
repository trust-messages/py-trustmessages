from setuptools import setup


VERSION = "0.1"
AUTHOR = "David Jelenc, University of Ljubljana"
EMAIL = "david.jelenc@fri.uni-lj.si"

setup(
    name='trustmessages',
    version=VERSION,
    description='Python ASN.1 trust messages',
    url='http://www.fri.uni-lj.si',
    author=AUTHOR,
    author_email=EMAIL,
    packages=['trustmessages'],
    install_requires=["pyasn1", "antlr4", "asn1ate"],
    test_suite='nose.collector',
    tests_require=['nose'],
    include_package_data=True,
    zip_safe=False)
