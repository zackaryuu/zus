import requests
import json

if __name__ == "__main__":
    url = "https://api.github.com/orgs/zackaryuu/repos"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch repositories: {response.status_code}")
        exit(1)

    eligibles = {}
    repos = response.json()
    for repo in repos:
        # filter
        if repo["archived"]:
            continue

        if repo["name"].startswith("z") or repo["name"].startswith("old"):
            continue

        topics = repo["topics"]
        if "no-update" in topics:
            eligibles[repo["name"]] = False
        else:
            eligibles[repo["name"]] = True

    with open("src/zs/mods/orgRepos.json", "w") as f:
        json.dump(eligibles, f)
        
