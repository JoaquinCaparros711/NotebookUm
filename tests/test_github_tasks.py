from app.github_tasks import (
    build_issue_body,
    build_issue_title,
    extract_user_scenarios_section,
    parse_user_stories,
)
from pathlib import Path


def test_extract_user_scenarios_section_reads_only_story_block():
    markdown = """
## User Scenarios & Testing

### User Story 1 - Crear resumen de archivos (Priority: P1)
Como usuario quiero resumir un archivo.

**Why this priority**: Entrega el valor principal.

**Independent Test**: Subir un archivo valido y obtener resumen.

**Acceptance Scenarios**:

1. **Given** un archivo valido, **When** lo proceso, **Then** obtengo un resumen

---

## Requirements

- FR-001
"""
    section = extract_user_scenarios_section(markdown)
    assert "Crear resumen de archivos" in section
    assert "Requirements" not in section


def test_parse_user_stories_returns_priority_and_content():
    markdown = """
## User Scenarios & Testing

### User Story 1 - Crear issue inicial (Priority: P1)
Como PO quiero sincronizar historias para planificar el trabajo.

**Why this priority**: Sin esto no existe el flujo base.

**Independent Test**: Ejecutar el script y ver una issue creada.

**Acceptance Scenarios**:

1. **Given** un spec valido, **When** corro el script, **Then** se crea una issue

---

### User Story 2 - Agregar al project (Priority: P2)
Como PO quiero que las issues entren al project automaticamente.

**Why this priority**: Reduce trabajo manual.

**Independent Test**: Crear una issue y verla en el project.

**Acceptance Scenarios**:

1. **Given** un project configurado, **When** corro el script, **Then** la issue se agrega al board
"""
    stories = parse_user_stories(markdown)

    assert [story.title for story in stories] == [
        "Crear issue inicial",
        "Agregar al project",
    ]
    assert [story.priority for story in stories] == ["P1", "P2"]
    assert "sincronizar historias" in stories[0].description.lower()
    assert len(stories[0].acceptance_scenarios) == 1


def test_build_issue_title_and_body_include_priority():
    markdown = """
## User Scenarios & Testing

### User Story 3 - Priorizar backlog (Priority: P3)
Como PO quiero priorizar automaticamente las historias.

**Why this priority**: Mejora la organizacion.

**Independent Test**: Ver la label p3 en GitHub.

**Acceptance Scenarios**:

1. **Given** una historia P3, **When** se crea la issue, **Then** tiene label p3
"""
    story = parse_user_stories(markdown)[0]

    assert build_issue_title(story) == "[P3] User Story 3: Priorizar backlog"

    body = build_issue_body(story, Path("spec.md"))
    assert "## Prioridad" in body
    assert "P3" in body
    assert "Mejora la organizacion." in body
