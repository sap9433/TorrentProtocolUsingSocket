import socket
from threading import Thread
import sys
import os

INDEX_SERVER_IP='localhost'
INDEX_SERVER_PORT=1024 #Yes , thats the lowest port for common use :)
BUFFER_SIZE = 4096

class ServerModule(Thread):
    def __init__(self,peerId,sock, fileName):
        Thread.__init__(self)
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
        print('\n Waiting patiently for new download requests')
        (conn, (clientip,clientport)) = tcpsock.accept()
        # Accepted connection now First recieve the filename to be sent
        # connection.recv recives butes. We need to decode it to String.
        fileName = (conn.recv(BUFFER_SIZE)).decode()
        print ('Recieved file request from ', (clientip, clientport))
        newthread = ServerModule(peerId, conn, fileName)
        newthread.start()
        threads.append(newthread)
        print("New sender started for client - ", (clientip, str(clientport), fileName))

    for t in threads:
        t.join()

def fetchLocationFromIndexServer(filename):
    sockt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sockt.connect((INDEX_SERVER_IP, INDEX_SERVER_PORT))
    sockt.sendall(str.encode('get|'+filename)) #This is the protocol Index server understands. get|Filename
    filepath = (sockt.recv(BUFFER_SIZE)).decode()
    return filepath.split('|') if not filepath == 'notfound' else False

def clientModule(peerId):
    while True:
        filename = input("\n ## Please input file name with extension. Or exit() to close.\n")
        if filename == 'exit()':
            break
        #elif os.path.isfile('./' + peerId + '/' + filename):
         #   print(filename + ' Already exists for this peer. No need to download from remote \n')
            #continue
        else:
            indexServerResponse = fetchLocationFromIndexServer(filename)
            if not indexServerResponse:
                print('\n Sorry file can not be found in any of the peer')
                continue
            [serverip, serverpeerid, serverport] = indexServerResponse
            sockt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sockt.connect((serverip, int(serverport)))
            sockt.sendall(str.encode('./' + serverpeerid + '/' + filename))

            with open('./' + peerId + '/copyof_' + filename, 'wb') as f:
                while True:
                    print('receiving data...')
                    data = sockt.recv(BUFFER_SIZE)
                    if not data:
                        f.close()
                        break
                    f.write(data) # Store data to a file.
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