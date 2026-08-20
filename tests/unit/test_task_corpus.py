"""The task corpus is consumed by a harness in another repository, so its shape
is validated here rather than discovered there."""

import pathlib
import re

import pytest
import yaml

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
TASKS_DIR = REPO_ROOT / "tests" / "tasks"
SCHEMA_KEYS = {
    "id",
    "prompt",
    "skill",
    "category",
    "required_all",
    "required_any",
    "forbidden",
    "rubric",
    "expected_refs",
    "blacklist_targets",
    "weight",
}


def _tasks():
    for path in sorted(TASKS_DIR.glob("*.yaml")):
        for entry in yaml.safe_load(path.read_text(encoding="utf-8")) or []:
            yield path.name, entry


def test_the_corpus_is_not_empty():
    assert list(_tasks())


@pytest.mark.parametrize(
    "filename,task",
    list(_tasks()),
    ids=lambda v: v["id"] if isinstance(v, dict) else v,
)
def test_task_uses_only_schema_keys(filename, task):
    assert set(task) <= SCHEMA_KEYS, f"{task['id']} in {filename}"


def test_task_ids_are_unique():
    ids = [task["id"] for _name, task in _tasks()]

    assert len(ids) == len(set(ids))


def test_every_regex_field_compiles():
    bad = []
    for _name, task in _tasks():
        for field in ("required_all", "required_any", "forbidden"):
            for pattern in task.get(field, []):
                try:
                    re.compile(pattern)
                except re.error as exc:
                    bad.append(f"{task['id']}.{field}: {pattern!r} ({exc})")

    assert bad == []


def test_expected_refs_name_files_that_exist():
    missing = []
    for _name, task in _tasks():
        skill_dir = REPO_ROOT / "skills" / task["skill"]
        for ref in task.get("expected_refs", []):
            if not (skill_dir / "references" / ref).exists() and not (skill_dir / ref).exists():
                missing.append(f"{task['id']} -> {ref}")

    assert missing == []


def test_data_modeling_is_covered():
    skills = {task["skill"] for _name, task in _tasks()}

    assert "aerospike-data-modeling" in skills
