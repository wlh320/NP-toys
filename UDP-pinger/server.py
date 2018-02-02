#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
UDP pinger server
"""
import random
import socket


def run():

    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    serverSocket.bind(('0.0.0.0', 12000))

    while True:
        rand = random.randint(0, 10)
        # receive client packet
        message, addr = serverSocket.recvfrom(1024)
        print('Received ping from {}:{}'.format(addr[0], addr[1]))
        message = message.upper()

        # simulate 30% packet loss
        if rand < 4:
            continue

        serverSocket.sendto(message, addr)

    serverSocket.close()


if __name__ == '__main__':
    run()
