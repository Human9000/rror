import sys
import logging 
import shutil
from pathlib import Path

PROJ_ROOT = None


def print_divider(text="", char="="):
    """pytest 中的分隔线"""
    width = shutil.get_terminal_size().columns 
    BOLD = '\033[1m'
    END = '\033[0m'
    if text:
        text = f" {BOLD}{text}{END} "
        padding = width - len(text)
        left_pad = padding // 2
        right_pad = padding - left_pad
        print(f"{char * left_pad}{text}{char * right_pad}")
    else:
        print(char * width)


def is_root(path):
    path = Path(path)
    return (path / "src").is_dir() \
        or (path / "test").is_dir() \
        or (path / ".mirror").is_dir() \
        or (path / "pytest.ini").is_file() \
        or (path / "pyproject.toml").is_file() \
        or (path / ".rror").is_file() 


def _find_project_root(start_path):
    path = Path(start_path).resolve()

    while True:
        if is_root(path):
            return path

        parent = path.parent
        if parent == path:
            return None

        path = parent


def _default_start_paths():

    main_file = getattr(sys.modules.get("__main__"), "__file__", '')
    main_file_path = Path(main_file).resolve()
    print('main_file:', main_file_path)
    if main_file:
        yield main_file_path.parent
        
    workspace = Path.cwd().resolve()  # 工作目录
    print('workspace:', workspace)
    yield workspace


def get_proj_root(start_path=None):
    global PROJ_ROOT
    print_divider("Import Time: get_proj_root")
    if PROJ_ROOT is not None:
        return PROJ_ROOT

    paths = [Path(start_path).resolve()] if start_path is not None else list(_default_start_paths())
    # print("paths:", paths)
    for path in paths:
        root = _find_project_root(path)
        if root is not None:
            PROJ_ROOT = root
            print(f"PROJ_ROOT: {root}") 
            logging.info(f"Set PROJ_ROOT:`{root}`")
            if str(root) not in sys.path:
                sys.path.insert(0, str(root))
                sys.path.insert(0, str(root/'src'))
            return PROJ_ROOT
    print(flush=True)
    raise RuntimeError("未找到项目根目录，请确保在项目根目录或其子目录下运行脚本。")


def set_proj_root_path_to_sys_from_cmd(path=None):
    get_proj_root(path)
    return True


try:
    PROJ_ROOT = get_proj_root()
except RuntimeError:
    PROJ_ROOT = None
