from webview import create_window, start

class Sharkfin:
    def closeWindow(self):
        window.destroy()
    
    def minimizeWindow(self):
        window.minimize()

sharkfin = Sharkfin()

if __name__ == "__main__":
    window = create_window(
        title="sharkfin",
        url="./main.html",
        
        # because frameless width and height isnt correct, we fix it.
        width=1000 + 16, height=800 + 39,
        frameless=True,
        easy_drag=True,
    )
    
    for name in dir(sharkfin):
        func = getattr(sharkfin, name)
        if callable(func) and not name.startswith("_"):
            window.expose(func)
    
    start(debug=True)