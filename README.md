## Environment / Libraries Used

### dnsClient.py

In the dnsClient we used 5 different libraries: socket, random, argparse, time, re.

The socket library and argparse library were the foundation of our dnsClient, providing the creation and connection to a socket and the arguments needed to construct the CLI (respectively). 

The random library was used to produce random 16 bit integers for the ids of the request packet.

The time library was used in order to keep track of timeouts.

The re library was used to validate the server provided in the arguments and assure that it did not contain invalid characters.

### dnsClientTestSuite.py

In the dnsClientTestSuite we use 3 different libraries: time, dnsClient, and unittest.

The unittest library gives us the capability to write assertions in order to test our code.

The time library is used to assess the timeout is correctly implemented.

Lastly, we import the dnsClient we worked on and call its main method in order to test its output.

## Python Version Used
Python 3.11.4
