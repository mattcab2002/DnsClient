import argparse

parser = argparse.ArgumentParser(description='DNS Client')
group = parser.add_mutually_exclusive_group()
parser.add_argument('-t', type = int, help = 'Timeout, in seconds, before retransmitting an unanswered query', default = 5)
parser.add_argument('-r', type = int, help = 'Maximum number of times to retransmit an unanswered query before giving up', default = 3)
parser.add_argument('-p', type = int, help = 'UDP port number of the DNS server', default = 53)
group.add_argument('-mx', action = 'store_true', help = 'Send a MX (mail server) query')    # string
group.add_argument('-ns', action = 'store_true', help = 'Send a NS (name server) query')    # string
parser.add_argument('server', help = 'IPv4 address of the DNS server, in a.b.c.d format') # string
parser.add_argument('name', help = 'Domain name to query for') # string

args = parser.parse_args()
