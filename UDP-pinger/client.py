#!/usr/bin/env python3
# -*- coding: utf-8
"""
simple UDP pinger client
"""
import time
import socket


def ping(host, port, seq_num, timeout):
    """udp pinger"""
    soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    soc.settimeout(timeout)
    loss_num = 0
    print('PING {}:'.format(host))
    for i in range(1, seq_num+1):
        try:
            send_time = time.time()
            ping_data = 'Ping {} {}'.format(i, send_time)
            soc.sendto(ping_data.encode(), (host, port))
            ret_data, addr = soc.recvfrom(1024)
            recv_time = time.time()
            rtt = (recv_time - send_time) * 1000
            print('%d bytes from %s: seq=%d time=%.3f ms' % (
                len(ret_data), addr[0], i, rtt
            ))
        except socket.timeout:
            # timeout, assume packet loss
            loss_num += 1
    soc.close()

    loss_rate = (loss_num / seq_num)*100
    print('--- statistics ---')
    print('%d packets transmitted, %d received, %d%% packet loss' %
          (seq_num, (seq_num-loss_num), loss_rate))


if __name__ == '__main__':
    ping(host='127.0.0.1', port=12000, seq_num=10, timeout=1)
