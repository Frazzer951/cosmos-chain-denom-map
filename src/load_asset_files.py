import json
import os

from tqdm_logging import setup_logger

logger = setup_logger('download_repo')


def find_asset_files(root_dir, exclude_dirs=[]):
    asset_files = []

    for dirpath, dirnames, filenames in os.walk(root_dir):
        # remove excluded directories
        dirnames[:] = [d for d in dirnames if d not in exclude_dirs]

        for filename in filenames:
            if filename == "assetlist.json":
                asset_files.append(os.path.join(dirpath, filename))

    return asset_files


def load_json_files(file_paths):
    loaded_files = []

    for file_path in file_paths:
        with open(file_path, 'r') as f:
            loaded_files.append(json.load(f))

    return loaded_files


def load_assets():
    root_directory = "./chain-registry"
    exclude_directories = [".git", ".github", "_template"]

    asset_file_paths = find_asset_files(root_directory, exclude_directories)
    loaded_assets = load_json_files(asset_file_paths)

    logger.info(f'Found {len(asset_file_paths)} asset files')
    return loaded_assets


if __name__ == "__main__":
    load_assets()
