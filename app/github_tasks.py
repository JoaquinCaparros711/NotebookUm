from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path


USER_SCENARIOS_HEADING_PATTERN = re.compile(
    r"^##\s+User Scenarios\s*&\s*Testing.*$",
    re.IGNORECASE,
)
NEXT_SECTION_PATTERN = re.compile(r"^##\s+.+$")
USER_STORY_HEADING_PATTERN = re.compile(
    r"^###\s+User Story\s+(?P<number>\d+)\s*-\s*(?P<title>.+?)\s+\(Priority:\s*(?P<priority>P\d+)\)$",
    re.IGNORECASE,
)


@dataclass(slots=True)
class UserStory:
    number: int
    title: str
    priority: str
    description: str
    why_priority: str
    independent_test: str
    acceptance_scenarios: list[str]


def extract_user_scenarios_section(markdown: str) -> str:
    lines = markdown.splitlines()
    start_index: int | None = None

    for index, line in enumerate(lines):
        if USER_SCENARIOS_HEADING_PATTERN.match(line.strip()):
            start_index = index + 1
            break

    if start_index is None:
        raise ValueError("No se encontro la seccion '## User Scenarios & Testing' en el spec.")

    section_lines: list[str] = []
    for line in lines[start_index:]:
        if NEXT_SECTION_PATTERN.match(line.strip()):
            break
        section_lines.append(line)

    section = "\n".join(section_lines).strip()
    if not section:
        raise ValueError("La seccion '## User Scenarios & Testing' esta vacia.")

    return section


def _clean_block(lines: list[str]) -> str:
    cleaned = [line.rstrip() for line in lines]
    while cleaned and not cleaned[0].strip():
        cleaned.pop(0)
    while cleaned and not cleaned[-1].strip():
        cleaned.pop()
    return "\n".join(cleaned).strip()


def parse_user_stories(markdown: str) -> list[UserStory]:
    section = extract_user_scenarios_section(markdown)
    lines = section.splitlines()
    stories: list[UserStory] = []
    current: dict | None = None

    def flush_current() -> None:
        nonlocal current
        if not current:
            return

        stories.append(
            UserStory(
                number=current["number"],
                title=current["title"],
                priority=current["priority"].upper(),
                description=_clean_block(current["description"]),
                why_priority=_clean_block(current["why_priority"]),
                independent_test=_clean_block(current["independent_test"]),
                acceptance_scenarios=[
                    scenario.strip()
                    for scenario in current["acceptance_scenarios"]
                    if scenario.strip()
                ],
            )
        )
        current = None

    mode = "description"

    for line in lines:
        stripped = line.strip()
        story_match = USER_STORY_HEADING_PATTERN.match(stripped)
        if story_match:
            flush_current()
            current = {
                "number": int(story_match.group("number")),
                "title": story_match.group("title").strip(),
                "priority": story_match.group("priority").strip(),
                "description": [],
                "why_priority": [],
                "independent_test": [],
                "acceptance_scenarios": [],
            }
            mode = "description"
            continue

        if current is None:
            continue

        if stripped.startswith("**Why this priority**:"):
            mode = "why_priority"
            value = stripped.split(":", 1)[1].strip()
            if value:
                current[mode].append(value)
            continue

        if stripped.startswith("**Independent Test**:"):
            mode = "independent_test"
            value = stripped.split(":", 1)[1].strip()
            if value:
                current[mode].append(value)
            continue

        if stripped.startswith("**Acceptance Scenarios**:"):
            mode = "acceptance_scenarios"
            continue

        if stripped == "---":
            flush_current()
            mode = "description"
            continue

        current[mode].append(line)

    flush_current()

    if not stories:
        raise ValueError("No se encontraron user stories parseables en el spec.")

    return stories


def _run_gh(args: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["gh", *args],
        cwd=str(cwd) if cwd else None,
        check=True,
        capture_output=True,
        text=True,
    )


def ensure_gh_available() -> None:
    try:
        _run_gh(["--version"])
    except FileNotFoundError as error:
        raise RuntimeError(
            "No se encontro 'gh'. Instala GitHub CLI y autenticalo con 'gh auth login'."
        ) from error
    except subprocess.CalledProcessError as error:
        raise RuntimeError(
            f"No se pudo ejecutar 'gh --version': {error.stderr.strip() or error.stdout.strip()}"
        ) from error


