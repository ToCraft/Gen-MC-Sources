#!/usr/bin/env python3
"""Decompile NeoForge and Minecraft client JARs."""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.request import urlretrieve

VINEFLOWER_URL = (
    "https://github.com/Vineflower/vineflower/releases/download/"
    "1.12.0/vineflower-1.12.0.jar"
)

TARGET_JARS = (
    Path("net/neoforged/minecraft-client-patched"),
    Path("net/neoforged/neoforge"),
)

VANILLA_JAR = Path("versions/26.3/26.3.jar")


def get_vineflower(explicit_path=None):
    for path in (explicit_path, "vineflower.jar"):
        if path and Path(path).is_file():
            return Path(path)

    jar = Path("vineflower.jar")
    urlretrieve(VINEFLOWER_URL, jar)
    return jar


def find_target_jars(libraries):
    targets = []

    for relative_path in TARGET_JARS:
        matches = sorted(
            (libraries / relative_path).glob("*/*.jar")
        )
        # Keep the newest version directory by name.
        if not matches:
            raise FileNotFoundError(
                f"No target JAR found under {libraries / relative_path}"
            )
        targets.append(matches[-1])

    return targets


def decompile(
    vineflower,
    jar,
    destination,
    force=False,
):
    destination.mkdir(parents=True, exist_ok=True)

    marker = destination / ".decompiled-from"
    if (
        not force
        and marker.exists()
        and marker.read_text(encoding="utf-8").strip()
        == str(jar.resolve())
        and any(destination.rglob("*.java"))
    ):
        print(f"Already decompiled: {jar.name}")
        return

    if force:
        for child in destination.iterdir():
            if child.is_dir():
                shutil.rmtree(child)
            else:
                child.unlink()

    print(f"Decompiling {jar} -> {destination}")

    subprocess.run([
        "java",
        "-Xmx4G",
        "-jar",
        str(vineflower),
        str(jar.resolve()),
        str(destination.resolve()),
    ], check=True)

    if not any(destination.rglob("*.java")):
        raise RuntimeError(
            f"Vineflower produced no Java sources for {jar}. "
            "Check the installed Vineflower version and CLI syntax."
        )

    marker.write_text(
        str(jar.resolve()) + "\n",
        encoding="utf-8",
    )

def run(mc_version, mode, game_dir="game_dir", vineflower=None, force=False):
    game_dir_path = Path(game_dir).resolve()
    print(f"GAME DIR: {game_dir}")
    libraries = game_dir_path / "libraries"
    output_root = Path("doxygen_sources")
    print(f"Decompiler running in {mode} mode.")

    if mode == "vanilla":
        vanilla_jar = (
            game_dir_path
            / "versions"
            / mc_version
            / f"{mc_version}.jar"
        )

        if not vanilla_jar.is_file():
            raise FileNotFoundError(
                f"Vanilla Minecraft JAR not found: {vanilla_jar}"
            )

        targets = [vanilla_jar]
    else:
        if not libraries.is_dir():
            raise FileNotFoundError(
                f"Libraries directory not found: {libraries}"
            )

        targets = find_target_jars(libraries)

    vineflower = get_vineflower(vineflower)

    for jar in targets:
        if mode == "vanilla":
            destination = output_root / jar.stem
        else:
            destination = (
                output_root / jar.parent.name / jar.stem
            )

        decompile(
            vineflower,
            jar,
            destination,
            force
        )

    print(f"\nSources generated under: {output_root}")

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "game_dir",
        nargs="?",
        default="game_dir",
        help="Minecraft/NeoForge installation directory "
             "(default: game_dir)",
    )
    parser.add_argument(
        "vineflower",
        nargs="?",
        default=None,
        help="Path to vineflower.jar",
    )
    parser.add_argument(
        "--mode",
        choices=("neoforge", "vanilla"),
        default="neoforge",
        help="Select NeoForge or vanilla Minecraft (default: neoforge)",
    )
    parser.add_argument(
        "--mc-version",
        default="26.3",
        help="Minecraft version for vanilla mode (default: 26.3)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-decompile existing output directories",
    )
    args = parser.parse_args(argv)
    run(args.game_dir, args.vineflower, args.mode, args.mc_version, args.force)
    


if __name__ == "__main__":
    try:
        main()
    except (
        OSError,
        subprocess.CalledProcessError,
        RuntimeError,
    ) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
