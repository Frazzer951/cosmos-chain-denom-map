import os
import subprocess

import requests

from tqdm_logging import setup_logger

# Constants
REPO_OWNER = "cosmos"
REPO_NAME = "chain-registry"
DESTINATION_FOLDER = "./chain-registry"

logger = setup_logger("download_repo")


def get_latest_commit_id(repo_owner=REPO_OWNER, repo_name=REPO_NAME):
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/commits/master"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data["sha"]
    except requests.RequestException as e:
        logger.error(f"Error fetching latest commit ID: {e}")
        return None


def clone_or_update_repo(repo_owner=REPO_OWNER, repo_name=REPO_NAME, destination_folder=DESTINATION_FOLDER):
    repo_url = f"https://github.com/{repo_owner}/{repo_name}.git"
    try:
        if not os.path.exists(destination_folder):
            # If the folder doesn't exist, clone the repo
            subprocess.run(["git", "clone", repo_url, destination_folder], check=True)
        else:
            # If the folder exists, navigate to it and pull the latest changes
            subprocess.run(["git", "-C", destination_folder, "pull"], check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Error during git operation: {e}")
        return False
    return True


def download_chain_registry():
    latest_commit_id = get_latest_commit_id()
    if not latest_commit_id:
        return False

    if not clone_or_update_repo():
        return False

    logger.info("Repository has been updated")
    return True


if __name__ == "__main__":
    download_chain_registry()
