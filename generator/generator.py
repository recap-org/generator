from pathlib import Path
import shutil
import yaml

from jinja2 import Environment, FileSystemLoader, StrictUndefined


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
BLOCKS = SRC / "blocks"
FILES = SRC / "files"
OUT = ROOT / "out"
MANIFEST = ROOT / "templates.yaml"
CONTENT = SRC / "atoms"

# Delimiter overrides by file extension
JINJA_ENV_OVERRIDES = {
    ".tex": {
        "block_start_string": "<!",
        "block_end_string": "!>",
        "variable_start_string": "<<",
        "variable_end_string": ">>",
        "comment_start_string": "<#",
        "comment_end_string": "#>",
    },
}


def load_manifest():
    with open(MANIFEST, "r") as f:
        return yaml.safe_load(f)


def jinja_env(file_ext=None):
    """Create a Jinja2 environment, optionally with custom delimiters for specific file types.

    Args:
        file_ext: File extension (e.g., '.tex') to use custom delimiters, or None for defaults.
    """
    kwargs = {
        "loader": FileSystemLoader(SRC),
        "undefined": StrictUndefined,
        "keep_trailing_newline": True,
        "autoescape": False,
        "lstrip_blocks": True,
        "trim_blocks": True,
    }

    # Apply delimiter overrides if specified for this file type
    if file_ext and file_ext in JINJA_ENV_OVERRIDES:
        kwargs.update(JINJA_ENV_OVERRIDES[file_ext])

    return Environment(**kwargs)


def clean_dir(path: Path):
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True)


def create_symlink(dst: Path, target: str):
    if dst.exists() or dst.is_symlink():
        dst.unlink()

    dst.symlink_to(target)


def copy_or_render(src: Path, dst: Path, context):
    dst.parent.mkdir(parents=True, exist_ok=True)

    # Rename _gitignore to .gitignore
    if src.name.startswith("_gitignore"):
        dst = dst.with_name(dst.name.replace("_gitignore", ".gitignore", 1))

    # Handle symlink sentinel
    if src.suffix == ".symlink":
        link_name = dst.with_suffix("")  # remove .symlink
        target = src.read_text().strip()

        create_symlink(link_name, target)
        return

    # Handle Jinja templates
    if src.suffix == ".j2":
        # Determine the target file extension (what it will be after .j2 is removed)
        # e.g., ".tex" from "main.tex.j2"
        target_ext = "".join(dst.suffixes[:-1])
        if not target_ext:
            # If there's no extension before .j2, check the stem
            target_ext = Path(dst.stem).suffix  # e.g., ".tex" from "main.tex"

        # Create environment with appropriate delimiters for the target file type
        env = jinja_env(target_ext)
        template = env.get_template(str(src.relative_to(SRC)))
        dst = dst.with_suffix("")  # drop .j2
        dst.write_text(template.render(context))
    else:
        shutil.copy2(src, dst)


def materialize(source_root: Path, outdir: Path, context):
    for src in source_root.rglob("*"):
        if src.is_dir():
            continue

        rel = src.relative_to(source_root)
        dst = outdir / rel
        copy_or_render(src, dst, context)


def render_template(spec: dict):
    template_id = spec["id"]
    blocks = spec.get("blocks", [])

    outdir = OUT / template_id
    print(f"→ Rendering {template_id}")
    clean_dir(outdir)

    context = {
        "id": spec["id"],
        "size": spec["size"],
        "language": spec["language"],
        "setup": spec["setup"],
        "run": spec["run"],
        "atoms": load_atoms(),
    }

    # 1. global files
    if FILES.exists():
        materialize(FILES, outdir, context)

    # 2. blocks (in order)
    for block in blocks:
        block_dir = BLOCKS / block
        if not block_dir.exists():
            raise RuntimeError(f"Unknown block: {block}")
        materialize(block_dir, outdir, context)


def load_atoms():
    atoms = {}

    if not CONTENT.exists():
        return atoms

    for entry in CONTENT.iterdir():
        name = entry.stem if entry.is_file() else entry.name

        if name in atoms:
            raise RuntimeError(f"Atom name collision: '{name}'")

        # --------------------------------------------------
        # Case 1: YAML atom (structured)
        # --------------------------------------------------
        if entry.is_file() and entry.suffix in {".yml", ".yaml"}:
            with open(entry, "r") as fh:
                atoms[name] = yaml.safe_load(fh)

        # --------------------------------------------------
        # Case 2: single-file atom (raw text)
        # --------------------------------------------------
        elif entry.is_file():
            atoms[name] = entry.read_text()

        # --------------------------------------------------
        # Case 3: directory atom (multi-format)
        # --------------------------------------------------
        elif entry.is_dir():
            atom = {}

            for f in entry.iterdir():
                if f.is_dir():
                    continue

                if not f.suffix:
                    raise RuntimeError(
                        f"Atom file '{f}' must have an extension"
                    )

                key = f.suffix.lstrip(".")

                if key in atom:
                    raise RuntimeError(
                        f"Duplicate atom key '{key}' in '{entry.name}'"
                    )

                if f.suffix in {".yml", ".yaml"}:
                    with open(f, "r") as fh:
                        atom[key] = yaml.safe_load(fh)
                else:
                    atom[key] = f.read_text()

            atoms[entry.name] = atom

    return atoms


def main():
    templates = load_manifest()

    for spec in templates:
        render_template(spec)


if __name__ == "__main__":
    main()
