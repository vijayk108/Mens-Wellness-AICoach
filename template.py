import os
from pathlib import Path
import logging
from typing import List, Union, Tuple, Dict, Any

logging.basicConfig(level=logging.INFO, format='[%(asctime)s]:%(message)s')


# Example input. Each entry may be:
# - a string path (creates an empty file)
# - a (path, content) tuple
# - a dict with keys 'path' and optional 'content'
list_of_files = [
    "src/__init__.py",
    "src/helper.py",
    "src/prompt.py",
    ".env",
    "setup.py",
    "app.py",
    "research/trails.ipynb",
    ("README_SAMPLE.md", "# Sample README\nThis file was created by template.py\n"),
]


def create_files(
    files: List[Union[str, Tuple[str, str], Dict[str, Any]]],
    base_dir: Union[str, Path] = Path.cwd(),
    dry_run: bool = False,
    overwrite: bool = False,
    default_content: str = "",
) -> List[Path]:
    """
    Create files on disk given `files` list.

    - files: list where each item is a path string, a (path, content) tuple,
      or a dict {'path': ..., 'content': ...}.
    - base_dir: directory to resolve relative paths against.
    - dry_run: if True, logs actions but does not write files.
    - overwrite: if True, overwrite existing files.
    - default_content: used when a path-only entry is given.

    Returns list of created file Paths (or would-be-created in dry-run).
    """
    created: List[Path] = []
    base_dir = Path(base_dir)

    for entry in files:
        if isinstance(entry, (list, tuple)):
            path_str, content = str(entry[0]), str(entry[1])
        elif isinstance(entry, dict):
            path_str = str(entry.get("path"))
            content = str(entry.get("content", default_content))
        else:
            path_str = str(entry)
            content = default_content

        # Resolve target path
        target = Path(path_str)
        if not target.is_absolute():
            target = (base_dir / target).resolve()
        else:
            target = target.resolve()

        # Safety: avoid creating files outside the repository root unless absolute path intended
        # (we allow absolute paths, but log a message)
        if not dry_run:
            logging.info(f"Preparing to create: {target}")
        else:
            logging.info(f"Dry-run: would create {target}")

        parent = target.parent
        try:
            if not dry_run:
                parent.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logging.error(f"Failed to create directory {parent}: {e}")
            continue

        if target.exists() and not overwrite:
            logging.info(f"Skipping existing file (use overwrite=True to replace): {target}")
            continue

        if dry_run:
            created.append(target)
            continue

        try:
            # Write content (if empty string, still create empty file)
            target.write_text(content, encoding="utf-8")
            created.append(target)
            logging.info(f"Created file: {target}")
        except Exception as e:
            logging.error(f"Failed to write file {target}: {e}")

    return created


if __name__ == "__main__":
    # Add a small CLI so caller can choose demo vs real run and enable dry-run/overwrite.
    import argparse

    repo_root = Path(__file__).parent

    parser = argparse.ArgumentParser(description="Create files listed in `list_of_files`.")
    parser.add_argument(
        "--no-demo",
        action="store_true",
        help="Create files directly in the repository root using `list_of_files` (dangerous).",
    )
    parser.add_argument("--dry-run", action="store_true", help="Show what would be created without writing files.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing files if present.")
    args = parser.parse_args()

    if args.no_demo:
        logging.info("Creating files directly in repository root (list_of_files).")
        list_to_create = list_of_files
    else:
        logging.info("Running demo: creating files under demo_created_files/")
        list_to_create = []
        for item in list_of_files:
            # Prepend demo folder so original paths don't accidentally overwrite repo files.
            if isinstance(item, (list, tuple)):
                list_to_create.append((str(Path("demo_created_files") / item[0]), item[1]))
            else:
                list_to_create.append(str(Path("demo_created_files") / str(item)))

    created = create_files(list_to_create, base_dir=repo_root, dry_run=args.dry_run, overwrite=args.overwrite)
    logging.info(f"Finished. Created {len(created)} files.")
