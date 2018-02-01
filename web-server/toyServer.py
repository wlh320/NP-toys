"""
simple web server
too simple, too naive
"""
import socket
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# config - not finished
ROOT = './test'


class ToyHttpRequest:
    METHOD = ['GET']

    def __init__(self, raw):
        self.raw = raw.decode('utf-8')
        self.status = None
        self.method = None
        self.path = None
        self.header = {}
        self.valid = True
        self.parse_raw()

    def parse_raw(self):
        """parse http request"""
        try:
            self.raw = self.raw.split('\r\n')
            self.status = self.raw[0]
            if self.status:
                self.method, self.path, _ = self.status.split()
            if self.method not in self.METHOD:  # unsupported method
                self.valid = False
            for line in self.raw[1:]:  # parse headers
                if not line:
                    continue
                line = line.split(':', 1)
                key = line[0]
                value = line[1]
                self.header[key] = value
        except Exception as e:
            self.valid = False


class ToyHttpResponse:
    CODE_DIC = {
        200: 'OK',
        400: 'Bad Request',
        404: 'Not Found'
    }
    MIME_TYPE = {
        'html': 'text/html',
        'jpg': 'image/jpeg',
        'ico': 'image/x-icon',
        'js': 'application/x-javascript'
    }

    def __init__(self):
        self.status = 'HTTP/1.1 %s %s'
        self.header = {'Server': 'ToyHttpServer'}
        self.content = ''
        self.raw = ''
        self.code = 200

    def set_header(self, key, value):
        self.header[key] = value
        pass

    def set_error(self, code):
        self.code = code
        self.pack()

    def pack(self):
        """pack up a response"""
        self.raw = self.status % (self.code, self.CODE_DIC[self.code])
        self.raw += '\r\n'
        for k, v in self.header.items():
            self.raw += '%s:%s\r\n' % (k, v)
        self.raw += '\r\n'
        self.raw += self.content

    def handle(self, req):
        """handle http request"""
        assert isinstance(req, ToyHttpRequest)
        if req.valid is False:
            self.set_error(400)
            return
        try:
            if req.path == '/':
                req.path = '/index.html'
            filename = ROOT + req.path.split('?')[0]
            suf = filename.split('.')[-1]
            fd = open(filename, 'r')
            self.content = fd.read()
            self.set_header('Content-type', self.MIME_TYPE[suf])
            self.pack()
        except IOError:
            self.set_error(404)


class ToyHttpServer:

    def __init__(self, host='0.0.0.0', port=8080):
        self._host = host
        self._port = port
        self._soc = None

    def create_server(self):
        try:
            self._soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._soc.bind((self._host, self._port))
            self._soc.listen(5)
        except Exception as e:
            logging.error(e)

    def serve_forever(self):
        logging.info("Ready to serve...")
        while True:
            conn, addr = self._soc.accept()
            try:
                message = conn.recv(8192)
                req = ToyHttpRequest(raw=message)
                res = ToyHttpResponse()
                res.handle(req)
                conn.sendall(res.raw.encode())
                logging.info('%s -- "%s" - %s', addr[0], req.status, res.code)
            except IOError:
                res = ToyHttpResponse()
                res.set_error(400)
                conn.sendall(res.raw.encode())
                logging.warn('%s -- "%s" - %s', addr[0], req.status, res.code)
            finally:
                conn.close()

        self._soc.close()


def main():
    server = ToyHttpServer()
    server.create_server()
    server.serve_forever()


if __name__ == '__main__':
    main()
