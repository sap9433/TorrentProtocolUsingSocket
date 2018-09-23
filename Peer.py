import socket
from threading import Thread
import sys
import glob
import os

INDEX_SERVER_IP='localhost'
INDEX_SERVER_PORT=1024 #Yes , thats the lowest port for common use :)
BUFFER_SIZE = 4096

class ServerModule(Thread):
    def __init__(self,peerId,sock, fileName):
        Thread.__init__(self)
        self.sock = sock
        self.fileName = fileName
        self.peerId = peerId

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
    # Server started. One time ops. Update all files to index server
    print('\n Server started. One time ops. Update all files to index server')
    for file in next(os.walk('./' + peerId + '/'))[2]: #glob.glob('./' + peerId + '/*'):
        talkToIndexServer(file, 'set', ip, peerId, port)

    print('\n Index server Updation complete')

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
        # Server started. One time ops. Update all files to index server

    for t in threads:
        t.join()

def talkToIndexServer(filename, verb,host,peerid,port):
    sockt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sockt.connect((INDEX_SERVER_IP, INDEX_SERVER_PORT))
    if verb == 'get':
        sockt.sendall(str.encode('get|'+filename)) #Protocol Index server understands. get|Filename
    else:
        # Protocol Index server understands. set|Filename|host|peerid|port
        sockt.sendall(str.encode('set|' + filename + '|' + host + '|' + peerid + '|'+ str(port)))
    filepath = (sockt.recv(BUFFER_SIZE)).decode()
    return filepath.split('|') if not filepath == 'notfound' else False

def clientModule(peerId,ip,port):
    while True:
        filename = input("\n ## Please input file name with extension. Or exit() to close.\n")
        if filename == 'exit()':
            break
        elif os.path.isfile('./' + peerId + '/' + filename):
           print(filename + ' Already exists for this peer. No need to download from remote \n')
           continue
        else:
            indexServerResponse = talkToIndexServer(filename, 'get', None, None, None)
            if not indexServerResponse:
                print('\n Sorry file can not be found in any of the peer')
                continue
            [serverip, serverpeerid, serverport] = indexServerResponse
            sockt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sockt.connect((serverip, int(serverport)))
            sockt.sendall(str.encode('./' + serverpeerid + '/' + filename))

            with open('./' + peerId + '/' + filename, 'wb') as f:
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
            print('\n Client closed connection. Now updating index server')
            talkToIndexServer(filename, 'set', ip, peerId, port)
    print('Client Exited')

if __name__ == '__main__':
    try: [module, peerId, ip, port ] = sys.argv[1:]
    except: pass # Client takes 1 argument so to avoid unpacking error
    if module == 'server':
        receiveConnection(peerId, ip, int(port))
    if module == 'client':
        clientModule(peerId,ip, int(port))