def gh_issue_list(repository: str) -> list[dict]:
    result = _run_gh(
        [
            "issue",
            "list",
            "--repo",
            repository,
            "--state",
            "all",
            "--limit",
            "200",
            "--json",
            "title,url,number",
        ]
    )
    return json.loads(result.stdout or "[]")


def gh_issue_create(repository: str, title: str, body: str, labels: list[str]) -> dict:
    args = [
        "issue",
        "create",
        "--repo",
        repository,
        "--title",
        title,
        "--body",
        body,
        "--json",
        "id,number,title,url",
    ]
    for label in labels:
        args.extend(["--label", label])

    result = _run_gh(args)
    return json.loads(result.stdout)


def gh_project_item_add(project_owner: str, project_number: int, issue_url: str) -> None:
    _run_gh(
        [
            "project",
            "item-add",
            str(project_number),
            "--owner",
            project_owner,
            "--url",
            issue_url,
        ]
    )


def find_existing_issue(issues: list[dict], title: str) -> dict | None:
    for issue in issues:
        if issue.get("title") == title:
            return issue
    return None


def build_issue_title(story: UserStory) -> str:
    return f"[{story.priority}] User Story {story.number}: {story.title}"


def build_issue_body(story: UserStory, spec_path: Path) -> str:
    acceptance = "\n".join(story.acceptance_scenarios).strip()
    acceptance_block = acceptance if acceptance else "- Sin escenarios definidos"
    description = story.description or "Sin descripcion"
    why_priority = story.why_priority or "Sin justificacion"
    independent_test = story.independent_test or "Sin test independiente"

    return (
        f"Generado automaticamente desde `{spec_path}`.\n\n"
        f"## Historia de Usuario\n{description}\n\n"
        f"## Prioridad\n- {story.priority}\n- {why_priority}\n\n"
        f"## Prueba Independiente\n{independent_test}\n\n"
        f"## Acceptance Scenarios\n{acceptance_block}\n"
    )


def sync_spec_user_stories(
    spec_path: Path,
    repository: str,
    project_owner: str | None = None,
    project_number: int | None = None,
    dry_run: bool = False,
) -> list[dict]:
    ensure_gh_available()
    stories = parse_user_stories(spec_path.read_text(encoding="utf-8"))
    existing_issues = gh_issue_list(repository) if not dry_run else []
    results: list[dict] = []

    for story in stories:
        title = build_issue_title(story)
        labels = [story.priority.lower(), "user-story"]
        existing_issue = find_existing_issue(existing_issues, title)

        if dry_run:
            results.append(
                {
                    "title": title,
                    "priority": story.priority,
                    "labels": labels,
                    "action": "dry-run",
                }
            )
            continue

        if existing_issue:
            issue_data = existing_issue
            action = "existing"
        else:
            issue_data = gh_issue_create(
                repository=repository,
                title=title,
                body=build_issue_body(story, spec_path),
                labels=labels,
            )
            action = "created"

        if project_owner and project_number is not None:
            gh_project_item_add(project_owner, project_number, issue_data["url"])

        results.append(
            {
                "title": title,
                "priority": story.priority,
                "labels": labels,
                "action": action,
                "issue_url": issue_data.get("url"),
            }
        )

    return results


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Lee user stories de spec.md y crea issues en GitHub usando gh CLI."
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
        help="Owner del GitHub Project",
    )
    parser.add_argument(
        "--project-number",
        type=int,
        default=int(os.getenv("GITHUB_PROJECT_NUMBER", "0")) or None,
        help="Numero del GitHub Project",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Solo parsea y muestra las historias, sin crear issues.",
    )
    return parser


def main() -> int:
    parser = build_argument_parser()
    args = parser.parse_args()

    if not args.repo:
        parser.error("Falta --repo o GITHUB_REPOSITORY.")

    results = sync_spec_user_stories(
        spec_path=Path(args.spec_path),
        repository=args.repo,
        project_owner=args.project_owner,
        project_number=args.project_number,
        dry_run=args.dry_run,
    )
    print(json.dumps(results, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
