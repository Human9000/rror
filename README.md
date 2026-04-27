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
from rror import mirror

# 首次导入会自动设置项目根目录，并创建 Mirror 单例

# 从镜像目录拉取文件到本地项目：镜像 -> 本地
mirror.pull("src/module.py", "src/module.py")

# 从本地项目推送文件到镜像目录：本地 -> 镜像
mirror.push("config/settings.yaml", "config/settings.yaml", updata=True)

# 使用绝对路径
mirror.pull_abs("/local/file.txt", "/mirror/file.txt")
mirror.push_abs("/local/file.txt", "/mirror/file.txt")
```

## API 说明

### `mirror`

`mirror` 是导入时创建的全局 Mirror 单例对象：

```python
from rror import mirror
```

首次 `import rror` 时会完成以下操作：

- 自动识别项目根目录并加入 `sys.path`。
- 在项目根目录下读取 `.projmirror` 配置文件。
- 如果 `.projmirror` 不存在，则自动创建。
- 如果 `.mirror/` 目录不存在，则自动创建。
- 根据配置中的 `mirror_path` 设置远程镜像目录。

默认 `.projmirror` 内容：

```json
{
  "mirror_path": ".mirror"
}
```

默认镜像目录是项目根目录下的 `.mirror/`。如果 `.projmirror` 不存在、`mirror_path` 为空，或 `.mirror/` 不存在，首次 `import rror` 会自动初始化这些内容。

### `Mirror()`

`Mirror` 类使用单例模式。第一次创建时会初始化配置和镜像目录；之后再次调用 `Mirror()` 都会返回同一个对象，不会重复初始化。

`Mirror()` 不接受 `mirror_path` 或 `config_path` 参数。配置文件路径固定为项目根目录下的 `.projmirror`，镜像目录固定从 `.projmirror` 中的 `mirror_path` 字段读取。

### `pull(local_path, mirror_path=None, updata=False)`

从镜像目录复制到本地项目目录，路径基于项目根目录。

- `local_path`：本地项目中的目标路径。
- `mirror_path`：镜像目录中的源路径；不传时默认与 `local_path` 相同。
- `updata`：目标路径已存在时是否覆盖，默认值为 `False`。

### `push(local_path, mirror_path=None, updata=False)`

从本地项目目录复制到镜像目录，路径基于项目根目录。

- `local_path`：本地项目中的源路径。
- `mirror_path`：镜像目录中的目标路径；不传时默认与 `local_path` 相同。
- `updata`：目标路径已存在时是否覆盖，默认值为 `False`。

### `pull_abs(local_path, mirror_path=None, updata=False)`

使用绝对路径从镜像位置复制到本地位置。

- `local_path`：本地目标路径。
- `mirror_path`：镜像源路径；不传时默认与 `local_path` 相同。
- `updata`：目标路径已存在时是否覆盖，默认值为 `False`。

### `push_abs(local_path, mirror_path=None, updata=False)`

使用绝对路径从本地位置复制到镜像位置。

- `local_path`：本地源路径。
- `mirror_path`：镜像目标路径；不传时默认与 `local_path` 相同。
- `updata`：目标路径已存在时是否覆盖，默认值为 `False`。

## 使用示例

### 备份源码目录

```python
from rror import mirror

mirror.push("src", "src", updata=True)
```

### 拉取共享配置

```python
from rror import mirror

mirror.pull("config", "config", updata=True)
```

### 简单双向同步

```python
from rror import mirror

mirror.pull("docs", "docs")
mirror.push("docs", "docs")
```

## `create` 命令

`rror` 提供 `create` 命令，用于快速创建标准 Python 项目结构。默认生成可安装的 `src` 包布局：

```bash
rror create [projname]
```

其中 `[projname]` 是要创建的项目名。例如：

```bash
rror create demo_project
```

执行后会在当前目录下创建 `demo_project` 文件夹，并生成以下无需安装的 sample 源码结构：

```text
demo_project/
├── README.md
├── .gitignore
├── .projmirror
├── pytest.ini
├── .mirror/
├── src/
│   ├── __init__.py
│   └── main.py
└── test/
    └── test_main.py
