import asyncio
import json
import os
import subprocess
import sys
import time
from threading import Thread

import aiofiles
import httpx
import pypresence
import webview

import sharkfin.RobloxDownloader as RobloxDownloader
import sharkfin.Utils as Utils
from sharkfin.Instance import Sharkfin as SharkfinInstance


#* use this when accessing files outside a frozen environment. (permanent, outside frozen)
#* else just use normal paths to get files inside a frozen environment (not-permanent, inside frozen)
def resource(path: str):
    return os.path.abspath(os.path.join(os.path.dirname(__file__), path))


#? main sharkfin window
class SharkfinWindow:
    #* ASYNC FUNCTIONS
    
    async def read(self, filepath: str):
        async with aiofiles.open(filepath, mode="r") as file:
            contents = await file.read()
            return json.loads(contents)
    
    async def write(self, filepath: str, config: dict):
        async with aiofiles.open(filepath, mode="w") as file:
            contents = json.dumps(config, indent=4)
            await file.write(contents)
    
    #* NON ASYNC FUNCTIONS
    
    def closeWindow(self):
        window.destroy()
    
    def minimizeWindow(self):
        window.minimize()
    
    def configureSetting(self, item, value=None):
        async def _func(item, value):
            config_path = resource("data/config.json")
            config = await self.read(config_path)
            
            if value is None:
                return config.get(item, None)
            else:
                config[item] = value
                await self.write(config_path, config)
                return True
        
        return asyncio.run(_func(item, value))

#? sharkfin window for editing fast flags. 
class SharkfinFFlagEditor:
    ...
        
#? sharkfin window for when running Roblox or Roblox Studio.
class SharkfinLoaderWindow:
    #? main function to do the checks
    #? this function is ran when the page loads.
    def start(self):
        def changeStatus(text):
            loader.run_js(f'document.getElementById("status").innerText = "{text}"')
        
        with open(resource(os.path.join("data", "config.json")), "r") as config:
            config = json.load(config)
        
        command = sys.argv[1]
        
        #? load roblox player
        if command.startswith("roblox"):
            robloxPlayerExists = os.path.exists(resource(os.path.join("Roblox", "Player", "RobloxPlayerBeta.exe")))
            
            if robloxPlayerExists:
                if config["deployment-autoupdate-roblox"]:
                    changeStatus("Checking for Roblox Update...")
                    
                    with open(resource(os.path.join("Roblox", "Player", "sf-version.txt")), "r") as file:
                        content = file.read()
                        local_version, local_clientVersionUpload = content.split("|")
                    
                    response = httpx.get(RobloxDownloader.WINDOWSPLAYER["clientVersionURL"]).json()
                    server_clientVersionUpload = response["clientVersionUpload"]
                    
                    if local_clientVersionUpload != server_clientVersionUpload:
                        for percentage, status in RobloxDownloader.download(RobloxDownloader.WINDOWSPLAYER):
                            changeStatus(f"({percentage}%) {status}")
                            loader.run_js(f'document.getElementById("progress").style.width = "{percentage}%"')
            else:
                for percentage, status in RobloxDownloader.download(RobloxDownloader.WINDOWSPLAYER):
                    changeStatus(f"({percentage}%) {status}")
                    loader.run_js(f'document.getElementById("progress").style.width = "{percentage}%"')
            
            loader.run_js('document.getElementById("progress").style.width = "0%"')
            
            if True: #! make this a conditional
                changeStatus("Starting Discord RPC...")
                instance = SharkfinInstance()
                RobloxClientId = "1351739329038258237" # for sharkfin
                RobloxRPC = pypresence.Presence(RobloxClientId)
                RobloxRPC.connect()

                #? i have no idea why but this makes it so that i dont have to define
                #? global variables that i need to put lol
                game = {
                    "name": "",
                    "image": "",
                    "maxPlayers": 0
                }

                user = {
                    "name": "",
                    "image": ""
                }

                server = {
                    "startTime": 0,
                    "isConnected": False,
                    "isReserved": False,
                    "isPrivate": False,
                    "pid": "",
                    "uid": "",
                    "id": "",
                    "ref": "",
                    "currentPlayers": 0,
                }

                #? only called when in-game
                @Utils.debounce(.1)
                def updateRichPresence():
                    if server["currentPlayers"] < 1:
                        RobloxRPC.update(
                            state="Home",
                            large_image="roblox"
                        )
                    else:
                        if server["isReserved"] or server["isPrivate"]:
                            stype = "private, reserved" if server["isReserved"] and server["isPrivate"] else "private" if server["isPrivate"] else "reserved"

                            RobloxRPC.update(
                                state="Playing " + game["name"],
                                details=f"In a {stype} server.",
                                large_image=game["image"],
                                small_image=user["image"],
                                small_text=user["name"],
                                start=server["startTime"]
                            )
                        else:
                            RobloxRPC.update(
                                state="Playing " + game["name"],
                                large_image=game["image"],
                                small_image=user["image"],
                                small_text=user["name"],
                                party_id=server["id"],
                                party_size=[server["currentPlayers"], game["maxPlayers"]],
                                start=server["startTime"]
                            )

                @instance.event
                async def player_joined(user, id):
                    server["currentPlayers"] += 1
                    updateRichPresence()

                @instance.event
                async def player_left(user, id):
                    if server["isConnected"]:
                        server["currentPlayers"] -= 1
                        updateRichPresence()

                @instance.event
                async def game_joined(place_id, universe_id, referral_page, instance_id, user_id):

                    #! ----- METHOD ONLY WORKS IF RAN IN WEBSITE!! -----
                    if server["isConnected"] and referral_page == "":
                        #gamePlaceData = httpx.get(f"https://games.roblox.com/v1/games/multiget-place-details?placeIds={place_id}").json()
                        if server["uid"] == universe_id and server["pid"] != place_id: #? server is reserved
                            print("detected that the game is a reserved server!!!")
                            server["isReserved"] = True
                            return

                    if referral_page in ["RequestPrivateGame"]: #? server is vip server
                        print("server is vip server!!!")
                        server["isPrivate"] = True
                    else:
                        server["isPrivate"] = False
                    server["isReserved"] = False #? revert to normal just in case.
                    #! ----- METHOD ONLY WORKS IF RAN IN WEBSITE!! -----

                    server["isConnected"] = True
                    server["startTime"] = time.time()

                    gameData = httpx.get(f"https://games.roblox.com/v1/games?universeIds={universe_id}").json()
                    gameIcon = httpx.get(f"https://thumbnails.roblox.com/v1/games/icons?universeIds={universe_id}&size=512x512&format=Png&isCircular=false").json()
                    userData = httpx.get(f"https://users.roblox.com/v1/users/{user_id}").json()
                    userIcon = httpx.get(f"https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds={user_id}&size=420x420&format=Png&isCircular=false").json()

                    game["name"] = gameData["data"][0]["name"]
                    game["image"] = gameIcon["data"][0]["imageUrl"]
                    game["maxPlayers"] = int(gameData["data"][0]["maxPlayers"])

                    user["name"] = userData["displayName"] + " (@" + userData["name"] + ")"
                    user["image"] = userIcon["data"][0]["imageUrl"]

                    server["pid"] = place_id
                    server["uid"] = universe_id
                    server["id"] = instance_id
                    server["ref"] = referral_page

                    print(f"joined to a {referral_page} game")
                    updateRichPresence()


                @instance.event
                async def game_leave():
                    server["isConnected"] = False
                    server["currentPlayers"] = 0
                    updateRichPresence()

                updateRichPresence()
                Thread(target=instance.run, daemon=True).start()
        
            #? apply fastflags and file mods
            
            #? start discord rpc and sharkfin mod server
            
            changeStatus("Starting Roblox...")
            time.sleep(1)
            loader.hide() # destroy = completely kill the entire process.. NO WONDER WHY RUNNING ROBLOX KILLS ALL OF THESE
            
            playerPath = resource(os.path.join("Roblox", "Player", "RobloxPlayerBeta.exe"))
            subprocess.run([playerPath, command], shell=True)
            
            if True: #! add rpc integration option if enabled or not pls
                RobloxRPC.close()
                
            loader.show()
            changeStatus("Stopping Processes...")
            
            #? remove file mods and fastflags
            
            #? stop discordrpc and sharkfin mod server

        elif command.startswith("studio"): # studio support soon
            ...
            
        loader.destroy()

        
