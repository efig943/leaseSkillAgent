# tests/test_skill_format.py
import os
import yaml

def test_skill_frontmatter():
    skill_path = ".agents/skills/generate-lease/SKILL.md"
    assert os.path.exists(skill_path), "SKILL.md must exist"
    with open(skill_path) as f:
        content = f.read()
    assert content.startswith("---"), "Must have YAML frontmatter"
    parts = content.split("---")
    assert len(parts) >= 3, "Frontmatter must be enclosed in ---"
    frontmatter = yaml.safe_load(parts[1])
    assert frontmatter["name"] == "generate-lease"
    assert frontmatter["description"].startswith("Use when")
    desc = frontmatter["description"].lower()
    assert "lease" in desc or "template" in desc
