import socket
from threading import Thread
import sys
import os

BUFFER_SIZE = 4096

class ServerModule(Thread):
    def __init__(self,peerId, ip, port, sock, fileName):
        Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.sock = sock
        self.fileName = fileName

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
                print('\n ## Successfully sent - ' + self.fileName)
                break

def receiveConnection(peerId, ip, port):
    tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    tcpsock.bind((ip, port))
    threads = []

    while True:
        tcpsock.listen(5)
        (conn, (clientip,clientport)) = tcpsock.accept()
        # Accepted connection now First recieve the filename to be sent
        # connection.recv recives butes. We need to decode it to String.
        fileName = (conn.recv(1024)).decode()
        print ('Recieved file request from ', (clientip, clientport))
        newthread = ServerModule(peerId, ip, port, conn, fileName)
        newthread.start()
        threads.append(newthread)
        print("New sender started for client - ", (clientip, str(clientport), fileName))

    for t in threads:
        t.join()

def clientModule(peerId):
    TCP_IP = 'localhost'
    TCP_PORT = 9001
    BUFFER_SIZE = 4096

    while True:
        fileName = input("\n ## Please input file name with extension. Or exit() to close.\n")
        fullPath = './' + peerId + '/' + fileName
        if fileName == 'exit()':
            break
        if os.path.isfile(fullPath):
            print(fileName + ' Already exists for this peer. No need to download from remote \n')
            #continue
        sockt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sockt.connect((TCP_IP, TCP_PORT))
        sockt.sendall(str.encode(fullPath))

        with open('./' + peerId + '/copyof_' + fileName, 'wb') as f:
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
        print('\nSuccessfully received entire file')
        # Sockt Close only doesn't ensure immediate release of file desc, hence Shutdown
        sockt.shutdown(socket.SHUT_WR)
        sockt.close()
        print('\n \n Client closed connection')
    print('Client Exited')

if __name__ == '__main__':
    try: [module, peerId, ip, port ] = sys.argv[1:]
    except: pass # Client takes 1 argument so to avoid unpacking error
    if module == 'server':
        receiveConnection(peerId, ip, int(port))
    if module == 'client':
        clientModule(peerId)