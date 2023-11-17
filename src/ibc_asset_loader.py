import json
import os

from tqdm_logging import setup_logger

logger = setup_logger("ibc_asset_loader")


def find_asset_files(root_dir, exclude_dirs=None):
    """Find asset files in the specified directory while excluding some."""

    if exclude_dirs is None:
        exclude_dirs = []

    asset_files = []

    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Remove excluded directories
        dirnames[:] = [d for d in dirnames if d not in exclude_dirs]

        for filename in filenames:
            if filename == "assetlist.json":
                asset_files.append(os.path.join(dirpath, filename))

    return asset_files


def load_json_files(file_paths):
    """Load JSON data from the specified file paths."""
    loaded_files = []

    for file_path in file_paths:
        with open(file_path, "r") as f:
            loaded_files.append(json.load(f))

    return loaded_files


def load_assets():
    """Load asset files from the chain registry."""
    root_directory = "./chain-registry"
    exclude_directories = [".git", ".github", "_template"]

    asset_file_paths = find_asset_files(root_directory, exclude_directories)
    loaded_assets = load_json_files(asset_file_paths)

    logger.info(f"Found {len(asset_file_paths)} asset files")
    return loaded_assets


def load_ibc_files():
    """Load IBC files from the IBC directory in the chain registry."""
    ibc_directory = "./chain-registry/_IBC"

    # Get all file paths in the IBC directory
    ibc_file_paths = [
        os.path.join(ibc_directory, filename)
        for filename in os.listdir(ibc_directory)
        if os.path.isfile(os.path.join(ibc_directory, filename))
    ]

    # Load the files
    loaded_ibc_files = load_json_files(ibc_file_paths)

    logger.info(f"Found {len(ibc_file_paths)} IBC files")
    return loaded_ibc_files


if __name__ == "__main__":
    load_assets()
