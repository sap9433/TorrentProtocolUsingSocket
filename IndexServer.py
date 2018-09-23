import socket
import random

BUFFER_SIZE = 1024
INDEX_SERVER_IP='localhost'
INDEX_SERVER_PORT=1024 # Yes,Thats the lowest port for common use :)

# Dictionary (Key, Val pair), key is string fileName, value is a set having string host|peerid|port
fileLocations ={'onekb.txt': {'localhost|peer1|1025'}}

if __name__ == '__main__':
    tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    tcpsock.bind((INDEX_SERVER_IP, INDEX_SERVER_PORT))
    threads = []
    while True:
        tcpsock.listen(5)
        print('\n Waiting patiently for search queries')
        (conn, (clientip,clientport)) = tcpsock.accept()
        # Request have a fixed protocol get|filename or set|filename|host|port
        requestedProtocol = (conn.recv(BUFFER_SIZE)).decode()
        [verb, filename ] = requestedProtocol.split('|')[0:2]
        if verb == 'get': #This Block serves file search queries
            fileLocation = 'notfound'
            if filename in fileLocations:
                fileLocation = random.sample(fileLocations[filename],1)[0] # Static Load-balancer. Randomly selecting peer.
            print(fileLocation)
            conn.send(str.encode(fileLocation))
            conn.close()
            print("Sent serach result to  - ", (clientip, str(clientport), filename, fileLocation))
        else: #This Block serves Index server update queries
            [filename, host, peerid, port] = requestedProtocol.split('|')[1:]
            existingList = fileLocations[filename]
            setEntry = host + '|' + peerid + '|' + port
            if existingList:
                existingList.add(setEntry)
            else:
                fileLocations[filename] = {setEntry}
            conn.send(b'Successfully Updated')
            conn.close()
            print("Updated index  - ", (clientip, str(clientport), filename, fileLocation))

