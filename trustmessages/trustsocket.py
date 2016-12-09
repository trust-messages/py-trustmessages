import select
import socket
import Queue
import threading
import multiprocessing


class TrustSocket(object):
    """Wrapper for sockets."""
    _BUF_SIZE = 8192

    def _default_incoming_handler(self, address, port, data):
        print("[default_handler] (%s, %d): %s" % (address, port, data))

    def __init__(self, address, port, incoming_handler=_default_incoming_handler):
        self._address = address
        self._port = port
        self._incoming_handler = incoming_handler

        # TODO: The reading of _source is blocking -- it should be non-blocking
        self._source, self._sink = multiprocessing.Pipe(False)

        self._server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server_sock.setblocking(0)
        self._server_sock.bind((self._address, self._port))

        self._in_socks = []
        self._out_socks = []
        self._out_queues = {}

    def connect(self, address, port):
        """Connect to given address and port.

        TODO: The method must be thread-safe."""
        self._sink.send([address, port, "connect", None])

    def disconnect(self, address, port):
        """Disconenct from given address and port.

        TODO: The method must be thread-safe."""
        self._sink.send([address, port, "disconnect", None])

    def send(self, address, port, payload):
        """Send payload to given address and port.

        TODO: The method must be thread-safe."""
        self._sink.send([address, port, "send", payload])

    def start(self):
        self._worker = threading.Thread(target=self._server_loop)
        self._worker.daemon = True
        self._worker.start()

    def _server_loop(self):
        self._server_sock.listen(5)

        print(" -- LISTENING (%s, %d) --" % (self._address if self._address else "*", self._port))

        self._in_socks.append(self._server_sock)
        self._in_socks.append(self._source)

        while self._in_socks:
            readable, writable, exceptional = select.select(
                self._in_socks, self._out_socks, self._in_socks)

            for s in readable:
                if s is self._server_sock:
                    self._handle_accept()
                elif s is self._source:
                    # TODO this call may block!
                    self._handle_pipe(*s.recv())
                else:
                    try:
                        data = s.recv(self._BUF_SIZE)
                    except Exception:
                        data = False

                    if data:
                        address, port = s.getpeername()
                        self._incoming_handler(self, address, port, data)
                    else:
                        self._handle_disconnect(s)

            for s in writable:
                self._flush_to_socket(s)

            for s in exceptional:
                self._handle_disconnect(s)

    def _handle_pipe(self, address, port, command, payload):
        if command == "connect":
            if self._find_socket(address, port):
                print("Already connected to (%s, %d), skipping" % (address, port))
                return

            new_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            new_sock.connect((address, port))
            new_sock.setblocking(0)

            self._in_socks.append(new_sock)
            self._out_queues[new_sock] = Queue.Queue()
        elif command == "disconnect":
            sock = self._find_socket(address, port)

            if sock:
                self._handle_disconnect(sock)
            else:
                print("No peer at (%s, %d)" % (address, port))
        elif command == "send":
            # self.send(address, port, payload)  # TODO requires change
            sock = self._find_socket(address, port)
            if sock is None:
                print("Send failed. No socket at (%s, %d)" % (address, port))
                return

            self._out_queues[sock].put(payload)

            if sock not in self._out_socks:
                self._out_socks.append(sock)
        else:
            print("Unknown command: %s %d %s %s" % (address, port, command, payload))

    def _find_socket(self, address, port):
        """Returns a reference to a socket for given address and port,
        or None if the socket does not exist."""

        for sock in self._out_queues:
            if (address, port) == sock.getpeername():
                return sock

        return None

    def _handle_accept(self):
        """Handles a new incoming connection"""
        connection, client_address = self._server_sock.accept()
        print("%s: CONNECTED" % (client_address,))
        connection.setblocking(0)

        self._in_socks.append(connection)
        self._out_queues[connection] = Queue.Queue()

    def _handle_disconnect(self, s):
        """Disconects given socket """
        try:
            print("%s: DISCONNECTED" % (s.getpeername(),))
        except Exception:
            print("DISCONNECTING AN ERRORED SOCKET")

        self._in_socks.remove(s)

        if s in self._out_socks:
            self._out_socks.remove(s)

        s.close()

        del self._out_queues[s]

    def _flush_to_socket(self, s):
        try:
            next_msg = self._out_queues[s].get_nowait()
        except Queue.Empty:
            self._out_socks.remove(s)
        else:
            print("-> %s [%dB]" % (s.getpeername(), len(next_msg)))
            s.send(next_msg)
