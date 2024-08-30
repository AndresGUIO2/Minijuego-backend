from .player import Player
from typing import Dict, List

class GameRoom:
    def __init__(self, room_id: str):
        self.room_id = room_id
        self.players: Dict[str, Player] = {}  # Player ID -> Player Object
        self.bullets: List[Dict] = []  # Lista de balas en el juego

    def add_player(self, player_id: str):
        if player_id not in self.players:
            self.players[player_id] = Player(player_id)

    def remove_player(self, player_id: str):
        if player_id in self.players:
            del self.players[player_id]

    def update_player_position(self, player_id: str, x: int, y: int):
        if player_id in self.players:
            self.players[player_id].x = x
            self.players[player_id].y = y

    def add_bullet(self, player_id: str, bullet_position: Dict):
        if player_id in self.players:
            self.bullets.append(bullet_position)

    def to_dict(self) -> Dict:
        return {
            "players": {player_id: player.to_dict() for player_id, player in self.players.items()},
            "bullets": self.bullets
        }
