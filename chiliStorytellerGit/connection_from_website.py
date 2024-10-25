from autobahn.twisted.component import Component, run
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.util import sleep
from multiprocessing.connection import Listener
import queue


import random


#Connection with the other node


print ('\n\nStarting... Waiting for conenction\n\n')
address = ('localhost', 6000)     # family is deduced to be 'AF_INET'
listener = Listener(address, authkey=b'secret password')
conn = listener.accept()
print ('Connection accepted from', listener.last_accepted)

from datetime import datetime
last_spoken = datetime.now()



@inlineCallbacks
def main(session, details):
    
    
    yield session.call("rie.dialogue.say", text="Ready to go!")


    messages = queue.Queue()


    speaking_acts = ['speakingAct1', 'speakingAct10', 'speakingAct11', 'speakingAct12', 'speakingAct13', 'speakingAct14', 'speakingAct15', 'speakingAct16', 'speakingAct17', 'speakingAct2', 'speakingAct3', 'speakingAct4', 'speakingAct5', 'speakingAct6', 'speakingAct7', 'speakingAct8', 'speakingAct9']

    print("Robot running and waiting for messages")

    yield sleep(0.01) 
    
    print("\n\nWaiting messages!")

    while True:
        
        print("Before")
        msg = conn.recv()
        global last_spoken
        last_spoken = datetime.now()
        # msg = input("type")
        # do something with msg
        print("\n\nMessage received:" + str(msg))

        if msg == 'close':
            # conn.close()
            running = False
            break

        else:
            # messages.
            
            
            yield session.call("rie.dialogue.say", text=msg)

        yield sleep(0.01) 

        if (datetime.now() - last_spoken).total_seconds()>15:
            task1 = session.call("rom.optional.behavior.play",name=random.choice(speaking_acts))
            # await task1
            last_spoken = datetime.now()
            print("Last: ", last_spoken)
    # listener.close()

    session.leave() # Sluit de verbinding met de robot

# Create wamp connection
wamp = Component(
transports=[{
    "url": "ws://wamp.robotsindeklas.nl",
    "serializers": ["json"]
    }],
    realm="rie.671a313a8d3e74c137eb1704",
)

wamp.on_join(main)

if __name__ == "__main__":
    run([wamp])