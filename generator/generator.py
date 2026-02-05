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


def load_manifest():
    with open(MANIFEST, "r") as f:
        return yaml.safe_load(f)


def jinja_env():
    return Environment(
        loader=FileSystemLoader(SRC),
        undefined=StrictUndefined,
        keep_trailing_newline=True,
        autoescape=False,
        lstrip_blocks=True,
        trim_blocks=True,
    )


def clean_dir(path: Path):
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True)


def copy_or_render(src: Path, dst: Path, env, context):
    dst.parent.mkdir(parents=True, exist_ok=True)

    # Rename _gitignore to .gitignore
    if src.name.startswith("_gitignore"):
        dst = dst.with_name(dst.name.replace("_gitignore", ".gitignore", 1))

    if src.suffix == ".j2":
        template = env.get_template(str(src.relative_to(SRC)))
        dst = dst.with_suffix("")  # drop .j2
        dst.write_text(template.render(context))
    else:
        shutil.copy2(src, dst)


def materialize(source_root: Path, outdir: Path, env, context):
    for src in source_root.rglob("*"):
        if src.is_dir():
            continue

        rel = src.relative_to(source_root)
        dst = outdir / rel
        copy_or_render(src, dst, env, context)


def render_template(spec: dict):
    template_id = spec["id"]
    blocks = spec.get("blocks", [])

    outdir = OUT / template_id
    print(f"→ Rendering {template_id}")
    clean_dir(outdir)

    env = jinja_env()

    context = {
        "id": spec["id"],
        "size": spec["size"],
        "language": spec["language"],
        "atoms": load_atoms(),
    }

    # 1. global files
    if FILES.exists():
        materialize(FILES, outdir, env, context)

    # 2. blocks (in order)
    for block in blocks:
        block_dir = BLOCKS / block
        if not block_dir.exists():
            raise RuntimeError(f"Unknown block: {block}")
        materialize(block_dir, outdir, env, context)


def load_atoms():
    atoms = {}

    if not CONTENT.exists():
        return atoms

    for atom_dir in CONTENT.iterdir():
        if not atom_dir.is_dir():
            continue

        atom_name = atom_dir.name
        atoms[atom_name] = {}

        for f in atom_dir.iterdir():
            if f.is_dir():
                continue

            key = f.stem

            if f.suffix in {".yml", ".yaml"}:
                with open(f, "r") as fh:
                    atoms[atom_name][key] = yaml.safe_load(fh)
            else:
                atoms[atom_name][key] = f.read_text()

    return atoms


def main():
    templates = load_manifest()

    for spec in templates:
        render_template(spec)


if __name__ == "__main__":
    main()
