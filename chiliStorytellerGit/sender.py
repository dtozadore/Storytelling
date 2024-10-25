from multiprocessing.connection import Client

address = ('localhost', 6000)
conn = Client(address, authkey=b'secret password')

print("Node started!\n")
print("Send 'close' to finish session\n")

while True:
    entry = input("Type the message to be sent: ")
    
    conn.send(entry)
    
    if entry == 'close':
        break

conn.close()