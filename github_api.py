import requests
import os

TOKEN_PATH = os.path.join(os.path.dirname(__file__), "gh_token.txt")
if not os.path.isfile(TOKEN_PATH):
    raise FileNotFoundError(f"The file {TOKEN_PATH} does not exist, create it and put there your GitHub Token with Issue Read permissions.")
with open(TOKEN_PATH, 'r') as file:
    TOKEN = file.read().strip()

OPENVINO_REPO_URL = "https://api.github.com/repos/openvinotoolkit/openvino/issues"


def parse_pagination_header(header):
    links = header.split(", ")
    urls = {link.split("; ")[1][5:-1]: link.split("; ")[0][1:-1] for link in links}
    return urls.get("next", None)


def get_repository_issues():
    issues = []

    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {TOKEN}",
    }

    params = {
        "labels": "good first issue",
        "state": "all",
        "per_page": "100"
    }

    response = requests.get(OPENVINO_REPO_URL, headers=headers, params=params)
    if response.status_code != 200:
        raise RuntimeError(f"Request failed with status code {response.status_code}: {response.reason}")
    issues.extend(response.json())
    next_page_url = parse_pagination_header(response.headers["Link"])

    while next_page_url:
        response = requests.get(next_page_url, headers=headers)
        if response.status_code != 200:
            raise RuntimeError(f"Request failed with status code {response.status_code}: {response.reason}")
        issues.extend(response.json())
        next_page_url = parse_pagination_header(response.headers["Link"])
    
    return issues
