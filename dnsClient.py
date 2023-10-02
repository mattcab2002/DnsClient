import socket
import random
import argparse
import time
import struct
import re

class DNSClientException(Exception):
    "Raise when any error in the DNS Client occurs"
    pass

class DNSPacket:
    def __init__(self, header, question, answer):
        self.header = header
        self.question = question
        self.answer = answer

    def __str__(self):
        return "{} {}".format(self.header.__str__(), self.question.__str__())

    @classmethod
    def get_request_dns_packet(cls):
        return cls(cls.Header.get_request_header(), cls.Question.get_request_question(),
                   cls.Answer.get_request_answer())

    @staticmethod
    def get_q_type(qtype_num: int) -> str:
        if qtype_num == 1:
            return "A"
        if qtype_num == 2:
            return "NS"
        if qtype_num == 15:
            return "MX"

    class Header:
        ID = None
        QDCOUNT = None
        FLAGS = None
        ANCOUNT = None
        NSCOUNT = None
        ARCOUNT = None

        def __init__(self, FLAGS, QDCOUNT, ANCOUNT, NSCOUNT, ARCOUNT, ID = random.getrandbits(16)):
            self.ID = ID
            self.FLAGS = FLAGS
            self.QDCOUNT = QDCOUNT
            self.ANCOUNT = ANCOUNT
            self.NSCOUNT = NSCOUNT
            self.ARCOUNT = ARCOUNT  # not using additional

        def __str__(self):
            return seperate_string("{:024x}".format(
                int("{:016b}{:016b}{:016b}{:016b}{:016b}{:016b}".format(self.ID, int(self.FLAGS.__str__(), 2),
                                                                        self.QDCOUNT, self.ANCOUNT, self.NSCOUNT,
                                                                        self.ARCOUNT), 2)), 2)

        @classmethod
        def get_request_header(cls, FLAGS, ANCOUNT=0x0000, ARCOUNT=0x0000):
            QDCOUNT = 0x0001
            NSCOUNT = 0x0000
            return cls(FLAGS, QDCOUNT, ANCOUNT, NSCOUNT, ARCOUNT)

        @classmethod
        def unpack(cls, incoming_response_header):
            flags = cls.Flags.unpack(incoming_response_header[2:4])
            return cls(ID=incoming_response_header[0:2], FLAGS=flags, QDCOUNT=incoming_response_header[4:6], ANCOUNT=incoming_response_header[6:8], NSCOUNT=incoming_response_header[8:10], ARCOUNT=incoming_response_header[10:12])

        class Flags:
            QR = None
            OPCODE = None
            AA = None
            TC = None
            RD = None
            RA = None
            Z = None
            RCODE = None

            def __init__(self, QR, OPCODE, AA, TC, RD, RA, Z, RCODE):
                self.QR = QR  # default to query
                self.OPCODE = OPCODE  # standard query
                self.AA = AA  # check in response
                self.TC = TC
                self.RD = RD
                self.RA = RA  # check in response
                self.Z = Z
                self.RCODE = RCODE  # check in response

            def __str__(self):
                return "{:01b}{:04b}{:01b}{:01b}{:01b}{:01b}{:03b}{:04b}".format(self.QR, self.OPCODE, self.AA, self.TC,
                                                                                 self.RD, self.RA, self.Z, self.RCODE)

            def to_hex(self):
                return "{:04x}".format(int(self.__str__(), 2))

            @classmethod
            def get_request_flags(cls, TC):
                QR = 0b0  # default to query
                OPCODE = 0b0000  # standard query
                AA = 0b0  # check in response
                RD = 0b1
                RA = 0b0  # check in response
                Z = 0b000
                RCODE = 0b0000  # check in response
                return cls(QR, OPCODE, AA, TC, RD, RA, Z, RCODE)

            @classmethod
            def unpack(cls, incoming_response_flags):
                flag_bits = list("{:016b}".format(int("{:02x}{:02x}".format(incoming_response_flags[0],incoming_response_flags[1]), 16)))
                return cls(QR=flag_bits[0], OPCODE=flag_bits[1:5], AA=flag_bits[6], TC=flag_bits[7], RD=flag_bits[8], RA=flag_bits[9], Z=flag_bits[10:13], RCODE=flag_bits[13:])

    class Question:
        QNAME = None
        QTYPE = None
        QCLASS = None

        def __init__(self, QNAME, QTYPE, QCLASS):
            self.QNAME = QNAME
            self.QTYPE = QTYPE
            self.QCLASS = QCLASS

        def __str__(self):
            labels = self.QNAME.split(".")
            return_string = ""
            for label in labels:
                return_string += "{:02x} ".format(len(label))
                for ch in label:
                    return_string += "{} ".format(hex(ord(ch))[2:])
            return_string += "{:02x} ".format(0)  # indicating end of QNAME
            return_string += "{} {} ".format("{:04x}".format(self.QTYPE)[:2], "{:04x}".format(self.QTYPE)[2:])
            return_string += "{} {}".format("{:04x}".format(self.QCLASS)[:2], "{:04x}".format(self.QCLASS)[2:])
            return return_string

        @classmethod
        def get_request_question(cls, QNAME, QTYPE):
            QCLASS = 0x0001
            return cls(QNAME, cls.get_q_num(QTYPE.upper()), QCLASS)

        @staticmethod
        def get_q_num(qtype_string: str) -> int:
            if qtype_string == "A":
                return 0x0001
            if qtype_string == "NS":
                return 0x0002
            if qtype_string == "MX":
                return 0x000f

        @classmethod
        def unpack(cls, numQuestions, question):
            qCounter = 0
            pointer = 12    # starts at 12 because of 12 byte header

            while qCounter < numQuestions:
                counter = 1     # start at 1 because of ending 0 byte
                name = question.QNAME
                labels = name.split('.')
                counter += len(labels)
        
                for label in labels:
                    for char in label:
                        counter += 1
        
                counter += 4    # QTYPE and QCLASS bytes 
                pointer += counter
                qCounter += 1

            # construct a question class for each one

            return pointer 

    class Answer:

        def __init__(self, NAME, TYPE, CLASS, TTL, RDLENGTH, RDATA):
            self.NAME = NAME
            self.TYPE = TYPE
            self.CLASS = CLASS
            self.TTL = TTL
            self.RDLENGTH = RDLENGTH
            self.RDATA = RDATA

        @classmethod
        def get_request_answer(cls, NAME, TYPE, RDLENGTH, RDATA):
            CLASS = 0x0000  # check response
            TTL = 0x00000000  # check response
            RDATA = RDATA()
            return cls(NAME, TYPE, CLASS, TTL, RDLENGTH, RDATA)

        def __str__(self, auth_bit = None):
            match self.TYPE:
                case 0x0001:
                    return f"IP \t {self.RDATA.DATA} \t {self.TTL} \t {auth_bit}\n"
                case 0x0002:
                    return f"NS \t {self.RDATA.DATA} \t {self.TTL} \t {auth_bit}\n"
                case 0x0005:
                    return f"CNAME \t {self.RDATA.DATA} \t {self.TTL} \t {auth_bit}\n"
                case 0x000f:
                    return f"MX \t {self.RDATA.ALIAS} \t {self.RDATA.PREFERENCE} \t {self.TTL} \t {auth_bit}\n"
                case default:
                    pass

        @classmethod
        def unpack(cls, data, name, pointer):
            type = data[pointer] << 8 | data[pointer + 1]
            pointer += 2
            packet_class = data[pointer: pointer+2]
            if packet_class[0] + packet_class[1] != 0x0001:
                print_error("Expected packet class to be 0x0001 but was {} instead".format(packet_class)) 
                raise DNSClientException()
            pointer += 2    # Beginning of TTL bytes

            match type:
                case 0x0005: # CNAME
                    ttl = getTTL(data, pointer)
                    pointer += 4    # Beginning of the RDLength
                    rdlength = data[pointer] << 8 | data[pointer + 1]
                    pointer += 2    # Beginning of RData
                    alias = get_alias(data, pointer)
                    pointer += rdlength ## Beginning of next answer
                    return (cls(name, type, packet_class,ttl, rdlength, cls.RDATA(alias, None, None)), pointer)
                case 0x0001: # A
                    ttl = getTTL(data, pointer)
                    pointer += 4
                    rdlength = data[pointer] << 8 | data[pointer + 1] 
                    pointer += 2 # go to RData
                    ip = get_ip_address(data, pointer)
                    pointer +=4 # Beginning of next answer
                    return (cls(name, type, packet_class,ttl, rdlength, cls.RDATA(ip, None, None)), pointer)
                case 0x0002: # NS
                    # print("THIS IS THE START OF THE NAME SERVER SECTION\n")
                    ttl = getTTL(data, pointer)
                    pointer += 4
                    rdlength = data[pointer] << 8 | data[pointer + 1]
                    pointer += 2
                    alias = get_alias(data,pointer)
                    pointer += rdlength
                    return (cls(name, type, packet_class,ttl, rdlength, cls.RDATA(alias, None, None)), pointer)
                case 0x000f: #MX
                    ttl = getTTL(data, pointer)
                    pointer += 4
                    rdlength = data[pointer] << 8 | data[pointer + 1]
                    pointer += 2
                    pref = data[pointer] << 8 | data[pointer + 1]
                    pointer += 2
                    exchange = get_alias(data, pointer)
                    pointer += rdlength
                    return (cls(name, type, packet_class,ttl, rdlength, cls.RDATA(None, pref,exchange)), pointer)
                case default:
                    return (None, pointer)

        class RDATA:
            def __init__(self, DATA, PREFERENCE, EXCHANGE=0):
                self.DATA = DATA
                self.PREFERENCE = PREFERENCE
                self.EXCHANGE = EXCHANGE

    class Authority:
        @staticmethod
        def unpack(self, incoming_authority):
            return self(incoming_authority)

    class Additional:

        @staticmethod
        def unpack(self, incoming_additional):
            return self(incoming_additional)


