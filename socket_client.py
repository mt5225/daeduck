# client.py  
import socket
import logging
import binascii

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
HOST = '127.0.0.1'               
PORT = 1470

if __name__ == '__main__':

    # create a socket object
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 

    # connection to hostname on the port.
    s.connect((HOST, PORT))                               

    # Receive no more than 1024 bytes
    buf = s.recv(1024)                                     

    s.close()
    data = binascii.hexlify(buf)
    logging.debug(data)
