from io import BytesIO
from os import makedirs, path
from time import sleep
from zipfile import ZipFile

from httpx import Client, HTTPError, Timeout

host_path = "https://setup-cfly.rbxcdn.com"

WINDOWSPLAYER = {
    "clientVersionURL": "https://clientsettings.roblox.com/v2/client-version/WindowsPlayer",
    "outputDir": "./Roblox/Player",
    "extractionPaths": {
        "RobloxApp.zip": "",
        "redist.zip": "",
        "shaders.zip": "shaders/",
        "ssl.zip": "ssl/",
        #"WebView2.zip": "",
        #"WebView2RuntimeInstaller.zip": "WebView2RuntimeInstaller/",
        "content-avatar.zip": "content/avatar/",
        "content-configs.zip": "content/configs/",
        "content-fonts.zip": "content/fonts/",
        "content-sky.zip": "content/sky/",
        "content-sounds.zip": "content/sounds/",
        "content-textures2.zip": "content/textures/",
        "content-models.zip": "content/models/",
        "content-platform-fonts.zip": "PlatformContent/pc/fonts/",
        "content-platform-dictionaries.zip": "PlatformContent/pc/shared_compression_dictionaries/",
        "content-terrain.zip": "PlatformContent/pc/terrain/",
        "content-textures3.zip": "PlatformContent/pc/textures/",
        "extracontent-places.zip": "ExtraContent/places/",
        "extracontent-luapackages.zip": "ExtraContent/LuaPackages/",
        "extracontent-translations.zip": "ExtraContent/translations/",
        "extracontent-models.zip": "ExtraContent/models/",
        "extracontent-textures.zip": "ExtraContent/textures/",
    },
}

# TODO: Fix the error that it returns when attempting to launch Roblox Studio.
WINDOWSSTUDIO64 = {
    "clientVersionURL": "https://clientsettings.roblox.com/v2/client-version/WindowsStudio64",
    "outputDir": "./Roblox/Studio",
    "extractionPaths": {
        "RobloxStudio.zip": "",
        "RibbonConfig.zip": "RibbonConfig/",
        "redist.zip": "",
        "Libraries.zip": "",
        "LibrariesQt5.zip": "",
        #"WebView2.zip": "",
        #"WebView2RuntimeInstaller.zip": "",
        "shaders.zip": "shaders/",
        "ssl.zip": "ssl/",
        "ApplicationConfig.zip": "ApplicationConfig/",
        "BuiltInStandalonePlugins.zip": "BuiltInStandalonePlugins/",
        "BuiltInPlugins.zip": "BuiltInPlugins/",
        "Plugins.zip": "Plugins/",
        "StudioFonts.zip": "StudioFonts/",
        "content-qt_translations.zip": "content/qt_translations/",
        "content-sky.zip": "content/sky/",
        "content-fonts.zip": "content/fonts/",
        "content-avatar.zip": "content/avatar/",
        "content-models.zip": "content/models/",
        "content-sounds.zip": "content/sounds/",
        "content-configs.zip": "content/configs/",
        "content-api-docs.zip": "content/api_docs/",
        "content-textures2.zip": "content/textures/",
        "content-studio_svg_textures.zip": "content/studio_svg_textures/",
        "content-platform-fonts.zip": "PlatformContent/pc/fonts/",
        "content-platform-dictionaries.zip": "PlatformContent/pc/shared_compression_dictionaries/",
        "content-terrain.zip": "PlatformContent/pc/terrain/",
        "content-textures3.zip": "PlatformContent/pc/textures/",
        "extracontent-scripts.zip": "ExtraContent/scripts/",
        "extracontent-luapackages.zip": "ExtraContent/LuaPackages/",
        "extracontent-translations.zip": "ExtraContent/translations/",
        "extracontent-models.zip": "ExtraContent/models/",
        "extracontent-textures.zip": "ExtraContent/textures/",
    },
}