def seperate_string(string, spacers):
    return ' '.join(string[i:i + spacers] for i in range(0, len(string), spacers))

def getTTL(data, pointer):
    ttl_bytes = data[pointer:pointer+4]  # TTL is 4 bytes long
    ttl = (ttl_bytes[0] << 24) | (ttl_bytes[1] << 16) | (ttl_bytes[2] << 8) | ttl_bytes[3]
    # print(f"THIS IS THE TTL IN SECONDS : {ttl}\n")
    return ttl

def get_alias(data, pointer):
    cname = []

    while True:
        label_length = data[pointer]
        if (label_length == 0xC0):
            pointer = data[pointer + 1]     # Sets the pointer to the pointed address
            label_length = data[pointer]

        labels = []
        for i in range(pointer + 1, pointer + label_length + 1):
            labels.append(chr(data[i]))
        cname.append(''.join(labels))
        
        pointer += label_length + 1
        if (data[pointer] == 0):
            break
    alias = '.'.join(cname)
    return alias

def get_ip_address(data, pointer):
    counter = 0
    sections = []
    ip = []
    while counter < 4:
        sections.append(data[pointer])
        counter += 1
        pointer += 1

    for i in sections:
        ip.append(str(i))

    ip = '.'.join(ip)
    return ip

def get_additional_information(data, pointer, additionalRecordsNum):
    print(f"*** Additional Section ({additionalRecordsNum} records) ***\n")
    authorityBit = (data[2] & 32) >> 5
    aCounter = 0
    # Iterates through response records
    while aCounter < additionalRecordsNum:
        # Finds byte after 'NAME' field in response

        while True:
            # Checks if we hit ending byte '0' and pointer to location after accordingly
            if (data[pointer] == 0):
                pointer += 1
                break;
            
            if ((data[pointer] & 0xC0) == 0xC0):
                pointer += 2
                break;

            pointer += 1

        aCounter += 1
        
        # Check type
        type = data[pointer] << 8 | data[pointer + 1]
        pointer += 4    # Beginning of TTL bytes
        match type:
            case 5:
                ttl = getTTL(data, pointer)
                pointer += 4    # Beginning of the RDLength
                rdlength = data[pointer] << 8 | data[pointer + 1]
                pointer += 2    # Beginning of RData
                alias = get_alias(data, pointer)
                pointer += rdlength ## Beginning of next answer
                print(f"CNAME \t {alias} \t {ttl} \t {authorityBit}\n")
            case 1:
                ttl = getTTL(data, pointer)
                pointer += 6 # go straight to RData
                ip = get_ip_address(data, pointer)
                pointer +=4 # Beginning of next answer
                print(f"IP \t {ip} \t {ttl} \t { authorityBit}\n")
            case 2:
                ttl = getTTL(data, pointer)
                pointer += 4
                rdlength = data[pointer] << 8 | data[pointer + 1]
                pointer += 2
                alias = get_alias(data,pointer)
                pointer += rdlength
                print(f"NS \t {alias} \t {ttl} \t {authorityBit}\n")
            case 15:
                ttl = getTTL(data, pointer)
                pointer += 4
                rdlength = data[pointer] << 8 | data[pointer + 1]
                pointer += 2
                pref = data[pointer] << 8 | data[pointer + 1]
                pointer += 2
                alias = get_alias(data, pointer)
                pointer += rdlength
                print(f"MX \t {alias} \t {pref} \t {ttl} \t {authorityBit}\n")
    return pointer



