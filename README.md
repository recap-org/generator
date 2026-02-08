# RECAP Template Generator

This repository contains the **RECAP template generator**: a small, opinionated tool that builds reproducible research templates from composable building blocks.

Templates are rendered as standalone project directories (and later synced to GitHub template repositories). The generator is deterministic, filesystem-driven, and designed to stay boring.

If you want to *use* a RECAP template, you should use one of the generated template repositories instead.

## Core concepts

RECAP templates are built from four orthogonal concepts:

### 1. Manifest (`templates.yaml`)
Defines **which templates exist** and which building blocks they use.

```yaml
- id: r-medium
  size: medium
  language: r
  setup: Rscript -e "install.packages(c('tidyverse', 'modelsummary', 'testthat'))"
  run: make
  test: make tests
  blocks: 
    - devcontainer
    - readme
    ...
    - data/medium-large
    - assets/medium-large
```

The manifest is declarative. It does not describe file paths or content.

### 2. Blocks (`src/blocks/`)
Blocks define **which files exist and where**.

Each block is a directory that mirrors the output filesystem. Files inside blocks are:
- copied as-is
- rendered if they end in `.j2`
- turned into symlinks if they end in `.symlink`

Blocks are composable.

### 3. Atoms (`src/atoms/`)
Atoms are **shared, quasi-constant content** injected into templates.

Atoms can be declared as:
- **YAML files** → structured objects  
- **single files** → raw text blobs  
- **directories** → the same content in multiple formats  

Example structure:
```
src/atoms/
  author.yaml
  references.bib
  intro/
    intro.md
    intro.tex
```

Available in Jinja as:
```jinja
{{ atoms.author }}
{{ atoms.references }}
{{ atoms.intro.md }}
{{ atoms.intro.tex }}
```

Atoms never decide file paths — blocks do.

### 4. Jinja templates
Jinja is used **only for content**, not structure.

- Jinja decides *what a file contains*
- the filesystem decides *where the file lives*
- Python decides *which blocks are combined*

This separation is intentional.

## Repository structure

<repository tree>

## How templates are built

From the repository root:

```bash
python generator/generator.py
```

This will:
1. read the manifest (`templates.yaml`)
2. compose the declared blocks in order
3. inject atoms into the Jinja context
4. write rendered templates to the `out/` directory

The build is deterministic and idempotent.

### Testing templates

```bash
python generator/test.py
```

This will:
1. spin up each template's dev container
2. run the `setup` command
3. run the `run` command
4. run the optional `test` command (if specified)
5. write detailed logs to `logs/test-{template_id}.log`

### Deploying templates

```bash
python generator/deploy.py
```

This will:
1. clone each `recap-org/template-{id}` repository
2. sync files from `out/{id}/`
3. commit changes with generator metadata
4. push to GitHub (only if changes detected)

## Symlinks

Symlinks are declared using `.symlink` sentinel files.

Example: 
```
assets.symlink
```

with contents: 
```
../../assets
```

This produces
```
assets -> ../../assets
```

## CI

CI runs the generator and verifies that all templates build successfully.  
Generated output is treated as a build artifact, not committed source.

## Contributing

Contributions are welcome, but please follow these principles:

- do not edit generated output by hand
- prefer adding blocks over adding conditionals
- keep atoms semantic and boring
- avoid putting logic in Jinja
- fail loudly on ambiguity

If you’re unsure where something belongs:
- **structure** → blocks  
- **shared meaning** → atoms  
- **variation** → Jinja  
- **composition** → manifest  
