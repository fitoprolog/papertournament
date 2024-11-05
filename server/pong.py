from websockets.sync.client import connect
import time 
import json 

def hello():
    with connect("ws://localhost:1337") as websocket:
        while True:
          time.sleep(1)
          websocket.send(json.dumps({
              "command"  : "ping",
          }))
          message = websocket.recv()
          print(f"Received: {message}")

hello()
