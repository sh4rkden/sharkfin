from subprocess import check_output
from re import split

def get_gpu_driver_info():
    try:
        output = check_output("wmic path win32_VideoController get Name,DriverVersion", shell=True)
        decoded_output = output.decode().strip().splitlines()
        
        gpu_names = []
        for line in decoded_output[1:]:
            if line.strip():
                parts = split(r'\s{2,}', line.strip())
                if parts:
                    gpu_names.append(parts[1])
        return gpu_names.reverse()
    except Exception as e:
        return f"Error retrieving GPU driver info on Windows: {e}"