def get_response_information(data, question, request_header):
    header = DNSPacket.Header.unpack(data[0:11])

    if header.FLAGS.RA == 0b0: # since we always want recursion
        print_error("Unexpected response: DNS Server does not support recursive queries")
        raise DNSClientException()
    else:
        print("DNS Server supports recursive querries. \n")

    if header.FLAGS.RCODE == 1:
        print_error("Format error: the name server was unable to interpret the query")
        raise DNSClientException()
    elif header.FLAGS.RCODE == 2:
        print_error("Server failure: the name server was unable to process this query due to a problem with the name server")
        raise DNSClientException()
    elif header.FLAGS.RCODE == 3:
        print("NOT FOUND Name error: meaningful only for responses from an authoritative name server, this code signifies that the domain name referenced in the query does not exist")
        raise DNSClientException()
    elif header.FLAGS.RCODE == 4:
        print_error("Not implemented: the name server does not support the requested kind of query")
        raise DNSClientException()
    elif header.FLAGS.RCODE == 5:
        print_error("Refused: the name server refuses to perform the requested operation for policy reasons")
        raise DNSClientException()

    if "{:02x} {:02x}".format(header.ID[0], header.ID[1]) != request_header.__str__()[:5]:
        print_error("Unexpected response: Request ID and Response ID do not match.")
        raise DNSClientException()

    authorityBit = header.FLAGS.AA
    
    numQuestions = int("{:02x}{:02x}".format(header.QDCOUNT[0],header.QDCOUNT[1]), 16) # number of questions

    if numQuestions != 1 :
        print_error("Unexpected response: expecting 1 question from DNS Server but received {}".format(numQuestions))
        raise DNSClientException()

    # Counts bytes taken by all questions
    pointer = DNSPacket.Question.unpack(numQuestions, question)
    
    numAnswers = int("{:02x}{:02x}".format(header.ANCOUNT[0],header.ANCOUNT[1]), 16) # number of answers

    print(f"*** Answers Section ({numAnswers} records) ***\n")
    
    aCounter = 0

    allAnswers = []
    while aCounter < numAnswers:
        # Finds byte after 'NAME' field in response

        starting_pointer = pointer
        
        while True:
            # Checks if we hit ending byte '0' and pointer to location after accordingly
            if (data[pointer] == 0):
                pointer += 1
                break;
            
            if ((data[pointer] & 0xC0) == 0xC0): # since labels are 63 octets long
                pointer += 2
                break;

            pointer += 1

        try:
            answer, pointer = DNSPacket.Answer.unpack(data, data[pointer-starting_pointer], pointer)
        except DNSClientException:
            raise DNSClientException() # persist exception

        if answer == None:
            print_error("Unexpected response: invalid DNS Packet Type Received")
            raise DNSClientException()
        else:
            allAnswers.append(answer)
        aCounter += 1
        
    return (allAnswers, authorityBit, pointer)

