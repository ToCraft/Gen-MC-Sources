import argparse
import install_neoforge
import decompile
import run_doxygen

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode",
        choices=("neoforge", "vanilla"),
        default="neoforge",
        help="Select NeoForge or vanilla Minecraft (default: neoforge)",
    )
    parser.add_argument(
        "mc_version",
        help="The Minecraft/NeoForge version you want to install. Specify ONLY one of them. The installer will automatically install both!",
    )
    args = parser.parse_args(argv)
    mcversion = args.mc_version
    mode = args.mode

    install_neoforge.run(mc_version=mcversion)
    decompile.run(mc_version=mcversion, mode=mode)
    run_doxygen.run()

if __name__ == "__main__":
    main()