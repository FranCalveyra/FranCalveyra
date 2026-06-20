#!/usr/bin/env python3
import sys
from pathlib import Path

import yaml

README_PATH = Path(__file__).resolve().parent.parent / "README.md"
START_MARKER = "<!-- SKILLS:START -->"
END_MARKER = "<!-- SKILLS:END -->"

# (tag, section title, emoji, alt text for the skillicons batch image),
# in the order they're rendered in the README.
SECTIONS = [
    ("language", "Core Languages", "💾", "Programming Languages"),
    ("framework", "Frameworks & Libraries", "🚀", "Frameworks"),
    ("ai", "AI & LLM Engineering", "🤖", "AI & LLM Engineering"),
    ("cloud", "Cloud & Infrastructure", "☁️", "Cloud & Infrastructure"),
    ("testing", "Testing & DevOps", "🧪", "Testing & DevOps"),
    ("tools", "Tools & Editors", "🧰", "Tools & Editors"),
]

# A skill can carry multiple tags (e.g. GitHub Actions is both "testing" and
# "cloud"); this order decides which single README section it lands in so it
# doesn't get rendered twice. Testing must outrank cloud, and tools is the
# catch-all so it only claims skills with no other mapped tag.
ASSIGNMENT_PRIORITY = ["language", "framework", "ai", "testing", "cloud", "tools"]
TAG_TO_TITLE = {tag: title for tag, title, _, _ in SECTIONS}


def load_skills(path: Path) -> list[dict]:
    data = yaml.safe_load(path.read_text())
    return data["skills"]


def assign_section(skill: dict) -> str | None:
    tags = skill.get("tags", [])
    for tag in ASSIGNMENT_PRIORITY:
        if tag in tags:
            return TAG_TO_TITLE[tag]
    return None


def render_section(title: str, emoji: str, alt: str, skills: list[dict]) -> str:
    skillicon_ids = []
    custom_imgs = []
    for skill in skills:
        icon = skill["icon"]
        if icon.startswith("skillicons:"):
            skillicon_ids.append(icon.removeprefix("skillicons:"))
        elif icon.startswith("custom:"):
            slug = icon.removeprefix("custom:")
            custom_imgs.append(
                f'  <img src="icons/{slug}.svg" width="48" height="48" alt="{skill["name"]}" />'
            )

    lines = [f"### {emoji} {title}", "<p>"]
    if skillicon_ids:
        lines.append(
            f'  <img src="https://skillicons.dev/icons?i={",".join(skillicon_ids)}&theme=dark" alt="{alt}" />'
        )
    lines.extend(custom_imgs)
    lines.append("</p>")
    return "\n".join(lines)


def build_block(skills: list[dict]) -> str:
    by_section: dict[str, list[dict]] = {title: [] for _, title, _, _ in SECTIONS}
    for skill in skills:
        title = assign_section(skill)
        if title is not None:
            by_section[title].append(skill)

    blocks = [
        render_section(title, emoji, alt, by_section[title])
        for _, title, emoji, alt in SECTIONS
        if by_section[title]
    ]
    return "\n\n".join(blocks)


def main() -> None:
    skills_yml_path = Path(sys.argv[1])
    skills = load_skills(skills_yml_path)
    block = build_block(skills)

    readme = README_PATH.read_text()
    start = readme.index(START_MARKER) + len(START_MARKER)
    end = readme.index(END_MARKER)
    new_readme = f"{readme[:start]}\n{block}\n{readme[end:]}"

    README_PATH.write_text(new_readme)


if __name__ == "__main__":
    main()
