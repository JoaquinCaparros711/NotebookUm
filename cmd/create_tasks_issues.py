#!/usr/bin/env python3
"""
Lee tasks.md, crea issues en GitHub para cada tarea, y actualiza tasks.md con los IDs.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class Task:
    id: str
    title: str
    description: str
    is_parallel: bool = False
    story: str | None = None
    phase: str | None = None


def parse_tasks_markdown(markdown: str) -> list[Task]:
    """
    Parsea tasks.md y extrae las tareas en formato:
    - [ ] [ID] [P?] [Story?] Description
    """
    tasks: list[Task] = []
    # Patrón para detectar tareas con checkbox
    # Ejemplo: - [ ] T001 [P] [US1] Create project structure
    task_pattern = re.compile(
        r"^\s*-\s*\[\s*\]\s+"  # Checkbox
        r"(?P<id>T\d{3})"  # Task ID (T001, T002, etc.)
        r"(?:\s+\[P\])?"  # Optional [P] for parallel
        r"(?:\s+\[US\d+\])?"  # Optional story label
        r"\s+(?P<description>.+)$",  # Description
        re.MULTILINE,
    )
    
    lines = markdown.splitlines()
    current_phase = None
    
    for line in lines:
        # Detectar fases (## Phase X:)
        if match := re.match(r"^##\s+Phase\s+\d+:", line):
            current_phase = line.strip()
            continue
        
        # Detectar tareas
        if match := task_pattern.match(line):
            task_id = match.group("id")
            description = match.group("description").strip()
            is_parallel = "[P]" in line
            
            # Extraer story label (US1, US2, etc.)
            story_match = re.search(r"\[US\d+\]", line)
            story = story_match.group() if story_match else None
            
            task = Task(
                id=task_id,
                title=f"{task_id}: {description.split(' in ')[0] if ' in ' in description else description[:50]}",
                description=description,
                is_parallel=is_parallel,
                story=story,
                phase=current_phase,
            )
            tasks.append(task)
    
    return tasks


def _run_gh(args: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    """Ejecuta comando gh."""
    return subprocess.run(
        ["gh", *args],
        cwd=str(cwd) if cwd else None,
        check=True,
        capture_output=True,
        text=True,
    )


def ensure_gh_available() -> None:
    """Verifica que gh CLI esté disponible y autenticado."""
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


def gh_issue_create(repository: str, title: str, body: str, labels: list[str] | None = None) -> dict:
    """Crea un issue en GitHub y retorna datos incluyendo el número."""
    args = [
        "issue",
        "create",
        "--repo",
        repository,
        "--title",
        title,
        "--body",
        body,
    ]
    
    # No agregar labels - para evitar error si no existen
    # Las labels se pueden crear manualmente después si es necesario
    
    result = _run_gh(args)
    
    # Parsear la salida para obtener el número de issue
    # La salida es: https://github.com/owner/repo/issues/NUMBER
    out_lines = result.stdout.strip().split()
    url = out_lines[-1] if out_lines else ""
    
    # Extraer número del URL
    issue_number = None
    if url and "/issues/" in url:
        issue_number = url.split("/issues/")[-1]
    
    return {
        "url": url,
        "number": issue_number,
    }


def build_issue_body(task: Task, tasks_path: Path) -> str:
    """Construye el body del issue a partir de la tarea."""
    return (
        f"Generado automaticamente desde `{tasks_path.name}`.\n\n"
        f"## Tarea\n**ID**: {task.id}\n**Descripción**: {task.description}\n\n"
        f"**Parallelizable**: {'Sí' if task.is_parallel else 'No'}\n"
        f"**Historia**: {task.story or 'N/A'}\n"
        f"**Fase**: {task.phase or 'N/A'}\n"
    )


def sync_tasks_to_issues(
    tasks_path: Path,
    repository: str,
    dry_run: bool = False,
) -> tuple[list[dict], dict[str, str]]:
    """
    Sincroniza tareas de tasks.md a issues en GitHub.
    Retorna: (resultados, mapeo de task_id -> issue_number)
    """
    ensure_gh_available()
    
    markdown = tasks_path.read_text(encoding="utf-8")
    tasks = parse_tasks_markdown(markdown)
    results: list[dict] = []
    task_to_issue: dict[str, str] = {}
    
    for task in tasks:
        labels = ["task"]
        if task.story:
            labels.append(task.story.lower().strip("[]"))
        if task.is_parallel:
            labels.append("parallel")
        
        # Construir título
        title = f"[TASK] {task.id}: {task.description[:60]}..."
        
        if dry_run:
            print(f"DRY-RUN: Creando issue '{title}'")
            results.append({
                "task_id": task.id,
                "title": title,
                "action": "dry-run",
                "story": task.story,
                "labels": labels,
            })
            continue
        
        try:
            issue_data = gh_issue_create(
                repository=repository,
                title=title,
                body=build_issue_body(task, tasks_path),
            )
            
            issue_number = issue_data.get("number")
            if issue_number:
                task_to_issue[task.id] = issue_number
            
            results.append({
                "task_id": task.id,
                "title": title,
                "action": "created",
                "issue_url": issue_data.get("url"),
                "issue_number": issue_number,
                "story": task.story,
                "labels": labels,
            })
            print(f"✓ {task.id}: Issue #{issue_number} creado")
        except subprocess.CalledProcessError as e:
            results.append({
                "task_id": task.id,
                "title": title,
                "action": "failed",
                "error": e.stderr,
                "story": task.story,
            })
            print(f"✗ {task.id}: Error al crear issue - {e.stderr}")
    
    return results, task_to_issue


def update_tasks_md(tasks_path: Path, task_to_issue: dict[str, str]) -> None:
    """
    Actualiza tasks.md con los números de issue creados.
    Modifica: - [ ] T001 Description
    A:        - [ ] T001 Description #123
    """
    content = tasks_path.read_text(encoding="utf-8")
    updated_content = content
    
    for task_id, issue_number in task_to_issue.items():
        # Patrón para encontrar la tarea sin número de issue
        # Buscar: - [ ] T001 (sin #número al final)
        pattern = rf"(^\s*-\s*\[\s*\]\s+{re.escape(task_id)}\s+.*?)(?:\s+#\d+)?(\s*$)"
        replacement = rf"\1 #{issue_number}\2"
        updated_content = re.sub(pattern, replacement, updated_content, flags=re.MULTILINE)
    
    tasks_path.write_text(updated_content, encoding="utf-8")
    print(f"\n✓ {tasks_path.name} actualizado con números de issue")


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Lee tasks.md y crea issues en GitHub usando gh CLI."
    )
    parser.add_argument("tasks_path", help="Ruta al archivo tasks.md")
    parser.add_argument(
        "--repo",
        default=os.getenv("GITHUB_REPOSITORY"),
        help="Repositorio GitHub en formato owner/repo",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Solo parsea y muestra las tareas, sin crear issues.",
    )
    parser.add_argument(
        "--update-file",
        action="store_true",
        help="Actualiza tasks.md con los números de issue creados.",
    )
    return parser


def main() -> int:
    parser = build_argument_parser()
    args = parser.parse_args()
    
    if not args.repo:
        parser.error("Falta --repo o GITHUB_REPOSITORY.")
    
    tasks_path = Path(args.tasks_path)
    if not tasks_path.exists():
        parser.error(f"Archivo no encontrado: {tasks_path}")
    
    print(f"Leyendo tareas desde: {tasks_path}")
    print(f"Repositorio: {args.repo}\n")
    
    results, task_to_issue = sync_tasks_to_issues(
        tasks_path=tasks_path,
        repository=args.repo,
        dry_run=args.dry_run,
    )
    
    # Mostrar resumen
    print("\n" + "=" * 60)
    print("RESUMEN DE RESULTADOS")
    print("=" * 60)
    print(json.dumps(results, ensure_ascii=False, indent=2))
    
    # Actualizar tasks.md si se solicitó
    if args.update_file and not args.dry_run and task_to_issue:
        update_tasks_md(tasks_path, task_to_issue)
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
