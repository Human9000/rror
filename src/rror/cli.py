import argparse
import os

os.environ.setdefault("PROJMIRROR_SKIP_IMPORT_INIT", "1")

import re
import stat
import subprocess
import sys
import shutil
from pathlib import Path


def normalize_package_name(projname):
    package_name = re.sub(r"[^0-9A-Za-z_]", "_", projname)
    package_name = re.sub(r"_+", "_", package_name).strip("_").lower()

    if not package_name:
        raise ValueError("项目名无法转换为合法的 Python 包名")

    if package_name[0].isdigit():
        package_name = "_" + package_name

    if not package_name.isidentifier():
        raise ValueError("项目名无法转换为合法的 Python 包名")

    return package_name


def _validate_project_name(projname):
    if not projname or not projname.strip():
        raise ValueError("项目名不能为空")

    if "/" in projname or "\\" in projname:
        raise ValueError("项目名不能包含路径分隔符")


def _make_user_writable(project_dir):
    for path in [project_dir, *project_dir.rglob("*")]:
        try:
            path.chmod(path.stat().st_mode | stat.S_IWRITE)
        except OSError:
            pass

    if os.name != "nt":
        return

    user_domain = os.environ.get("USERDOMAIN")
    username = os.environ.get("USERNAME")
    if not username:
        return

    user = f"{user_domain}\\{username}" if user_domain else username
    subprocess.run(
        ["icacls", str(project_dir), "/setowner", user, "/T", "/C"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    subprocess.run(
        ["icacls", str(project_dir), "/grant", f"{user}:(OI)(CI)F", "/T", "/C"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    subprocess.run(
        ["icacls", str(project_dir), "/grant", "*S-1-1-0:(OI)(CI)F", "/T", "/C"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )


def _canonical_layout(layout):
    if layout == "simple":
        return "simple"
    if layout == "install":
        return "install"
    raise ValueError("layout 必须是 install 或 simple")


def _copy_template(layout, project_dir):
    templates_dir = Path(__file__).resolve().parent / "templates"
    common_template_path = templates_dir / "common"
    layout_template_path = templates_dir / layout

    shutil.copytree(common_template_path, project_dir)
    shutil.copytree(layout_template_path, project_dir, dirs_exist_ok=True)
    (project_dir / ".mirror").mkdir(exist_ok=True)


def _replace_placeholders(project_dir, projname, package_name):
    replacements = {
        "__PROJNAME__": projname,
        "__PACKAGE_NAME__": package_name,
    }

    package_marker = project_dir / "src" / "__PACKAGE_NAME__"
    if package_marker.exists():
        package_marker.rename(project_dir / "src" / package_name)

    for path in project_dir.rglob("*"):
        if not path.is_file():
            continue

        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue

        updated = text
        for old, new in replacements.items():
            updated = updated.replace(old, new)

        if updated != text:
            path.write_text(updated, encoding="utf-8")


def _run_git(project_dir, args, env=None):
    try:
        return subprocess.run(
            ["git", *args],
            cwd=project_dir,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
    except FileNotFoundError as exc:
        raise RuntimeError("未找到 git 命令，请先安装 Git") from exc
    except subprocess.CalledProcessError as exc:
        message = (exc.stderr or exc.stdout or str(exc)).strip()
        raise RuntimeError(f"git {' '.join(args)} 执行失败：{message}") from exc


def _init_git_repo(project_dir):
    env = os.environ.copy()
    env.setdefault("GIT_AUTHOR_NAME", "projmirror")
    env.setdefault("GIT_AUTHOR_EMAIL", "projmirror@example.local")
    env.setdefault("GIT_COMMITTER_NAME", env["GIT_AUTHOR_NAME"])
    env.setdefault("GIT_COMMITTER_EMAIL", env["GIT_AUTHOR_EMAIL"])

    _run_git(project_dir, ["init"])
    _run_git(project_dir, ["branch", "-M", "master"])
    _run_git(project_dir, ["add", "."])
    _run_git(project_dir, ["commit", "-m", "Initial commit"], env=env)
    _run_git(project_dir, ["checkout", "-b", "dev", "master"])


def _format_tree(root):
    root = Path(root)
    lines = [f"{root.name}/"]

    def sort_key(path):
        return (path.is_file(), path.name.lower())

    def add_children(directory, prefix=""):
        entries = [path for path in directory.iterdir() if path.name != ".git"]
        entries = sorted(entries, key=sort_key)
        for index, path in enumerate(entries):
            is_last = index == len(entries) - 1
            connector = "└── " if is_last else "├── "
            suffix = "/" if path.is_dir() else ""
            lines.append(f"{prefix}{connector}{path.name}{suffix}")

            if path.is_dir():
                child_prefix = prefix + ("    " if is_last else "│   ")
                add_children(path, child_prefix)

    add_children(root)
    return "\n".join(lines)


def create_project(projname, target_dir=None, layout="simple"):
    _validate_project_name(projname)
    layout = _canonical_layout(layout)

    package_name = normalize_package_name(projname)
    base_dir = Path.cwd() if target_dir is None else Path(target_dir)
    project_dir = base_dir / projname

    if project_dir.exists():
        raise FileExistsError(f"目标项目目录已存在：{project_dir}")

    _copy_template(layout, project_dir)
    _replace_placeholders(project_dir, projname, package_name)
    _init_git_repo(project_dir)

    _make_user_writable(project_dir)

    return project_dir


def _build_parser():
    parser = argparse.ArgumentParser(prog="projmirror")
    subparsers = parser.add_subparsers(dest="command")

    create_parser = subparsers.add_parser("create", help="创建标准 Python 项目结构")
    create_parser.add_argument("projname", help="要创建的项目名")
    create_parser.add_argument(
        "--layout",
        choices=("install", "simple"),
        default="simple",
        help="项目结构类型：simple 为无需安装的源码结构，install 为可安装 src 包结构",
    )
    create_parser.add_argument(
        "--install",
        action="store_true",
        help="生成可安装的 src 包结构，等同于 --layout install",
    )

    return parser


def main(argv=None):
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "create":
        # 解析项目名和目标目录
        projname_input = args.projname
        if "/" in projname_input or "\\" in projname_input:
            path = Path(projname_input)
            projname = path.name
            if path.parent == Path("."):
                target_dir = None
            else:
                target_dir = str(path.parent)
        else:
            projname = projname_input
            target_dir = None

        layout = "install" if args.install else _canonical_layout(args.layout)
        try:
            project_dir = create_project(projname, target_dir=target_dir, layout=layout)
        except (FileExistsError, RuntimeError, ValueError) as exc:
            print(f"错误：{exc}", file=sys.stderr)
            return 1

        print(f"已创建项目：{project_dir}")
        print(f"项目结构：{layout}")
        print("文件树：")
        print(_format_tree(project_dir))
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
