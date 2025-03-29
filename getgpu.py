from sharkfin.Instance import Sharkfin
from toasted import Toast

sharkfin = Sharkfin()

@sharkfin.event
async def game_join(instance_id, game_id):
    await sharkfin.get_user()
    print(f"Game Joined: {game_id} ({instance_id})")

@sharkfin.event
async def game_leave():
    await sharkfin.get_user()
    print("Left game (signal to put sharkfin in idle)")

@sharkfin.event
async def message_send(message):
    print(f"Message Sent: {message}")
    
@sharkfin.event
async def message_receive(message):
    print(f"Message Received: {message}")

@sharkfin.event
async def player_joined(username, id):
    print(f"Player Joined: {username} ({id})")

#! user-only event (other users won't trigger this)
#! tells any mods that the user has loaded in the game
@sharkfin.event
async def player_loaded(username):
    print(f"Player Loaded: {username}")

@sharkfin.event
async def player_leave(username, id):
    print(f"Player Left: {username} ({id})")

sharkfin.run()