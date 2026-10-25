"""Install NeoForge client to a dummy game directory so it can be processed further."""

import re
import sys
import subprocess
import argparse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

BASE = "https://maven.neoforged.net/releases/net/neoforged/neoforge"
METADATA_URL = f"{BASE}/maven-metadata.xml"

def download_installer(version):
    with urllib.request.urlopen(METADATA_URL, timeout=30) as response:
        root = ET.fromstring(response.read())

    versions = [
        node.text
        for node in root.findall("./versioning/versions/version")
        if node.text and node.text.startswith(version)
    ]

    if not versions:
        raise RuntimeError(f"No NeoForge {version} versions found.")

    # Maven metadata lists published versions; select the last matching entry.
    version = versions[-1]
    filename = f"neoforge-{version}-installer.jar"
    url = f"{BASE}/{version}/{filename}"

    existed = Path(filename).exists()
    if existed:
        print(f"Found installer file {filename}.")
    else:
        print(f"Downloading {filename}...")
        urllib.request.urlretrieve(url, filename)
        print(f"Saved to: {filename}")
    return filename, existed

def run_installer(installer_file, game_dir, existed):
    print("Installing...")
    game_path = Path(game_dir)
    game_path.mkdir(parents=True, exist_ok=True)

    # create launcher dummy so the installer success
    profiles_path = game_path / "launcher_profiles.json"
    if not profiles_path.exists():
        profiles_path.write_text('{"profiles":{}}', encoding="utf-8")
    
    # run installer
    result = subprocess.run(["java", "-jar", installer_file, "--installClient", game_dir], check=True)
    if result.returncode == 0:
        print("NeoForge installer succeeded!")
        if existed == True:
            print(f"The installer file {installer_file} will be kept because it was already existed.")
        else:
            Path(installer_file).unlink(missing_ok=True)
            Path(f"{installer_file}.log").unlink(missing_ok=True)
            print(f"The installer file {installer_file} was deleted.")
    else:
        print(f"RESULT: {result}")
	
def run(mc_version, game_dir="game_dir"):
    installer_file, existed = download_installer(mc_version)
    run_installer(installer_file, game_dir, existed)

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "mc_version",
        help="The Minecraft/NeoForge version you want to install. Specify ONLY one of them. The installer will automatically install both!",
    )
    parser.add_argument(
        "--game-dir",
        nargs="?",
        default="game_dir",
        help="Minecraft/NeoForge installation directory"
             "(default: game_dir)",
    )
    args = parser.parse_args(argv)
    run(args.mc_version, args.game_dir)

if __name__ == "__main__":
    main()