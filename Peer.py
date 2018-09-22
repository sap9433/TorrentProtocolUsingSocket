import socket
from threading import Thread
from multiprocessing import Process
import os

TCP_IP = 'localhost'
TCP_PORT = 9001
BUFFER_SIZE = 1024

class ServerModule(Thread):
    def __init__(self,ip,port,sock, fileName):
        Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.sock = sock
        self.fileName = fileName
        print ("New sender started for client - ",(ip,str(port),fileName))

    def run(self):
        filetobesent = open(self.fileName,'rb')
        while True:
            filepart = filetobesent.read(BUFFER_SIZE)
            while (filepart):
                self.sock.send(filepart)
                filepart = filetobesent.read(BUFFER_SIZE)
            if not filepart:
                filetobesent.close()
                self.sock.close()
                print('\n Successfully sent - ' + self.fileName + '\n \n')
                break

def receiveConnection():
    tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    tcpsock.bind((TCP_IP, TCP_PORT))
    threads = []

    while True:
        tcpsock.listen(5)
        print ("\nWaiting for peers to request file\n")
        (conn, (ip,port)) = tcpsock.accept()
        # Accepted connection now First recieve the filename to be sent
        fileName = conn.recv(1024)
        # connection.recv recives butes. We need to decode it to String.
        fileName = fileName.decode()
        print ('Recieved file request from ', (ip,port,fileName))
        newthread = ServerModule(ip, port, conn, fileName)
        newthread.start()
        threads.append(newthread)

    for t in threads:
        t.join()

def clientModule(clientId):
    TCP_IP = 'localhost'
    TCP_PORT = 9001
    BUFFER_SIZE = 1024

    while True:
        fileName = input("\n\n Please input file name with extension. Or exit() to close.\n\n")
        fullPath = './' + clientId + '/' + fileName
        if fileName == 'exit()':
            break
        if os.path.isfile(fullPath):
            print(fileName + ' Already exists for this peer. No need to download from remote \n')
            #continue
        sockt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sockt.connect((TCP_IP, TCP_PORT))
        sockt.sendall(str.encode(fullPath))

        with open('./' + clientId + '/copyof_' + fileName, 'wb') as f:
            print
            'file opened'
            while True:
                print('receiving data...')
                data = sockt.recv(BUFFER_SIZE)
                if not data:
                    f.close()
                    print('file closed')
                    break
                # write data to a file
                f.write(data)
        print('\n \n Successfully received entire file \n \n')
        # Sockt Close only doesn't ensure immediate release of file desc, hence Shutdown
        sockt.shutdown(socket.SHUT_WR)
        sockt.close()
        print('\n \n Client closed connection \n \n')
    print('Client Exited')

if __name__ == '__main__':
    if 0:
        receiveConnection()
    if 1:
        clientModule(clientId='peer1')