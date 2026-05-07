# rror

`rror` 是一个面向 Python 项目的文件镜像与同步工具，用于在本地项目目录和镜像存储目录之间复制文件或目录。

## 功能特性

- **文件镜像**：在本地项目和镜像目录之间同步文件。
- **双向同步**：支持从镜像拉取到本地，也支持从本地推送到镜像。
- **路径映射**：本地路径和镜像路径可以保持一致，也可以手动指定不同路径。
- **覆盖控制**：通过 `updata` 参数控制目标文件已存在时是否覆盖。
- **相对路径和绝对路径**：同时支持基于项目根目录的相对路径操作，以及直接使用绝对路径操作。
- **自动设置项目根目录**：导入本库后会自动查找项目根目录，并加入 `sys.path`，方便测试文件直接导入项目代码。
- **项目脚手架**：通过 `rror create [projname]` 快速创建标准 Python 项目结构。

## 安装

从源码安装：

```bash
pip install -e .
```

安装开发依赖：

```bash
pip install -e ".[dev]"
```

## 快速开始

```python
from rror import Mirror

m = Mirror()

# 从官方镜像拉取（默认）
m.pull("src/module.py")

# 从私有镜像拉取
m.pull("data/private.db", private=True)

# 推送到官方镜像并覆盖
m.push("config/settings.yaml", updata=True)

# 使用绝对路径
m.pull_abs("/local/file.txt", "/mirror/file.txt")
m.push_abs("/local/file.txt", "/mirror/file.txt")
```

## API 说明

### `Mirror()`

`Mirror` 类使用单例模式。第一次创建时会初始化配置和镜像目录；之后再次调用 `Mirror()` 都会返回同一个对象。

配置文件路径固定为项目根目录下的 `.rror`，包含 `official_remote` 和 `private_remote` 两个镜像路径。

- `private_remote` 所指向的目录在初始化时必须存在（自动创建）。
- `official_remote` 可不存在，不存在时所有操作自动降级到 `private_remote`。

默认 `.rror` 内容：

```json
{
  "official_remote": ".mirror",
  "private_remote": ".mirror"
}
```

### `remote(path=None, private=False)`

获取镜像路径。

- `path`：子路径；为 `None` 时返回远程基础目录。
- `private`：`False`（默认）返回官方路径，`True` 返回私有路径。

### `local(path=None)`

获取本地镜像路径。

- `path`：子路径；为 `None` 时返回本地基础目录。

### `pull(local_path, mirror_path=None, updata=False, private=False)`

从镜像目录复制到本地项目目录。

- `local_path`：本地目标路径。
- `mirror_path`：镜像源路径；不传时默认与 `local_path` 相同。
- `updata`：目标已存在时是否覆盖，默认 `False`。
- `private`：`True` 时从私有镜像拉取，默认 `False`（官方镜像）。

### `push(local_path, mirror_path=None, updata=False, private=False)`

从本地项目目录复制到镜像目录。

- `local_path`：本地源路径。
- `mirror_path`：镜像目标路径；不传时默认与 `local_path` 相同。
- `updata`：目标已存在时是否覆盖，默认 `False`。
- `private`：`True` 时推送到私有镜像，默认 `False`（官方镜像）。

### `pull_abs(local_path, mirror_path=None, updata=False, private=False)`

使用绝对路径从镜像位置复制到本地位置。

### `push_abs(local_path, mirror_path=None, updata=False, private=False)`

使用绝对路径从本地位置复制到镜像位置。

## 使用示例

### 备份源码目录

```python
from rror import Mirror

Mirror().push("src", "src", updata=True)
```

### 拉取共享配置

```python
from rror import Mirror

Mirror().pull("config", "config", updata=True)
```

### 推送到私有镜像

```python
from rror import Mirror

Mirror().push("docs", "docs", private=True)
```

## `create` 命令

`rror` 提供 `create` 命令，快速创建标准 Python 项目结构。默认生成无需安装的 `simple` 源码布局：

```bash
rror create [projname]
```

其中 `[projname]` 是要创建的项目名。例如：

```bash
rror create demo_project
```

执行后会在当前目录下创建 `demo_project` 文件夹，并生成以下无需安装的 simple 源码结构：

```text
demo_project/
├── README.md
├── .gitignore
├── .rror
├── pytest.ini
├── .mirror/
├── src/
│   ├── __init__.py
│   └── main.py
└── test/
    └── test_main.py
```

也可以显式指定 `--layout`：

```bash
rror create demo_project --layout simple
rror create demo_project --layout install
```

或者使用快捷参数 `--install`（等同于 `--layout install`）：

```bash
rror create demo_project --install
```

`install` 结构额外生成 `pyproject.toml` 和 `src/<package>/` 包目录：

```text
demo_project/
├── README.md
├── .gitignore
├── .rror
├── pytest.ini
├── .mirror/
├── pyproject.toml
├── src/
│   └── demo_project/
│       └── __init__.py
└── test/
    └── test_main.py
```

### 生成规则

