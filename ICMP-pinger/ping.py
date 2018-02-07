#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""simple ICMP pinger"""

import os
import sys
import time
import select
import socket
import struct

ICMP_ECHO_REQ = 8


def checksum(data):
    """calculate checksum"""
    csum = 0
    count_to = (len(data) / 2) * 2

    count = 0
    while count < count_to:
        word_val = (data[count+1] << 8) + data[count]
        csum = csum + word_val
        count += 2

    if count_to < len(data):
        csum = csum + data[len(data) - 1]
        csum = csum & 0xffffffff

    csum = (csum >> 16) + (csum & 0xffff)
    csum = csum + (csum >> 16)

    csum = (~csum) & 0xffff
    csum = csum >> 8 | (csum << 8 & 0xff00)
    return csum


def send_one_ping(soc, dest_addr, pid, seq_num):
    """send one ICMP ping packet"""
    chksum = 0
    header = struct.pack("!bbHHh", ICMP_ECHO_REQ, 0, chksum, pid, seq_num)
    data = struct.pack("!d", time.time())
    chksum = checksum(bytearray(header + data))
    if sys.platform == 'darwin':  # ?
        chksum &= 0xffff
    header = struct.pack("!bbHHh", ICMP_ECHO_REQ, 0, chksum, pid, seq_num)
    packet = header + data
    soc.sendto(packet, (dest_addr, 1))


def receive_one_ping(soc, pid, timeout):
    """receive ICMP pong from dest_addr"""
    time_left = timeout
    while True:
        start_sel = time.time()
        sel = select.select([soc], [], [], time_left)
        sel_time = (time.time() - start_sel)
        if sel[0] == []:
            return "Request time out."

        time_recv = time.time()
        pkt, addr = soc.recvfrom(1024)
        ttl = struct.unpack("!B", pkt[8:9])[0]
        # parse ICMP header
        header, data = pkt[20:28], pkt[28:]
        chksum = checksum(header + data)
        icmp_type, _, _, icmp_id, seq = struct.unpack("!bbHHh", header)
        # check ICMP header
        if icmp_type == 0 and chksum == 0 and pid == icmp_id:
            time_send = struct.unpack("!d", data)[0]
            rtt = (time_recv - time_send) * 1000
            print("%d bytes from %s: icmp_seq=%d ttl=%d time=%.1f ms" %
                  (len(pkt), addr[0], seq, ttl, rtt))
            return rtt

        time_left = time_left - sel_time
        if time_left <= 0:
            return "Request time out."


def do_one_ping(dest_addr, timeout, seq_num):
    """do one ping, print result"""
    icmp = socket.getprotobyname("icmp")
    # we need SOCK_RAW to handle ICMP packet
    soc = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)

    pid = os.getpid() & 0xffff
    send_one_ping(soc, dest_addr, pid, seq_num)
    delay = receive_one_ping(soc, pid, timeout)

    soc.close()
    return delay


def ping(host, timeout=1):
    """ping"""
    dest = socket.gethostbyname(host)
    print("PING " + host + "(%s):" % dest)
    time_start = time.time()
    cnt = 0
    pkt_loss = 0
    delays = []
    try:
        while True:
            delay = do_one_ping(dest, timeout, cnt)
            if isinstance(delay, str):  # timeout
                pkt_loss += 1
                print(delay)
            else:
                delays.append(delay)
            cnt += 1
            time.sleep(1)
    except KeyboardInterrupt:  # ctrl-c
        time_end = time.time()
        print('')
        print('--- %s ping statistics ---' % host)
        print('%d packets transmitted, %d received, %d%% packet loss, time %d ms' % (
            cnt, (cnt-pkt_loss), pkt_loss/cnt*100, (time_end-time_start)*1000))
        if delays:
            print('rtt min/avg/max/mdev= %.3f/%.3f/%.3f/0.000 ms' %
                  (min(delays), sum(delays)/len(delays), max(delays)))


if __name__ == '__main__':
    if len(sys.argv) == 1:
        print('Usage: sudo ./ping.py host')
    else:
        ping(sys.argv[1])
