import socket
from threading import Thread
from multiprocessing import Process


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
        print (" New thread started for "+ip+":"+str(port))

    def run(self):
        f = open(self.fileName,'rb')
        while True:
            l = f.read(BUFFER_SIZE)
            while (l):
                self.sock.send(l)
                l = f.read(BUFFER_SIZE)
            if not l:
                f.close()
                self.sock.close()
                break

def receiveConnection():
    tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    tcpsock.bind((TCP_IP, TCP_PORT))
    threads = []

    while True:
        tcpsock.listen(5)
        print ("Waiting for peers to request file")
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

def clientModule(clientId, fileName):
    TCP_IP = 'localhost'
    TCP_PORT = 9001
    BUFFER_SIZE = 1024

    sockt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sockt.connect((TCP_IP, TCP_PORT))
    sockt.sendall(str.encode('./'+clientId+'/'+fileName))
    with open('./' + clientId + '/copyof_' + fileName, 'wb') as f:
        print
        'file opened'
        while True:
            print('receiving data...')
            data = sockt.recv(BUFFER_SIZE)
            print('data=%s', (data))
            if not data:
                f.close()
                print
                'file close()'
                break
            # write data to a file
            f.write(data)

    print('Successfully get the file')
    sockt.close()
    print('connection closed')


def startConnectionReceiver():
    serverProcess = Process(target=receiveConnection)
    serverProcess.start()
    serverProcess.join() 

def startClient(clientId, fileName):
    clientProcess = Process(target=clientModule, args=(clientId, fileName, ))
    clientProcess.start()
    clientProcess.join()

if __name__ == '__main__':
    if 0:
        startConnectionReceiver()
    if 1:
        startClient(clientId='peer1', fileName = 'onekb.txt')