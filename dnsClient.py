import socket
import random
import argparse
import time
import struct


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

        @staticmethod
        def unpack(self, incoming_response_header):
            return self(incoming_response_header)

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
            return cls(QNAME, cls.get_q_type(QTYPE.upper()), QCLASS)

        @staticmethod
        def get_q_type(qtype_string: str) -> int:
            if qtype_string == "A":
                return 0x0001
            if qtype_string == "NS":
                return 0x0002
            if qtype_string == "MX":
                return 0x000f

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

        class RDATA:
            def __init__(self, TYPE, DATA, PREFERENCE, EXCHANGE=0):
                self.DATA = DATA

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
    print(f"THIS IS THE TTL IN SECONDS : {ttl}\n")
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
            print(f"VALUE AT THE {pointer} BYTE : {data[pointer]}\n")
            # Checks if we hit ending byte '0' and pointer to location after accordingly
            if (data[pointer] == 0):
                print(f"ZERO BYTE FOUND AT : {pointer}\n")
                pointer += 1
                break;
            
            if ((data[pointer] & 0xC0) == 0xC0):
                print(f"POINTER FOUND AT : {pointer}\n")
                pointer += 2
                break;

            pointer += 1

        aCounter += 1
        
        # Check type
        print(f'THIS IS THE START OF THE TYPE SECTION : {pointer}\n')
        type = data[pointer] << 8 | data[pointer + 1]
        print(f"THIS IS THE TYPE: {type} \n")
        pointer += 4    # Beginning of TTL bytes
        match type:
            case 5:
                print("THIS IS THE START OF THE CNAME SECTION\n")
                print(f"THIS IS THE START OF THE TTL SECTION : {pointer}\n")
                ttl = getTTL(data, pointer)
                pointer += 4    # Beginning of the RDLength
                print(f"THIS IS THE START OF THE RDLENGTH SECTION : {pointer}\n")
                rdlength = data[pointer] << 8 | data[pointer + 1]
                print(f"THIS IS THE LENGTH OF RDATA IN BYTES : {rdlength}\n")
                pointer += 2    # Beginning of RData
                print(f"THIS IS THE START OF THE RDATA SECTION : {pointer}\n")
                alias = get_alias(data, pointer)
                pointer += rdlength ## Beginning of next answer
                print(f"CNAME \t {alias} \t {ttl} \t {authorityBit}\n")
            case 1:
                print("THIS IS THE START OF THE IP SECTION\n")
                ttl = getTTL(data, pointer)
                pointer += 6 # go straight to RData
                ip = get_ip_address(data, pointer)
                pointer +=4 # Beginning of next answer
                print(f"IP \t {ip} \t {ttl} \t { authorityBit}\n")
            case 2:
                print("THIS IS THE START OF THE NAME SERVER SECTION\n")
                ttl = getTTL(data, pointer)
                pointer += 4
                rdlength = data[pointer] << 8 | data[pointer + 1]
                pointer += 2
                alias = get_alias(data,pointer)
                pointer += rdlength
                print(f"NS \t {alias} \t {ttl} \t {authorityBit}\n")
            case 15:
                print("THIS IS THE START OF THE MAIL SERVER SECTION\n")
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



def get_response_information(data, question):
    authorityBit = (data[2] & 32) >> 5

    numQuestions = (data[4] << 8) | data[5] # number of questions
    qCounter = 0
    pointer = 12    # starts at 12 because of 12 byte header
    print(f"THIS IS THE NUMBER OF QUESTIONS : {numQuestions}\n")

    # Counts bytes taken by all questions
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
    
    numAnswers = (data[6] << 8) | data[7]  # takes answer bytes into integer
    print(f"*** Answers Section ({numAnswers} records) ***\n")
    aCounter = 0

    # makes sure we start at the beginning of the byte sequence
    print(f'THIS IS THE CURRENT START OF THE ANSWER SECTION : {pointer}\n')
    # Iterates through response records
    while aCounter < numAnswers:
        # Finds byte after 'NAME' field in response

        while True:
            print(f"VALUE AT THE {pointer} BYTE : {data[pointer]}\n")
            # Checks if we hit ending byte '0' and pointer to location after accordingly
            if (data[pointer] == 0):
                print(f"ZERO BYTE FOUND AT : {pointer}\n")
                pointer += 1
                break;
            
            if ((data[pointer] & 0xC0) == 0xC0):
                print(f"POINTER FOUND AT : {pointer}\n")
                pointer += 2
                break;

            pointer += 1

        aCounter += 1
        
        # Check type
        print(f'THIS IS THE START OF THE TYPE SECTION : {pointer}\n')
        type = data[pointer] << 8 | data[pointer + 1]
        print(f"THIS IS THE TYPE: {type} \n")
        pointer += 4    # Beginning of TTL bytes
        match type:
            case 5:
                print("THIS IS THE START OF THE CNAME SECTION\n")
                print(f"THIS IS THE START OF THE TTL SECTION : {pointer}\n")
                ttl = getTTL(data, pointer)
                pointer += 4    # Beginning of the RDLength
                print(f"THIS IS THE START OF THE RDLENGTH SECTION : {pointer}\n")
                rdlength = data[pointer] << 8 | data[pointer + 1]
                print(f"THIS IS THE LENGTH OF RDATA IN BYTES : {rdlength}\n")
                pointer += 2    # Beginning of RData
                print(f"THIS IS THE START OF THE RDATA SECTION : {pointer}\n")
                alias = get_alias(data, pointer)
                pointer += rdlength ## Beginning of next answer
                print(f"CNAME \t {alias} \t {ttl} \t {authorityBit}\n")
            case 1:
                print("THIS IS THE START OF THE IP SECTION\n")
                ttl = getTTL(data, pointer)
                pointer += 6 # go straight to RData
                ip = get_ip_address(data, pointer)
                pointer +=4 # Beginning of next answer
                print(f"IP \t {ip} \t {ttl} \t { authorityBit}\n")
            case 2:
                print("THIS IS THE START OF THE NAME SERVER SECTION\n")
                ttl = getTTL(data, pointer)
                pointer += 4
                rdlength = data[pointer] << 8 | data[pointer + 1]
                pointer += 2
                alias = get_alias(data,pointer)
                pointer += rdlength
                print(f"NS \t {alias} \t {ttl} \t {authorityBit}\n")
            case 15:
                print("THIS IS THE START OF THE MAIL SERVER SECTION\n")
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


def main():
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

    args = parser.parse_args()

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
    print(dnsPacket)


    retries = 0
    while retries <= args.r:

        try:

            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect((args.server, args.p))

            print(f"DnsClient sending request for [{dnsPacket.question.QNAME}] \nServer: [{args.server}] \nRequest type: [{dnsPacket.question.QTYPE}]\n")

            startTime = time.time()
            s.send(bytes.fromhex(dnsPacket.__str__()))
            try:
                while True:
                    data = s.recv(1024)
                    endTime = time.time()
                    responseTime = endTime - startTime
                    print(f"Response received after {responseTime} seconds ({retries} retries)\n")
                    if data is not None:
                        print("Received Data!")
                        print(data)
                        pointer = get_response_information(data, question)
                        additionalRecords = data[10] << 8 | data[11]
                        if (additionalRecords > 0):
                            get_additional_information(data, pointer, additionalRecords)
                        else:
                            print("NOT FOUND\n")

            except KeyboardInterrupt:
                pass
            finally:
                s.close()
                return
        except socket.error:
            retries += 1



if __name__ == "__main__":
    main()
