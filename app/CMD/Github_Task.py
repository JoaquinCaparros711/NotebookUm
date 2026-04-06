from __future__ import annotations
import argparse, json, os, re, subprocess, tempfile
from dataclasses import dataclass, field
from pathlib import Path

_PHASE_RE = re.compile(r"^##\s+(?:Phase|Fase)\s+(?P<num>\d+):\s*(?P<rest>.+)$", re.I)
_PRIORITY_RE = re.compile(r"\((?:Priority|Prioridad):\s*(?P<p>P\d+)\)")
_TASK_RE = re.compile(r"^-\s+\[[ x]\]\s+(?P<id>T\d+)\s+(?P<rest>.+)$")
_STORY_TAG = re.compile(r"\[US(?P<n>\d+)\]")
_PARALLEL_TAG = re.compile(r"\[P\]")

_LABEL_COLORS: dict[str, tuple[str, str]] = {
    "p1": ("d73a4a", "Prioridad crítica"), "p2": ("e4a435", "Prioridad media"),
    "p3": ("0075ca", "Prioridad baja"), "historia-de-usuario": ("7057ff", "Historia de usuario"),
    "high": ("b60205", "Dificultad alta"), "medium": ("fbca04", "Dificultad media"),
    "low": ("0e8a16", "Dificultad baja"), "paralelo": ("c5def5", "Puede correr en paralelo"),
    "configuración": ("bfd4f2", "Configuración inicial"), "base": ("d4c5f9", "Infraestructura base"),
    "implementación": ("1d76db", "Implementación"), "prueba": ("e99695", "Prueba/TDD"),
    "mejoras": ("f9d0c4", "Mejoras y optimización"),
}
_DIFF = {"P1": "high", "P2": "medium", "P3": "low"}
_PHASE_LABEL: dict[int, str] = {1: "configuración", 2: "base"}
_TITLE_ES: dict[str, str] = {
    "Setup": "Configuración", "Shared Infrastructure": "Infraestructura Compartida",
    "Foundational": "Base", "Blocking Prerequisites": "Prerrequisitos Bloqueantes",
    "Polish & Cross-Cutting Concerns": "Mejoras y Aspectos Transversales",
    "User Story": "Historia de Usuario",
}


@dataclass(slots=True)
class Task:
    id: str
    description: str
    phase_num: int
    story: str | None = None
    parallel: bool = False
    is_test: bool = False


@dataclass(slots=True)
class Phase:
    number: int
    title: str
    priority: str | None = None
    purpose: str = ""
    tasks: list[Task] = field(default_factory=list)


def parse_tasks_md(text: str) -> list[Phase]:
    phases: list[Phase] = []
    current: Phase | None = None
    in_purpose = False

    for line in text.splitlines():
        pm = _PHASE_RE.match(line.strip())
        if pm:
            rest = pm.group("rest")
            pri_m = _PRIORITY_RE.search(rest)
            title = _PRIORITY_RE.sub("", rest).strip().rstrip("🎯 MVP").strip()
            for eng, esp in _TITLE_ES.items():
                title = title.replace(eng, esp)
            current = Phase(number=int(pm.group("num")), title=title,
                            priority=pri_m.group("p") if pri_m else None)
            phases.append(current)
            in_purpose = True
            continue

        if current is None:
            continue

        s = line.strip()
        if in_purpose and (s.startswith("**Purpose**:") or s.startswith("**Propósito**:")):
            current.purpose = s.split(":", 1)[1].strip()
            in_purpose = False
            continue
        in_purpose = False

        tm = _TASK_RE.match(s)
        if tm:
            rest = tm.group("rest")
            story_m = _STORY_TAG.search(rest)
            desc = _STORY_TAG.sub("", _PARALLEL_TAG.sub("", rest)).strip()
            is_test = any(kw in desc.lower() for kw in ("test ", "test for"))
            current.tasks.append(Task(
                id=tm.group("id"), description=desc, phase_num=current.number,
                story=f"US{story_m.group('n')}" if story_m else None,
                parallel=bool(_PARALLEL_TAG.search(rest)), is_test=is_test,
            ))
    return phases


# ── GitHub CLI ────────────────────────────────────────────────────────────────
def gh(*args: str) -> str:
    r = subprocess.run(["gh", *args], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"gh {' '.join(args[:3])} falló:\n{r.stderr.strip() or r.stdout.strip()}")
    return r.stdout.strip()


def ensure_labels(repo: str, labels: set[str]) -> None:
    for label in labels:
        color, desc = _LABEL_COLORS.get(label, ("ededed", label))
        gh("label", "create", label, "--repo", repo, "--color", color, "--description", desc, "--force")


def get_or_create_milestone(repo: str, title: str) -> None:
    for m in json.loads(gh("api", f"repos/{repo}/milestones") or "[]"):
        if m["title"] == title:
            return
    gh("api", f"repos/{repo}/milestones", "-X", "POST",
       "-f", f"title={title}", "-f", f"description=Feature: {title}")


def create_issue(repo: str, title: str, body: str, labels: list[str], milestone: str) -> dict:
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as f:
        f.write(body)
        bf = f.name
    try:
        args = ["issue", "create", "--repo", repo, "--title", title,
                "--body-file", bf, "--milestone", milestone]
        for lb in labels:
            args += ["--label", lb]
        url = gh(*args).split()[-1]
        return {"url": url, "number": int(url.split("/")[-1])}
    finally:
        Path(bf).unlink(missing_ok=True)


