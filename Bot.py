import requests
from mastodon import Mastodon
import time
import json

# GitHub API configurations
GITHUB_USERNAME = "Your GitHub username"
GITHUB_ACCESS_TOKEN = "Your GitHub access token"
GITHUB_API_URL = f"https://api.github.com/users/{GITHUB_USERNAME}/repos"

# Mastodon API configurations
MASTODON_API_URL = "Your Mastodon API URL"
MASTODON_ACCESS_TOKEN = "Your Mastodon access token"


# Initialize Mastodon client
mastodon = Mastodon(
    access_token=MASTODON_ACCESS_TOKEN,
    api_base_url=MASTODON_API_URL
)

def get_user_repositories():
    headers = {
        "Authorization": f"token {GITHUB_ACCESS_TOKEN}"
    }
    url = f"https://api.github.com/users/{GITHUB_USERNAME}/repos"
    response = requests.get(url, headers=headers)
    response_json = response.json()
    repositories = [repo["name"] for repo in response_json]
    return repositories

def get_latest_commit_sha(repo_name):
    headers = {
        "Authorization": f"token {GITHUB_ACCESS_TOKEN}"
    }
    url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{repo_name}/commits"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        response_json = response.json()
        if response_json:
            latest_commit_sha = response_json[0]["sha"]
            return latest_commit_sha
    return None

def load_last_commit_shas():
    try:
        with open("last_commit_shas.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_last_commit_shas(last_commit_shas):
    with open("last_commit_shas.json", "w") as file:
        json.dump(last_commit_shas, file)

def post_to_mastodon(message):
    mastodon.status_post(message)

def main():
    repositories = get_user_repositories()
    last_commit_shas = load_last_commit_shas()

    while True:
        for repo in repositories:
            latest_commit_sha = get_latest_commit_sha(repo)

            if latest_commit_sha and latest_commit_sha != last_commit_shas.get(repo):
                commit_url = f"https://github.com/{GITHUB_USERNAME}/{repo}/commit/{latest_commit_sha}"
                message = f"New commit detected on GitHub in repository '{repo}': {commit_url}"
                post_to_mastodon(message)
                last_commit_shas[repo] = latest_commit_sha

        save_last_commit_shas(last_commit_shas)

        # Adjust the sleep duration (in seconds) based on how often you want to check for updates
        time.sleep(300)  # Check every 5 minutes

if __name__ == "__main__":
    main()