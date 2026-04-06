from __future__ import annotations

import argparse
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path


TASK_SECTION_PATTERN = re.compile(
    r"^(#{1,6}\s*)?4\.\s*Tareas(?:\s*\(.*?\))?\s*$",
    re.IGNORECASE,
)
HEADING_PATTERN = re.compile(r"^(#{1,6}\s+.+|\d+\.\s+.+)$")
TASK_LINE_PATTERN = re.compile(
    r"^\s*(?:(?:[-*+]\s+(?:\[(?P<checked>[ xX])\]\s*)?)|(?:\d+\.\s+\[(?P<numbered_checked>[ xX])\]\s*))(?P<text>.+?)\s*$"
)


@dataclass(slots=True)
class TaskItem:
    title: str
    completed: bool = False


def extract_tasks_section(markdown: str) -> str:
    lines = markdown.splitlines()
    start_index: int | None = None

    for index, line in enumerate(lines):
        if TASK_SECTION_PATTERN.match(line.strip()):
            start_index = index + 1
            break

    if start_index is None:
        raise ValueError("No se encontro la seccion '4. Tareas' en el spec.")

    section_lines: list[str] = []
    for line in lines[start_index:]:
        stripped_line = line.strip()
        if HEADING_PATTERN.match(stripped_line) and not TASK_LINE_PATTERN.match(stripped_line):
            break
        section_lines.append(line)

    return "\n".join(section_lines).strip()


def parse_tasks_from_markdown(markdown: str) -> list[TaskItem]:
    section = extract_tasks_section(markdown)
    tasks: list[TaskItem] = []

    for line in section.splitlines():
        match = TASK_LINE_PATTERN.match(line)
        if not match:
            continue

        task_text = match.group("text").strip()
        if not task_text:
            continue

        tasks.append(
            TaskItem(
                title=task_text,
                completed=((match.group("checked") or match.group("numbered_checked") or "").lower() == "x"),
            )
        )

    if not tasks:
        raise ValueError("La seccion '4. Tareas' no contiene tareas parseables.")

    return tasks


class GitHubClient:
    def __init__(self, token: str, api_base_url: str = "https://api.github.com") -> None:
        self.token = token
        self.api_base_url = api_base_url.rstrip("/")

    def _request(
        self,
        method: str,
        path: str,
        payload: dict | None = None,
        graphql: bool = False,
    ) -> dict:
        url = f"{self.api_base_url}{path}"
        data = None
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self.token}",
            "User-Agent": "NotebookUm-spec-sync",
        }

        if payload is not None:
            data = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"

        request = urllib.request.Request(url, data=data, headers=headers, method=method)

        try:
            with urllib.request.urlopen(request) as response:
                charset = response.headers.get_content_charset() or "utf-8"
                body = response.read().decode(charset)
                return json.loads(body) if body else {}
        except urllib.error.HTTPError as error:
            charset = error.headers.get_content_charset() or "utf-8"
            body = error.read().decode(charset)
            raise RuntimeError(
                f"GitHub API error ({error.code}) en {path}: {body}"
            ) from error

    def find_issue_by_title(self, repository: str, title: str) -> dict | None:
        query = urllib.parse.quote(title)
        data = self._request(
            "GET",
            f"/repos/{repository}/issues?state=all&per_page=100&creator=&labels=&sort=created&direction=desc",
        )

        for issue in data:
            if issue.get("pull_request"):
                continue
            if issue.get("title") == title:
                return issue
        return None

    def create_issue(self, repository: str, title: str, body: str) -> dict:
        return self._request(
            "POST",
            f"/repos/{repository}/issues",
            {"title": title, "body": body},
        )

    def get_project_v2_id(self, owner: str, number: int) -> str:
        query = """
        query($owner: String!, $number: Int!) {
          user(login: $owner) {
            projectV2(number: $number) { id }
          }
          organization(login: $owner) {
            projectV2(number: $number) { id }
          }
        }
        """
        response = self._request(
            "POST",
            "/graphql",
            {"query": query, "variables": {"owner": owner, "number": number}},
            graphql=True,
        )
        data = response.get("data", {})
        project = (data.get("user") or {}).get("projectV2") or (
            data.get("organization") or {}
        ).get("projectV2")
        if not project:
            raise RuntimeError(
                f"No se pudo resolver el GitHub Project v2 owner={owner} number={number}."
            )
        return project["id"]

    def add_issue_to_project(self, project_id: str, issue_node_id: str) -> dict:
        mutation = """
        mutation($projectId: ID!, $contentId: ID!) {
          addProjectV2ItemById(input: {projectId: $projectId, contentId: $contentId}) {
            item { id }
          }
        }
        """
        return self._request(
            "POST",
            "/graphql",
            {
                "query": mutation,
                "variables": {"projectId": project_id, "contentId": issue_node_id},
            },
            graphql=True,
        )


