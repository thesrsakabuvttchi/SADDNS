import socket
import argparse

def send_udp_packet(ip, port):
    """
    Sends a zero-byte UDP packet to a specified IP and port. Checks for responses or ICMP errors.
    """
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt( socket.IPPROTO_IP, 11, 1 )  
    sock.setsockopt( socket.IPPROTO_IP, 26, 1 ) 
    #sock.bind(('10.0.0.102', 0))
    try:
        # Send a zero-byte message
        sock.sendto(b'', (ip, port))
        print(f"Zero-byte packet sent to {ip}:{port}")

        # Try to receive a response or ICMP error
        sock.settimeout(2)  # Set a timeout period
        try:
            data, server = sock.recvfrom(1024)
            print(f"Received response from {server}: {data.decode()}")
        except socket.timeout:
            print("No response received. The packet might have been discarded or accepted without response.")
        except ConnectionRefusedError:
            print("ICMP Port Unreachable received. The port is closed.")

    finally:
        sock.close()

def main():
    parser = argparse.ArgumentParser(description="Send a zero-byte UDP packet to a specified IP and port.")
    parser.add_argument("ip", type=str, help="The IP address to which the UDP packet is sent.")
    parser.add_argument("port", type=int, help="The UDP port number to which the packet is sent.")
    args = parser.parse_args()

    send_udp_packet(args.ip, args.port)

if __name__ == "__main__":
    main()

