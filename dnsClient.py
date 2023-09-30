import socket
import random


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

        def __init__(self, FLAGS, QDCOUNT, ANCOUNT, NSCOUNT, ARCOUNT):
            self.ID = random.getrandbits(16)
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
                return "{:01b}{:04b}{:01b}{:01b}{:01b}{:01b}{:03b}{:04b}".format(self.QR, self.OPCODE, self.AA, self.TC, self.RD, self.RA, self.Z, self.RCODE)

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
                return_string += "{:02x}".format(len(label))
                for ch in label:
                    return_string += "{}".format(hex(ord(ch))[2:])
            return_string += "{:02x}".format(0)  # indicating end of QNAME
            return_string += "{:04x}".format(self.QTYPE)
            return_string += "{:04x}".format(self.QCLASS)
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

def main():
    server = "8.8.8.8"
    port = 53
    name = "www.mcgill.ca"
    query_type = "A"
    flags = DNSPacket.Header.Flags.get_request_flags(0b0)  # how to handle truncating ?
    header = DNSPacket.Header.get_request_header(flags)
    question = DNSPacket.Question.get_request_question(name, query_type)

    dnsPacket = DNSPacket(header, question, answer=None)

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect((server, port))

    print(f"DnsClient sending request for [{dnsPacket.question.QNAME}] \nServer: [{server}] \nRequest type: [{dnsPacket.question.QTYPE}]\n")

    s.send(bytes.fromhex(dnsPacket.__str__()))

    try:
        while True:
            data = s.recv(1024)
            if data is not None:
                print("Received Data!")
                print(data)
    except KeyboardInterrupt:
        pass
    finally:
        s.close()


if __name__ == "__main__":
    main()