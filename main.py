import subprocess
import sys
import asyncio
from json import load, loads, dumps
from os import chdir, listdir, path
from shutil import rmtree
from time import sleep

import aiofiles
from httpx import HTTPStatusError, get
from webview import create_window, start

from sharkfin.RobloxDownloader import WINDOWSPLAYER, download
from sharkfin.Utils import get_gpu_list, set_protocol


class Sharkfin:
    reinstallingClient = False

    async def _async_read_config(self, filepath: str):
        async with aiofiles.open(filepath, mode="r") as file:
            contents = await file.read()
            return loads(contents)

    async def _async_write_config(self, filepath: str, config: dict):
        async with aiofiles.open(filepath, mode="w") as file:
            contents = dumps(config, indent=4)
            await file.write(contents)

    def configureSetting(self, configItem, configValue=None):
        return asyncio.run(self._async_configureSetting(configItem, configValue))

    async def _async_configureSetting(self, configItem, configValue=None):
        config_path = resource("data/config.json")
        config = await self._async_read_config(config_path)
        if configValue is None:
            return config.get(configItem, None)
        else:
            config[configItem] = configValue
            await self._async_write_config(config_path, config)
            return True

    def updateFrontendConfigDisplays(self):
        return asyncio.run(self._async_updateFrontendConfigDisplays())

    async def _async_updateFrontendConfigDisplays(self):
        config_path = resource("data/config.json")
        config = await self._async_read_config(config_path)
        
        preferredGPU = "Automatic" if config["fflag-preferred-gpu"].lower() == "auto" else config["fflag-preferred-gpu"]
        renderingMode = config["fflag-rendering-mode"]
        msaaQuality = config["fflag-msaa-quality"]
        textureQuality = config["fflag-texture-quality"]
        lightingTechnology = config["fflag-lighting-technology"]
        mouseCursor = config["customization-custom-cursor"]
        bootstrapperTheme = config["sharkfin-bootstrapper-name"]

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
        set_text("bootstrapper-change-theme-text", bootstrapperTheme)

    def closeWindow(self):
        window.destroy()

    def minimizeWindow(self):
        window.minimize()

    def getGPUList(self):
        return get_gpu_list()

    def getBootstrapperThemeList(self):
        return [f for f in listdir(resource(path.join("bootstrappers")))
                if path.isdir(resource(path.join("bootstrappers", f)))]

    def getClientSettings(self):
        config_path = resource("data/config.json")
        with open(config_path, "r") as file:
            config = load(file)
        try:
            channel = config["deployment-roblox-channel"]
            url = "https://clientsettings.roblox.com/v2/client-version/WindowsPlayer"
            if channel != "production":
                url += f"channel/{channel}"
            response = get(url)
            response.raise_for_status()
            data = response.json()
            version = data.get("version")
            clientVersionUpload = data.get("clientVersionUpload")
            return version, clientVersionUpload
        except HTTPStatusError:
            return "???", "???"

    def setDefault(self):
        if getattr(sys, "frozen", False):
            application_path = f'"{sys.executable}"'
        else:
            application_path = f'"{sys.executable}" "{__file__}"'
        set_protocol("roblox", application_path, "sharkfin")
        set_protocol("roblox-player", application_path, "sharkfin")

    def reinstallRoblox(self):
        if not self.reinstallingClient:
            self.reinstallingClient = True
            window.run_js('document.getElementById("reinstallprogress").style.pointerEvents = "none"')

            def changeStatus(text):
                window.run_js(f'document.getElementById("status").innerText = "{text}"')

            changeStatus("Starting Reinstallation...")
            try:
                rmtree(resource(path.join("Roblox", "Player")))
            except FileNotFoundError:
                pass

            for percentage, status in download(WINDOWSPLAYER):
                changeStatus(f"({percentage}%) {status}")
                window.run_js(
                    f'document.getElementById("reinstallprogress").style.background = "linear-gradient(to right, #3f85c7 {percentage}%, grey {percentage}%"'
                )
            window.run_js('document.getElementById("reinstallprogress").style.background = ""')
            window.run_js('document.getElementById("reinstallprogress").style.pointerEvents = "all"')
            changeStatus("Roblox Client Reinstalled!")
            sleep(5)
            changeStatus("Reinstall the Roblox Client.")
            self.reinstallingClient = False

