#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""simple ICMP traceroute"""
import os
import sys
import time
import select
import struct
import socket

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


def build_packet():
    """build raw ICMP packet"""
    chksum = 0
    pid = os.getpid() & 0xffff
    seq_num = 1
    header = struct.pack("!bbHHh", ICMP_ECHO_REQ, 0, chksum, pid, seq_num)
    data = struct.pack("!d", time.time())
    chksum = checksum(bytearray(header + data))
    if sys.platform == 'darwin':  # ?
        chksum &= 0xffff
    header = struct.pack("!bbHHh", ICMP_ECHO_REQ, 0, chksum, pid, seq_num)
    packet = header + data
    return packet


def creat_socket(ttl, timeout, mode):
    """create sockets, and set TTL in ip header"""
    recv_soc = socket.socket(socket.AF_INET, socket.SOCK_RAW,
                             socket.getprotobyname("icmp"))
    recv_soc.settimeout(timeout)
    if mode == 'udp':
        # send udp packet
        send_soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    else:
        # send icmp packet
        send_soc = recv_soc
    # set TTL
    send_soc.setsockopt(socket.IPPROTO_IP, socket.IP_TTL,
                        struct.pack('I', ttl))

    return send_soc, recv_soc


def do_one_trace(send_soc, recv_soc, host, timeout):
    """do one trace, output router address and rtt"""
    time_left = timeout
    try:
        if send_soc == recv_soc:
            send_soc.sendto(build_packet(), (host, 0))
        else:
            send_soc.sendto(b"abcdefg", (host, 33333))
        time_start = time.time()
        sel = select.select([recv_soc], [], [], time_left)
        time_sel = (time.time() - time_start)
        if sel[0] == []:  # timeout
            raise socket.timeout
        pkt, addr = recv_soc.recvfrom(2048)
        time_recv = time.time()
        time_left = time_left - time_sel
        if time_left <= 0:  # timeout
            raise socket.timeout
    except socket.timeout:
        return None, None
    else:
        icmp_type, _, _, _, _ = struct.unpack("!bbHHh", pkt[20:28])
        rtt = (time_recv - time_start) * 1000
        if icmp_type == 11:  # TTL equals 0
            return addr[0], rtt
        elif icmp_type == 3:  # unreachable
            return addr[0], rtt
        elif icmp_type == 0:  # reach destination
            return addr[0], rtt
    return None, None


def traceroute(host, max_hop=30, tries=3, timeout=2, mode='icmp'):
    """traceroute"""
    modes = ['icmp', 'udp']
    if mode not in modes:
        return
    dest_addr = socket.gethostbyname(host)
    print('traceroute to %s(%s), %d hops max' % (host, dest_addr, max_hop))
    for ttl in range(1, max_hop+1):
        for _ in range(tries):
            send_soc, recv_soc = creat_socket(ttl, timeout, mode)
            addr, rtt = do_one_trace(send_soc, recv_soc, host, timeout)
            if addr and rtt:
                print("%d %s rtt=%.3f ms" % (ttl, addr, rtt))
            else:
                print("%d *" % ttl)
            send_soc.close()
            recv_soc.close()
            if addr == dest_addr:
                return


if __name__ == '__main__':
    traceroute('www.baidu.com', mode='icmp')
    traceroute('www.baidu.com', mode='udp')
