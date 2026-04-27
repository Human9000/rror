import json
import logging
import shutil
from pathlib import Path 
from .root import PROJ_ROOT


CONFIG_FILENAME = ".rror"
DEFAULT_MIRROR_DIR = ".mirror"


def _read_config(config_path):
    try:
        return json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"mirror_path": ""}


def _write_config(config_path, mirror_path):
    data = {"mirror_path": str(mirror_path or "")}
    config_path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def init_mirror_config(proj_root):
    if proj_root is None:
        return None, None

    proj_root = Path(proj_root)
    config_path = proj_root / CONFIG_FILENAME 
    if config_path.exists():
        configured_path = _read_config(config_path).get("mirror_path", "")
    else:
        configured_path = DEFAULT_MIRROR_DIR
        _write_config(config_path, configured_path) 
    if not configured_path:
        configured_path = DEFAULT_MIRROR_DIR
        _write_config(config_path, configured_path)

    mirror_root = Path(configured_path).expanduser()
    mirror_root = mirror_root.resolve()
    mirror_root.mkdir(parents=True, exist_ok=True)
    return config_path, mirror_root


class Mirror:
    _instance = None
    _root = None
    _local = None
    _remote = None
    _config= None

    def __new__(cls, ):
        if cls._instance is None:
            cls._instance = super().__new__(cls) 
        return cls._instance

    def __init__(self,):  
        if self._root != None:
            return
        self._root = PROJ_ROOT
        self._local = Path(PROJ_ROOT) / DEFAULT_MIRROR_DIR
        self._config, self._remote = init_mirror_config(proj_root=PROJ_ROOT)
        

    def _read_config(self):
        return _read_config(self._config)

    def _write_config(self, mirror_path):
        _write_config(self._config, mirror_path)

    @property
    def local_root(self):
        return self._local

    @property
    def mirror_root(self):
        return self._remote

    @property
    def config_path(self):
        return self._config

    def pull(self, local_path, mirror_path=None, updata=False): 
        if mirror_path is None:
            mirror_path = local_path

        assert self._remote is not None , "未设置 remote"

        return self._copy(
            src=self.mirror(mirror_path),
            dst=self.local(local_path),
            updata=updata,
        )

    def push(self, local_path, mirror_path=None, updata=False):
        if mirror_path is None:
            mirror_path = local_path

        if self._remote is None:
            return self.mirror(mirror_path)

        return self._copy(
            src=self.local(local_path),
            dst=self.mirror(mirror_path),
            updata=updata,
        )

    def pull_abs(self, local_path, mirror_path=None, updata=False):
        if mirror_path is None:
            mirror_path = Path(str(local_path).replace(
                str(self._local),
                str(self._remote)
            ))
        return self._copy(
            src=mirror_path,
            dst=local_path,
            updata=updata,
        )

    def push_abs(self, local_path, mirror_path=None, updata=False):
        if mirror_path is None:
            mirror_path = Path(str(local_path).replace(
                str(self._local),
                str(self._remote)
            ))
        return self._copy(
            src=local_path,
            dst=mirror_path,
            updata=updata,
        )

    def mirror(self, path): 
        return str(self._remote / path)

    def local(self, path):
        return str(self._local / path)

    def _copy(self, src, dst, updata=False):
        src_path = Path(src)
        dst_path = Path(dst)
        

        if src_path.resolve() == dst_path.resolve() and not updata:
            return str(dst_path)
 
        assert src_path.exists() or dst_path.exists() , f"src: {src_path} 和 dst: {dst_path}文件均不存在:"
            
            # return str(dst_path)
        if not src_path.exists():
            return str(dst_path)

        if dst_path.exists() and not updata:
            return str(dst_path)

        dst_path.parent.mkdir(parents=True, exist_ok=True)

        if src_path.is_dir():
            # if dst_path.exists() and updata:
            #     shutil.rmtree(dst_path)
            shutil.copytree(src_path, dst_path, dirs_exist_ok=True)
        else:
            shutil.copyfile(src_path, dst_path)
            
        logging.info("copy:%s to %s", src_path, dst_path)
        return str(dst_path)


# mirror = Mirror() if PROJ_ROOT is not None else None
