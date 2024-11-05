from pydantic import BaseModel,ValidationError
from typing import Optional,Literal
import json 
from uuid import uuid4
from dataclasses import dataclass
from time import time
import websockets
import traceback

TEAM_PASSWORD={
    "green" : "greenpwd",
    "red"   : "redpwd" , 
    "computer" : "brainpwd",
    "viewer"   : "viewer",
}
max_players_per_team = 3

SAMPLING_PERIOD = 0.25

class GameObject:
    id : int
    x : int
    y : int 

class ActionSchema(BaseModel):
    alias  : str
    cookie : str
    action : Optional[Literal['grab','release','hit']] =None
    dx :  Literal[-1,0,1]
    dy :  Literal[-1,0,1]

class LoginSchema(BaseModel):
    team : Literal["green","red","computer"]
    alias : str
    password : str

@dataclass
class PlayerStatus:
    team : str
    alias : str
    last_access_time : float 
    cookie  : str 
    sid : websockets.WebSocketServerProtocol 
    x : int = 0 
    y : int = 0 
    r : int = 0
    attempts : int = 0
    latency_punishment = 0
    captured_object : Optional[GameObject] = None

class Client:
    type_ : str
    socket : websockets.WebSocketClientProtocol 

class Game:
    
    players : dict[str,PlayerStatus] = {}
    objects : list[GameObject] =[]
    players_counts : dict = {}
    t : float
    brain : websockets.WebSocketServerProtocol
    game_objects : list[GameObject]

    def __init__(self):
        for key in TEAM_PASSWORD:
            self.players_counts[key]=0

    def invalid_period(self,last_access_time):
       print(self.t , "VS" , last_access_time)
       dt = self.t - last_access_time 
       print(dt)
       if dt < SAMPLING_PERIOD:
           return '{"error" : "maxium 4 request per second" }'

    def join_player(self,data : dict, client: websockets.WebSocketServerProtocol):
        try:
          login = LoginSchema(**data)

          if TEAM_PASSWORD.get(login.team) != login.password:
              return '{"error" : "invalid password"}'

          existing_player = self.players.get(login.alias)
          if existing_player:
              is_flooding=self.invalid_period(existing_player.last_access_time)
              if is_flooding:
                  return is_flooding
              existing_player.attempts+=1
              existing_player.last_access_time = time()
              existing_player.cookie = str(uuid4())
              existing_player.sid = client
          else:
              if self.players_counts[login.team]+1 > max_players_per_team:
                  return '{"error" : "maxium players per team exceded" }'
              self.players_counts[login.team]+=1
              existing_player=self.players[login.alias] = PlayerStatus(team = login.team,
                                                                       alias = login.alias,
                                                                       last_access_time=self.t,
                                                                       cookie=str(uuid4()),
                                                                       sid =client)
          ret =  existing_player.__dict__.copy()
          del ret["sid"]
          return json.dumps(ret)
        except ValidationError as e:
            return json.dumps(e.json())

    def disconnect_player(self):
        pass

    async def tick(self):
        self.t = time();
        for key in list(self.players.keys()):
            player  = self.players[key]
            if (self.t-player.last_access_time) >=5.0:
                player.latency_punishment+=1
        await self.broadcast('{"command":"ping"}')

    async def broadcast(self,message):
        for pkey in  list(self.players.keys()):
            try:
                await self.players[pkey].sid.send(message)
            except:
                traceback.print_exc()
                self.players[pkey].latency_punishment+=1

    def update(self , data : dict ):
        try:
            action = ActionSchema(**data)
            if self.players[action.alias].cookie != action.cookie:
                return '{"error":"invalid cookie"}'
            return '{"status":"ok"}' 
        except ValidationError as e:
            return json.dumps(e.json())
        pass
    def simon_says(self, data : dict):
        pass
     
