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
        return {}


def _write_config(config_path, *, official_remote=None, private_remote=None):
    data = {}
    if official_remote is not None:
        data["official_remote"] = str(official_remote)
    if private_remote is not None:
        data["private_remote"] = str(private_remote)
    config_path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _resolve_remote(configured_path, config_key):
    path = configured_path.get(config_key, "") or configured_path.get("mirror_path", "") or DEFAULT_MIRROR_DIR
    return Path(path).expanduser().resolve()


def init_mirror_config(proj_root):
    if proj_root is None:
        return None, None, None

    proj_root = Path(proj_root)
    config_path = proj_root / CONFIG_FILENAME
    if config_path.exists():
        config_data = _read_config(config_path)
    else:
        config_data = {}
        _write_config(config_path, official_remote=DEFAULT_MIRROR_DIR, private_remote=DEFAULT_MIRROR_DIR)

    official_root = _resolve_remote(config_data, "official_remote")
    private_root = _resolve_remote(config_data, "private_remote")
    private_root.mkdir(parents=True, exist_ok=True)

    return config_path, official_root, private_root


class Mirror:
    _instance = None          # 单例实例
    _root = None              # 项目根目录
    _local = None             # 本地镜像目录（始终 .mirror）
    _official_remote = None   # 官方远程路径
    _private_remote = None    # 私有远程路径（official 不存在时降级到此）
    _config = None            # 配置文件路径

    def __new__(cls, ):
        if cls._instance is None:
            cls._instance = super().__new__(cls) 
        return cls._instance

    def __init__(self,):  
        if self._root != None:
            return
        self._root = PROJ_ROOT
        self._local = Path(PROJ_ROOT) / DEFAULT_MIRROR_DIR
        self._config, self._official_remote, self._private_remote = init_mirror_config(proj_root=PROJ_ROOT)
         
    @property
    def config_path(self):
        return self._config

    def _get_remote_base(self, private=False):
        if private:
            return self._private_remote
        if self._official_remote is not None and self._official_remote.exists():
            return self._official_remote
        return self._private_remote
 

    def pull(self, local_path, mirror_path=None, updata=False, private=False):
        if mirror_path is None:
            mirror_path = local_path

        assert self._official_remote is not None, "未设置 remote"

        return self._copy(
            src=self.remote(mirror_path, private=private),
            dst=self.local(local_path),
            updata=updata,
        )

    def push(self, local_path, mirror_path=None, updata=False, private=False):
        if mirror_path is None:
            mirror_path = local_path

        if self._official_remote is None and self._private_remote is None:
            return self.remote(mirror_path, private=private)

        return self._copy(
            src=self.local(local_path),
            dst=self.remote(mirror_path, private=private),
            updata=updata,
        )

    def pull_abs(self, local_path, mirror_path=None, updata=False, private=False):
        if mirror_path is None:
            mirror_path = Path(str(local_path).replace(
                str(self._local),
                str(self._get_remote_base(private))
            ))
        return self._copy(
            src=mirror_path,
            dst=local_path,
            updata=updata,
        )

    def push_abs(self, local_path, mirror_path=None, updata=False, private=False):
        if mirror_path is None:
            mirror_path = Path(str(local_path).replace(
                str(self._local),
                str(self._get_remote_base(private))
            ))
        return self._copy(
            src=local_path,
            dst=mirror_path,
            updata=updata,
        )

    def remote(self, path=None, private=False):
        base = self._get_remote_base(private)
        if path is None:
            return str(base)
        return str(base / path)

    def local(self, path=None):
        base =  self._local
        if path is None:
            return str(base)
        return str(base / path)

    def _copy(self, src, dst, updata=False):
        src_path = Path(src)
        dst_path = Path(dst)
         
        logging.debug("start copy:%s to %s", src_path, dst_path)
        if src_path.resolve() == dst_path.resolve() and not updata:
            return str(dst_path)
 
        assert src_path.exists() or dst_path.exists() , f"src: {src_path} 和 dst: {dst_path}文件均不存在:"
            
        if not src_path.exists():
            return str(dst_path)

        if dst_path.exists() and not updata:
            return str(dst_path)

        dst_path.parent.mkdir(parents=True, exist_ok=True)

        if src_path.is_dir(): 
            shutil.copytree(src_path, dst_path, dirs_exist_ok=True)
        else:
            shutil.copyfile(src_path, dst_path)

        logging.debug("end copy:%s to %s", src_path, dst_path)
        return str(dst_path)


# mirror = Mirror() if PROJ_ROOT is not None else None