- 项目根目录名称使用用户传入的 `[projname]`。
- 自动创建 `README.md`，标题使用项目名。
- 自动创建 `.rror`，默认 `official_remote` 和 `private_remote` 均为 `.mirror`。
- 自动创建 `pytest.ini`，默认测试目录为 `test`，并把 `src` 加入 pytest 的导入路径。
- 自动创建 `.gitignore`。
- 自动创建空的 `.mirror/` 目录，用作默认镜像目录。
- 自动创建 `test/` 目录，用于保存测试文件。
- `install` 布局会自动创建 `pyproject.toml`，并生成 `src/[package_name]/__init__.py`。
- `install` 布局下，如果 `[projname]` 中包含 `-`，包目录名会转换为合法 Python 包名，例如 `my-demo` 对应 `src/my_demo/`。
- `simple` 布局不会创建 `pyproject.toml`，会生成 `src/__init__.py` 和 `src/main.py`。
- `simple` 布局会生成 `test/test_main.py`，测试文件会先执行 `from rror import Mirror`，再通过 pytest 测试类调用 `src/main.py` 的 `main()` 函数；也可以直接执行 `python test/test_main.py` 启动 pytest。
- `create` 基于 `src/rror/templates/` 下的模板复制项目，不在 CLI 中临时拼接项目文件内容。
- 创建完成后会自动执行 `git init`，提交一次 `Initial commit`，创建 `master` 分支，并从 `master` 创建 `dev` 分支。
- 创建完成后会在命令行打印新项目的文件树。

### 冲突处理

- 如果目标项目目录已经存在，默认应停止创建并给出错误提示。
- 当前版本不会覆盖已有目录，避免误删用户文件。
- Windows 下创建完成后会尝试清除只读属性，并授予当前用户和 Everyone 完全控制权限，避免资源管理器删除或修改时提示需要管理员授权。

### 命令行参数

当前版本支持：

```bash
rror create [projname]
rror create [projname] --layout install
rror create [projname] --layout simple
rror create [projname] --install
```

参数说明：

- `--layout install`：生成可安装项目结构。
- `--layout simple`：生成无需安装的源码结构，默认值。
- `--install`：快捷参数，等同于 `--layout install`。

### 实现位置

`pyproject.toml` 中声明了命令行入口：

```toml
[project.scripts]
rror = "rror.cli:main"
```

命令实现位于：

```text
src/rror/cli.py
```

模板位于：

```text
src/rror/templates/common/
src/rror/templates/simple/
src/rror/templates/install/
```

实现使用 Python 标准库 `argparse` 和 `importlib.resources`，不引入额外依赖。

内部主要函数：

```python
def main():
    ...

def create_project(projname: str, target_dir=None, layout="simple"):
    ...

def normalize_package_name(projname: str) -> str:
    ...
```

### `pyproject.toml` 模板

生成的新项目可以使用如下基础模板：

```toml
[build-system]
requires = ["setuptools>=45", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "[projname]"
version = "0.2.0"
description = ""
readme = "README.md"
requires-python = ">=3.8"
dependencies = []

[tool.setuptools]
package-dir = {"" = "src"}

[tool.setuptools.packages.find]
where = ["src"]
```

### README 模板

生成的新项目 `README.md` 可以使用如下内容：

```markdown
# [projname]

项目说明。
```

## 项目根目录识别

本库支持自动设置项目根目录。只要测试文件或脚本首先导入了本库，模块导入时就会从当前工作目录开始向上查找项目根目录；如果没有找到，会继续尝试从当前执行文件所在目录向上查找。

找到项目根目录后，本库会自动执行以下操作：

- 将项目根目录记录为相对路径同步时使用的本地根目录。
- 将项目根目录加入 `sys.path`，让后续 `import` 可以直接从本项目根目录解析模块。

这对测试文件尤其有用。例如测试文件先导入本库后，就可以在不手动修改 `PYTHONPATH` 的情况下继续导入项目内的其他模块：

```python
from rror import Mirror

from your_project_module import some_function
```

当前实现会把包含以下任一内容的目录视为项目根目录：

- `pyproject.toml`
- `src` 目录

根目录逻辑位于 `src/rror/root.py`，并使用单例变量 `PROJ_ROOT` 保存。首次导入时会设置一次，之后再次调用会复用已有值。

## Mirror 单例与配置

Mirror 逻辑位于 `src/rror/mirror.py`。首次创建 `Mirror()` 实例时会自动读取或创建 `.rror` 配置文件，并确保私有镜像目录存在。

```python
from rror import Mirror

m = Mirror()
```

配置文件固定为项目根目录下的 `.rror`：

```json
{
  "official_remote": ".mirror",
  "private_remote": ".mirror"
}
```

- `private_remote` 在初始化时自动创建（必须存在）。
- `official_remote` 可以不存在，不存在时自动降级到 `private_remote`。
- `push()` 和 `pull()` 默认使用官方镜像，传 `private=True` 时使用私有镜像。

## 日志

复制操作会通过 Python 标准库 `logging` 记录日志，日志内容包括源路径和目标路径。可以在调用方自行配置日志输出格式、日志级别和日志文件。

## 许可证

MIT License

## 作者

Author: `HaoLiu`

Email: `hliu1997ac@163.com`