def print_error(message):
    print("ERROR \t {}".format(message))

def main(args):
    if args.server.replace("@","").count('.') != 3 or re.search("[a-zA-Z]", args.server.replace("@","")): # a.b.c.d format and regex for no alpha
        print_error("Invalid DNS server provided. The server should only contain numbers, 3 periods (.), and @ symbol.")
        return 0

    for octet in args.server.replace("@","").split("."):
        if int(octet) > 255:
            print_error("Invalid DNS server provided. IPV4 octets cannot exceed 255.")
            return 0

    if args.mx:
        requestType = "MX"
    elif args.ns:
        requestType = "NS"
    else:
        requestType = "A"

    flags = DNSPacket.Header.Flags.get_request_flags(0b0)  # how to handle truncating ?
    header = DNSPacket.Header.get_request_header(flags)
    question = DNSPacket.Question.get_request_question(args.name, requestType)

    dnsPacket = DNSPacket(header, question, answer=None)

    retries = 0
    response_received = False

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(args.t)
    s.connect((args.server.replace("@",''), args.p))

    while not response_received:

        print(f"DnsClient sending request for [{dnsPacket.question.QNAME}] \nServer: [{args.server.replace('@','')}] \nRequest type: [{dnsPacket.get_q_type(dnsPacket.question.QTYPE)}]\n")

        startTime = time.time()
        s.send(bytes.fromhex(dnsPacket.__str__()))

        try:
            while True:
                data = s.recv(1024)
                endTime = time.time()
                responseTime = endTime - startTime

                print(f"Response received after {responseTime} seconds ({retries} retries)\n")

                if data is not None:
                    try:
                        answers, authorityBit, pointer = get_response_information(data, question, header)
                    except DNSClientException:
                        return 0

                    for answer in answers:
                        print(answer.__str__(authorityBit))

                    additionalRecords = data[10] << 8 | data[11]
                    if (additionalRecords > 0):
                        get_additional_information(data, pointer, additionalRecords)
                    else:
                        print("NOT FOUND\n")

                response_received = True
                break
        except socket.error:
            if retries >= args.r:
                print_error("Maximum number of retries exceeded: {}".format(args.r))
                return 0

            retries += 1
            continue
    return 1



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='DNS Client')
    group = parser.add_mutually_exclusive_group()
    parser.add_argument('-t', type=int, help='Timeout, in seconds, before retransmitting an unanswered query',
                        default=5)
    parser.add_argument('-r', type=int,
                        help='Maximum number of times to retransmit an unanswered query before giving up', default=3)
    parser.add_argument('-p', type=int, help='UDP port number of the DNS server', default=53)
    group.add_argument('-mx', action='store_true', help='Send a MX (mail server) query')  # string
    group.add_argument('-ns', action='store_true', help='Send a NS (name server) query')  # string
    parser.add_argument('server', help='IPv4 address of the DNS server, in a.b.c.d format')  # string
    parser.add_argument('name', help='Domain name to query for')  # string

    main(args=parser.parse_args())
