from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from game.manager import ConnectionManager
from fastapi.middleware.cors import CORSMiddleware
import logging

app = FastAPI(
    title="Websocket",
    description="Gran juego"
)

manager = ConnectionManager()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    room, player_id = await manager.assign_room(websocket)
    
    await websocket.accept()
    await websocket.send_json({
        "action": "init",
        "room": room,
        "player_id": player_id
    })
    logging.debug(f"active rooms: {manager.active_rooms}")
    
    try:
        while True:
            data = await websocket.receive_json()
            if "action" in data:
                if data["action"] == "move":
                    if room in manager.active_rooms:
                        x = data.get("x")
                        y = data.get("y")
                        manager.active_rooms[room].update_player_position(player_id, x, y)
                        
                        response = {
                            "action": "player_moved",
                            "player_id": player_id,
                            "x": x,
                            "y": y
                        }
                        await websocket.send_json(response)
                        
                    else:
                        await websocket.send_json({"error": "Room does not exist"})
                        
                elif data["action"] == "shoot":
                    if room in manager.active_rooms:
                        manager.active_rooms[room].add_bullet(player_id, data["bullet_position"])
                    else:
                        await websocket.send_json({"error": "Room does not exist"})

            if room in manager.active_rooms:
                await manager.broadcast(room)
            else:
                await websocket.send_json({"error": "Room does not exist"})

    except WebSocketDisconnect:
        manager.disconnect(websocket, room, player_id)
        if room in manager.active_rooms:
            await manager.broadcast(room)