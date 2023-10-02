# ECSE 316 DNS Client Assignment Report

## Design

We have decided to split our design into two top-level classes while trying to follow an OOP standard: **DnsPacket** and **Parser**. Error handling has implemented all throughout these classes and method. We also decided to use the `argparse` library and `socket` library to parse arguments coming from the CLI and establish a UDP socket connection with the DNS Servers (respectively).

### DNSPacket

The first class is DnsPacket and it contains sub-classes Header, Question, Answer, Authority, and Additional Information; All representing the components of a DnsPacket. All the subclasses contain their own string representations which help to construct their respective segments.
#### Header

The Header sub-class contains instance variables such as the ID, QDCOUNT, ANCOUNT, NSCOUNT, and ARCOUNT. Additionally, it contains another sub-class called Flags which is also used as an instance variable.
##### Flags

The Flags sub-class contains instance variables such as QR, Opcode, AA, TC, RD, RA, Z, RCODE. It contains and initializer method which helps to construct the Flags class and it also had a helper method called unpack which can be used to demarshal the flags of an incoming response DNS Packet.
### Question

The Question sub-class contains information about the question being asked in the DNS packet. In particular it contains the instance variables: QNAME, QTYPE, and QCLASS.
### Answer

The Answer sub-class contains information about the answer to the question in the DNS packet. It is not used so much in the construction of the DNS request packet but it contains helpful methods for the demarshalling of the DNS response packet.

### Authority

The Authority sub-class contains instance variables specific to the authority but nothing related to the construction of the authority section of a DNS packet because we are not implementing it in this assignment. Instead, it contains functions responsible for demarshaling the authority section of an incoming DNS response packet.
### Additional

Similar to the Authority sub-class it only contains methods and instance variables related to demarshaling a DNS response packet.

### Parser
The Parser class contains the initialization of the argument parser for the command line interface (CLI). The argument parser is responsible for parsing the arguments passed to the CLI and converting them into a format that can be used by your program. The Parser class provides the CLI with arguments such as domain names, IP addresses, query type, and more.

### Helper Functions

Additionally, there are some global helper functions that are used throughout the class so specifying at the top-level of the file is beneficial.

### Main

Lastly, we have our top-level main method which is responsible for wiring everything together. It is responsible for intializing a UDP connection to the DNS server of the users choice, construsting a DNS request packet using the appropriate arguments from the parser and DnsPacket class, sending that packet while also waiting for a response and demarshaling it.

## Testing

In order to test our implementation we utilized the `unittest` library and created a test suit library called dnsClientTestSuite.py. 

We wrote test cases related to the construction of DNS packets, marshalling and unmarshalling data, timeouts and response times of sending/receiving packets over a UDP socket, along with testing our dns clients error handling.

We achieved this by creating a series of functions and either using example data provided in the outline of the assignment or personal mock data and created various assertions that would make the function succeed or fail. More specifically we were able to test the timeouts and response times of our client by "mocking" the arguments a user would have passed in the console in the form of a class called `TestParser` and running our client with the arguments and checking return result along with the runtime of our client.

## Environment / Libraries Used

### dnsClient.py

In the dnsClient we used 6 different libraries: socket, random, argparse, time, re.

The socket library and argparse library were the foundation of our dnsClient, providing the creation and connection to a socket and the arguments needed to construct the CLI (respectively). 

The random library was used to produce random 16 bit integers for the ids of the request packet.

The time library was used in order to keep track of timeouts.

The re library was used to validate the server provided in the arguments and assuring it does not contain invalid characters.

### dnsClientTestSuite.py

In the dnsClientTestSuite we use 3 different libraries: time, dnsClient, and unittest.

The unittest library gives us the capability to write assertions in order to test our code.

The time library is used to assess the timeout is correctly implemented.

Lastly, we import the dnsClient we worked on and call its main method in order to test its output.

## Error Handling

In order to ensure our DNS Client works properly we created various error checks accross our implementation. In order to facilitate catching some of these exceptions from nested functions we also created a custom exception called DNSClientException which we could "raise" from within an inner function and catch in its parent function. This allows us to change the context of the program running while being rest assured we are catching self-invoked errors.

Some of the notable error checks we have are the following:

- Checking to see if the server name follows an "a.b.c.d" format; That is 4 octets of value less than 256 and integers.
- Checking to see if the id of the request packet matches that of the response packet.
- Checking to see if the amount of retries has exceeded or the timeout has exceeded.
- Checking to see if the number of questions in the answer matches the number of questions sent in the request.
- Checking to see if the response's rcode contains an unexpected value.
- Checking to see if the DNS server accepts recursive querries.
## Experiment

> What are the IP addresses of McGill’s DNS servers? Use the Google public DNS server (8.8.8.8) to perform a NS query for mcgill.ca and any subsequent follow-up queries that may be required. What response do you get? Does this match what you expected?


> Use your client to run DNS queries for 5 different website addresses, of your choice, in addition to www.google.com and www.amazon.com, for a total of seven addresses. Query the seven addresses using the Google public DNS server (8.8.8.8).

> Briefly explain what a DNS server does and how a query is carried out. Modern web browsers are designed to cache DNS records for a set amount of time. Explain how caching DNS records can speed up the process of resolving an IP address. You can draw a diagram to help clarify your answer.

The main responsibility of a DNS server is to resolve host names to ip addresses so user querries in the form of requests can be resolved. Moreover DNS is meant to act s a distributed database in which its servers (who implement an application-layer protocol) all contribute to the goal of name resolution.

Caching DNS records can limit the overhead placed on DNS servers and resolve user queries more quickly by limiting round trip time. Instead of a DNS Server('s) having to spend resources on resolving the request our browser can use a previously resolved request (for the same ip address) and do it for us. 