sharkfin = Sharkfin()

if __name__ == "__main__":
    from threading import Thread
    
    chdir(path.dirname(path.abspath(__file__)))
    def resource(filename: str):
        return path.abspath(path.join(path.dirname(__file__), filename))
    
    if len(sys.argv) > 1: #? Launch Roblox Player or Studio
        arguments = sys.argv[1]

        #? get sharkfin config
        with open(resource(path.join("data", "config.json")), "r") as config_file:
            config = load(config_file)

        bootstrapperName = config["sharkfin-bootstrapper-name"]
        
        #? get current bootstrapper config
        with open(resource(path.join("bootstrappers", bootstrapperName, "config.json")), "r") as bootstrapper_config:
            bootstrapperConfig = load(bootstrapper_config)
            
        windowTitle, wwidth, wheight = bootstrapperConfig["windowTitle"], bootstrapperConfig["windowWidth"], bootstrapperConfig["windowHeight"]
        
        loader = create_window(
            title=windowTitle,
            url=resource(path.join("bootstrappers", bootstrapperName, "window.html")),

            width=wwidth + 16, height=wheight + 39,
            frameless=True,
            easy_drag=True,
        )

        def doChecks():
            def changeStatus(text):
                loader.run_js(f'document.getElementById("status").innerText = "{text}"')
                
            # Launch Roblox Player
            if arguments.startswith("roblox"):
                # update roblox - compare version from server and local
                if config["deployment-autoupdate-roblox"]:
                    robloxPlayerExists = path.exists(resource(path.join("Roblox", "Player", "RobloxPlayerBeta.exe")))
                    
                    if robloxPlayerExists:
                        changeStatus("Checking for Roblox Update...")
                        with open(resource(path.join("Roblox", "Player", "sf-version.txt")), "r") as file:
                            content = file.read()
                            local_version, local_clientVersionUpload = content.split("|")

                        response = get(WINDOWSPLAYER["clientVersionURL"]).json()
                        server_clientVersionUpload = response["clientVersionUpload"]

                        if local_clientVersionUpload != server_clientVersionUpload:
                            for percentage, status in download(WINDOWSPLAYER):
                                changeStatus(f"({percentage}%) {status}")
                                loader.run_js(f'document.getElementById("progress").style.width = "{percentage}%"')
                    else:
                        for percentage, status in download(WINDOWSPLAYER):
                            changeStatus(f"({percentage}%) {status}")
                            loader.run_js(f'document.getElementById("progress").style.width = "{percentage}%"')

                
                #? apply fastflags (so it can be reverted later once the robloxplayer stops)
                #? we construct the json data here and then shove it to the user's fastflags and if
                #? the respect user fflags is enabled it should discard the fflags that it will append to the user's
                #? else if its disabled we just overwrite the flags.
    
                #? create the user's fastflag, then insert other flags from config
                #? check for flags to not override if respect flags option is turned on
                
                sleep(2)
                loader.destroy()
                subprocess.run([resource(path.join("Roblox", "Player", "RobloxPlayerBeta.exe")), arguments], shell=True)
                
            elif arguments.startswith("studio"): # studio support soon
                ...#robloxStudioExists = path.exists(resource(path.join("Roblox", "Studio", "RobloxStudioBeta.exe")))
                
            else:
                print("Invalid Protocol Launch Arguments.")
            
        Thread(target=doChecks, daemon=True).start()
        start(debug=True)
        
    else: #? Launch Sharkfin
        window = create_window(
            title="sharkfin",
            url=resource("./main.html"),

            #? because frameless width and height isnt correct when frameless is true, we fix it.
            width=1000 + 16, height=800 + 39,
            frameless=True,
            easy_drag=True,
            js_api=sharkfin,
        )

        start(debug=True)