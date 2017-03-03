import socket
import sys
import time

TCP_IP = '127.0.0.1'
TCP_PORT = 5102
BUFFER_SIZE = 1024

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Bind the socket to the port
print >>sys.stderr, 'Starting up server on %s port %s' % (TCP_IP,TCP_PORT)


def start_daq(daq_options,server_socket):
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Connect the socket to the port where the server is listening

    server_address = ('192.168.0.248', 51010)
    print >>sys.stderr, 'connecting to %s port %s' % server_address
    sock.connect(server_address)
    try:
        # Send data
        message = 'python daq_continous_2MPA.py '+str(daq_options)+'\n'
        #print >>sys.stderr, 'sending "%s"' % message
        sock.sendall(message)
        # Look for the response
        while True:
            data = sock.recv(4096)
            #time.sleep(.1)
            if len(data)>0:
                if "\n" in data:
                    print "End of Run "
                    print data.rstrip("\n")
                    with open("DAQ_LOG.csv", "a") as myfile:
                        myfile.write(data)
                    break
                print >>sys.stderr, '%s' % data
    finally:
        #print >>sys.stderr, 'closing socket'
        sock.close()
lines = [line.rstrip('\n') for line in open('options.csv')]
for line in lines:
    #print line
    start_daq(line,s)
