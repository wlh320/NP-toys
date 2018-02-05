#!/usr/bin/env python3
#-*- coding:utf-8 -*-
"""multi-threading toy HTTP proxy"""

import socket
import logging
import threading
from urllib.parse import urlparse

logging.basicConfig(
    format='%(asctime)s-%(levelname)s-%(module)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)


def resolveAddr(url):
    """
    parse url, return (host, port, path)
    based on: http_URL = "http:" "//" host [ ":" port ] [ abs_path [ "?" query ]] - RFC 2616

    I should write it myself but I'm too lazy
    """
    if url.find('//') == -1:
        url = '//' + url  # RFC 1808
    res = urlparse(url, scheme='http')
    host = res.hostname
    port = 80 if res.port is None else res.port
    path = '/' if res.path == '' else res.path
    return host, port, path


class ProxyThread(threading.Thread):
    """handle request from browser"""
    MAX_RECV = 10240

    def __init__(self, conn, cli_addr):
        threading.Thread.__init__(self)
        self.conn = conn
        self.cli_addr = cli_addr

    def run(self):

        request = self.conn.recv(self.MAX_RECV)
        # get request line and other part
        req_line, req_other = request.split(b'\r\n', 1)
        # parse request line
        method, url, version = req_line.decode().split()
        # resolve http_URL, get server info
        srv_host, srv_port, path = resolveAddr(url)

        # pack new HTTP request
        new_req_line = ('%s %s %s\r\n' % (method, path, version)).encode()
        new_req = new_req_line + req_other

        logging.info('Proxying %s %s %s %s' %
                     (self.cli_addr[0], method, url, version))

        try:
            # connect to server and send request
            soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            soc.connect((srv_host, srv_port))
            soc.sendall(new_req)
            while True:
                ret_data = soc.recv(self.MAX_RECV)
                if ret_data:
                    self.conn.sendall(ret_data)
                else:
                    break
        except socket.error:
            logging.error("socket error")
        finally:
            soc.close()
            self.conn.close()


class ToyProxy:
    BACKLOG = 8

    def __init__(self, host='localhost', port=8888):
        self.host = host
        self.port = port
        self.sock = None

    def serve(self):
        """run server"""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind((self.host, self.port))
            self.sock.listen(self.BACKLOG)

            logging.info("Proxy server running on %s:%s", self.host, self.port)
            while True:
                conn, cli_addr = self.sock.accept()
                # start new thread to handle browser request
                handler = ProxyThread(conn, cli_addr)
                handler.start()

            self.sock.close()
        except socket.error as err:
            print(err)


def test():
    proxy = ToyProxy(port=8080)
    proxy.serve()


if __name__ == '__main__':
    test()