```

也可以显式指定 sample 源码结构：

```bash
rror create demo_project --layout sample
```

`simple` 是兼容旧版本的别名，也会生成 sample 结构：

```bash
rror create demo_project --layout simple
```

或者使用快捷参数：

```bash
rror create demo_project --no-install
```

sample 结构不会生成 `pyproject.toml`，`src` 下面直接放源码文件：

```text
demo_project/
├── README.md
├── .gitignore
├── .projmirror
├── pytest.ini
├── .mirror/
├── src/
│   ├── __init__.py
│   └── main.py
└── test/
    └── test_main.py
```

### 生成规则

- 项目根目录名称使用用户传入的 `[projname]`。
- 自动创建 `README.md`，标题使用项目名。
- 自动创建 `.projmirror`，默认 `mirror_path` 为 `.mirror`。
- 自动创建 `pytest.ini`，默认测试目录为 `test`，并把 `src` 加入 pytest 的导入路径。
- 自动创建 `.gitignore`，其中会忽略 `data/` 和 `.mirror/` 目录。
- 自动创建空的 `.mirror/` 目录，用作默认本地镜像目录。
- 自动创建 `test/` 目录，用于保存测试文件。
- `install` 布局会自动创建 `pyproject.toml`，并生成 `src/[package_name]/__init__.py`。
- `install` 布局下，如果 `[projname]` 中包含 `-`，包目录名会转换为合法 Python 包名，例如 `my-demo` 对应 `src/my_demo/`。
- `sample` 布局不会创建 `pyproject.toml`，会生成 `src/__init__.py` 和 `src/main.py`。
- `sample` 布局会生成 `test/test_main.py`，测试文件会先执行 `from rror import mirror`，再通过 pytest 测试类调用 `src/main.py` 的 `main()` 函数；也可以直接执行 `python test/test_main.py` 启动 pytest。
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
rror create [projname] --layout sample
rror create [projname] --layout simple
rror create [projname] --no-install
```

参数说明：

- `--layout install`：生成可安装项目结构。
- `--layout sample`：生成无需安装的 sample 源码结构，默认值。
- `--layout simple`：兼容旧版本，等同于 `--layout sample`。
- `--no-install`：快捷参数，等同于 `--layout sample`。

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
src/rror/templates/sample/
src/rror/templates/install/
```

实现使用 Python 标准库 `argparse` 和 `importlib.resources`，不引入额外依赖。

内部主要函数：

```python
def main():
    ...

def create_project(projname: str, target_dir=None, layout="sample"):
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
version = "0.1.0"
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
from rror import mirror

from your_project_module import some_function
```

当前实现会把包含以下任一内容的目录视为项目根目录：

- `pyproject.toml`
- `src` 目录

根目录逻辑位于 `src/rror/root.py`，并使用单例变量 `PROJ_ROOT` 保存。首次导入时会设置一次，之后再次调用会复用已有值。

## Mirror 单例与配置

Mirror 逻辑位于 `src/rror/mirror.py`。首次 `import rror` 会确保 `.projmirror` 和 `.mirror/` 存在。访问 `mirror` 时会创建全局单例：

```python
from rror import mirror
```

配置文件固定为项目根目录下的 `.projmirror`。如果文件不存在，首次启动会自动创建：

```json
{
  "mirror_path": ".mirror"
}
```

默认镜像目录是项目根目录下的 `.mirror/`。如果配置文件不存在、`mirror_path` 为空，或 `.mirror/` 不存在，首次导入会自动创建并写入默认配置。`push()` 和 `pull()` 会在本地项目目录和该镜像目录之间同步。

## 日志

复制操作会通过 Python 标准库 `logging` 记录日志，日志内容包括源路径和目标路径。可以在调用方自行配置日志输出格式、日志级别和日志文件。

## 许可证

MIT License

## 作者

Author: `HaoLiu`

Email: `hliu1997ac@163.com`
