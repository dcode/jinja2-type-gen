# Tutorial Example

## Initialize a new project

```bash
mkdir tutorial
cd tutorial
uv init --name tutorial --app --build-backend hatch  --author-from git  --no-workspace
```

## Add jinja2-type-gen as a workspace dependency

!!! note
If your `utotiral` project has a virtual env folder (e.g. `.venv`), you should delete that first.

```bash
uv add jinja2-type-gen --workspace
```

## Add jinja2 as a dependency

```bash
uv add jinja2
```

## Add jinja2-type-gen as a workspace dependency

```bash
uv add jinja2-type-gen --workspace
```