sharkfin = SharkfinWindow()
sharkfinEditor = SharkfinFFlagEditor()
sharkfinLoader = SharkfinLoaderWindow()

if __name__ == "__main__":
    #? Make sure that the script's path when accessing files n stuff is where the script/executable is currently on.
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    if len(sys.argv) > 1: #? launch loader (to load roblox or roblox studio)
        with open(resource(os.path.join("data", "config.json")), "r") as config:
            config = json.load(config)

        loaderName = config["sharkfin-loader-name"]
        with open(resource(os.path.join("loader-themes", loaderName, "config.json")), "r") as loaderConfig:
            loaderConfig = json.load(loaderConfig)
            debug, loaderTitle, loaderWidth, loaderHeight, loadingColor = loaderConfig.get("debug", False), loaderConfig.get("title", "sharkfin"), loaderConfig.get("width", 700), loaderConfig.get("height", 400), loaderConfig.get("loadingColor", "#FFFFFF")
        
        loader = webview.create_window(
            title="sharkfin" if loaderTitle == "" else loaderTitle,
            url=resource(os.path.join("loader-themes", loaderName, "window.html")),
            
            width=loaderWidth + 16, height=loaderHeight + 39,
            frameless=True,
            easy_drag=True,
            js_api=sharkfinLoader,
            background_color="#000000"
        )
        
        webview.start(debug=debug)
        
    else: #? launch sharkfin
        SharkfinRPC = pypresence.Presence("1351733786651660318")
        SharkfinRPC.connect()
        SharkfinRPC.update(
            state="Configuring Roblox Settings"
        )
        
        window = webview.create_window(
            title="sharkfin",
            url="./new.html",
            
            width=1100 + 16, height=780 + 39,
            frameless=True,
            easy_drag=True,
            js_api=sharkfin
        )
        
        webview.start(debug=False)