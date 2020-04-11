import socket
import threading
import re
import hashlib
import base64

def recv(client):
    print("hello\n\n")
    first_byte = bytearray(client.recv(1))[0]
    FIN = (0xFF & first_byte) >> 7
    opcode = (0x0F & first_byte)
    second_byte = bytearray(client.recv(1))[0]
    mask = (0xFF & second_byte) >> 7
    payload_len = (0x7F & second_byte)
    if opcode < 3:
        if (payload_len == 126):
            payload_len = struct.unpack_from('>H', bytearray(client.recv(2)))[0]
        elif (payload_len == 127):
            payload_len = struct.unpack_from('>Q', bytearray(client.recv(8)))[0]
        if mask == 1:
            masking_key = bytearray(client.recv(4))
        masked_data = bytearray(client.recv(payload_len))
        if mask == 1:
            data = [masked_data[i] ^ masking_key[i%4] for i in range(len(masked_data))]
        else:
            data = masked_data
    else:
        return opcode, bytearray(b'\x00')
    return opcode, bytearray(data)

def handshake(client):
    request = client.recv(2048)
    p=re.compile('Sec-WebSocket-Key: (.*)\\r')
    m = p.search(request.decode())

    print(request)
    
    key = m.group(1)+'258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
    #key = 'dGhlIHNhbXBsZSBub25jZQ=='+'258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
    h=hashlib.sha1()
    h.update(key.encode())

    print('\n')
    
    #sh1_key = hashlib.sha1().digest()
    base64_key = base64.b64encode(h.digest())
    #print(base64_key.decode())

    response = "HTTP/1.1 101 Switching Protocols\r\n"+\
           "Upgrade: websocket\r\n"+\
           "Connection: Upgrade\r\n"+\
           "Sec-WebSocket-Accept: %s\r\n"+\
           "\r\n"

    r = response % (base64_key.decode())
    print(r)
    client.send(r.encode())
    
def handle_client (client, addr):
    print('working\n')
    handshake(client)


def run_server(port):
    sock = socket.socket()
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('',port))
    sock.listen(5)
    
    

    while True:
        print('Waiting for connection on port' + str(port) + '...')
        client, addr = sock.accept()
        print('Connection from : ' + str(addr))
        threading.Thread(target = handle_client, args = (client, addr)).start()
    #msg = client.recv(1024)
    #print(f'{msg.decode()}')
    
    #print(msg.decode('utf-8'))
    #conn.send(b'{msg}')
    sock.close()

if __name__ == '__main__':
  run_server(9999)
