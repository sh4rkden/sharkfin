import os
import sys
import ctypes
import winreg

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False

def elevate():
    # Re-run the program with admin privileges using ShellExecuteW
    params = " ".join([f'"{arg}"' for arg in sys.argv])
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
    sys.exit(0)

def get_command():
    # If the script is frozen (e.g. using PyInstaller), use the frozen executable.
    # Otherwise, run the Python interpreter with this script.
    if getattr(sys, "frozen", False):
        # Running as a frozen executable
        return f'"{sys.executable}" "%1"'
    else:
        # Running as a regular Python script
        script_path = os.path.abspath(__file__)
        return f'"{sys.executable}" "{script_path}" "%1"'

def register_protocol(protocol, description):
    try:
        # Create or open the key for the protocol under HKEY_CLASSES_ROOT
        key = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, protocol)
        winreg.SetValueEx(key, "", 0, winreg.REG_SZ, f"URL:{description} Protocol")
        winreg.SetValueEx(key, "URL Protocol", 0, winreg.REG_SZ, "")
        
        # Create the command key that launches your app when the URL is activated
        command_key = winreg.CreateKey(key, r"shell\open\command")
        command = get_command()
        winreg.SetValueEx(command_key, "", 0, winreg.REG_SZ, command)
        
        winreg.CloseKey(command_key)
        winreg.CloseKey(key)
        
        print(f"Successfully registered the '{protocol}' protocol.")
    except Exception as e:
        print(f"Failed to register protocol '{protocol}'. Error: {e}")

if __name__ == "__main__":
    if not is_admin():
        print("Administrator privileges required. Relaunching with elevated rights...")
        elevate()
    
    # Define the protocols and a simple description
    protocols = ["roblox", "roblox-player"]
    description = "My Python App"
    
    for protocol in protocols:
        register_protocol(protocol, description)

    input()
    
    # If launched with a URL, handle it here
    if len(sys.argv) > 1:
        url = sys.argv[1]
        print(f"Handling protocol URL: {url}")
        # Insert your URL handling logic here.
