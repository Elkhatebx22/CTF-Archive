import socket
import logging
from .utils import ROOT_SERVERS
from .query import Query, DNSHeader, DNSQuestion, DNSRecord
import time
import threading
import hashlib
import struct

class Resolver:
    def __init__(self, internal_domain: str, cache_limit: int = 1000):
        self.cache = {}
        self.cache_limit = cache_limit
        self.internal_domain = internal_domain
        self.lock = threading.Lock()
        self.pending_tids = set()
        self.responses = {}

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('', 53535))

        self.listener_thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.listener_thread.start()

    def _listen_loop(self):
        while True:
            try:
                res, _ = self.sock.recvfrom(512)
                if len(res) < 2:
                    continue
                tid = int.from_bytes(res[:2], byteorder='big')
                with self.lock:
                    if tid not in self.pending_tids or tid in self.responses:
                        continue

                    self.responses[tid] = res
                    self.pending_tids.remove(tid)
            except Exception as e:
                logging.error(f"Listener error: {e}")

    def resolve_host(self, domain: str, caller: str):
        cache_check = self.check_cache(domain)
        if self.is_internal_domain(domain):
            if not cache_check:
                return None
            caller_hash = hashlib.sha256(caller.encode()).hexdigest()[0:63]
            if domain.split(".")[0] != caller_hash: # Only access your own subdomain!
                return None
            return cache_check if cache_check == '127.0.0.1' else None

        if cache_check:
            return cache_check

        query = self.build_query(domain, caller)
        if not query:
            return None

        tld_server = self.resolve_next_hop(query, ROOT_SERVERS)
        print(f"[{int(time.time())}] Resolved TLD server for {query.questions[0].qname} to {tld_server}")
        if not tld_server:
            logging.error(f"Failed to resolve TLD server for {domain}")
            return None

        time.sleep(0.1)

        auth_server = self.resolve_next_hop(query, [tld_server])
        print(f"[{int(time.time())}] Resolved Authoritative server for {query.questions[0].qname} to {auth_server}")
        if not auth_server:
            logging.error(f"Failed to resolve authoritative server for {domain}")
            return None
        
        time.sleep(0.1)
        
        final_ip = self.resolve_next_hop(query, [auth_server], expect_final_answer=True)
        print(f"[{int(time.time())}] Resolved Final IP for {query.questions[0].qname} to {final_ip}")
        if not final_ip:
                logging.error(f"No answer found for {domain}")
                return None

        self.update_cache(query.questions[0].qname, final_ip)
        return final_ip
  
    def check_cache(self, domain: str):
        return self.cache[domain] if domain in self.cache else None
    
    def update_cache(self, domain: str, ip: int):
        if len(self.cache) >= self.cache_limit:
            self.cache.clear()

        self.cache[domain] = ip

    def build_query(self, domain: str, caller: str) -> Query:
        timestamp = int(time.time()) // 4
        data = f"{caller}_{timestamp}".encode()
        hash_bytes = hashlib.md5(data).digest()
        tid = struct.unpack("!H", hash_bytes[:2])[0] 

        try:
            header = DNSHeader(
                tid=tid,
                flags=0x0100, 
                qdcount=1
            )
            question = DNSQuestion(domain, 1, 1)
            return Query(header, [question])
        except Exception as e:
            logging.error(f"Failed to build query: {e}")
            return None

    def resolve_next_hop(self, query: Query, servers: list[str], expect_final_answer: bool = False) -> str | None:
        serialized_query = query.serialize()

        for ip in servers:
            res_bytes = self.send_query(query.header.tid, serialized_query, ip)
            res = self.parse_query(res_bytes)

            if not res or not res.authorities or not res.additionals:
                continue
            if res.header.tid != query.header.tid: # Ensure correct request/response association
                break
            
            if expect_final_answer:
                for record in res.answers:
                    if record.type == 1:  # A record
                        return record.data
                continue

            ip_map = { record.name: record.data for record in res.additionals if record.type == 1 }

            next_hop_ip = next(
                (ip_map.get(ns.data) for ns in res.authorities if ns.data in ip_map),
                None
            )

            if next_hop_ip:
                query.questions[0].qname = res.questions[0].qname
                return next_hop_ip

        return None
    
    def send_query(self, tid: int, query: bytes, server_ip: str):
        with self.lock:
            if tid in self.responses:
                return self.responses.pop(tid)
            self.pending_tids.add(tid)

        time.sleep(0.5)
        self.sock.sendto(query, (server_ip, 53))
        
        start = time.time()
        while time.time() - start < 5:
            with self.lock:
                if tid in self.responses:
                    response = self.responses.pop(tid)
                    self.pending_tids.discard(tid)
                    return response

            time.sleep(0.2)

        with self.lock:
            if tid in self.pending_tids:
                self.pending_tids.remove(tid)
            self.responses.pop(tid, None)

        logging.warning(f"No matching response received for tid {tid}")
        return b''

    def parse_query(self, response: bytes):
        try:
            query = Query.deserialize(response)
            return query
        except Exception as e:
            logging.error(f"Failed to parse response: {e}")
            return None

    def build_record(self, domain: str, ip: str):
        return DNSRecord(
            name=domain,
            type=1,
            record_class=1,
            ttl=300,
            data=ip
        )
    
    def is_internal_domain(self, domain: str) -> bool:
        domain = domain.lower().strip('.')
        internal_base = self.internal_domain.lower().strip('.')
        return domain.endswith('.' + internal_base) and domain != internal_base