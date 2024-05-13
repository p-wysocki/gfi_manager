from sys import argv
from datetime import datetime, timedelta
from github_api import get_repository_issues
from dataclasses import dataclass
from typing import Union


@dataclass
class GitHubIssue:
    number: int
    url: str
    state: str
    title: str
    owner: str
    assignee_name: Union[str, None]
    assignee_url: Union[str, None]
    created_at: datetime.date
    updated_at: datetime.date
    closed_at: Union[datetime.date, None]
    time_since_update: datetime.date

def remove_gfi_prefix(text, prefix = "[Good First Issue]"):
    if text.startswith(prefix):
        return text[len(prefix):]
    return text

def parse_issues(issues_json):
    """
    Returns a list of GitHubIssue objects sorted by time_since_update
    """
    issues = []
    current_time = datetime.now()
    for raw_issue in issues_json:

        if raw_issue["assignee"]:
            assignee_name = raw_issue["assignee"]["login"]
            assignee_url = raw_issue["assignee"]["html_url"]
        else:
            assignee_name = None
            assignee_url = None

        if raw_issue["closed_at"]:
            closed_at = datetime.strptime(raw_issue["closed_at"], "%Y-%m-%dT%H:%M:%SZ")
        else:
            closed_at = None

        issues.append(
            GitHubIssue(
                number = raw_issue["number"],
                url = raw_issue["html_url"],
                state = raw_issue["state"],
                title = remove_gfi_prefix(raw_issue["title"]),
                owner = raw_issue["user"]["login"],
                assignee_name = assignee_name,
                assignee_url = assignee_url,
                created_at = datetime.strptime(raw_issue["created_at"], "%Y-%m-%dT%H:%M:%SZ"),
                updated_at = datetime.strptime(raw_issue["updated_at"], "%Y-%m-%dT%H:%M:%SZ"),
                closed_at = closed_at,
                time_since_update = current_time - datetime.strptime(raw_issue["updated_at"], "%Y-%m-%dT%H:%M:%SZ"),
            )
        )
        sorted_issues = sorted(issues, key=lambda issue: issue.time_since_update)

    return sorted_issues

if __name__ == "__main__":
    issues = parse_issues(get_repository_issues())
    try:
        days_without_update = argv[1]
    except IndexError:
        days_without_update = 7
    time_period = timedelta(days=int(days_without_update))
    print(f"Isses with time since update longer than {time_period.days} days:")
    i = 1
    for issue in issues:
        if issue.time_since_update > time_period and issue.state != "closed":
            print(f"{i}.\t {issue.title[:50]}...\t | {issue.url} | Time since last update: {issue.time_since_update.days}")
            i += 1
