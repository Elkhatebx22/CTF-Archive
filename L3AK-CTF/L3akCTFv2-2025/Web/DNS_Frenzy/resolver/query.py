from dataclasses import dataclass, field
from typing import List
import struct

#IPv6 is annoying, so I skipped it =)

def encode_name(name: str) -> bytes:
    parts = name.strip('.').split('.')
    result = b''
    for part in parts:
        length = len(part)
        result += bytes([length]) + part.encode('utf-8')
    result += b'\x00'
    return result

def encode_to_compressed(name: str) -> bytes:
    parts = name.strip('.').split('.')
    encoded = b''.join(struct.pack('B', len(part)) + part.encode() for part in parts)
    return encoded + b'\x00'

def decode_from_compressed(data: bytes, offset: int) -> tuple[str, int]:
    """
    Convert compressed domain back to original format (handles pointer decompression)
    """
    labels = []
    jumped = False
    original_offset = offset

    while True:
        length = data[offset]

        if length & 0xC0 == 0xC0:  # Pointer was used
            pointer = ((length & 0x3F) << 8) | data[offset + 1]
            if not jumped:
                original_offset = offset + 2
            offset = pointer
            jumped = True
            continue

        if length == 0:
            offset += 1
            break

        offset += 1
        label = data[offset:offset + length]
        labels.append(label.decode())
        offset += length

    domain = ".".join(labels)
    return domain, (offset if not jumped else original_offset)

@dataclass
class DNSHeader:
    tid: int
    flags: int = 0
    qdcount: int = 0
    ancount: int = 0
    nscount: int = 0
    arcount: int = 0

    def to_bytes(self) -> bytes:
        return struct.pack('!HHHHHH', self.tid, self.flags, self.qdcount,
                           self.ancount, self.nscount, self.arcount)

    @classmethod
    def from_bytes(cls, data: bytes) -> "DNSHeader":
        if len(data) < 12:
            raise ValueError("Invalid header size")
        tid, flags, qdcount, ancount, nscount, arcount = struct.unpack('!HHHHHH', data[:12])
        return cls(tid, flags, qdcount, ancount, nscount, arcount)

@dataclass
class DNSQuestion:
    qname: str = ""
    qtype: int = 1  # A record by default
    qclass: int = 1  # IN class by default

    def clean_domain(self, domain: str) -> str:
        domain = domain.strip().lower()
        if not domain.endswith('.'):
            domain += '.'
        if not domain:
            raise ValueError("Domain name can't be empty")
        if len(domain.encode('utf-8')) > 255:
            raise ValueError("Domain name too long")
        return domain

    def __post_init__(self):
        self.qname = self.clean_domain(self.qname)

    def to_bytes(self) -> bytes:
        return encode_to_compressed(self.qname) + struct.pack('!HH', self.qtype, self.qclass)
    
    def __repr__(self):
        return f"DNSQuestion(qname='{self.qname}', qtype={self.qtype}, qclass={self.qclass})"

@dataclass
class DNSRecord:
    name: str
    type: int
    record_class: int
    ttl: int
    data: str

    def encode_rdata(self) -> bytes:
        if self.type == 1:
            return self.encode_ipv4(self.data)
        elif self.type == 2:
            return encode_name(self.data)
        elif self.type == 16:
            txt = self.data.encode('utf-8')
            if len(txt) > 255:
                txt = txt[:255]
            return bytes([len(txt)]) + txt

        raise NotImplementedError(f"RDATA encoding not implemented for type {self.type}")

    @staticmethod
    def encode_ipv4(addr: str) -> bytes:
        parts = addr.split('.')
        if len(parts) != 4:
            raise ValueError(f"Invalid IPv4 address: {addr}")
        return bytes(int(part) for part in parts)

    def to_bytes(self) -> bytes:
        encoded_name = encode_to_compressed(self.name)
        rdata = self.encode_rdata()
        rdlength = len(rdata)
        return (
            encoded_name +
            struct.pack('!HHI', self.type, self.record_class, self.ttl) +
            struct.pack('!H', rdlength) +
            rdata
        )
    
    def __repr__(self) -> str:
        type_map = {
            1: "A",
            2: "NS",
            5: "CNAME",
            6: "SOA",
            12: "PTR",
            15: "MX",
            28: "AAAA"
        }

        class_map = {
            1: "IN"
        }

        type_str = type_map.get(self.type, str(self.type))
        class_str = class_map.get(self.record_class, str(self.record_class))

        return (
            f"DNSRecord(Name: {self.name}, "
            f"Type: {type_str}, "
            f"Class: {class_str}, "
            f"TTL: {self.ttl}, "
            f"Data: {self.data})"
        )

@dataclass
class Query:
    header: DNSHeader
    questions: List[DNSQuestion] = field(default_factory=list)
    answers: List[DNSRecord] = field(default_factory=list)
    authorities: List[DNSRecord] = field(default_factory=list)
    additionals: List[DNSRecord] = field(default_factory=list)

    def __repr__(self):
        return (
            f"<Query TID={self.header.tid} "
            f"Flags=0x{self.header.flags:04x} "
            f"Questions={len(self.questions)} "
            f"Answers={len(self.answers)} "
            f"Authorities={len(self.authorities)} "
            f"Additionals={len(self.additionals)}>"
        )

    def serialize(self) -> bytes:
        data = self.header.to_bytes()
        for question in self.questions:
            data += question.to_bytes()
        for record in self.answers:
            data += record.to_bytes()
        for record in self.authorities:
            data += record.to_bytes()
        for record in self.additionals:
            data += record.to_bytes()
        return data

    @classmethod
    def deserialize(cls, data: bytes) -> "Query":
        header = DNSHeader.from_bytes(data[:12])
        offset = 12
        questions = []
        answers = []
        authorities = []
        additionals = []

        for _ in range(header.qdcount):
            qname, offset = decode_from_compressed(data, offset)
            qtype, qclass = struct.unpack('!HH', data[offset:offset + 4])
            offset += 4
            questions.append(DNSQuestion(qname, qtype, qclass))

        def parse_record(data: bytes, offset: int) -> tuple[DNSRecord, int]:
            name, offset = decode_from_compressed(data, offset)
            rtype, rclass, ttl, rdlength = struct.unpack('!HHIH', data[offset:offset + 10])
            offset += 10
            rdata_bytes = data[offset:offset + rdlength]

            if rtype == 1:
                rdata = ".".join(str(b) for b in rdata_bytes)
            elif rtype == 2:  # NS record
                rdata, _ = decode_from_compressed(data, offset)
            else:
                rdata = rdata_bytes.hex()

            record = DNSRecord(name, rtype, rclass, ttl, rdata)
            offset += rdlength
            return record, offset

        for _ in range(header.ancount):
            record, offset = parse_record(data, offset)
            answers.append(record)

        for _ in range(header.nscount):
            record, offset = parse_record(data, offset)
            authorities.append(record)

        for _ in range(header.arcount):
            record, offset = parse_record(data, offset)
            additionals.append(record)

        return cls(
            header=header,
            questions=questions,
            answers=answers,
            authorities=authorities,
            additionals=additionals
        )
