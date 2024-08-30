import logging
from fastapi import WebSocket
from starlette.websockets import WebSocketState
from typing import Dict
from .models.gameroom import GameRoom
import uuid

class ConnectionManager:
    def __init__(self):
        self.active_rooms: Dict[str, GameRoom] = {}
        self.waiting_players: Dict[str, WebSocket] = {}
        logging.basicConfig(level=logging.DEBUG)

    async def assign_room(self, websocket: WebSocket):
        # Look for a room with max 2 players
        for room_id, room in self.active_rooms.items():
            if len(room.players) < 2:
                player_id = str(uuid.uuid4())
                logging.debug(f"Assigning room {room_id} to player {player_id}")
                await self.connect(websocket, room_id, player_id)
                return room_id, player_id

        # Create new room if there's no space
        room_id = str(uuid.uuid4())
        player_id = str(uuid.uuid4())
        logging.debug(f"Creating new room {room_id} and assigning player {player_id}")
        self.active_rooms[room_id] = GameRoom(room_id)
        await self.connect(websocket, room_id, player_id)
        return room_id, player_id

    async def connect(self, websocket: WebSocket, room_id: str, player_id: str):
        if room_id not in self.active_rooms:
            self.active_rooms[room_id] = GameRoom(room_id)
            logging.debug(f"Created new GameRoom for room {room_id}")

        # Add player to room
        self.active_rooms[room_id].add_player(player_id)
        self.active_rooms[room_id].players[player_id].socket = websocket
        logging.debug(f"Player {player_id} connected to room {room_id}")
        logging.debug(f"Players per room: {self.active_rooms[room_id].players}")
        logging.debug(f"roomdict: {self.active_rooms[room_id].to_dict()}")

    def disconnect(self, websocket: WebSocket, room_id: str, player_id: str):
        if room_id in self.active_rooms:
            self.active_rooms[room_id].remove_player(player_id)
            if not self.active_rooms[room_id].players:
                del self.active_rooms[room_id]
                logging.debug(f"Room {room_id} deleted due to no players")

    async def broadcast(self, room: str):
        if room in self.active_rooms:
            game_state = self.active_rooms[room].to_dict()
            logging.debug(f"Broadcasting to room {room}, game state: {game_state}")

            for player in self.active_rooms[room].players.values():
                if player.socket.client_state == WebSocketState.CONNECTED:
                    try:
                        await player.socket.send_json({
                            "action": "update",
                            "state": game_state
                        })
                        logging.debug(f"Sent game state to player {player.id}")
                    except Exception as e:
                        logging.error(f"Error sending game state to player {player.id}: {e}")
                else:
                    logging.debug(f"Player {player.id} socket is not WebSocketState.CONNECTED, state: {player.socket.client_state}")
        else:
            logging.error(f"Room {room} does not exist for broadcasting")