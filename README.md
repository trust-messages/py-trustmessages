# Python Trust Messages

An example Python application that uses `trust messages` ASN.1 schema. 

## Overview

The application is a simple command-line tool with netstat-like behavior: once you run the program, you are given an input prompt where you can connect to other such programs and query them for trust and reputation information. If another system connects to your program and sends a request, you are shown the incoming query on the standard output. The requests are replied automatically.

## Running

To build this program you require Python 2 or 3 (recommended), and [pip](https://en.wikipedia.org/wiki/Pip_(package_manager)) to install required libraries. To download and install all libraries for Python 2, run:
```
pip install -r requirements-2.txt
```

And for Python 3, run:
```
pip install -r requirements-3.txt
```

Once the libraries are installed, you can run the program with:
```
python node.py <port> <qtm|sl> <trs-name> 
```
The arguments have to following semantics:

* `port` represents the network port on which this program listens for incoming requests,
* `qtm` or `sl` represent two examples of trust and reputation systems (a qualitative trust model or subjective logic),
* `trs-name` the identity of the system you want to connect.

An example run:

```
$ python node.py 6000 qtm system2
 -- LISTENING (*, 6000) --
```

## Usage

Once the program is run, you can issue commands.

Every command has the form of `IP PORT COMMAND` where you specify the `IP` address and the `PORT` number of the system to which you want to send the `COMMAND`.

### Connecting to other systems

To connect to another instance of such program that runs on `localhost` on port `5000`, issue the following.

```
127.0.0.1 50000 connect
```

To connect to multiple systems, issue multiple connect statements.

### Requesting `Rating` definitions

To obtain the definitions of the `Rating`’s `value` component, issue the `freq` command.

```
127.0.0.1 5000 freq
-> ('127.0.0.1', 5000) [9B]
(127.0.0.1, 5000): format-response [size=203B]
FormatResponse:
 rid=310
 assessment-id=2.2.2
 assessment-def=ValueFormat DEFINITIONS ::= BEGIN ValueFormat ::= SEQUENCE { b REAL, d REAL, u REAL } END
 trust-id=2.2.2
 trust-def=ValueFormat DEFINITIONS ::= BEGIN ValueFormat ::= SEQUENCE { b REAL, d REAL, u REAL } END
```

### Requesting trust and assessments

To obtain assessments or trust values from a remote system, issue the `areq` or `treq` command (assessment-request or trust-request) and then specify the `query`.

When specifying the query, keep keep in mind that both example trust and reputation systems contain: 

* four different entities (`alice`, `bob`, `charlie`, `david`, `eve`), 
* four different services (`seller`, `buyer`, `renter`, `letter`),
* all `date` values are between `0` and `79`.

Also, remember to capitalize logical operators `AND` and `OR`.

```
127.0.0.1 5000 areq source = alice AND target = bob AND date > 1
-> ('127.0.0.1', 5000) [54B]
(127.0.0.1, 5000): data-response [size=271B]
4 hits: DataResponse:
 rid=3170
 format=2.2.2
 type='assessment'
 provider=system1
 response=SequenceOf:
  Rating:
   source=alice
   target=bob
   service=seller
   date=100
   value=0x3021090980cd07595143012371090980cb0e48d0f6d50ca90909c0cb0bae1602d99a6d
  Rating:
   source=alice
   target=bob
   service=letter
   date=101
   value=0x3021090980cd07c873f7d9b08d090980cb0b4a317a9802b70909c0cb0a6c0159fec4eb
  Rating:
   source=alice
   target=bob
   service=renter
   date=102
   value=0x3020090980cb180cb4fac1302f090980cb0e63a4c234b0890908c0cece0b379ebc17
  Rating:
   source=alice
   target=bob
   service=buyer
   date=103
   value=0x3020090880cbfa7cf548956f090980c60f5102cbce2ef1090980cb1e8afaf458f919
```

### Responding to incoming requests

Incoming requests are responded automatically. Here is an example output that is shown when a request is received and immediately responded. (No user input is required; the system only prints out debugging information.)

An example output for `FormatRequest`.

```
(127.0.0.1, 5000): format-request [size=8B]
100
-> ('127.0.0.1', 5000) [280B]
```

An example output for `TrustRequest`.

```
(127.0.0.1, 5000): data-request [size=56B]
DataRequest:
 rid=2058559624
 type='trust'
 query=Query:
  exp=Expression:
   operator='and'
   left=Query:
    exp=Expression:
     operator='and'
     left=Query:
      con=Constraint:
       operator='eq'
       value=Value:
        source=alice
     right=Query:
      con=Constraint:
       operator='eq'
       value=Value:
        target=bob
   right=Query:
    con=Constraint:
     operator='gt'
     value=Value:
      date=1
-> ('127.0.0.1', 5000) [87B]
```

## Data generation

1. To generate data requests and response, run `python file_encoder.py`. This should generate `.ber` encodings for `DataRequest`s and `DataResponse`s.
2. To generate `DataRequest`s and `DataResponse`s for other formats, use `python converter.py`.
