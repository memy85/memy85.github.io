"""Turn a vault Markdown draft into a post page and list it on its project page.

Usage: uv run --with markdown scripts/build_post.py <draft.md>
"""
import datetime, html, pathlib, re, sys
import markdown

ROOT = pathlib.Path(__file__).resolve().parent.parent
PROJECTS = {"noteaid-r1": "NoteAid-r1", "noteaid-aqg": "NoteAid-AQG",
            "patient-world-model": "Patient World Model"}

draft = pathlib.Path(sys.argv[1])
_, front, body = draft.read_text().split("---", 2)
meta = {k.strip(): v.split("#")[0].strip()
        for k, v in (line.split(":", 1) for line in front.strip().splitlines())}
project, title = meta["project"], meta["title"]
if project not in PROJECTS or not title:
    sys.exit(f"bad front matter: project={project!r} title={title!r}")
date = datetime.date.fromisoformat(meta["date"])
nice_date = f"{date:%B} {date.day}, {date.year}"
slug = draft.stem
t = html.escape(title)

page = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{t}</title>
  <link rel="stylesheet" href="../../style.css">
</head>
<body>
<main>
  <p class="links"><a href="../{project}.html">&larr; {PROJECTS[project]}</a></p>

  <article>
    <h1>{t}</h1>
    <p class="pub-venue">{nice_date}</p>
{markdown.markdown(body)}
  </article>
</main>
</body>
</html>
"""
out = ROOT / "blog" / project / f"{slug}.html"
out.parent.mkdir(exist_ok=True)
out.write_text(page)

# Add to the project's log list, newest first; skip if already listed.
index = ROOT / "blog" / f"{project}.html"
s = index.read_text()
href = f"{project}/{slug}.html"
if href not in s:
    item = (f'    <li>\n      <div class="pub-title"><a href="{href}">{t}</a></div>\n'
            f'      <div class="pub-venue"><a href="{href}">{nice_date}</a></div>\n    </li>\n')
    s = re.sub(r'(<ol class="pubs">\n)', lambda m: m.group(1) + item, s, count=1)
    index.write_text(s)
print(f"wrote {out.relative_to(ROOT)}; listed on {index.relative_to(ROOT)}")
