from websockets.sync.client import connect
import time 
import json 

def hello():
    with connect("ws://localhost:1337") as websocket:
          websocket.send(json.dumps({
              "command"  : "join",
              "alias"    : "werks",
              "password" : "redpwd",
              "team"     : "red"
          }))
          message = websocket.recv()
          print(f"Received: {message}")
          payload = json.loads(message)
          while True:
            time.sleep(1)
            websocket.send(json.dumps({
              "command"  : "play",
              "dx"       : 1,
              "dy"       : 0,
              "alias"    : "werks",
              "cookie"   : payload.get("cookie")+"x",
            }))
            message = websocket.recv()
            print(f"Received: {message}")

hello()
