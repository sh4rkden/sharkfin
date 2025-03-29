import asyncio
import json
import os
import platform
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
    reinstallingClient = False
    window = None
    
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

    def updateFrontendConfigDisplays(self):
        async def _func():
            config_path = resource("data/config.json")
            config = await self.read(config_path)
            
            preferredGPU = "Automatic" if config["fflag-preferred-gpu"].lower() == "auto" else config["fflag-preferred-gpu"]
            renderingMode = config["fflag-rendering-mode"]
            msaaQuality = config["fflag-msaa-quality"]
            textureQuality = config["fflag-texture-quality"]
            lightingTechnology = config["fflag-lighting-technology"]
            mouseCursor = config["customization-custom-cursor"]
            loaderTheme = config["sharkfin-loader-name"]

            display_mappings = {
                "rendering_mode": {
                    "auto": "Automatic",
                    "vulkan": "Vulkan",
                    "opengl": "OpenGL",
                    "d3d10": "Direct3D 10",
                    "d3d11": "Direct3D 11",
                },
                "msaa_quality": {
                    "auto": "Automatic",
                    "1": "1x",
                    "2": "2x",
                    "4": "4x",
                    "8": "8x (buggy)",
                    "16": "16x (buggy)",
                },
                "texture_quality": {
                    "auto": "Automatic",
                    "0": "Lowest (0)",
                    "1": "Low (1)",
                    "2": "High (2)",
                    "3": "Highest (3)",
                },
                "lighting_technology": {
                    "auto": "Automatic",
                    "voxel": "Voxel",
                    "shadowmap": "Shadow Map",
                    "future": "Future",
                },
                "mouse_cursor": {
                    "default": "Default",
                    "angular": "Angular",
                    "cartoony": "Cartoony",
                },
            }

            def set_text(element_id, text):
                window.run_js(f'document.getElementById("{element_id}").innerText = "{text}"')

            set_text("preferred-gpu-text", preferredGPU)
            set_text("rendering-mode-text", display_mappings["rendering_mode"].get(renderingMode, renderingMode))
            set_text("msaa-quality-text", display_mappings["msaa_quality"].get(msaaQuality, msaaQuality))
            set_text("texture-quality-text", display_mappings["texture_quality"].get(textureQuality, textureQuality))
            set_text("lighting-technology-text", display_mappings["lighting_technology"].get(lightingTechnology, lightingTechnology))
            set_text("roblox-mouse-cursor-text", display_mappings["mouse_cursor"].get(mouseCursor, mouseCursor))
            set_text("loader-change-theme-text", loaderTheme)

        return asyncio.run(_func())
    
    def getGPUList(self):
        return Utils.get_gpu_list()

    def getLoaderThemeList(self):
        return [f for f in os.listdir(resource(os.path.join("loader-themes")))
                if os.path.isdir(resource(os.path.join("loader-themes", f)))]
    
    def openLoaderThemesFolder(self):
        opsys = platform.system()
        folderpath = resource(os.path.join("loader-themes"))
        
        # different systems
        # hopefully i get proper darwin support
        if opsys == "Windows":
            os.startfile(folderpath)
        elif opsys == "Darwin":
            subprocess.call(["open", folderpath])
    
    def getClientSettings(self):
        time.sleep(0.05)
        config_path = resource("data/config.json")
        
        with open(config_path, "r") as file:
            config = json.load(file)
            try:
                channel = config["deployment-roblox-channel"]
                url = "https://clientsettings.roblox.com/v2/client-version/WindowsPlayer"
                
                if channel != "production":
                    url = url + f"/channel/{channel}"
                    
                response = httpx.get(url)
                response.raise_for_status()
                data = response.json()
                version = data.get("version")
                clientVersionUpload = data.get("clientVersionUpload")
                return version, clientVersionUpload
            except httpx.HTTPStatusError:
                return "???", "???"
    
    def setDefault(self):
        if getattr(sys, "frozen", False):
            application_path = f'"{sys.executable}"'
        else:
            application_path = f'"{sys.executable}" "{__file__}"'
            
        Utils.set_protocol("roblox", application_path, "sharkfin")
        Utils.set_protocol("roblox-player", application_path, "sharkfin")
    
    def reinstallRoblox(self):
        if not self.reinstallingClient:
            self.reinstallingClient = True
            window.run_js('document.getElementById("reinstallprogress").style.pointerEvents = "none"')

            def changeStatus(text):
                window.run_js(f'document.getElementById("status").innerText = "{text}"')

            changeStatus("Starting Reinstallation...")
            
            try:
                os.rmtree(resource(os.path.join("Roblox", "Player")))
            except FileNotFoundError:
                pass

            for percentage, status in RobloxDownloader.download(RobloxDownloader.WINDOWSPLAYER):
                changeStatus(f"({percentage}%) {status}")
                window.run_js(
                    f'document.getElementById("reinstallprogress").style.background = "linear-gradient(to right, #3f85c7 {percentage}%, grey {percentage}%"'
                )
                
            window.run_js('document.getElementById("reinstallprogress").style.background = ""')
            window.run_js('document.getElementById("reinstallprogress").style.pointerEvents = "all"')
            
            changeStatus("Roblox Client Reinstalled!")
            time.sleep(5)
            changeStatus("Reinstall the Roblox Client.")
            self.reinstallingClient = False

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
            
            
            instance = SharkfinInstance()
            RobloxRPC = pypresence.Presence("1351739329038258237")
            RobloxRPC.connect()
            RobloxRPC.update(state="Loading...")

            @instance.event
            async def game_join(instance_id, game_id):
                print("joining " + game_id)

            @instance.event
            async def player_loaded(username):
                print(f"Player Loaded: {username}")
                
            Thread(target=instance.run, daemon=True).start()
        
            #? apply fastflags and file mods
            
            #? start discord rpc and sharkfin mod server
            
            changeStatus("Starting Roblox...")
            time.sleep(1)
            loader.hide() # destroy = completely kill the entire process.. NO WONDER WHY RUNNING ROBLOX KILLS ALL OF THESE
            playerPath = resource(os.path.join("Roblox", "Player", "RobloxPlayerBeta.exe"))
            subprocess.run([playerPath, command], shell=True)
            loader.show()
            changeStatus("Stopping Roblox...")
            time.sleep(1)
            
            #? remove file mods and fastflags
            
            #? stop discordrpc and sharkfin mod server

        elif command.startswith("studio"): # studio support soon
            ...
        else:
            print("ERROR: INVALID PROTOCOL LAUNCH ARGUMENT")
            input("Press enter to exit.")
            
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
            url="./main.html",
            
            width=1000 + 16, height=800 + 39,
            frameless=True,
            easy_drag=True,
            js_api=sharkfin
        )
        
        webview.start(debug=True)