# API 参考

> 📚 Conda 环境管理工具箱的代码 API 文档

## 核心类

### CondaManager

管理 Conda 环境的核心类。

```python
from conda_env_toolkit import CondaManager

conda = CondaManager()
```

#### 方法

##### `get_envs()`

获取所有 Conda 环境列表。

**返回:** `List[EnvironmentInfo]`

```python
envs = conda.get_envs()
for env in envs:
    print(env.name, env.python_version)
```

##### `get_packages(env_name: str)`

获取指定环境的包列表。

**参数:**
- `env_name`: 环境名称

**返回:** `List[PackageInfo]`

```python
packages = conda.get_packages("myenv")
for pkg in packages:
    print(pkg.name, pkg.version)
```

##### `install_package(env_name: str, package: str)`

在指定环境中安装包。

**参数:**
- `env_name`: 环境名称
- `package`: 包名称或 "name==version"

**返回:** `bool`

```python
success = conda.install_package("myenv", "numpy")
```

### RestoreManager

管理环境恢复的核心类。

```python
from conda_env_toolkit import RestoreManager

restorer = RestoreManager()
```

#### 方法

##### `restore_conda(backup_file: str, target: str, **kwargs)`

从备份文件恢复 Conda 环境。

**参数:**
- `backup_file`: 备份文件路径
- `target`: 目标环境名称
- `use_uv`: 是否使用 UV 加速
- `parallel`: 是否并行安装
- `resume`: 是否断点续传

**返回:** `RestoreReport`

```python
report = restorer.restore_conda(
    "backup.json",
    "newenv",
    use_uv=True,
    parallel=True
)
```

### BackupManager

管理环境备份的核心类。

```python
from conda_env_toolkit import BackupManager

backup = BackupManager()
```

#### 方法

##### `backup_env(env_name: str, output_dir: str, formats: List[str])`

备份指定环境。

**参数:**
- `env_name`: 环境名称
- `output_dir`: 输出目录
- `formats`: 格式列表 ["json", "md", "yml", "txt"]

**返回:** `List[str]` 生成的文件路径

```python
files = backup.backup_env("myenv", "./backups", ["json", "md"])
```

## 数据类

### EnvironmentInfo

```python
@dataclass
class EnvironmentInfo:
    name: str
    python_version: Optional[str] = None
    packages: List[PackageInfo] = field(default_factory=list)
```

### PackageInfo

```python
@dataclass
class PackageInfo:
    name: str
    version: Optional[str] = None
    channel: Optional[str] = None
    build: Optional[str] = None
    source: PackageSource = PackageSource.UNKNOWN
```

### RestoreReport

```python
@dataclass
class RestoreReport:
    env_name: str
    start_time: str
    end_time: Optional[str] = None
    conda_success: List[str] = field(default_factory=list)
    pip_success: List[str] = field(default_factory=list)
    failed: List[Dict] = field(default_factory=list)
```

## 枚举类型

### PackageSource

```python
class PackageSource(Enum):
    CONDA = auto()
    PIP = auto()
    UV = auto()
    UNKNOWN = auto()
```

### InstallStatus

```python
class InstallStatus(Enum):
    PENDING = "⏳ 等待中"
    INSTALLING = "🔄 安装中"
    SUCCESS = "✅ 成功"
    FAILED = "❌ 失败"
    SKIPPED = "⏭️ 已跳过"
    ALREADY_EXISTS = "📦 已存在"
```

## 工具函数

### `run_cmd(cmd: List[str], timeout: int = 60)`

运行系统命令。

**参数:**
- `cmd`: 命令列表
- `timeout`: 超时时间（秒）

**返回:** `(bool, str, str)` - (是否成功, stdout, stderr)

```python
from conda_env_toolkit import run_cmd

ok, out, err = run_cmd(["conda", "--version"])
```

### `log(message: str, level: LogLevel = LogLevel.INFO)`

打印日志。

```python
from conda_env_toolkit import log, LogLevel

log("操作成功", LogLevel.SUCCESS)
log("发生错误", LogLevel.ERROR)
```

## 配置类

### Config

```python
class Config:
    AUTO_USE_UV = True
    AUTO_USE_MIRROR = True
    KEEP_TEMP_FILES = False
    VERBOSE = False
    DEFAULT_MAX_WORKERS = 4
```

---

*返回 [文档首页](index.md)*
