from winreg import CreateKey, SetValue, SetValueEx, CloseKey, HKEY_CURRENT_USER, REG_SZ
from subprocess import check_output
from threading import Timer
from re import split

def debounce(time):
    def decorator(fn):
        timer = None
        def debounced(*args, **kwargs):
            nonlocal timer
            if timer is not None:
                timer.cancel()
            timer = Timer(time, lambda: fn(*args, **kwargs))
            timer.start()
        return debounced
    return decorator

def get_gpu_list():
    try:
        output = check_output("wmic path win32_VideoController get Name,DriverVersion", shell=True)
        decoded_output = output.decode().strip().splitlines()
        
        gpu_names = []
        for line in decoded_output[1:]:
            if line.strip():
                parts = split(r'\s{2,}', line.strip())
                if parts:
                    gpu_names.append(parts[1])
        return gpu_names
    except Exception as e:
        return f"Error retrieving GPU driver info on Windows: {e}"

def set_protocol(protocol, application_path, program_name):
    try:
        base_path = fr"Software\Classes\{protocol}"
        key = CreateKey(HKEY_CURRENT_USER, base_path)
        SetValue(key, None, REG_SZ, f"{program_name} Protocol")
        SetValueEx(key, "URL Protocol", 0, REG_SZ, "")
        SetValueEx(key, "FriendlyName", 0, REG_SZ, program_name)

        icon_key = CreateKey(key, "DefaultIcon")
        SetValue(icon_key, None, REG_SZ, application_path)
        CloseKey(icon_key)

        command_key = CreateKey(key, r"shell\open\command")
        command = f'{application_path} "%1"'
        SetValue(command_key, None, REG_SZ, command)
        CloseKey(command_key)

        CloseKey(key)
        print(f"Successfully registered protocol: {protocol} with name: {program_name}")
    except Exception as e:
        print(f"Failed to register protocol {protocol}: {e}")
