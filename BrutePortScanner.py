import socket
import argparse
import time

def send_udp_packet(bind_ip, ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.IPPROTO_IP, 11, 1)
    sock.setsockopt(socket.IPPROTO_IP, 26, 1)
    sock.bind((bind_ip, 0))
    retval = 0
    try:
        sock.sendto(b'', (ip, port))
        sock.settimeout(1)
        try:
            data, server = sock.recvfrom(1024)
            print(f"Received response from {server}: {data.decode()}")
        except socket.timeout:
            retval = 1
            print(f"port: {port} No response received.")
        except ConnectionRefusedError:
            pass
    finally:
        sock.close()
        return retval

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("ip", type=str)
    parser.add_argument("port_start", type=int)
    parser.add_argument("port_end", type=int)
    args = parser.parse_args()

    IP_BASE = "10.0.0."
    IP_START = 120
    IP_END = 200
    IP_VERIFICATION = "10.0.0.201"

    ip_list = [IP_BASE + str(ip) for ip in range(IP_START, IP_END+1)]

    for iter, port in enumerate(range(args.port_start, args.port_end+1)):
        send_ip = ip_list[iter % len(ip_list)]
        print(f"Scanning {send_ip}:{port}")
        if send_udp_packet(send_ip, args.ip, port) == 1:
            print(f"Re-Scanning {send_ip}:{port}")
            if send_udp_packet(IP_VERIFICATION, args.ip, port) == 1:
                input("Continue?")
        if iter % 50 == 0:
            time.sleep(0.001)

if __name__ == "__main__":
    main()
