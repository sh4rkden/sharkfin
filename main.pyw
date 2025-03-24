from webview import create_window, start
from json import load, dump
from httpx import get
from time import sleep

from sharkfin.RobloxDownloader import WINDOWSPLAYER, download
import sys
import subprocess
from os import path, chdir
from shutil import rmtree

class Sharkfin:
    reinstallingClient = False
    
    def closeWindow(self):
        window.destroy()

    def minimizeWindow(self):
        window.minimize()

    # yoinked from rod n' mod project lol
    def configureSetting(self, configItem, configValue=None):
        with open(resource("data/config.json"), "r") as file:
            config = load(file)

        if configValue is None:
            return config.get(configItem, None)
        else:
            config[configItem] = configValue
            with open(resource("data/config.json"), 'w') as file:
                dump(config, file, indent=4)
            return True
    
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
                window.run_js(f'document.getElementById("reinstallprogress").style.background = "linear-gradient(to right, #3f85c7 {percentage}%, grey {percentage}%"')

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
        
        # get sharkfin config
        with open(resource(path.join("data", "config.json")), "r") as config:
            config = load(config)
            
        bootstrapperName = config["sharkfin-bootstrapper-name"]
        
        with open(resource(path.join("data", "bootstrapper", bootstrapperName, "config.json")), "r") as config:
            bootstrapperConfig = load(config)
            
        windowTitle, wwidth, wheight = bootstrapperConfig["windowTitle"], bootstrapperConfig["windowWidth"], bootstrapperConfig["windowHeight"]
        
        loader = create_window(
            title=windowTitle,
            url=resource(path.join("data", "bootstrapper", bootstrapperName, "window.html")),

            width=wwidth + 16, height=wheight + 39,
            frameless=True,
            easy_drag=True,
        )

        def doChecks():
            def changeStatus(text):
                loader.run_js(f'document.getElementById("status").innerText = "{text}"')
                
            # Launch Roblox Player
            if arguments.startswith("roblox"):
                # compare version from server and local
                if config["deployment-autoupdate-roblox"]:
                    loader.run_js('document.getElementById("status").innerText = "Checking for Roblox Update..."')
                    robloxPlayerExists = path.exists(resource(path.join("Roblox", "Player", "RobloxPlayerBeta.exe")))

                    if robloxPlayerExists:
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
        )

        #? Expose functions that the frontend should have
        for name in dir(sharkfin):
            func = getattr(sharkfin, name)
            if callable(func) and not name.startswith("_"):
                window.expose(func)

        start(debug=True)