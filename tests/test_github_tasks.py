from app.github_tasks import extract_tasks_section, parse_tasks_from_markdown


def test_extract_tasks_section_reads_section_four():
    markdown = """
1. Contexto
Texto

4. Tareas (issues?)
- [ ] Crear endpoint para subir archivos
- [x] Agregar validaciones

5. Notas
Texto final
"""
    section = extract_tasks_section(markdown)
    assert "Crear endpoint para subir archivos" in section
    assert "Agregar validaciones" in section
    assert "5. Notas" not in section


def test_parse_tasks_from_markdown_returns_expected_tasks():
    markdown = """
# Spec

4. Tareas
1. [ ] Crear issue inicial
- [x] Conectar GitHub Project
+ Documentar workflow
"""
    tasks = parse_tasks_from_markdown(markdown)

    assert [task.title for task in tasks] == [
        "Crear issue inicial",
        "Conectar GitHub Project",
        "Documentar workflow",
    ]
    assert [task.completed for task in tasks] == [False, True, False]
