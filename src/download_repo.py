import json
import os
import subprocess

import requests


def get_latest_commit_id(repo_owner, repo_name):
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/commits/master"
    response = requests.get(url)
    data = response.json()
    return data["sha"]


def clone_or_update_repo(repo_owner, repo_name, destination_folder):
    repo_url = f"https://github.com/{repo_owner}/{repo_name}.git"

    if not os.path.exists(destination_folder):
        # If the folder doesn't exist, clone the repo
        subprocess.run(["git", "clone", repo_url, destination_folder])
    else:
        # If the folder exists, navigate to it and pull the latest changes
        subprocess.run(["git", "-C", destination_folder, "pull"])


def get_saved_commit_id(filename):
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return json.load(f).get("last_commit_id")
    return None


def save_commit_id(filename, commit_id):
    with open(filename, "w") as f:
        json.dump({"last_commit_id": commit_id}, f)


def download_chain_registry():
    repo_owner = "cosmos"
    repo_name = "chain-registry"
    destination_folder = "./chain-registry"

    latest_commit_id = get_latest_commit_id(repo_owner, repo_name)
    saved_commit_id = get_saved_commit_id("commit_id.json")

    if saved_commit_id != latest_commit_id:
        clone_or_update_repo(repo_owner, repo_name, destination_folder)
        save_commit_id("commit_id.json", latest_commit_id)
        print("Repository has been updated")
        return True
    else:
        print("Repository has not been updated since the last check.")
        return False


if __name__ == "__main__":
    download_chain_registry()
