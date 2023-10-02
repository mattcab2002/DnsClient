import unittest
import time
from dnsClient import main

class TestParser():
    
    def __init__(self, server, name, port=53, timeout=5, retries=3, type="A", mx = False, ns = False):
        self.server = server
        self.name = name
        self.p = port
        self.t = timeout
        self.r = retries
        self.type = type
        self.mx = mx
        self.ns = ns

class TestConstructDNSRequestPacket(unittest.TestCase):

    def test_construct_flags(self):
        test_flags = dnsClient.DNSPacket.Header.Flags(0, 0, 0, 0, 1, 0, 0, 0)
        self.assertEqual(test_flags.__str__(), "{:016b}".format(0x0100))

    def test_construct_header(self):
        test_flags = dnsClient.DNSPacket.Header.Flags(0, 0, 0, 0, 1, 0, 0, 0)
        test_header = dnsClient.DNSPacket.Header(test_flags, 1, 0, 0, 0, 0x827a)
        self.assertEqual(test_header.__str__(), "82 7a 01 00 00 01 00 00 00 00 00 00")

    def test_construct_header_different_flags(self):
        test_flags = dnsClient.DNSPacket.Header.Flags(0, 0, 1, 0, 1, 0, 0, 0)
        test_header = dnsClient.DNSPacket.Header(test_flags, 1, 0, 0, 0, 0x827a)
        self.assertEqual(test_header.__str__(), "82 7a {} {} 00 01 00 00 00 00 00 00".format("{:02x}".format(0b00000101), "{:02x}".format(0b0)))

    def test_construct_header_with_random_id(self):
        test_flags = dnsClient.DNSPacket.Header.Flags(0, 0, 0, 0, 1, 0, 0, 0)
        test_header = dnsClient.DNSPacket.Header(test_flags, 1, 0, 0, 0, 0x827a)
        self.assertEqual(test_header.__str__()[6:], "01 00 00 01 00 00 00 00 00 00")
        self.assertNotEqual(test_header.__str__()[:6], "")

    def test_construct_question(self):
        test_question = dnsClient.DNSPacket.Question("www.mcgill.ca", 1, 1)
        self.assertEqual(test_question.__str__(), "03 77 77 77 06 6d 63 67 69 6c 6c 02 63 61 00 00 01 00 01")

    def test_construct_request_packet(self):
        test_flags = dnsClient.DNSPacket.Header.Flags(0, 0, 0, 0, 1, 0, 0, 0)
        test_header = dnsClient.DNSPacket.Header(test_flags, 1, 0, 0, 0, 0x827a)
        test_question = dnsClient.DNSPacket.Question("www.mcgill.ca", 1, 1)
        test_request_packet = dnsClient.DNSPacket(test_header, test_question, None)
        self.assertEqual(test_request_packet.__str__(), "82 7a 01 00 00 01 00 00 00 00 00 00 03 77 77 77 06 6d 63 67 69 6c 6c 02 63 61 00 00 01 00 01")

    def test_dns_response_to_mcgill_using_google(self):
        self.assertNotEqual(main(TestParser("8.8.8.8","mcgill.ca")), 0) # indicated an error
        self.assertEqual(main(TestParser("8.8.8.8","mcgill.ca")), 1) # exits cleanly

    def test_timeout_and_retry_fail(self):
        startTime = time.time()
        self.assertEqual(main(TestParser("255.255.255.255","mcgill.ca")), 0) # indicated an error
        self.assertTrue(time.time() - startTime > 15)
    
if __name__ == '__main__':
    unittest.main()