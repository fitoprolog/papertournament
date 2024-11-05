import asyncio
import asyncio
from websockets.server import serve
import websockets
import json
from game_logic import Game
import traceback
game = Game()
async def echo(websocket):
    try:
        async for message in websocket:
            try:
                await game.tick()
                data = json.loads(message)
                command = data.get("command")
                ret_message = '{"error" :"invalid command (use join or play or ping)"}'
                if command: 
                    del data["command"]
                if command == "join":
                    ret_message=game.join_player(data,websocket)
                if command == "play":
                    ret_message=game.update(data)
                if command == "simon_says":
                    ret_message=game.simon_says(data)
                if command == "ping":
                    ret_message = '{"command" : "pong"}'
                await websocket.send(ret_message)
            except:
                traceback.print_exc();
                await websocket.send('{"error":"invalid json"}')
    except websockets.ConnectionClosedError:
        print("client died")
    except Exception as e:
        print(f"unexpected error: {e}")

async def main():
    async with serve(echo, "localhost", 1337):
        await asyncio.get_running_loop().create_future()  # run forever
asyncio.run(main())
