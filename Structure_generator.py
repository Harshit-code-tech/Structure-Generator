from __future__ import annotations

import fnmatch
import os
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox


COMMON_IGNORE_PATTERNS: tuple[str, ...] = (
    ".git/",
    ".hg/",
    ".svn/",
    ".idea/",
    ".vscode/",
    ".DS_Store",
    "Thumbs.db",
    "desktop.ini",
    "__pycache__/",
    "*.pyc",
    "*.pyo",
    "*.pyd",
    "*.so",
    "*.dll",
    "*.dylib",
    "*.egg-info/",
    ".pytest_cache/",
    ".mypy_cache/",
    ".ruff_cache/",
    ".tox/",
    ".nox/",
    ".coverage",
    ".venv/",
    "venv/",
    "env/",
    "ENV/",
    "node_modules/",
    "dist/",
    "build/",
    "target/",
    "coverage/",
    ".cache/",
    "*.log",
)


def _read_gitignore_patterns(folder: Path) -> list[str]:
    gitignore_file = folder / ".gitignore"
    if not gitignore_file.is_file():
        return []

    patterns: list[str] = []
    for raw_line in gitignore_file.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        patterns.append(line)
    return patterns


def _matches_pattern(relative_path: Path, pattern: str, is_dir: bool) -> bool:
    path_text = relative_path.as_posix()
    name = relative_path.name

    dir_only = pattern.endswith("/")
    cleaned = pattern.rstrip("/")
    if cleaned.startswith("/"):
        cleaned = cleaned[1:]

    if dir_only and not is_dir:
        return False

    if "/" in cleaned:
        if fnmatch.fnmatch(path_text, cleaned):
            return True
        if is_dir and path_text.startswith(f"{cleaned}/"):
            return True
        return False

    return fnmatch.fnmatch(name, cleaned)


def _is_ignored(relative_path: Path, is_dir: bool, patterns: list[str]) -> bool:
    ignored = False
    for raw_pattern in patterns:
        negate = raw_pattern.startswith("!")
        pattern = raw_pattern[1:] if negate else raw_pattern
        if not pattern:
            continue

        if _matches_pattern(relative_path, pattern, is_dir):
            ignored = not negate

    return ignored


def _build_tree(folder: Path, ignore_unwanted: bool) -> str:
    ignore_patterns: list[str] = list(COMMON_IGNORE_PATTERNS)
    if ignore_unwanted:
        # If .gitignore exists, merge its rules with common defaults.
        ignore_patterns.extend(_read_gitignore_patterns(folder))

    lines: list[str] = [f"{folder.name}/"]

    for root_text, dirs, files in os.walk(folder, topdown=True):
        root = Path(root_text)
        relative_root = root.relative_to(folder)
        level = 0 if relative_root == Path(".") else len(relative_root.parts)

        if ignore_unwanted and relative_root != Path("."):
            if _is_ignored(relative_root, is_dir=True, patterns=ignore_patterns):
                dirs.clear()
                continue

        dirs.sort()
        files.sort()

        if ignore_unwanted:
            filtered_dirs: list[str] = []
            for directory in dirs:
                relative_dir = (relative_root / directory) if relative_root != Path(".") else Path(directory)
                if not _is_ignored(relative_dir, is_dir=True, patterns=ignore_patterns):
                    filtered_dirs.append(directory)
            dirs[:] = filtered_dirs

            files = [
                filename
                for filename in files
                if not _is_ignored(
                    (relative_root / filename) if relative_root != Path(".") else Path(filename),
                    is_dir=False,
                    patterns=ignore_patterns,
                )
            ]

        if relative_root != Path("."):
            lines.append(f"{'    ' * level}├── {root.name}/")

        file_indent = "    " * (level + 1)
        for filename in files:
            lines.append(f"{file_indent}├── {filename}")

    return "\n".join(lines)


class StructureGeneratorApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Folder Structure Generator")

        self.folder_path_var = tk.StringVar()
        self.mode_var = tk.StringVar(value="ignore")
        self.preview_text_widget: tk.Text | None = None

        self._build_ui()

    def _build_ui(self) -> None:
        folder_frame = tk.Frame(self.root)
        folder_frame.pack(padx=10, pady=10, fill="x")

        label = tk.Label(folder_frame, text="Selected Folder:")
        label.pack(side=tk.LEFT)

        entry = tk.Entry(folder_frame, textvariable=self.folder_path_var, width=55)
        entry.pack(side=tk.LEFT, padx=5)

        browse_button = tk.Button(folder_frame, text="Browse", command=self.browse_folder)
        browse_button.pack(side=tk.LEFT)

        mode_frame = tk.LabelFrame(self.root, text="Generation Mode", padx=10, pady=8)
        mode_frame.pack(padx=10, pady=5, fill="x")

        full_option = tk.Radiobutton(
            mode_frame,
            text="1) Generate full structure",
            value="full",
            variable=self.mode_var,
        )
        full_option.pack(anchor="w")

        ignore_option = tk.Radiobutton(
            mode_frame,
            text="2) Ignore unwanted (uses .gitignore if present + common ignores)",
            value="ignore",
            variable=self.mode_var,
        )
        ignore_option.pack(anchor="w")

        action_frame = tk.Frame(self.root)
        action_frame.pack(pady=8)

        preview_button = tk.Button(action_frame, text="Generate Preview", command=self.generate_preview)
        preview_button.pack(side=tk.LEFT, padx=4)

        save_button = tk.Button(action_frame, text="Save Structure", command=self.save_structure)
        save_button.pack(side=tk.LEFT, padx=4)

        preview_frame = tk.LabelFrame(self.root, text="Structure Preview", padx=8, pady=8)
        preview_frame.pack(padx=10, pady=(0, 10), fill="both", expand=True)

        preview_scrollbar = tk.Scrollbar(preview_frame)
        preview_scrollbar.pack(side=tk.RIGHT, fill="y")

        self.preview_text_widget = tk.Text(
            preview_frame,
            wrap="none",
            height=18,
            width=100,
            yscrollcommand=preview_scrollbar.set,
        )
        self.preview_text_widget.pack(side=tk.LEFT, fill="both", expand=True)
        preview_scrollbar.config(command=self._preview_scroll_command)

    def browse_folder(self) -> None:
        selected = filedialog.askdirectory()
        if selected:
            self.folder_path_var.set(selected)

    def save_structure(self) -> None:
        tree_structure = self._generate_tree_from_inputs()
        if tree_structure is None:
            return

        save_path = filedialog.asksaveasfilename(
            initialfile=f"structure_{Path(self.folder_path_var.get().strip()).name}.txt",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )

        if not save_path:
            return

        Path(save_path).write_text(tree_structure, encoding="utf-8")
        messagebox.showinfo("Success", f"Structure saved to {save_path}")

    def generate_preview(self) -> None:
        tree_structure = self._generate_tree_from_inputs()
        if tree_structure is None or self.preview_text_widget is None:
            return

        self.preview_text_widget.delete("1.0", tk.END)
        self.preview_text_widget.insert("1.0", tree_structure)

    def _generate_tree_from_inputs(self) -> str | None:
        folder_text = self.folder_path_var.get().strip()
        if not folder_text:
            messagebox.showerror("Error", "Please select a folder first.")
            return None

        folder = Path(folder_text)
        if not folder.is_dir():
            messagebox.showerror("Error", "Selected path is not a valid folder.")
            return None

        ignore_unwanted = self.mode_var.get() == "ignore"
        return _build_tree(folder=folder, ignore_unwanted=ignore_unwanted)

    def _preview_scroll_command(self, *args: str) -> None:
        if self.preview_text_widget is None:
            return
        self.preview_text_widget.tk.call(str(self.preview_text_widget), "yview", *args)


def main() -> None:
    root = tk.Tk()
    StructureGeneratorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