def download(config, channel=None):
    timeout = Timeout(120)
    last_progress = 0.0

    def safe_yield(progress, message):
        nonlocal last_progress
        progress = round(progress, 2)
        if progress < last_progress:
            progress = last_progress
        last_progress = progress
        yield progress, message

    with Client(timeout=timeout) as client:

        def fetch(url, retries=2, delay=3):
            for attempt in range(retries + 1):
                try:
                    resp = client.get(url)
                    resp.raise_for_status()
                    return resp
                except HTTPError as e:
                    if attempt < retries:
                        sleep(delay)
                    else:
                        raise e

        # Fetch version info
        if channel is None or channel == "production":
            resp = fetch(config["clientVersionURL"])
        else:
            resp = fetch(config["clientVersionURL"] + f"/channel/{channel}")
            
        version = resp.json().get("version")
        client_version_upload = resp.json().get("clientVersionUpload")
        yield from safe_yield(0.00, f"version: {version}")
        yield from safe_yield(0.00, f"ClientVersionUpload: {client_version_upload}")

        output_dir = config["outputDir"]
        makedirs(output_dir, exist_ok=True)
        
        with open(path.join(output_dir, "AppSettings.xml"), "w", encoding="utf-8") as f:
            f.write(
                """<?xml version="1.0" encoding="UTF-8"?>
<Settings>
    <ContentFolder>content</ContentFolder>
    <BaseUrl>http://www.roblox.com</BaseUrl>
</Settings>"""
            )
        yield from safe_yield(0.00, "Wrote AppSettings.xml")

        manifest_url = f"{host_path}/{client_version_upload}-rbxPkgManifest.txt"
        manifest_text = fetch(manifest_url).text
        pkg_manifest = [line.strip() for line in manifest_text.splitlines() if line.strip()]

        if not pkg_manifest or pkg_manifest[0] != "v0":
            yield from safe_yield(100.00, "Unexpected manifest format.")
            return

        total_packages = sum(1 for pkg in pkg_manifest[1:] if pkg.endswith(".zip"))
        processed_packages = 0

        for pkg in pkg_manifest[1:]:
            if not pkg.endswith(".zip"):
                continue

            pkg_url = f"{host_path}/{client_version_upload}-{pkg}"
            base_progress = (processed_packages / total_packages) * 100

            yield from safe_yield(base_progress, f"Starting download for {pkg}...")

            try:
                with client.stream("GET", pkg_url) as response:
                    response.raise_for_status()
                    total_length = int(response.headers.get("Content-Length", 0))
                    downloaded = 0
                    chunks = []
                    for chunk in response.iter_bytes(chunk_size=8192):
                        if chunk:
                            chunks.append(chunk)
                            downloaded += len(chunk)
                            download_percent = (downloaded / total_length) * 100 if total_length else 0
                            overall_progress = base_progress + (download_percent / total_packages)
                            yield from safe_yield(overall_progress, f"Downloading {pkg}: {download_percent:.2f}%")
                    zip_data = b"".join(chunks)
            except Exception as e:
                yield from safe_yield(base_progress, f"Failed to download {pkg}: {e}")
                processed_packages += 1
                continue

            extract_subdir = config["extractionPaths"].get(pkg, "")
            target_folder = path.join(output_dir, extract_subdir) if extract_subdir else output_dir
            makedirs(target_folder, exist_ok=True)

            try:
                with ZipFile(BytesIO(zip_data)) as z:
                    total_files = len(z.infolist()) or 1
                    extracted_files = 0
                    for member in z.infolist():
                        if member.is_dir():
                            continue
                        target_path = path.join(target_folder, member.filename.replace("\\", "/"))
                        makedirs(path.dirname(target_path), exist_ok=True)
                        with z.open(member) as source, open(target_path, "wb") as target:
                            target.write(source.read())
                        extracted_files += 1
                        overall_progress = ((processed_packages + (extracted_files / total_files)) / total_packages) * 100
                        yield from safe_yield(overall_progress, f"Extracting {member.filename}")
                processed_packages += 1
            except Exception as e:
                yield from safe_yield(base_progress, f"Failed to extract {pkg}: {e}")
                processed_packages += 1
        
        with open(path.join(output_dir, "sf-version.txt"), "w") as file:
            file.write(f"{version}|{client_version_upload}")
            
        yield from safe_yield(100.00, "Download complete.")


if __name__ == "__main__":  # testing
    for progress, status in download(WINDOWSPLAYER):
        print(f"{progress}% - {status}")
