from typing import Dict

class Player:
    def __init__(self, player_id: str, x: int = 0, y: int = 0, health: int = 100):
        self.id = player_id
        self.x = x
        self.y = y
        self.health = health

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "x": self.x,
            "y": self.y,
            "health": self.health
        }