def build_issue_body(task: TaskItem, spec_path: Path) -> str:
    status = "completada" if task.completed else "pendiente"
    return (
        "Issue generado automaticamente desde spec.md.\n\n"
        f"- Origen: `{spec_path}`\n"
        f"- Estado en spec: `{status}`\n"
    )


def sync_spec_tasks(
    spec_path: Path,
    repository: str,
    token: str,
    project_owner: str | None = None,
    project_number: int | None = None,
    dry_run: bool = False,
) -> list[dict]:
    tasks = parse_tasks_from_markdown(spec_path.read_text(encoding="utf-8"))
    results: list[dict] = []

    if dry_run:
        return [
            {
                "title": task.title,
                "completed": task.completed,
                "action": "dry-run",
            }
            for task in tasks
        ]

    client = GitHubClient(token=token)
    project_id = None
    if project_owner and project_number is not None:
        project_id = client.get_project_v2_id(project_owner, project_number)

    for task in tasks:
        existing_issue = client.find_issue_by_title(repository, task.title)
        issue = existing_issue
        action = "existing"

        if issue is None:
            issue = client.create_issue(
                repository=repository,
                title=task.title,
                body=build_issue_body(task, spec_path),
            )
            action = "created"

        if project_id and issue.get("node_id"):
            client.add_issue_to_project(project_id=project_id, issue_node_id=issue["node_id"])

        results.append(
            {
                "title": task.title,
                "completed": task.completed,
                "action": action,
                "issue_url": issue.get("html_url"),
            }
        )

    return results


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Lee spec.md, extrae '4. Tareas' y crea issues en GitHub."
    )
    parser.add_argument("spec_path", help="Ruta al archivo spec.md")
    parser.add_argument(
        "--repo",
        default=os.getenv("GITHUB_REPOSITORY"),
        help="Repositorio GitHub en formato owner/repo",
    )
    parser.add_argument(
        "--project-owner",
        default=os.getenv("GITHUB_PROJECT_OWNER"),
        help="Owner del GitHub Project v2",
    )
    parser.add_argument(
        "--project-number",
        type=int,
        default=int(os.getenv("GITHUB_PROJECT_NUMBER", "0")) or None,
        help="Numero del GitHub Project v2",
    )
    parser.add_argument(
        "--token",
        default=os.getenv("GITHUB_TOKEN"),
        help="Token GitHub con permisos para issues y projects",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Solo parsea y muestra tareas, sin crear issues.",
    )
    return parser


def main() -> int:
    parser = build_argument_parser()
    args = parser.parse_args()

    if not args.repo:
        parser.error("Falta --repo o GITHUB_REPOSITORY.")

    if not args.dry_run and not args.token:
        parser.error("Falta --token o GITHUB_TOKEN.")

    results = sync_spec_tasks(
        spec_path=Path(args.spec_path),
        repository=args.repo,
        token=args.token or "",
        project_owner=args.project_owner,
        project_number=args.project_number,
        dry_run=args.dry_run,
    )

    print(json.dumps(results, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
