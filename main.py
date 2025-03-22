from webview import create_window, start

class Sharkfin:
    ...

sharkfin = Sharkfin()

if __name__ == "__main__":
    window = create_window(
        title="sharkfin",
        url="./main.html",
        width=900, height=800,
        frameless=True,
        easy_drag=True,
    )
    
    for name in dir(sharkfin):
        func = getattr(sharkfin, name)
        if callable(func) and not name.startswith("_"):
            window.expose(func)
    
    start(debug=True)