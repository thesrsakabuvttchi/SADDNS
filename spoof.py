from scapy.all import *
import argparse

def send_udp_and_listen_for_icmp(target_ip, target_port, spoofed_ip, spoofed_port):
    # Construct the IP layer
    ip = IP(src=spoofed_ip, dst=target_ip)
    
    # Construct the UDP layer
    udp = UDP(sport=spoofed_port, dport=target_port)
    
    # Construct the payload
    payload = Raw(load="")
    
    # Combine the layers into a single packet
    packet = ip / udp / payload
    
    # Send the packet and listen for replies
    # Using sr1 to send a packet and receive the first reply
    # Adding nofilter=True to ensure ICMP errors are captured
    response = sr1(packet, timeout=1, verbose=True, nofilter=True)
    
    # Check if the response is an ICMP packet indicating a destination unreachable error
    if response is not None:
        if ICMP in response:
            if response[ICMP].type == 3 and response[ICMP].code == 3:
                print("ICMP Destination Unreachable received for port:", target_port)
                return 0
            else:
                print("Received ICMP response, but it's not Destination Unreachable.")
                return -1
        else:
            print("Received response, but it's not an ICMP message.")
            return -1
    else:
        print("No response received.")
        return 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Send a zero-byte UDP packet to a specified IP and port.")
    parser.add_argument("ip", type=str, help="The IP address to which the UDP packet is sent.")
    parser.add_argument("port", type=int, help="The UDP port number to which the packet is sent.")

    args = parser.parse_args()

    target_ip = args.ip
    target_port = args.port
    spoofed_ip = '10.0.0.120'  # Adjust to the appropriate spoofed IP
    spoofed_port = 53        # Adjust to the appropriate spoofed port

    send_udp_and_listen_for_icmp(target_ip, target_port, spoofed_ip, spoofed_port)

