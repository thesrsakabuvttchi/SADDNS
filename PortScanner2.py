import socket
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import threading


def send_udp_packet(ip, port, start_barrier):
    """
    Sends a zero-byte UDP packet to a specified IP and port at a specific start time.
    """
    start_barrier.wait()
    # Create a UDP socket
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.setsockopt(socket.IPPROTO_IP, 11, 1)  
        sock.setsockopt(socket.IPPROTO_IP, 26, 1) 
        rval = 0
        try:
            sock.sendto(b'', (ip, port))
            sock.settimeout(0.02)
            try:
                sock.recvfrom(1024)
            except socket.timeout:
                pass
            except ConnectionRefusedError:
                rval = 1
        finally:
            return rval

def send_verif_packet(ip, port, start_barrier):
    """
    Sends a verification UDP packet to a specified IP and port at a specific start time.
    """
    start_barrier.wait()
    # Create a UDP socket
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.setsockopt(socket.IPPROTO_IP, 11, 1)
        sock.setsockopt(socket.IPPROTO_IP, 26, 1)
        sock.bind(('10.0.0.122', 0))
        rval = 0
        try:
            sock.sendto(b'', (ip, port))
            sock.settimeout(0.1)
            try:
                data, server = sock.recvfrom(1024)
            except socket.timeout:
                pass
            except ConnectionRefusedError:
                rval = 1
        finally:
            sock.close()
            return rval

def main():
    parser = argparse.ArgumentParser(description="Send a zero-byte UDP packet to a specified IP and port.")
    parser.add_argument("ip", type=str, help="The IP address to which the UDP packet is sent.")
    parser.add_argument("port_start", type=int, help="The start range of UDP ports to which the packet is sent.")
    parser.add_argument("port_end", type=int, help="The start range of UDP ports to which the packet is sent.")
    args = parser.parse_args()

    port_range = list(range(args.port_start, args.port_end))
    max_workers = 51
    batch_size = 50

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for i in range(0, len(port_range), batch_size):

            batch_ports = port_range[i:i + batch_size]
            barrier = threading.Barrier(max_workers)
           
            futures = [executor.submit(send_udp_packet, args.ip, port, barrier) for port in port_range[:batch_size]]
            futures.append(executor.submit(send_verif_packet, args.ip, args.port_start, barrier))
            
            num_unreach =0
            # Wait for all futures in the batch to complete
            for future in as_completed(futures[:-1]):
                num_unreach+=future.result()  # Ensure all packets are sent

            verification_result = futures[-1].result()

            print(f"{port_range[i]} to {port_range[min(i+batch_size,len(port_range)-1)]} {num_unreach}: {verification_result}")
            if(num_unreach==1 and verification_result==1):
                print("This is the likely port range!!!")

            time.sleep(1)  # Sleep after each batch

if __name__ == "__main__":
    main()