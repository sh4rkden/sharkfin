from webview import create_window, start






if __name__ == "__main__":
    window = create_window(
        title="sharkfin",
        url="./main.html",
        width=1280, height=800,
        frameless=True,
        easy_drag=True,
        resizable=True
    )
    
    
    start(debug=True)