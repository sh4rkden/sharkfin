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
        "WebView2.zip": "",
        "WebView2RuntimeInstaller.zip": "WebView2RuntimeInstaller/",
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
        "WebView2.zip": "",
        "WebView2RuntimeInstaller.zip": "",
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

        if channel is None:
            resp = fetch(config["clientVersionURL"])
        else:
            resp = fetch(config["clientVersionURL"] + f"/channel/{channel}")
            
        version = resp.json().get("version")
        client_version_upload = resp.json().get("clientVersionUpload")
        yield 0, f"version: {version}"
        yield 0, f"ClientVersionUpload: {client_version_upload}"

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
        yield 5, "Wrote AppSettings.xml"

        manifest_url = f"{host_path}/{client_version_upload}-rbxPkgManifest.txt"
        manifest_text = fetch(manifest_url).text
        pkg_manifest = [line.strip() for line in manifest_text.splitlines() if line.strip()]

        if not pkg_manifest or pkg_manifest[0] != "v0":
            yield 100, "Unexpected manifest format."
            return

        total_packages = sum(1 for pkg in pkg_manifest[1:] if pkg.endswith(".zip"))
        processed_packages = 0

        for pkg in pkg_manifest[1:]:
            if not pkg.endswith(".zip"):
                continue
            pkg_url = f"{host_path}/{client_version_upload}-{pkg}"
            yield min(100, int((processed_packages / total_packages) * 100)), f"Downloading {pkg}..."
            try:
                zip_data = fetch(pkg_url).content
            except Exception as e:
                yield min(100, int((processed_packages / total_packages) * 100)), f"Failed to download {pkg}: {e}"
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
                        progress = int(((processed_packages + extracted_files / total_files) / total_packages) * 100)
                        yield progress, f"Extracting {member.filename} from {pkg}"
                processed_packages += 1
                #yield min(100, int((processed_packages / total_packages) * 100)), f"Extracted {pkg} to {target_folder}"
            except Exception as e:
                yield min(100, int((processed_packages / total_packages) * 100)), f"Failed to extract {pkg}: {e}"
                processed_packages += 1
        
        with open(path.join(output_dir, "sf-version.txt"), "w") as file:
            file.write(f"{version}|{client_version_upload}")
        yield 100, "Download complete."


if __name__ == "__main__": # testing
    for x in download(WINDOWSPLAYER):
        print(x)