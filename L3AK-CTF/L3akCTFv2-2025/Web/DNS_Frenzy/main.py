import socket
import logging
from concurrent.futures import ThreadPoolExecutor
from resolver import Resolver
from resolver.query import DNSRecord, Query

internal_domain = "dns_l3ak.ctf"
FLAG = "L3AK{bad_tx1d_+_r4c3_c0nd1t10n_+_dn5_sp00f1ng_=_flag!!!}"
MAX_WORKERS = 10

def handle_request(data, addr, sock, resolver):
    try:
        query = Query.deserialize(data)
        qname = query.questions[0].qname
        print(f"[Worker] Received query for: {qname} from {addr}")

        resolved_ip = resolver.resolve_host(qname, addr[0])
        if not resolved_ip:
            print(f"[Worker] Failed to resolve: {qname}")
            return

        http_comment = (
            f"I like your subdomain: {FLAG}"
            if resolved_ip == '127.0.0.1' and internal_domain in qname
            else None
        )

        response_header = query.header
        response_header.flags = 0x8080

        answers = [resolver.build_record(qname, resolved_ip)]
        if http_comment:
            chunks = [http_comment[i:i + 255] for i in range(0, len(http_comment), 255)]
            for chunk in chunks:
                answers.append(DNSRecord(
                    name=qname,
                    type=16,  # TXT record
                    record_class=1,
                    ttl=60,
                    data=chunk
                ))

        response_header.ancount = len(answers)
        response = Query(
            header=response_header,
            questions=query.questions,
            answers=answers
        )

        sock.sendto(response.serialize(), addr)
        print(f"[Worker] Sent answer: {resolved_ip} to {addr}")

    except Exception as e:
        logging.error(f"[Worker] Error handling request: {e}")

def run_dns_server(host='0.0.0.0', port=5335):
    resolver = Resolver(internal_domain)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        sock.bind((host, port))
        print(f"DNS Server listening on {host}:{port} with max {MAX_WORKERS} worker threads")
    except PermissionError:
        print(f"Permission denied: Port {port} requires root privileges.")
        return
    except Exception as e:
        print(f"Failed to bind to port {port}: {e}")
        return

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        try:
            while True:
                data, addr = sock.recvfrom(512)
                executor.submit(handle_request, data, addr, sock, resolver)
        except KeyboardInterrupt:
            print("\nShutting down DNS server.")
        except Exception as e:
            logging.error(f"Main loop error: {e}")

if __name__ == '__main__':
    run_dns_server()