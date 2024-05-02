import asyncio
from dnslib import DNSRecord, DNSHeader, RR, CNAME, A, QTYPE
from socket import AF_INET, SOCK_DGRAM, socket

class DNSProtocol(asyncio.DatagramProtocol):
    def __init__(self, socket):
        self.socket = socket

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        print(f"Received DNS query from {addr[0]}:{addr[1]}")
        asyncio.create_task(self.handle_dns_request(data, addr))

    async def handle_dns_request(self, data, addr):
        """
        Handle incoming DNS requests and respond with an A record after a delay.
        """
        request = DNSRecord.parse(data)
        print("Received DNS request:")
        print(request)

        # Create DNS response
        reply = DNSRecord(DNSHeader(id=request.header.id, qr=1, aa=1, ra=1), q=request.q)
        reply.add_answer(RR(request.q.qname, QTYPE.A, rdata=A("10.0.0.57"), ttl=300))
        response = reply.pack()

        await asyncio.sleep(3)  

        for byte in response:
            # `bytes([byte])` converts the integer `byte` to a bytes object of length 1
            self.transport.sendto(bytes([byte]), addr)
            await asyncio.sleep(3)  # Adjust the delay as needed between sending each byte

        print(f"Response sent to {addr} after a delay.")

async def run_dns_server():
    """
    Run an asynchronous DNS server on port 53 that responds to all A record queries with a delayed response.
    """
    # Create UDP server socket
    loop = asyncio.get_running_loop()
    listen = loop.create_datagram_endpoint(
        lambda: DNSProtocol(socket(AF_INET, SOCK_DGRAM)),
        local_addr=('0.0.0.0', 53))

    transport, protocol = await listen

    print("DNS Server is running on port 53...")

    try:
        await asyncio.sleep(3600 * 5)  # Run for 5 hours
    except KeyboardInterrupt:
        print("DNS Server is shutting down...")
    finally:
        transport.close()

if __name__ == '__main__':
    asyncio.run(run_dns_server())
