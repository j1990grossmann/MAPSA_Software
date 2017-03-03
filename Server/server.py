import socket
import sys
import time
import subprocess

TCP_IP = '127.0.0.1'
TCP_PORT = 5101
BUFFER_SIZE = 1024

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Bind the socket to the port
print >>sys.stderr, 'Starting up server on %s port %s' % (TCP_IP,TCP_PORT)
try:
    s.bind((TCP_IP, TCP_PORT))
except socket.error, exc:
    print "Caught exception socket.error : %s" % exc
s.listen(1)
def recv_timeout():
    while True:
        # Wait for a connection
        print >>sys.stderr, 'waiting for a connection'
        connection, client_address = s.accept()
        connection.settimeout(.05)
        try:
            print >>sys.stderr, 'connection from', client_address
            # Receive the data in small chunks and retransmit it
            total_data=[]
            data=''
            timeout=1
            begin=time.time()
            recv_string=''
            while True:
                if total_data and time.time()-begin > timeout:
                    connection.sendall(recv_string)
                    connection.sendall("timeout after data")
                    break
                elif time.time()-begin > timeout*2:
                    connection.sendall("timeout no data received")
                    break
                check = recv_string.find('\n')
                if check!=(-1):
                    #print "found line ending shortened string reads:"
                    cmd="python daq_continous_2MPA.py"
                    cmdlend=len(cmd)
                    start_daq = recv_string[:check].find(cmd)
                    if start_daq > -1:
                        print "Starting DAQ with options"
                        options= recv_string[start_daq+cmdlend:check]
                        print options
                        connection.sendall("Starting DAQ with options\t")
                        connection.sendall(options)
                        error_daq = subprocess.check_call(["sleep","1"])
                        result=subprocess.check_output("ls -rt ../readout_data/", shell=True)
                        last=result.splitlines()[-1]
                        connection.sendall("Run Number\t" + last.rstrip('\n')+"\tDAQ state\t"+str(error_daq)+"\toptions"+options)
                        connection.sendall("\n")
                    break
                try:
                    data = connection.recv(64)
                    if data:
                        #print >>sys.stderr, 'received "%s"' % data
                        total_data.append(data)
                        begin=time.time()
                except:
                    print "timed out"
                recv_string=''.join(total_data)
        finally:
            #Clean up the connection
            connection.close()
recv_timeout()