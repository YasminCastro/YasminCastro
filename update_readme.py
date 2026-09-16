import os
import re
import requests

USERNAME = "YasminCastro"
README_PATH = "README.md"
START_MARKER = "<!-- PROJECTS:START -->"
END_MARKER = "<!-- PROJECTS:END -->"


def fetch_latest_projects(limit=2):
    token = os.environ.get("ACCESS_TOKEN")
    headers = {"Authorization": f"bearer {token}"} if token else {}

    response = requests.get(
        f"https://api.github.com/users/{USERNAME}/repos",
        params={"sort": "pushed", "direction": "desc", "per_page": 10},
        headers=headers,
        timeout=10,
    )
    response.raise_for_status()
    repos = response.json()

    projects = [repo for repo in repos if not repo.get("fork") and repo.get("name") != USERNAME]
    return projects[:limit]


def format_projects_line(projects):
    if not projects:
        return "🔭 I'm currently building new projects — check back soon!"

    links = [f'<a href="{repo["html_url"]}">{repo["name"]}</a>' for repo in projects]
    return f"🔭 I'm currently working on {' and '.join(links)}."


def update_readme(line):
    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    pattern = re.compile(
        re.escape(START_MARKER) + r".*?" + re.escape(END_MARKER), re.DOTALL
    )
    replacement = f"{START_MARKER} {line} {END_MARKER}"
    new_content = pattern.sub(replacement, content)

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(new_content)


def main():
    projects = fetch_latest_projects()
    line = format_projects_line(projects)
    update_readme(line)


if __name__ == "__main__":
    main()