def add_to_project(owner: str, number: int, url: str) -> str | None:
    try:
        gh("project", "item-add", str(number), "--owner", owner, "--url", url)
        return None
    except RuntimeError as e:
        return str(e)


def update_tasks_md(path: Path, task_id: str, url: str) -> None:
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    updated = re.sub(
        rf"(- \[[ x]\] {task_id} )", rf"\1[#{url.split('/')[-1]}]({url}) ", text, count=1,
    )
    if updated != text:
        path.write_text(updated, encoding="utf-8")


# ── Body builders ─────────────────────────────────────────────────────────────
def build_phase_body(phase: Phase, feature: str) -> str:
    task_list = "\n".join(f"- [ ] **{t.id}**: {t.description}" for t in phase.tasks)
    return (
        f"> Fase {phase.number} de `{feature}` — {phase.purpose or phase.title}\n\n"
        f"## Tareas ({len(phase.tasks)})\n{task_list}\n"
    )


def build_task_body(task: Task, phase: Phase, feature: str, parent_url: str) -> str:
    labels = f"`{task.id}` | Fase {phase.number}"
    if task.story:
        labels += f" | {task.story}"
    return (
        f"> Parte de [{phase.title}]({parent_url}) en `{feature}`\n\n"
        f"## {labels}\n{task.description}\n"
    )


# ── Orchestration ─────────────────────────────────────────────────────────────
def sync(spec_dir: Path, repo: str, project_owner: str | None = None,
         project_number: int | None = None, dry_run: bool = False) -> list[dict]:
    tasks_path = spec_dir / "tasks.md"
    phases = parse_tasks_md(tasks_path.read_text(encoding="utf-8"))
    feature = spec_dir.name
    total_tasks = sum(len(p.tasks) for p in phases)

    if dry_run:
        return [{"phase": p.number, "title": p.title, "tasks": len(p.tasks),
                 "priority": p.priority} for p in phases] + [{"total_issues": total_tasks + len(phases)}]

    get_or_create_milestone(repo, feature)
    last_phase = max(p.number for p in phases)
    all_labels: set[str] = {"paralelo"}
    for p in phases:
        all_labels.add(_PHASE_LABEL.get(p.number, "mejoras" if p.number == last_phase else "implementación"))
        if p.priority:
            all_labels |= {p.priority.lower(), _DIFF.get(p.priority, "medium")}
        for t in p.tasks:
            if t.story:
                all_labels.add("historia-de-usuario")
            if t.is_test:
                all_labels.add("prueba")
    ensure_labels(repo, all_labels)

    existing = {i["title"] for i in json.loads(
        gh("issue", "list", "--repo", repo, "--state", "all", "--limit", "500", "--json", "title")
    )}
    results: list[dict] = []

    for phase in phases:
        phase_title = f"[Fase {phase.number}] {phase.title}"
        if phase_title in existing:
            parent_url = ""
            results.append({"title": phase_title, "action": "existing"})
        else:
            phase_labels = [_PHASE_LABEL.get(phase.number, "mejoras" if phase.number == last_phase else "implementación")]
            if phase.priority:
                phase_labels += [phase.priority.lower(), _DIFF.get(phase.priority, "medium")]
            parent = create_issue(repo, phase_title, build_phase_body(phase, feature), phase_labels, feature)
            parent_url = parent["url"]
            if project_owner and project_number:
                add_to_project(project_owner, project_number, parent_url)
            results.append({"title": phase_title, "action": "created", "url": parent_url})

        for task in phase.tasks:
            title = f"[{task.id}] {task.description[:80]}"
            if title in existing:
                results.append({"title": title, "action": "existing"})
                continue
            labels = [_PHASE_LABEL.get(phase.number, "mejoras" if phase.number == last_phase else "implementación")]
            if task.story:
                labels.append("historia-de-usuario")
            if task.is_test:
                labels.append("prueba")
            if task.parallel:
                labels.append("paralelo")
            if phase.priority:
                labels += [phase.priority.lower(), _DIFF.get(phase.priority, "medium")]
            issue = create_issue(repo, title, build_task_body(task, phase, feature, parent_url), labels, feature)
            if project_owner and project_number:
                add_to_project(project_owner, project_number, issue["url"])
            update_tasks_md(tasks_path, task.id, issue["url"])
            results.append({"title": title, "action": "created", "url": issue["url"]})

    return results


def main() -> int:
    p = argparse.ArgumentParser(description="Sincroniza tasks.md → Issues de GitHub + Etiquetas + Hito + Proyecto.")
    p.add_argument("spec_dir", help="Directorio de la feature (contiene tasks.md)")
    p.add_argument("--repo", default=os.getenv("GITHUB_REPOSITORY"), help="owner/repo")
    p.add_argument("--project-owner", default=os.getenv("GITHUB_PROJECT_OWNER"))
    p.add_argument("--project-number", type=int, default=int(os.getenv("GITHUB_PROJECT_NUMBER", "0")) or None)
    p.add_argument("--dry-run", action="store_true", help="Solo parsea, sin crear issues.")
    args = p.parse_args()
    if not args.repo:
        p.error("Falta --repo o GITHUB_REPOSITORY.")
    print(json.dumps(
        sync(Path(args.spec_dir), args.repo, args.project_owner, args.project_number, args.dry_run),
        ensure_ascii=False, indent=2,
    ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
