import unittest
import dnsClient

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
    
if __name__ == '__main__':
    unittest.main()