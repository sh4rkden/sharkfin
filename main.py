from webview import create_window, start
from os import path, getcwd
from json import load, dump

def resource(filename: str):
    return path.abspath(path.join(getcwd(), filename))
class Sharkfin:
    def closeWindow(self):
        window.destroy()

    def minimizeWindow(self):
        window.minimize()

    # yoinked from rod n' mod project lol
    def configureSetting(self, configItem, configValue=None):
        with open(resource("data/config.json"), "r") as file:
            config = load(file)

        if configValue is None:
            return config.get(configItem, "Not a configuration item")
        else:
            config[configItem] = configValue
            with open(resource("data/config.json"), 'w') as file:
                dump(config, file, indent=4)
            return "Configured!"

sharkfin = Sharkfin()

if __name__ == "__main__":
    window = create_window(
        title="sharkfin",
        url="./main.html",
        
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