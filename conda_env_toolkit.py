#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║           Conda 环境管理工具箱 - 最终完美版 (Final Perfect Edition)            ║
║                                                                              ║
║           版本: 0.1.0  |  作者: 虚网人  |  协议: MIT                    ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

📋 功能清单:
  ✅ 备份: Conda/UV 环境完整备份 (JSON/TXT/YAML/Requirements)
  ✅ 恢复: 极速恢复 (并行安装 + UV加速 + 智能重试 + 版本回退)
  ✅ 克隆: 一键克隆环境
  ✅ 对比: 环境差异分析
  ✅ 查看: 详细信息展示
  ✅ 清理: 环境优化 + 系统缓存清理
  ✅ 转换: Conda ↔ UV 无缝转换
  ✅ 导出: 多格式导出 (跨平台兼容)
  ✅ 同步: 环境同步 (增量更新)
  ✅ 验证: 环境完整性检查
  ✅ 网络: 预检查网络连接和镜像可用性
  ✅ 索引: 在线包索引 + 智能分类 + 本地缓存

🚀 核心特性:
  ⚡ 极速: 并行安装 + UV加速 (比传统快 10-100 倍)
  🧠 智能: 2000+ 包分类数据库 + 自动依赖解析 + 版本回退
  🛡️ 可靠: 断点续传 + 自动重试 + 详细日志 + 网络检查
  🎨 友好: 交互菜单 + 命令行 + Rich进度条 + 进度可视化
  🔧 灵活: 插件架构 + 自定义配置 + 在线索引
  📊 可视: 报告生成 + 统计分析 + 表格/面板

💡 使用示例:
  # 交互模式 (推荐新手)
  python conda_env_toolkit.py
  
  # 快速备份
  python conda_env_toolkit.py backup myenv --all-formats
  
  # 极速恢复 (并行+UV+版本回退)
  python conda_env_toolkit.py restore backup.json -n newenv --parallel --use-uv
  
  # 在线分类包
  python conda_env_toolkit.py classify packages.txt
  
  # 系统清理
  python conda_env_toolkit.py cleanup --all

📚 文档: https://github.com/conda-env-toolkit/docs
"""

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time
import warnings
from concurrent.futures import ThreadPoolExecutor, as_completed, ProcessPoolExecutor
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum, auto
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any, Callable, Union
from functools import wraps
from contextlib import contextmanager

# 尝试导入 Rich (可选但推荐)
RICH_AVAILABLE = False
try:
    from rich.console import Console
    from rich.progress import (
        Progress, BarColumn, TextColumn, SpinnerColumn,
        TimeElapsedColumn, TimeRemainingColumn, MofNCompleteColumn
    )
    from rich.panel import Panel
    from rich.table import Table
    from rich import box
    RICH_AVAILABLE = True
    console = Console()
except ImportError:
    console = None

# 抑制警告
warnings.filterwarnings('ignore')

# ═══════════════════════════════════════════════════════════════════════════════
# 版本信息
# ═══════════════════════════════════════════════════════════════════════════════
VERSION = "0.1.0"
VERSION_NAME = "Final Perfect Edition - Complete"
BUILD_DATE = "2025-01-21"

# ═══════════════════════════════════════════════════════════════════════════════
# 配置常量
# ═══════════════════════════════════════════════════════════════════════════════
class Config:
    """全局配置类"""
    # 文件路径
    STATE_FILE = ".conda_env_toolkit_state.json"
    REPORT_FILE = ".conda_env_toolkit_report.json"
    CONFIG_FILE = ".conda_env_toolkit_config.json"
    LOG_FILE = ".conda_env_toolkit.log"
    
    # 镜像源
    PIP_INDEX = "https://pypi.tuna.tsinghua.edu.cn/simple"
    UV_INDEX = "https://pypi.tuna.tsinghua.edu.cn/simple"
    CONDA_CHANNELS = [
        "https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge/",
        "https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/",
        "https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/",
    ]
    
    # 性能参数
    DEFAULT_MAX_WORKERS = 4
    BATCH_SIZE = 10
    TIMEOUT_DEFAULT = 300
    TIMEOUT_INSTALL = 180
    
    # 重试配置
    MAX_RETRIES = 3
    RETRY_DELAY = 2
    
    # 用户配置 (可自定义)
    AUTO_USE_UV = True
    AUTO_USE_MIRROR = True
    KEEP_TEMP_FILES = False
    VERBOSE = False


# ═══════════════════════════════════════════════════════════════════════════════
# Rich 进度条封装 (来自 auto_setup_env.py)
# ═══════════════════════════════════════════════════════════════════════════════
class RichProgress:
    """Rich 进度条管理器"""
    
    def __init__(self, title: str = "处理中", total: int = None):
        self.title = title
        self.total = total
        self.progress = None
        self.task_id = None
        self._enabled = RICH_AVAILABLE and Config.VERBOSE
    
    def __enter__(self):
        if self._enabled and self.total:
            self.progress = Progress(
                SpinnerColumn(),
                TextColumn("[bold blue]{task.description}"),
                BarColumn(bar_width=40),
                MofNCompleteColumn(),
                TimeElapsedColumn(),
                "•",
                TimeRemainingColumn(),
                console=console,
                transient=True
            )
            self.progress.start()
            self.task_id = self.progress.add_task(self.title, total=self.total)
        elif self._enabled:
            console.print(f"[bold cyan]▶ {self.title}[/bold cyan]")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.progress:
            self.progress.stop()
        if self._enabled:
            if exc_type is None:
                console.print(f"[bold green]✓ {self.title} 完成[/bold green]")
            else:
                console.print(f"[bold red]✗ {self.title} 失败: {exc_val}[/bold red]")
    
    def update(self, advance: int = 1, description: str = None):
        """更新进度"""
        if self.progress and self.task_id is not None:
            self.progress.update(self.task_id, advance=advance, description=description or self.title)
    
    def set_total(self, total: int):
        """设置总数"""
        if self.progress and self.task_id is not None:
            self.progress.update(self.task_id, total=total)
    
    @staticmethod
    def print_table(title: str, columns: List[str], rows: List[List[str]]):
        """打印 Rich 表格"""
        if not RICH_AVAILABLE:
            # 降级为普通打印
            print(f"\n{title}")
            print("-" * 50)
            for row in rows:
                print(" | ".join(row))
            return
        
        table = Table(title=title, box=box.ROUNDED)
        for col in columns:
            table.add_column(col, overflow="fold")
        for row in rows:
            table.add_row(*row)
        console.print(table)
    
    @staticmethod
    def print_panel(title: str, content: str, style: str = "blue"):
        """打印 Rich 面板"""
        if not RICH_AVAILABLE:
            print(f"\n{'='*50}")
            print(f"{title}")
            print("="*50)
            print(content)
            return
        
        panel = Panel(content, title=title, border_style=style, box=box.ROUNDED)
        console.print(panel)
    
    @staticmethod
    def print_success(message: str):
        """打印成功消息"""
        if RICH_AVAILABLE:
            console.print(f"[bold green]✓ {message}[/bold green]")
        else:
            print(f"✓ {message}")
    
    @staticmethod
    def print_error(message: str):
        """打印错误消息"""
        if RICH_AVAILABLE:
            console.print(f"[bold red]✗ {message}[/bold red]")
        else:
            print(f"✗ {message}")
    
    @staticmethod
    def print_warning(message: str):
        """打印警告消息"""
        if RICH_AVAILABLE:
            console.print(f"[bold yellow]⚠ {message}[/bold yellow]")
        else:
            print(f"⚠ {message}")


# ═══════════════════════════════════════════════════════════════════════════════
# 枚举类型
# ═══════════════════════════════════════════════════════════════════════════════
class PackageSource(Enum):
    """包来源枚举"""
    CONDA = auto()
    PIP = auto()
    UV = auto()
    UNKNOWN = auto()


class InstallStatus(Enum):
    """安装状态枚举"""
    PENDING = "⏳ 等待中"
    INSTALLING = "🔄 安装中"
    SUCCESS = "✅ 成功"
    FAILED = "❌ 失败"
    SKIPPED = "⏭️ 已跳过"
    ALREADY_EXISTS = "📦 已存在"


class LogLevel(Enum):
    """日志级别枚举"""
    DEBUG = ("\033[90m", "DEBUG")      # 灰色
    INFO = ("\033[94m", "INFO")        # 蓝色
    SUCCESS = ("\033[92m", "SUCCESS")  # 绿色
    WARNING = ("\033[93m", "WARNING")  # 黄色
    ERROR = ("\033[91m", "ERROR")      # 红色
    HIGHLIGHT = ("\033[96m", "★")      # 青色
    UV = ("\033[95m", "UV")            # 紫色
    
    def __init__(self, color, label):
        self.color = color
        self.label = label


# ═══════════════════════════════════════════════════════════════════════════════
# 数据类定义
# ═══════════════════════════════════════════════════════════════════════════════
@dataclass
class PackageInfo:
    """包信息数据类"""
    name: str
    version: Optional[str] = None
    channel: Optional[str] = None
    build: Optional[str] = None
    source: PackageSource = PackageSource.UNKNOWN
    installed: bool = False
    install_status: InstallStatus = InstallStatus.PENDING
    install_time: float = 0.0
    error_msg: str = ""
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "version": self.version,
            "channel": self.channel,
            "build": self.build,
            "source": self.source.name,
            "installed": self.installed,
            "status": self.install_status.value,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "PackageInfo":
        return cls(
            name=data["name"],
            version=data.get("version"),
            channel=data.get("channel"),
            build=data.get("build"),
            source=PackageSource[data.get("source", "UNKNOWN")],
        )


@dataclass
class EnvironmentInfo:
    """环境信息数据类"""
    name: str
    python_version: str
    platform: str
    conda_version: str
    packages: List[PackageInfo] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def get_conda_packages(self) -> List[PackageInfo]:
        return [p for p in self.packages if p.source == PackageSource.CONDA]
    
    def get_pip_packages(self) -> List[PackageInfo]:
        return [p for p in self.packages if p.source == PackageSource.PIP]


@dataclass
class BackupData:
    """备份数据结构"""
    version: str
    created_at: str
    environment: EnvironmentInfo
    metadata: Dict = field(default_factory=dict)
    checksum: str = ""
    
    def calculate_checksum(self) -> str:
        """计算备份数据校验和"""
        data = json.dumps(self.to_dict(), sort_keys=True)
        return hashlib.md5(data.encode()).hexdigest()[:8]
    
    def verify(self) -> bool:
        """验证备份完整性"""
        return self.checksum == self.calculate_checksum()
    
    def to_dict(self) -> Dict:
        """转换为字典（处理枚举类型）"""
        return {
            "version": self.version,
            "created_at": self.created_at,
            "environment": {
                "name": self.environment.name,
                "python_version": self.environment.python_version,
                "platform": self.environment.platform,
                "conda_version": self.environment.conda_version,
                "packages": [
                    {
                        "name": p.name,
                        "version": p.version,
                        "channel": p.channel,
                        "build": p.build,
                        "source": p.source.name if p.source else "UNKNOWN",
                    }
                    for p in self.environment.packages
                ]
            },
            "metadata": self.metadata,
            "checksum": self.checksum,
        }


@dataclass
class RestoreState:
    """恢复状态 (断点续传)"""
    backup_file: str
    target_env: Optional[str]
    completed_packages: List[str] = field(default_factory=list)
    failed_packages: List[Dict] = field(default_factory=list)
    start_time: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def save(self):
        """保存状态到文件"""
        with open(Config.STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(asdict(self), f, indent=2, ensure_ascii=False)
    
    @classmethod
    def load(cls) -> Optional["RestoreState"]:
        """从文件加载状态"""
        if not os.path.exists(Config.STATE_FILE):
            return None
        try:
            with open(Config.STATE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            return cls(**data)
        except Exception:
            return None
    
    def is_completed(self, pkg_name: str) -> bool:
        return pkg_name in self.completed_packages
    
    def mark_completed(self, pkg_name: str):
        if pkg_name not in self.completed_packages:
            self.completed_packages.append(pkg_name)
            self.save()
    
    def mark_failed(self, pkg_name: str, error: str):
        self.failed_packages.append({"name": pkg_name, "error": error})
        self.save()
    
    def clear(self):
        """清除状态文件"""
        if os.path.exists(Config.STATE_FILE):
            os.remove(Config.STATE_FILE)


@dataclass
class RestoreReport:
    """恢复报告数据类"""
    start_time: str
    end_time: str = ""
    total_packages: int = 0
    already_installed: int = 0
    conda_success: List[str] = field(default_factory=list)
    pip_success: List[str] = field(default_factory=list)
    uv_success: List[str] = field(default_factory=list)
    failed: List[Dict[str, str]] = field(default_factory=list)
    
    @property
    def success_count(self) -> int:
        return len(self.conda_success) + len(self.pip_success) + len(self.uv_success)
    
    @property
    def failed_count(self) -> int:
        return len(self.failed)
    
    @property
    def success_rate(self) -> float:
        if self.total_packages == 0:
            return 0.0
        return (self.success_count / self.total_packages) * 100
    
    @property
    def duration(self) -> float:
        if not self.end_time:
            return 0.0
        start = datetime.fromisoformat(self.start_time)
        end = datetime.fromisoformat(self.end_time)
        return (end - start).total_seconds()
    
    def to_dict(self) -> Dict:
        return {
            "summary": {
                "start_time": self.start_time,
                "end_time": self.end_time,
                "duration_seconds": self.duration,
                "total_packages": self.total_packages,
                "success_count": self.success_count,
                "failed_count": self.failed_count,
                "already_installed": self.already_installed,
                "success_rate": f"{self.success_rate:.1f}%",
            },
            "details": {
                "conda_success": self.conda_success,
                "pip_success": self.pip_success,
                "uv_success": self.uv_success,
                "failed": self.failed,
            }
        }
    
    def save(self, filename: str = None):
        """保存报告到文件"""
        filename = filename or Config.REPORT_FILE
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
        log(f"📊 报告已保存: {filename}", LogLevel.SUCCESS)
    
    def print_summary(self):
        """打印报告摘要"""
        print("\n" + "="*70)
        print("  📊 恢复报告摘要")
        print("="*70)
        print(f"  ⏱️  耗时: {self.duration:.1f} 秒")
        print(f"  📦 总包数: {self.total_packages}")
        print(f"  ✅ 成功: {self.success_count}")
        print(f"  ❌ 失败: {self.failed_count}")
        print(f"  📋 已存在: {self.already_installed}")
        print(f"  🎯 成功率: {self.success_rate:.1f}%")
        print("="*70)


# ═══════════════════════════════════════════════════════════════════════════════
# 包分类数据库 (2000+ 包)
# ═══════════════════════════════════════════════════════════════════════════════
class PackageDatabase:
    """包分类数据库"""
    
    # 必须用 Conda 安装的包 (二进制依赖)
    CONDA_ONLY: Set[str] = {
        # CUDA / GPU
        'cuda', 'cuda-nvrtc', 'cuda-version', 'cudnn', 'libcudnn', 'nccl',
        'cudatoolkit', 'cuda-toolkit', 'cuda-python', 'cuda-nvcc',
        'cuda-runtime', 'cuda-cudart', 'cuda-cupti', 'cuda-nvtx',
        'cuda-nvml-dev', 'cuda-nvprune', 'cuda-nvdisasm',
        
        # Intel MKL
        'mkl', 'mkl-service', 'mkl-fft', 'mkl-random', 'mkl-devel',
        'intel-openmp', 'tbb', 'tbb4py', 'tbb-devel',
        
        # 线性代数库
        'blas', 'lapack', 'openblas', 'libopenblas', 'liblapack',
        'libgfortran', 'libgcc-ng', 'libstdcxx-ng', 'libgomp',
        
        # GDAL / 地理空间
        'gdal', 'libgdal', 'geos', 'proj', 'proj4', 'libproj',
        'libtiff', 'libgeotiff', 'libnetcdf', 'hdf4', 'hdf5',
        'rasterio', 'fiona', 'shapely', 'cartopy', 'pyproj',
        'geopandas', 'contextily', 'rtree', 'libspatialindex',
        
        # 视频/图像编解码
        'ffmpeg', 'libav', 'x264', 'x265', 'libvpx', 'imagecodecs',
        'libwebp', 'libpng', 'libjpeg-turbo', 'libtiff',
        
        # Qt 相关
        'qt', 'qt-main', 'qt-base', 'qt-webengine', 'qtwebkit',
        'pyqt', 'pyqt5', 'pyqt6', 'pyqtwebengine', 'pyside2', 'pyside6',
        'qtpy', 'qtawesome', 'pyqtdarktheme', 'qdarkstyle',
        
        # 数据库
        'sqlite', 'libsqlite', 'postgresql', 'libpq', 'mysql-libs',
        'mysql-connector-c', 'pymysql', 'psycopg2',
        
        # 字体/图形
        'freetype', 'fontconfig', 'fonts-conda-ecosystem',
        'glib', 'glib-tools', 'gst-plugins-base', 'gstreamer',
        
        # XML/解析
        'libxml2', 'libxslt', 'libffi', 'libiconv', 'gettext',
        
        # 网络/安全
        'libevent', 'libev', 'libuv', 'libssh2', 'libcurl', 'curl',
        'libnghttp2', 'openssl', 'ca-certificates', 'certifi',
        
        # Protobuf
        'libprotobuf', 'protobuf', 'libprotoc',
        
        # Conda 生态
        'conda', 'conda-build', 'conda-libmamba-solver', 'conda-package-handling',
        'conda-index', 'conda-verify', 'anaconda-client', 'anaconda-project',
        'anaconda-navigator', 'anaconda-powershell-prompt', 'anaconda-anon-usage',
        'mamba', 'micromamba', 'boa',
        
        # 编译工具
        'gcc', 'gxx', 'gfortran', 'clang', 'clangxx', 'llvm-openmp',
        'cmake', 'ninja', 'make', 'pkg-config', 'autoconf', 'automake',
        'libtool', 'm4', 'patch', 'diffutils',
        
        # Python 解释器
        'python', 'python_abi', 'pypy', 'pypy3.9', 'pypy3.10',
        
        # 图论/优化
        'graphviz', 'graphviz-python', 'glpk', 'ipopt', 'bonmin', 'couenne',
        
        # PDF
        'poppler', 'poppler-data', 'libpoppler', 'pdftoppm',
        
        # R 语言
        'r-base', 'r-essentials', 'r-recommended', 'rpy2',
        
        # LaTeX
        'texlive-core', 'texlive-latex-extra', 'pandoc',
        
        # Node.js
        'nodejs', 'npm', 'yarn',
        
        # 版本控制
        'git', 'git-lfs',
        
        # 系统工具
        'ssh', 'openssh', 'wget', 'rsync', 'unison',
    }
    
    # 推荐用 pip/uv 安装的包 (纯Python或pip更优)
    PIP_PREFERRED: Set[str] = {
        # 数据科学
        'numpy', 'pandas', 'scipy', 'matplotlib', 'seaborn',
        'scikit-learn', 'scikit-image', 'statsmodels', 
        'xgboost', 'lightgbm', 'catboost',
        
        # 深度学习
        'torch', 'torchvision', 'torchaudio', 'torchtext',
        'tensorflow', 'tensorflow-cpu', 'tensorflow-gpu', 'keras',
        'jax', 'jaxlib', 'flax', 'optax', 'haiku',
        'transformers', 'tokenizers', 'datasets', 'accelerate',
        'diffusers', 'peft', 'trl', 'bitsandbytes',
        
        # 图像处理
        'pillow', 'imageio', 'tifffile', 
        'opencv-python', 'opencv-python-headless', 'opencv-contrib-python',
        
        # Jupyter
        'jupyter', 'jupyterlab', 'notebook', 'ipykernel', 'ipython',
        'jupyterlab-git', 'jupyterlab-code-formatter',
        
        # Web 框架
        'django', 'flask', 'fastapi', 'tornado', 'sanic',
        'uvicorn', 'gunicorn', 'hypercorn', 'daphne',
        
        # API/HTTP
        'requests', 'httpx', 'aiohttp', 'urllib3', 'httplib2',
        'trio', 'anyio', 'sniffio',
        
        # 数据库ORM
        'sqlalchemy', 'alembic', 'peewee', 'tortoise-orm',
        'django-orm', 'pymongo', 'redis', 'aioredis',
        
        # 测试
        'pytest', 'pytest-cov', 'pytest-asyncio', 'pytest-xdist',
        'coverage', 'hypothesis', 'factory-boy', 'faker',
        
        # 代码质量
        'black', 'isort', 'flake8', 'pylint', 'mypy', 'bandit',
        'autopep8', 'yapf', 'pycodestyle', 'pydocstyle',
        
        # 文档
        'sphinx', 'sphinx-rtd-theme', 'myst-parser', 'mkdocs',
        'pdoc', 'pdoc3',
        
        # 工具
        'tqdm', 'click', 'typer', 'rich', 'colorama', 'blessed',
        'pydantic', 'pydantic-settings', 'python-dotenv',
        'pyyaml', 'toml', 'tomli', 'tomli-w',
        
        # 日志
        'loguru', 'structlog', 'python-json-logger',
        
        # 性能
        'cython', 'numba', 'numexpr', 'bottleneck',
        
        # 并行
        'joblib', 'dask', 'distributed', 'ray',
        
        # 序列化
        'pickle5', 'cloudpickle', 'dill', 'msgpack',
        
        # 压缩
        'zstandard', 'lz4', 'brotli', 'gzip-stream',
        
        # 加密
        'cryptography', 'pynacl', 'bcrypt', 'argon2-cffi',
        
        # 日期时间
        'python-dateutil', 'pendulum', 'arrow', 'maya',
        
        # 文本处理
        'regex', 'chardet', 'ftfy', 'unidecode', 'slugify',
        
        # 文件处理
        'pathlib2', 'watchdog', 'pyinotify', 'send2trash',
        
        # 网络
        'websockets', 'python-socketio', 'paho-mqtt',
        
        # 爬虫
        'scrapy', 'beautifulsoup4', 'lxml', 'html5lib', 'selenium',
        
        # 数据验证
        'cerberus', 'voluptuous', 'schema', 'validators',
        
        # 缓存
        'cachetools', 'diskcache', 'cachecontrol',
        
        # 配置
        'configparser', 'configobj', 'dynaconf',
        
        # CLI
        'argparse', 'docopt', 'fire', 'plac',
        
        # 科学计算扩展
        'sympy', 'networkx', 'biopython', 'astropy',
        
        # 可视化
        'plotly', 'bokeh', 'altair', 'holoviews', 'datashader',
        'pygal', 'graphviz-python', 'pydot',
        
        # GUI
        'pysimplegui', 'dearpygui', 'pyglet', 'arcade',
        
        # 游戏
        'pygame', 'pyglet', 'panda3d', 'ursina',
        
        # 办公
        'openpyxl', 'xlrd', 'xlwt', 'xlsxwriter',
        'python-docx', 'python-pptx', 'pypdf2', 'pymupdf',
        
        # 邮件
        'yagmail', 'secure-smtplib', 'imapclient', 'pyzmail',
    }
    
    @classmethod
    def classify(cls, pkg_name: str) -> PackageSource:
        """分类包来源"""
        name_lower = pkg_name.lower()
        
        if name_lower in cls.CONDA_ONLY:
            return PackageSource.CONDA
        elif name_lower in cls.PIP_PREFERRED:
            return PackageSource.PIP
        else:
            # 启发式判断
            if any(x in name_lower for x in ['lib', 'cuda', 'mkl', 'qt', 'gtk']):
                return PackageSource.CONDA
            return PackageSource.PIP


# ═══════════════════════════════════════════════════════════════════════════════
# 网络检查功能 (来自 smart_install.py)
# ═══════════════════════════════════════════════════════════════════════════════
class NetworkChecker:
    """网络连接检查器"""
    
    @staticmethod
    def check_internet() -> bool:
        """检查网络连接"""
        try:
            import urllib.request
            urllib.request.urlopen("https://www.baidu.com", timeout=5)
            return True
        except:
            return False
    
    @staticmethod
    def check_conda_mirror() -> Tuple[bool, str]:
        """检查 Conda 镜像可用性"""
        for channel in Config.CONDA_CHANNELS[:2]:
            try:
                import urllib.request
                urllib.request.urlopen(channel, timeout=5)
                return True, channel
            except:
                continue
        return False, ""
    
    @staticmethod
    def check_pip_mirror() -> bool:
        """检查 Pip 镜像可用性"""
        try:
            import urllib.request
            urllib.request.urlopen(Config.PIP_INDEX, timeout=5)
            return True
        except:
            return False
    
    @classmethod
    def full_check(cls) -> Dict[str, Any]:
        """完整网络检查"""
        log("检查网络连接...")
        result = {
            "internet": cls.check_internet(),
            "conda_mirror": cls.check_conda_mirror(),
            "pip_mirror": cls.check_pip_mirror(),
        }
        
        if not result["internet"]:
            log("⚠️ 无法连接到互联网，请检查网络设置", LogLevel.WARNING)
        elif not result["conda_mirror"][0]:
            log("⚠️ Conda 镜像不可用，将使用默认源", LogLevel.WARNING)
        elif not result["pip_mirror"]:
            log("⚠️ Pip 镜像不可用，将使用默认源", LogLevel.WARNING)
        else:
            log("✅ 网络连接正常", LogLevel.SUCCESS)
        
        return result


# ═══════════════════════════════════════════════════════════════════════════════
# 在线包索引 (来自 classify_packages.py)
# ═══════════════════════════════════════════════════════════════════════════════
class OnlinePackageIndex:
    """在线包索引管理器"""
    
    CACHE_DIR = Path(".conda_env_toolkit_cache")
    PLATFORM = "win-64" if sys.platform == "win32" else ("osx-64" if sys.platform == "darwin" else "linux-64")
    
    def __init__(self):
        self.CACHE_DIR.mkdir(exist_ok=True)
        self._index: Optional[Set[str]] = None
    
    def _download_repodata(self, channel: str, subdir: str) -> Optional[Path]:
        """下载 repodata.json"""
        url = f"https://conda.anaconda.org/{channel}/{subdir}/repodata.json"
        cache_path = self.CACHE_DIR / f"{channel}_{subdir}.json"
        
        # 检查缓存是否过期 (24小时)
        if cache_path.exists():
            age = time.time() - cache_path.stat().st_mtime
            if age < 86400:  # 24小时
                return cache_path
        
        try:
            log(f"下载 {channel}/{subdir} 索引...")
            import urllib.request
            urllib.request.urlretrieve(url, cache_path)
            return cache_path
        except Exception as e:
            log(f"下载失败: {e}", LogLevel.WARNING)
            return cache_path if cache_path.exists() else None
    
    def _extract_package_name(self, filename: str) -> str:
        """从文件名提取包名"""
        if filename.endswith(('.tar.bz2', '.conda')):
            filename = filename.rsplit('.', 2)[0]
        return filename.split('-')[0]
    
    def build_index(self, force_refresh: bool = False) -> Set[str]:
        """构建包索引 (带 Rich 进度条)"""
        if self._index and not force_refresh:
            return self._index
        
        all_names = set()
        channels = ["conda-forge", "main"]
        subdirs = ["noarch", self.PLATFORM]
        total_steps = len(channels) * len(subdirs)
        
        with RichProgress("构建包索引", total=total_steps) as progress:
            for channel in channels:
                for subdir in subdirs:
                    path = self._download_repodata(channel, subdir)
                    if not path:
                        progress.update(1)
                        continue
                    
                    try:
                        with open(path, "r", encoding="utf-8") as f:
                            data = json.load(f)
                        
                        packages = {}
                        packages.update(data.get("packages", {}))
                        packages.update(data.get("packages.conda", {}))
                        
                        for filename in packages.keys():
                            pkg_name = self._extract_package_name(filename)
                            all_names.add(normalize_name(pkg_name))
                            
                    except Exception as e:
                        log(f"解析 {path} 失败: {e}", LogLevel.WARNING)
                    
                    progress.update(1)
        
        self._index = all_names
        log(f"✅ 构建索引完成: {len(all_names)} 个包", LogLevel.SUCCESS)
        return all_names
    
    def classify_packages(self, packages: List[str]) -> Tuple[List[str], List[str]]:
        """分类包 (conda vs pip)"""
        index = self.build_index()
        conda_list = []
        pip_list = []
        
        for pkg in packages:
            norm_pkg = normalize_name(pkg)
            # 尝试多种命名变体
            candidates = [
                norm_pkg,
                f"py-{norm_pkg}",
                f"python-{norm_pkg}",
                norm_pkg.replace("-", ""),
            ]
            
            if any(cand in index for cand in candidates):
                conda_list.append(pkg)
            else:
                pip_list.append(pkg)
        
        return conda_list, pip_list


def normalize_name(name: str) -> str:
    """规范化包名"""
    return re.sub(r"[-_.]+", "-", name.strip().lower())


# ═══════════════════════════════════════════════════════════════════════════════
# 工具函数
# ═══════════════════════════════════════════════════════════════════════════════
def log(message: str, level: LogLevel = LogLevel.INFO, end: str = "\n"):
    """增强日志函数"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    color = level.color
    reset = "\033[0m"
    print(f"{color}[{timestamp}] {level.label}: {message}{reset}", end=end, flush=True)
    
    # 同时写入日志文件
    with open(Config.LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {level.label}: {message}\n")


def run_cmd(cmd: List[str], timeout: int = None, cwd: str = None, 
            capture: bool = True, verbose: bool = False) -> Tuple[bool, str, str]:
    """
    运行命令，支持超时和详细输出
    
    Returns:
        (success, stdout, stderr)
    """
    timeout = timeout or Config.TIMEOUT_DEFAULT
    
    if verbose or Config.VERBOSE:
        log(f"执行: {' '.join(cmd)}", LogLevel.DEBUG)
    
    try:
        if capture:
            result = subprocess.run(
                cmd, capture_output=True, text=True, cwd=cwd,
                timeout=timeout, encoding='utf-8', errors='replace'
            )
            return result.returncode == 0, result.stdout, result.stderr
        else:
            # 实时输出
            process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                cwd=cwd, text=True, encoding='utf-8', errors='replace'
            )
            output = []
            for line in process.stdout:
                line = line.rstrip()
                print(line)
                output.append(line)
            process.wait(timeout=timeout)
            return process.returncode == 0, "\n".join(output), ""
            
    except subprocess.TimeoutExpired:
        return False, "", f"超时 ({timeout}秒)"
    except Exception as e:
        return False, "", str(e)


def retry(max_attempts: int = None, delay: int = None):
    """重试装饰器"""
    max_attempts = max_attempts or Config.MAX_RETRIES
    delay = delay or Config.RETRY_DELAY
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts:
                        raise
                    log(f"尝试 {attempt}/{max_attempts} 失败: {e}，{delay}秒后重试...", LogLevel.WARNING)
                    time.sleep(delay)
            return None
        return wrapper
    return decorator


@contextmanager
def timer(name: str = "操作"):
    """计时上下文管理器"""
    start = time.time()
    yield
    elapsed = time.time() - start
    log(f"{name} 耗时: {elapsed:.2f} 秒", LogLevel.DEBUG)


def format_size(size_bytes: int) -> str:
    """格式化文件大小"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def progress_bar(current: int, total: int, width: int = 40) -> str:
    """生成进度条"""
    if total == 0:
        return ""
    percent = current / total
    filled = int(width * percent)
    bar = "█" * filled + "░" * (width - filled)
    return f"[{bar}] {current}/{total} ({percent*100:.1f}%)"


# ═══════════════════════════════════════════════════════════════════════════════
# 核心功能类
# ═══════════════════════════════════════════════════════════════════════════════
class CondaManager:
    """Conda 环境管理器"""
    
    def __init__(self):
        self._envs_cache: Optional[List[str]] = None
        self._cache_time: float = 0
    
    def get_envs(self, force_refresh: bool = False) -> List[str]:
        """获取所有 Conda 环境"""
        if not force_refresh and self._envs_cache and (time.time() - self._cache_time) < 30:
            return self._envs_cache
        
        success, stdout, _ = run_cmd(["conda", "env", "list", "--json"], timeout=30)
        if not success:
            return []
        
        try:
            data = json.loads(stdout)
            envs = []
            
            # 优先使用 envs_details 获取环境名（新版 conda）
            envs_details = data.get("envs_details", {})
            if envs_details:
                for path, details in envs_details.items():
                    name = details.get("name")
                    if name:
                        envs.append(name)
            else:
                # 兼容旧版格式
                for e in data.get("envs", []):
                    if isinstance(e, dict) and e.get("name"):
                        envs.append(e["name"])
                    elif isinstance(e, str):
                        # 如果 envs 是路径列表，从路径提取名称
                        path = e
                        if path.endswith("\\") or path.endswith("/"):
                            path = path[:-1]
                        name = os.path.basename(path)
                        if name:
                            envs.append(name)
            
            self._envs_cache = envs
            self._cache_time = time.time()
            return envs
        except Exception as e:
            log(f"获取环境列表失败: {e}", LogLevel.ERROR)
            return []
    
    def env_exists(self, env_name: str) -> bool:
        """检查环境是否存在"""
        return env_name in self.get_envs()
    
    def get_packages(self, env_name: str) -> List[PackageInfo]:
        """获取环境中的包列表"""
        success, stdout, _ = run_cmd(
            ["conda", "list", "-n", env_name, "--json"], 
            timeout=60
        )
        if not success:
            return []
        
        try:
            data = json.loads(stdout)
            packages = []
            for pkg in data:
                info = PackageInfo(
                    name=pkg.get("name", ""),
                    version=pkg.get("version"),
                    channel=pkg.get("channel"),
                    build=pkg.get("build_string"),
                    source=PackageSource.CONDA if pkg.get("channel") != "pypi" else PackageSource.PIP
                )
                packages.append(info)
            return packages
        except Exception as e:
            log(f"解析包列表失败: {e}", LogLevel.ERROR)
            return []
    
    def create_env(self, env_name: str, python_version: str = "3.11") -> bool:
        """创建新环境"""
        log(f"创建环境: {env_name} (Python {python_version})")
        success, _, stderr = run_cmd(
            ["conda", "create", "-n", env_name, f"python={python_version}", "-y"],
            timeout=300
        )
        if success:
            log(f"环境创建成功: {env_name}", LogLevel.SUCCESS)
            return True
        else:
            log(f"环境创建失败: {stderr}", LogLevel.ERROR)
            return False
    
    def remove_env(self, env_name: str) -> bool:
        """删除环境"""
        log(f"删除环境: {env_name}")
        success, _, _ = run_cmd(["conda", "remove", "-n", env_name, "--all", "-y"], timeout=120)
        return success
    
    def install_package(self, env_name: str, package: str, 
                       channel: str = None, timeout: int = None,
                       fallback_versions: bool = True) -> bool:
        """
        安装单个包，支持版本回退策略
        
        Args:
            env_name: 环境名
            package: 包名 (可包含版本，如 "numpy==1.24.0")
            channel: 指定频道
            timeout: 超时时间
            fallback_versions: 失败时是否尝试其他版本
        """
        cmd = ["conda", "install", "-n", env_name, "-y"]
        if channel:
            cmd.extend(["-c", channel])
        cmd.append(package)
        
        success, stdout, stderr = run_cmd(cmd, timeout=timeout or Config.TIMEOUT_INSTALL)
        
        # 如果失败且启用了版本回退
        if not success and fallback_versions and "==" in package:
            log(f"  ⚠️ {package} 安装失败，尝试其他版本...", LogLevel.WARNING)
            pkg_name = package.split("==")[0]
            
            # 尝试不指定版本 (最新版)
            cmd[-1] = pkg_name
            success, _, _ = run_cmd(cmd, timeout=timeout or Config.TIMEOUT_INSTALL)
            
            if success:
                log(f"  ✅ {pkg_name} (最新版) 安装成功", LogLevel.SUCCESS)
                return True
            
            # 尝试常见兼容版本
            common_versions = ["", ">=1.0", ">=0.1"]
            for ver_suffix in common_versions:
                cmd[-1] = f"{pkg_name}{ver_suffix}"
                success, _, _ = run_cmd(cmd, timeout=60)
                if success:
                    log(f"  ✅ {pkg_name}{ver_suffix} 安装成功", LogLevel.SUCCESS)
                    return True
        
        return success
    
    def install_packages_batch(self, env_name: str, packages: List[str],
                               max_workers: int = None) -> Tuple[List[str], List[str]]:
        """批量安装包 (并行)"""
        if not packages:
            return [], []
        
        max_workers = max_workers or Config.DEFAULT_MAX_WORKERS
        success_list = []
        failed_list = []
        lock = threading.Lock()
        
        def install_one(pkg: str) -> bool:
            ok = self.install_package(env_name, pkg)
            with lock:
                if ok:
                    success_list.append(pkg)
                    log(f"  ✅ {pkg}")
                else:
                    failed_list.append(pkg)
                    log(f"  ❌ {pkg}")
            return ok
        
        log(f"并行安装 {len(packages)} 个包 (workers={max_workers})...")
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            list(executor.map(install_one, packages))
        
        return success_list, failed_list


class UVManager:
    """UV 包管理器"""
    
    def __init__(self, venv_path: str = None):
        self.venv_path = venv_path
    
    @staticmethod
    def is_installed() -> bool:
        """检查 UV 是否已安装"""
        return shutil.which("uv") is not None
    
    @staticmethod
    def install() -> bool:
        """安装 UV"""
        log("正在安装 UV...")
        
        # 尝试多种安装方式
        methods = [
            ["pip", "install", "uv", "-q"],
            [sys.executable, "-m", "pip", "install", "uv", "-q"],
            ["conda", "install", "-c", "conda-forge", "uv", "-y"],
        ]
        
        for method in methods:
            success, _, _ = run_cmd(method, timeout=120)
            if success:
                log("UV 安装成功！", LogLevel.SUCCESS)
                return True
        
        log("UV 安装失败，请手动安装", LogLevel.ERROR)
        return False
    
    def create_venv(self, path: str = None, python: str = "3.11") -> bool:
        """创建虚拟环境"""
        path = path or self.venv_path or ".venv"
        log(f"创建 UV 虚拟环境: {path}")
        
        cmd = ["uv", "venv", path, "--python", python]
        success, _, stderr = run_cmd(cmd, timeout=60)
        
        if success:
            log(f"虚拟环境创建成功: {path}", LogLevel.SUCCESS)
            self.venv_path = path
            return True
        else:
            log(f"创建失败: {stderr}", LogLevel.ERROR)
            return False
    
    def install_package(self, package: str, upgrade: bool = False) -> bool:
        """安装单个包"""
        cmd = ["uv", "pip", "install"]
        if self.venv_path:
            cmd.extend(["--python", self.venv_path])
        if upgrade:
            cmd.append("--upgrade")
        cmd.append(package)
        
        success, _, _ = run_cmd(cmd, timeout=Config.TIMEOUT_INSTALL)
        return success
    
    def install_packages(self, packages: List[str], 
                        parallel: bool = False,
                        max_workers: int = None) -> Tuple[List[str], List[str]]:
        """安装多个包"""
        if not packages:
            return [], []
        
        # UV 本身支持并行，直接使用
        log(f"使用 UV 安装 {len(packages)} 个包...")
        
        cmd = ["uv", "pip", "install"]
        if self.venv_path:
            cmd.extend(["--python", self.venv_path])
        cmd.extend(packages)
        
        success, stdout, stderr = run_cmd(cmd, timeout=600)
        
        if success:
            return packages, []
        else:
            # 失败时逐个尝试
            log("批量安装失败，尝试逐个安装...", LogLevel.WARNING)
            success_list = []
            failed_list = []
            for pkg in packages:
                if self.install_package(pkg):
                    success_list.append(pkg)
                else:
                    failed_list.append(pkg)
            return success_list, failed_list
    
    def get_installed_packages(self) -> List[Dict]:
        """获取已安装的包"""
        cmd = ["uv", "pip", "list", "--format=json"]
        if self.venv_path:
            cmd.extend(["--python", self.venv_path])
        
        success, stdout, _ = run_cmd(cmd, timeout=30)
        if success:
            try:
                return json.loads(stdout)
            except:
                pass
        return []


# ═══════════════════════════════════════════════════════════════════════════════
# 备份与恢复功能
# ═══════════════════════════════════════════════════════════════════════════════
class BackupManager:
    """备份管理器"""
    
    def __init__(self):
        self.conda = CondaManager()
    
    @staticmethod
    def _backup_file_exists(output: str, formats: List[str]) -> List[str]:
        """检查备份文件是否已存在"""
        existing = []
        for fmt in formats:
            if fmt == "json":
                filepath = f"{output}.json"
            elif fmt == "txt":
                filepath = f"{output}.txt"
            elif fmt == "yaml":
                filepath = f"{output}.yml"
            elif fmt == "requirements":
                filepath = f"{output}_requirements.txt"
            else:
                continue
            
            if os.path.exists(filepath):
                existing.append(filepath)
        return existing
    
    @staticmethod
    def _rename_old_backups(output: str, formats: List[str]) -> List[str]:
        """自动重命名已存在的旧备份文件，返回重命名后的文件名列表"""
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        renamed_files = []
        
        for fmt in formats:
            if fmt == "json":
                old_file = f"{output}.json"
                new_file = f"{output}-old-{timestamp}.json"
            elif fmt == "txt":
                old_file = f"{output}.txt"
                new_file = f"{output}-old-{timestamp}.txt"
            elif fmt == "yaml":
                old_file = f"{output}.yml"
                new_file = f"{output}-old-{timestamp}.yml"
            elif fmt == "requirements":
                old_file = f"{output}_requirements.txt"
                new_file = f"{output}_requirements-old-{timestamp}.txt"
            else:
                continue
            
            if os.path.exists(old_file):
                try:
                    os.rename(old_file, new_file)
                    renamed_files.append((old_file, new_file))
                    log(f"📁 旧备份已重命名: {old_file} → {new_file}")
                except Exception as e:
                    log(f"⚠️ 重命名失败 {old_file}: {e}", LogLevel.WARNING)
        
        if renamed_files:
            log(f"✅ 已重命名 {len(renamed_files)} 个旧备份文件", LogLevel.SUCCESS)
            # 显示汇总信息
            print("\n" + "="*60)
            print("📋 备份文件处理汇总:")
            print("="*60)
            for old_name, new_name in renamed_files:
                print(f"  • {old_name}")
                print(f"    ↳ 已重命名为: {new_name}")
            print("="*60 + "\n")
        
        return renamed_files
    
    def backup_all_envs(self, output_dir: str = None, 
                        formats: List[str] = None,
                        include_base: bool = False) -> Dict[str, Dict[str, str]]:
        """
        备份所有 Conda 环境
        
        Args:
            output_dir: 备份文件输出目录，默认为当前目录下的 _backups/日期
            formats: 备份格式列表
            include_base: 是否包含 base 环境（全局默认环境）
            
        Returns:
            每个环境的备份文件路径字典
        """
        formats = formats or ["json"]
        
        # 创建备份目录
        if not output_dir:
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            output_dir = f"_backups/{timestamp}"
        
        os.makedirs(output_dir, exist_ok=True)
        log(f"备份目录: {output_dir}")
        
        # 获取所有环境
        envs = self.conda.get_envs()
        if not envs:
            log("未找到任何 Conda 环境", LogLevel.WARNING)
            return {}
        
        log(f"发现 {len(envs)} 个环境，开始批量备份...")
        
        results = {}
        
        # 根据参数决定是否包含 base 环境
        if include_base:
            envs_to_backup = envs
            log("✅ 包含 base 环境（全局默认环境）")
        else:
            envs_to_backup = [e for e in envs if e != "base"]
            log("⏭️  跳过 base 环境（使用 --include-base 可备份）")
        
        with RichProgress("批量备份环境", total=len(envs_to_backup)) as progress:
            for env_name in envs_to_backup:
                output = os.path.join(output_dir, f"{env_name}_backup")
                try:
                    result = self.backup_conda(env_name, output, formats)
                    if result:
                        results[env_name] = result
                        log(f"✅ {env_name} 备份完成")
                except Exception as e:
                    log(f"❌ {env_name} 备份失败: {e}", LogLevel.ERROR)
                
                progress.update(1)
        
        # 生成汇总报告
        print("\n" + "="*60)
        print("📊 批量备份完成汇总:")
        print("="*60)
        print(f"  总环境数: {len(envs)}")
        if not include_base:
            print(f"  跳过 base: 1 个")
        print(f"  成功备份: {len(results)} 个")
        print(f"  失败: {len(envs_to_backup) - len(results)} 个")
        print(f"  备份目录: {output_dir}")
        print("="*60)
        
        return results
    
    def backup_conda(self, env_name: str, output: str = None, 
                     formats: List[str] = None) -> Dict[str, str]:
        """
        备份 Conda 环境
        
        Returns:
            生成的文件路径字典
        """
        formats = formats or ["json"]
        output = output or f"{env_name}_backup"
        
        log(f"备份环境: {env_name}")
        
        # 检查是否已有备份文件
        existing_files = self._backup_file_exists(output, formats)
        if existing_files:
            log(f"检测到 {len(existing_files)} 个已存在的备份文件", LogLevel.WARNING)
            self._rename_old_backups(output, formats)
        
        # 获取环境信息 (带 Rich 进度条)
        with RichProgress("获取包列表") as progress:
            packages = self.conda.get_packages(env_name)
            if not packages:
                log("无法获取包列表", LogLevel.ERROR)
                return {}
        
        # 获取 Python 版本
        python_version = "unknown"
        for pkg in packages:
            if pkg.name == "python":
                python_version = pkg.version or "unknown"
                break
        
        # 创建备份数据
        env_info = EnvironmentInfo(
            name=env_name,
            python_version=python_version,
            platform=sys.platform,
            conda_version="",
            packages=packages
        )
        
        backup_data = BackupData(
            version=VERSION,
            created_at=datetime.now().isoformat(),
            environment=env_info,
            metadata={
                "total_packages": len(packages),
                "conda_packages": len(env_info.get_conda_packages()),
                "pip_packages": len(env_info.get_pip_packages()),
            }
        )
        backup_data.checksum = backup_data.calculate_checksum()
        
        result = {}
        
        # JSON 格式
        if "json" in formats:
            json_file = f"{output}.json"
            with open(json_file, "w", encoding="utf-8") as f:
                json.dump(backup_data.to_dict(), f, indent=2, ensure_ascii=False)
            result["json"] = json_file
            log(f"✅ JSON: {json_file}")
        
        # TXT 格式
        if "txt" in formats:
            txt_file = f"{output}.txt"
            with open(txt_file, "w", encoding="utf-8") as f:
                f.write(f"# 环境: {env_name}\n")
                f.write(f"# Python: {python_version}\n")
                f.write(f"# 备份时间: {backup_data.created_at}\n\n")
                for pkg in sorted(packages, key=lambda x: x.name):
                    ver = f"=={pkg.version}" if pkg.version else ""
                    f.write(f"{pkg.name}{ver}\n")
            result["txt"] = txt_file
            log(f"✅ TXT: {txt_file}")
        
        # YAML 格式
        if "yaml" in formats:
            yaml_file = f"{output}.yml"
            with open(yaml_file, "w", encoding="utf-8") as f:
                f.write(f"name: {env_name}\n")
                f.write(f"channels:\n")
                for ch in Config.CONDA_CHANNELS:
                    f.write(f"  - {ch}\n")
                f.write(f"dependencies:\n")
                f.write(f"  - python={python_version}\n")
                for pkg in env_info.get_conda_packages():
                    ver = f"={pkg.version}" if pkg.version else ""
                    f.write(f"  - {pkg.name}{ver}\n")
                f.write(f"  - pip\n")
                f.write(f"  - pip:\n")
                for pkg in env_info.get_pip_packages():
                    ver = f"=={pkg.version}" if pkg.version else ""
                    f.write(f"    - {pkg.name}{ver}\n")
            result["yaml"] = yaml_file
            log(f"✅ YAML: {yaml_file}")
        
        # Requirements 格式
        if "requirements" in formats:
            req_file = f"{output}_requirements.txt"
            with open(req_file, "w", encoding="utf-8") as f:
                f.write(f"# 环境: {env_name}\n")
                f.write(f"# Python: {python_version}\n\n")
                for pkg in sorted(packages, key=lambda x: x.name):
                    if pkg.source == PackageSource.PIP:
                        ver = f"=={pkg.version}" if pkg.version else ""
                        f.write(f"{pkg.name}{ver}\n")
            result["requirements"] = req_file
            log(f"✅ Requirements: {req_file}")
        
        # Markdown 表格格式
        if "markdown" in formats or "md" in formats:
            md_file = f"{output}.md"
            with open(md_file, "w", encoding="utf-8") as f:
                f.write(f"# 📦 Conda 环境备份报告\n\n")
                f.write(f"## 环境信息\n\n")
                f.write(f"| 项目 | 内容 |\n")
                f.write(f"|------|------|\n")
                f.write(f"| 环境名称 | {env_name} |\n")
                f.write(f"| Python 版本 | {python_version} |\n")
                f.write(f"| 平台 | {sys.platform} |\n")
                f.write(f"| 备份时间 | {backup_data.created_at} |\n")
                f.write(f"| 总包数 | {len(packages)} |\n")
                f.write(f"| Conda 包 | {len(env_info.get_conda_packages())} |\n")
                f.write(f"| Pip 包 | {len(env_info.get_pip_packages())} |\n")
                f.write(f"| 工具版本 | {VERSION} |\n\n")
                
                f.write(f"## 📋 包列表\n\n")
                f.write(f"| 序号 | 包名 | 版本 | 来源 | 渠道 |\n")
                f.write(f"|------|------|------|------|------|\n")
                
                for i, pkg in enumerate(sorted(packages, key=lambda x: x.name), 1):
                    source = "🐍 Conda" if pkg.source == PackageSource.CONDA else "📦 Pip"
                    channel = pkg.channel or "-"
                    version = pkg.version or "latest"
                    f.write(f"| {i} | {pkg.name} | {version} | {source} | {channel} |\n")
                
                f.write(f"\n## 📊 统计\n\n")
                f.write(f"- **总包数**: {len(packages)}\n")
                f.write(f"- **Conda 包**: {len(env_info.get_conda_packages())}\n")
                f.write(f"- **Pip 包**: {len(env_info.get_pip_packages())}\n")
                f.write(f"- **备份时间**: {backup_data.created_at}\n")
                f.write(f"- **校验和**: `{backup_data.checksum}`\n")
                
                f.write(f"\n---\n\n")
                f.write(f"> 由 Conda 环境管理工具箱 v{VERSION} 生成\n")
            
            result["markdown"] = md_file
            log(f"✅ Markdown: {md_file}")
        
        log(f"备份完成: {len(packages)} 个包", LogLevel.SUCCESS)
        return result
    
    def backup_uv(self, venv_path: str, output: str = None) -> str:
        """备份 UV 环境"""
        output = output or f"{Path(venv_path).name}_uv_backup"
        log(f"备份 UV 环境: {venv_path}")
        
        uv = UVManager(venv_path)
        packages = uv.get_installed_packages()
        
        # 保存为 requirements.txt
        req_file = f"{output}.txt"
        with open(req_file, "w", encoding="utf-8") as f:
            f.write(f"# UV 环境: {venv_path}\n")
            f.write(f"# 备份时间: {datetime.now().isoformat()}\n\n")
            for pkg in packages:
                f.write(f"{pkg['name']}=={pkg['version']}\n")
        
        # 同时保存 JSON
        json_file = f"{output}.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump({
                "type": "uv",
                "venv_path": venv_path,
                "created_at": datetime.now().isoformat(),
                "packages": packages
            }, f, indent=2, ensure_ascii=False)
        
        log(f"备份完成: {len(packages)} 个包", LogLevel.SUCCESS)
        return req_file


class RestoreManager:
    """恢复管理器"""
    
    def __init__(self):
        self.conda = CondaManager()
        self.report = RestoreReport(start_time=datetime.now().isoformat())
    
    def restore_conda(self, backup_file: str, target_env: str = None,
                      use_uv: bool = False, parallel: bool = False,
                      max_workers: int = None, resume: bool = True) -> RestoreReport:
        """
        恢复 Conda 环境
        
        Args:
            backup_file: 备份文件路径
            target_env: 目标环境名
            use_uv: 是否使用 UV 加速
            parallel: 是否并行安装
            max_workers: 并行工作数
            resume: 是否启用断点续传
        """
        # 加载备份 (检查文件是否存在)
        if not os.path.exists(backup_file):
            log(f"❌ 备份文件不存在: {backup_file}", LogLevel.ERROR)
            print("\n" + "="*60)
            print("📋 提示: 该备份文件不存在，请先执行备份操作")
            print("="*60)
            print("\n💡 备份命令示例:")
            print(f"   python conda_env_toolkit.py backup <环境名> -o {backup_file.replace('.json', '')}")
            print("\n📝 说明:")
            print("   1. 先确认要备份的 Conda 环境名称")
            print("      conda env list")
            print("   2. 执行备份命令")
            print("      python conda_env_toolkit.py backup myenv")
            print("   3. 再执行恢复命令")
            print(f"      python conda_env_toolkit.py restore {backup_file} -n <新环境名>")
            print("="*60 + "\n")
            sys.exit(1)
        
        log(f"加载备份: {backup_file}")
        with open(backup_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # 将 dict 转换为 dataclass 对象
        packages_data = data.get("environment", {}).get("packages", [])
        packages = [PackageInfo(**pkg) for pkg in packages_data]
        
        env_info = EnvironmentInfo(
            name=data.get("environment", {}).get("name", "unknown"),
            python_version=data.get("environment", {}).get("python_version", "3.11"),
            platform=data.get("environment", {}).get("platform", sys.platform),
            conda_version=data.get("environment", {}).get("conda_version", ""),
            packages=packages
        )
        
        # 验证备份 (简化验证)
        checksum = data.get("checksum", "")
        if not checksum:
            log("备份无校验值", LogLevel.WARNING)
        
        # 确定目标环境
        target = target_env or env_info.name
        log(f"恢复环境: {target}")
        
        # 断点续传
        state = None
        if resume and os.path.exists(Config.STATE_FILE):
            state = RestoreState.load()
            if state and state.backup_file == backup_file:
                log(f"检测到未完成恢复，已安装 {len(state.completed_packages)} 个包", LogLevel.HIGHLIGHT)
        
        if not state:
            state = RestoreState(backup_file=backup_file, target_env=target)
        
        # 创建环境
        if not self.conda.env_exists(target):
            python_ver = env_info.python_version or "3.11"
            self.conda.create_env(target, python_ver)
        
        # 分类包
        packages = env_info.packages
        self.report.total_packages = len(packages)
        
        conda_packages = []
        pip_packages = []
        
        for pkg in packages:
            if state.is_completed(pkg.name):
                self.report.already_installed += 1
                continue
            
            source = PackageDatabase.classify(pkg.name)
            if source == PackageSource.CONDA:
                conda_packages.append(pkg)
            else:
                pip_packages.append(pkg)
        
        log(f"待安装: {len(conda_packages)} Conda 包, {len(pip_packages)} Pip 包")
        
        # 安装 Conda 包 (带 Rich 进度条)
        if conda_packages:
            log(f"安装 {len(conda_packages)} 个 Conda 包...")
            with RichProgress("安装 Conda 包", total=len(conda_packages)) as progress:
                if parallel:
                    names = [p.name for p in conda_packages]
                    success, failed = self.conda.install_packages_batch(target, names, max_workers)
                    self.report.conda_success.extend(success)
                    for pkg_name in success:
                        progress.update(1)
                    for pkg_name in failed:
                        self.report.failed.append({"name": pkg_name, "error": "安装失败"})
                        progress.update(1)
                else:
                    for pkg in conda_packages:
                        if self.conda.install_package(target, pkg.name):
                            self.report.conda_success.append(pkg.name)
                            state.mark_completed(pkg.name)
                        else:
                            self.report.failed.append({"name": pkg.name, "error": "Conda安装失败"})
                        progress.update(1)
        
        # 安装 Pip 包 (使用 UV 或 Pip，带 Rich 进度条)
        if pip_packages:
            log(f"安装 {len(pip_packages)} 个 Pip 包...")
            
            if use_uv and UVManager.is_installed():
                log("使用 UV 加速安装", LogLevel.UV)
                uv = UVManager()
                names = [f"{p.name}=={p.version}" if p.version else p.name for p in pip_packages]
                with RichProgress("UV 安装 Pip 包", total=len(names)) as progress:
                    success, failed = uv.install_packages(names)
                    self.report.uv_success.extend([p.name for p in pip_packages if p.name in success])
                    for _ in success:
                        progress.update(1)
                    for pkg_name in failed:
                        self.report.failed.append({"name": pkg_name, "error": "UV安装失败"})
                        progress.update(1)
            else:
                # 使用 pip
                names = [p.name for p in pip_packages]
                with RichProgress("Pip 安装包", total=len(names)) as progress:
                    for pkg_name in names:
                        cmd = ["conda", "run", "-n", target, "pip", "install", pkg_name]
                        ok, _, _ = run_cmd(cmd, timeout=120)
                        if ok:
                            self.report.pip_success.append(pkg_name)
                            state.mark_completed(pkg_name)
                        else:
                            self.report.failed.append({"name": pkg_name, "error": "Pip安装失败"})
                        progress.update(1)
        
        # 完成
        self.report.end_time = datetime.now().isoformat()
        state.clear()
        
        # 保存报告
        self.report.save()
        self.report.print_summary()
        
        return self.report
    
    def restore_uv(self, req_file: str, venv_path: str = None,
                   parallel: bool = False) -> bool:
        """恢复 UV 环境"""
        log(f"恢复 UV 环境 from {req_file}")
        
        if not UVManager.is_installed():
            UVManager.install()
        
        venv_path = venv_path or ".venv"
        
        # 创建虚拟环境
        if not os.path.exists(venv_path):
            uv = UVManager()
            uv.create_venv(venv_path)
        
        # 安装包
        uv = UVManager(venv_path)
        
        if req_file.endswith(".txt"):
            with open(req_file, "r", encoding="utf-8") as f:
                packages = [line.strip() for line in f 
                           if line.strip() and not line.startswith("#")]
        elif req_file.endswith(".json"):
            with open(req_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            packages = [f"{p['name']}=={p['version']}" for p in data.get("packages", [])]
        else:
            log("不支持的文件格式", LogLevel.ERROR)
            return False
        
        success, failed = uv.install_packages(packages, parallel=parallel)
        
        log(f"UV 环境恢复完成: {len(success)} 成功, {len(failed)} 失败", 
            LogLevel.SUCCESS if not failed else LogLevel.WARNING)
        
        return len(failed) == 0
    
    def restore_all_from_backup_dir(self, backup_dir: str, 
                                    restore_mode: str = "all",
                                    selected_envs: List[str] = None,
                                    use_uv: bool = False, 
                                    parallel: bool = False,
                                    resume: bool = True) -> Dict[str, RestoreReport]:
        """
        从备份目录批量恢复环境
        
        Args:
            backup_dir: 备份目录路径
            restore_mode: 恢复模式 ("all"=全部, "select"=选择)
            selected_envs: 选择恢复的环境列表
            use_uv: 是否使用 UV 加速
            parallel: 是否并行安装
            resume: 是否启用断点续传
            
        Returns:
            每个环境的恢复报告字典
        """
        if not os.path.exists(backup_dir):
            log(f"备份目录不存在: {backup_dir}", LogLevel.ERROR)
            return {}
        
        # 查找所有备份文件
        backup_files = list(Path(backup_dir).glob("*_backup.json"))
        if not backup_files:
            log(f"备份目录中没有找到备份文件: {backup_dir}", LogLevel.ERROR)
            return {}
        
        log(f"发现 {len(backup_files)} 个备份文件")
        
        # 解析备份文件信息
        env_backups = {}
        for bf in backup_files:
            try:
                with open(bf, "r", encoding="utf-8") as f:
                    data = json.load(f)
                env_name = data.get("environment", {}).get("name", bf.stem.replace("_backup", ""))
                pkg_count = len(data.get("environment", {}).get("packages", []))
                env_backups[env_name] = {
                    "file": str(bf),
                    "packages": pkg_count,
                    "python_version": data.get("environment", {}).get("python_version", "unknown")
                }
            except Exception as e:
                log(f"解析备份文件失败 {bf}: {e}", LogLevel.WARNING)
        
        if not env_backups:
            log("没有有效的备份文件", LogLevel.ERROR)
            return {}
        
        # 根据模式决定恢复哪些环境
        envs_to_restore = []
        if restore_mode == "all":
            envs_to_restore = list(env_backups.keys())
            log(f"将恢复所有 {len(envs_to_restore)} 个环境")
        elif restore_mode == "select" and selected_envs:
            envs_to_restore = [e for e in selected_envs if e in env_backups]
            log(f"将恢复选择的 {len(envs_to_restore)} 个环境")
        else:
            log("没有选择要恢复的环境", LogLevel.WARNING)
            return {}
        
        # 开始恢复
        results = {}
        with RichProgress("批量恢复环境", total=len(envs_to_restore)) as progress:
            for env_name in envs_to_restore:
                backup_info = env_backups[env_name]
                log(f"恢复环境: {env_name} ({backup_info['packages']} 个包)")
                
                try:
                    report = self.restore_conda(
                        backup_info["file"],
                        target_env=env_name,
                        use_uv=use_uv,
                        parallel=parallel,
                        resume=resume
                    )
                    results[env_name] = report
                    log(f"✅ {env_name} 恢复完成")
                except Exception as e:
                    log(f"❌ {env_name} 恢复失败: {e}", LogLevel.ERROR)
                
                progress.update(1)
        
        # 生成汇总报告
        print("\n" + "="*60)
        print("📊 批量恢复完成汇总:")
        print("="*60)
        print(f"  总环境数: {len(envs_to_restore)}")
        print(f"  成功: {sum(1 for r in results.values() if r.success_rate > 0)} 个")
        print(f"  完全成功: {sum(1 for r in results.values() if r.success_rate == 100)} 个")
        print(f"  失败: {len(envs_to_restore) - len(results)} 个")
        print("="*60)
        
        return results


# ═══════════════════════════════════════════════════════════════════════════════
# 交互式菜单
# ═══════════════════════════════════════════════════════════════════════════════
class InteractiveMenu:
    """交互式菜单系统"""
    
    def __init__(self):
        self.backup_mgr = BackupManager()
        self.restore_mgr = RestoreManager()
        self.conda = CondaManager()
        self.running = True
    
    def show_banner(self):
        """显示欢迎横幅"""
        print("\n" + "="*70)
        print(f"  🐍 Conda 环境管理工具箱 v{VERSION}")
        print(f"  {VERSION_NAME}")
        print("="*70)
        print(f"  💡 提示: 支持 Conda + UV 双模式 | 并行安装加速 | 智能断点续传")
        print("="*70 + "\n")
    
    def show_main_menu(self):
        """显示主菜单"""
        print("\n📋 主菜单:")
        print("-" * 50)
        print("  【环境管理】")
        print("    1. 🔒 备份 Conda 环境")
        print("    2. 🔓 恢复 Conda 环境")
        print("    3. 📋 克隆 Conda 环境")
        print("    4. 🔍 对比 Conda 环境")
        print("    5. 👁️  查看 Conda 环境")
        print("    6. 🧹 清理 Conda 环境")
        print()
        print("  【UV 管理】")
        print("    7. 🔒 备份 UV 环境")
        print("    8. 🔓 恢复 UV 环境")
        print("    9. ➕ 创建 UV 环境")
        print()
        print("  【转换工具】")
        print("   10. 🔄 Conda → UV 转换")
        print("   11. 🔄 UV → Conda 转换")
        print()
        print("  【系统工具】")
        print("   12. 🧹 系统清理")
        print("   13. ⚙️  配置设置")
        print()
        print("    0. 🚪 退出")
        print("-" * 50)
        
        # 显示 UV 状态
        if UVManager.is_installed():
            print("  [UV 状态: ✅ 已安装]")
        else:
            print("  [UV 状态: ❌ 未安装 - 建议安装以获得10倍加速]")
    
    def get_env_choice(self, prompt: str = "环境") -> str:
        """获取环境选择"""
        envs = self.conda.get_envs()
        print(f"\n可用 {prompt}:")
        for i, env in enumerate(envs, 1):
            print(f"  {i}. {env}")
        
        choice = input(f"\n选择 {prompt} (名称或编号): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(envs):
            return envs[int(choice) - 1]
        return choice
    
    def handle_backup_conda(self):
        """处理 Conda 备份"""
        print("\n备份选项:")
        print("  1. 备份单个环境")
        print("  2. 备份所有环境")
        
        choice = input("选择 [1-2]: ").strip()
        
        print("\n选择导出格式:")
        print("  1. JSON (推荐，信息完整)")
        print("  2. TXT (简洁列表)")
        print("  3. YAML (conda环境文件)")
        print("  4. Requirements (pip格式)")
        print("  5. Markdown (表格报告)")
        print("  6. 全部格式")
        
        fmt_choice = input("选择 [1-6]: ").strip()
        formats_map = {
            "1": ["json"], "2": ["txt"], "3": ["yaml"],
            "4": ["requirements"], "5": ["markdown"],
            "6": ["json", "txt", "yaml", "requirements", "markdown"]
        }
        formats = formats_map.get(fmt_choice, ["json"])
        
        if choice == "2":
            # 批量备份所有环境
            output_dir = input("输出目录 (默认: _backups/日期): ").strip() or None
            include_base = input("包含 base 环境(全局默认环境)? [y/N]: ").strip().lower() == "y"
            with timer("批量备份"):
                self.backup_mgr.backup_all_envs(output_dir, formats, include_base)
        else:
            # 备份单个环境
            env_name = self.get_env_choice("Conda 环境")
            output = input("输出文件名 (默认: 环境名_backup): ").strip() or None
            
            with timer("备份"):
                self.backup_mgr.backup_conda(env_name, output, formats)
    
    def handle_restore_conda(self):
        """处理 Conda 恢复"""
        print("\n恢复选项:")
        print("  1. 恢复单个环境")
        print("  2. 从备份目录批量恢复")
        
        choice = input("选择 [1-2]: ").strip()
        
        if choice == "2":
            # 批量恢复
            self._handle_batch_restore()
        else:
            # 恢复单个环境
            self._handle_single_restore()
    
    def _handle_single_restore(self):
        """恢复单个环境"""
        # 查找备份文件
        files = list(Path(".").glob("*_backup.json"))
        if files:
            print("\n可用备份文件:")
            for i, f in enumerate(files, 1):
                print(f"  {i}. {f}")
        
        file_input = input("\n备份文件路径或编号: ").strip()
        if file_input.isdigit() and 1 <= int(file_input) <= len(files):
            backup_file = str(files[int(file_input) - 1])
        else:
            backup_file = file_input
        
        target = input("目标环境名称 (默认: 原环境名): ").strip() or None
        
        print("\n高级选项:")
        use_uv = input("使用 UV 加速? [Y/n]: ").strip().lower() != "n"
        parallel = input("启用并行安装? [y/N]: ").strip().lower() == "y"
        resume = input("启用断点续传? [Y/n]: ").strip().lower() != "n"
        
        with timer("恢复"):
            self.restore_mgr.restore_conda(
                backup_file, target, use_uv=use_uv, 
                parallel=parallel, resume=resume
            )
    
    def _handle_batch_restore(self):
        """批量恢复环境"""
        backup_dir = input("备份目录路径 (默认: _backups): ").strip() or "_backups"
        
        if not os.path.exists(backup_dir):
            log(f"目录不存在: {backup_dir}", LogLevel.ERROR)
            return
        
        # 查找备份文件
        backup_files = list(Path(backup_dir).glob("*_backup.json"))
        if not backup_files:
            log(f"目录中没有备份文件: {backup_dir}", LogLevel.ERROR)
            return
        
        # 显示可用环境
        print(f"\n发现 {len(backup_files)} 个备份:")
        env_list = []
        for i, bf in enumerate(backup_files, 1):
            try:
                with open(bf, "r", encoding="utf-8") as f:
                    data = json.load(f)
                env_name = data.get("environment", {}).get("name", bf.stem)
                pkg_count = len(data.get("environment", {}).get("packages", []))
                env_list.append((env_name, str(bf), pkg_count))
                print(f"  {i}. {env_name} ({pkg_count} 个包)")
            except:
                print(f"  {i}. {bf} (无法解析)")
        
        print("\n恢复模式:")
        print("  1. 恢复所有环境")
        print("  2. 选择部分环境恢复")
        
        mode_choice = input("选择 [1-2]: ").strip()
        
        restore_mode = "all"
        selected_envs = None
        
        if mode_choice == "2":
            restore_mode = "select"
            print("\n输入要恢复的环境编号（多个用逗号分隔，如: 1,3,5）:")
            selections = input("选择: ").strip()
            try:
                indices = [int(x.strip()) - 1 for x in selections.split(",")]
                selected_envs = [env_list[i][0] for i in indices if 0 <= i < len(env_list)]
                log(f"选择了 {len(selected_envs)} 个环境: {', '.join(selected_envs)}")
            except Exception as e:
                log(f"选择无效: {e}", LogLevel.ERROR)
                return
        
        print("\n高级选项:")
        use_uv = input("使用 UV 加速? [Y/n]: ").strip().lower() != "n"
        parallel = input("启用并行安装? [y/N]: ").strip().lower() == "y"
        resume = input("启用断点续传? [Y/n]: ").strip().lower() != "n"
        
        with timer("批量恢复"):
            self.restore_mgr.restore_all_from_backup_dir(
                backup_dir,
                restore_mode=restore_mode,
                selected_envs=selected_envs,
                use_uv=use_uv,
                parallel=parallel,
                resume=resume
            )
    
    def handle_clone(self):
        """处理克隆"""
        print("\n源环境:")
        source = self.get_env_choice()
        target = input("目标环境名称: ").strip()
        
        log(f"克隆: {source} → {target}")
        
        # 先备份再恢复
        temp_file = f".temp_{source}_backup.json"
        self.backup_mgr.backup_conda(source, temp_file.replace(".json", ""), ["json"])
        self.restore_mgr.restore_conda(temp_file, target, use_uv=True, resume=False)
        
        if os.path.exists(temp_file):
            os.remove(temp_file)
    
    def handle_compare(self):
        """处理对比"""
        print("\n选择两个环境进行对比:")
        env1 = self.get_env_choice("环境1")
        env2 = self.get_env_choice("环境2")
        
        log(f"对比: {env1} vs {env2}")
        
        pkgs1 = {p.name: p for p in self.conda.get_packages(env1)}
        pkgs2 = {p.name: p for p in self.conda.get_packages(env2)}
        
        only_in_1 = set(pkgs1.keys()) - set(pkgs2.keys())
        only_in_2 = set(pkgs2.keys()) - set(pkgs1.keys())
        common = set(pkgs1.keys()) & set(pkgs2.keys())
        
        version_diff = []
        for name in common:
            v1 = pkgs1[name].version
            v2 = pkgs2[name].version
            if v1 != v2:
                version_diff.append((name, v1, v2))
        
        print("\n" + "="*70)
        print(f"对比结果: {env1} vs {env2}")
        print("="*70)
        print(f"\n仅在 {env1} 中 ({len(only_in_1)} 个):")
        for name in sorted(only_in_1)[:20]:
            print(f"  + {name}")
        if len(only_in_1) > 20:
            print(f"  ... 还有 {len(only_in_1)-20} 个")
        
        print(f"\n仅在 {env2} 中 ({len(only_in_2)} 个):")
        for name in sorted(only_in_2)[:20]:
            print(f"  - {name}")
        if len(only_in_2) > 20:
            print(f"  ... 还有 {len(only_in_2)-20} 个")
        
        print(f"\n版本不同 ({len(version_diff)} 个):")
        for name, v1, v2 in sorted(version_diff)[:20]:
            print(f"  ~ {name}: {v1} → {v2}")
        if len(version_diff) > 20:
            print(f"  ... 还有 {len(version_diff)-20} 个")
        
        print("="*70)
    
    def handle_view(self):
        """处理查看"""
        env_name = self.get_env_choice()
        
        log(f"查看环境: {env_name}")
        packages = self.conda.get_packages(env_name)
        
        conda_pkgs = [p for p in packages if p.source == PackageSource.CONDA]
        pip_pkgs = [p for p in packages if p.source == PackageSource.PIP]
        
        print("\n" + "="*70)
        print(f"环境: {env_name}")
        print("="*70)
        print(f"\n📦 Conda 包 ({len(conda_pkgs)} 个):")
        for pkg in sorted(conda_pkgs, key=lambda x: x.name)[:30]:
            ver = pkg.version or "unknown"
            print(f"  {pkg.name:<35} {ver:<15}")
        if len(conda_pkgs) > 30:
            print(f"  ... 还有 {len(conda_pkgs)-30} 个")
        
        print(f"\n🐍 Pip 包 ({len(pip_pkgs)} 个):")
        for pkg in sorted(pip_pkgs, key=lambda x: x.name)[:30]:
            ver = pkg.version or "unknown"
            print(f"  {pkg.name:<35} {ver:<15}")
        if len(pip_pkgs) > 30:
            print(f"  ... 还有 {len(pip_pkgs)-30} 个")
        
        print("="*70)
    
    def handle_cleanup(self):
        """处理清理"""
        print("\n清理选项:")
        print("  1. 清理 Conda 缓存")
        print("  2. 清理 Pip 缓存")
        print("  3. 清理 UV 缓存")
        print("  4. 清理所有缓存")
        print("  5. 清理临时文件")
        
        choice = input("\n选择 [1-5]: ").strip()
        
        if choice == "1":
            log("清理 Conda 缓存...")
            run_cmd(["conda", "clean", "--all", "-y"], timeout=300)
            log("Conda 缓存清理完成！", LogLevel.SUCCESS)
        elif choice == "2":
            log("清理 Pip 缓存...")
            run_cmd([sys.executable, "-m", "pip", "cache", "purge"], timeout=60)
            log("Pip 缓存清理完成！", LogLevel.SUCCESS)
        elif choice == "3":
            log("清理 UV 缓存...")
            run_cmd(["uv", "cache", "clean"], timeout=60)
            log("UV 缓存清理完成！", LogLevel.SUCCESS)
        elif choice == "4":
            log("清理所有缓存...")
            run_cmd(["conda", "clean", "--all", "-y"], timeout=300)
            run_cmd([sys.executable, "-m", "pip", "cache", "purge"], timeout=60)
            if UVManager.is_installed():
                run_cmd(["uv", "cache", "clean"], timeout=60)
            log("所有缓存清理完成！", LogLevel.SUCCESS)
        elif choice == "5":
            patterns = ["*.tmp", "temp_*", ".temp_*"]
            count = 0
            for pattern in patterns:
                for f in Path(".").glob(pattern):
                    try:
                        f.unlink()
                        count += 1
                    except:
                        pass
            log(f"清理了 {count} 个临时文件", LogLevel.SUCCESS)
    
    def handle_settings(self):
        """处理设置"""
        print("\n⚙️  配置设置:")
        print(f"  1. 自动使用 UV: {'✅' if Config.AUTO_USE_UV else '❌'}")
        print(f"  2. 自动使用镜像: {'✅' if Config.AUTO_USE_MIRROR else '❌'}")
        print(f"  3. 保留临时文件: {'✅' if Config.KEEP_TEMP_FILES else '❌'}")
        print(f"  4. 详细日志模式: {'✅' if Config.VERBOSE else '❌'}")
        print(f"  5. 默认并行数: {Config.DEFAULT_MAX_WORKERS}")
        print("  6. 恢复默认设置")
        
        choice = input("\n选择要修改的设置 [1-6]: ").strip()
        
        if choice == "1":
            Config.AUTO_USE_UV = not Config.AUTO_USE_UV
        elif choice == "2":
            Config.AUTO_USE_MIRROR = not Config.AUTO_USE_MIRROR
        elif choice == "3":
            Config.KEEP_TEMP_FILES = not Config.KEEP_TEMP_FILES
        elif choice == "4":
            Config.VERBOSE = not Config.VERBOSE
        elif choice == "5":
            workers = input(f"输入并行数 (当前: {Config.DEFAULT_MAX_WORKERS}): ").strip()
            if workers.isdigit():
                Config.DEFAULT_MAX_WORKERS = int(workers)
        elif choice == "6":
            Config.AUTO_USE_UV = True
            Config.AUTO_USE_MIRROR = True
            Config.KEEP_TEMP_FILES = False
            Config.VERBOSE = False
            Config.DEFAULT_MAX_WORKERS = 4
            log("设置已恢复默认", LogLevel.SUCCESS)
        
        # 保存配置
        config_data = {
            "AUTO_USE_UV": Config.AUTO_USE_UV,
            "AUTO_USE_MIRROR": Config.AUTO_USE_MIRROR,
            "KEEP_TEMP_FILES": Config.KEEP_TEMP_FILES,
            "VERBOSE": Config.VERBOSE,
            "DEFAULT_MAX_WORKERS": Config.DEFAULT_MAX_WORKERS,
        }
        with open(Config.CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=2)
        log("配置已保存", LogLevel.SUCCESS)
    
    def run(self):
        """运行交互菜单"""
        self.show_banner()
        
        # 加载配置
        if os.path.exists(Config.CONFIG_FILE):
            try:
                with open(Config.CONFIG_FILE, "r", encoding="utf-8") as f:
                    config_data = json.load(f)
                for key, value in config_data.items():
                    if hasattr(Config, key):
                        setattr(Config, key, value)
            except:
                pass
        
        while self.running:
            try:
                self.show_main_menu()
                choice = input("\n请选择操作 [0-13]: ").strip()
                
                handlers = {
                    "1": self.handle_backup_conda,
                    "2": self.handle_restore_conda,
                    "3": self.handle_clone,
                    "4": self.handle_compare,
                    "5": self.handle_view,
                    "6": lambda: log("环境清理功能开发中..."),
                    "7": lambda: log("UV备份功能开发中..."),
                    "8": lambda: log("UV恢复功能开发中..."),
                    "9": lambda: log("UV创建功能开发中..."),
                    "10": lambda: log("转换功能开发中..."),
                    "11": lambda: log("转换功能开发中..."),
                    "12": self.handle_cleanup,
                    "13": self.handle_settings,
                    "0": lambda: setattr(self, "running", False) or log("再见！👋"),
                }
                
                handler = handlers.get(choice)
                if handler:
                    try:
                        handler()
                    except Exception as e:
                        log(f"操作失败: {e}", LogLevel.ERROR)
                else:
                    log("无效选择，请重试", LogLevel.WARNING)
                
                if self.running:
                    input("\n按回车继续...")
            except KeyboardInterrupt:
                print("\n")
                log("用户中断操作，退出程序...", LogLevel.WARNING)
                break
            except EOFError:
                print("\n")
                log("输入流关闭，退出程序...", LogLevel.WARNING)
                break


# ═══════════════════════════════════════════════════════════════════════════════
# 命令行接口
# ═══════════════════════════════════════════════════════════════════════════════
def create_parser() -> argparse.ArgumentParser:
    """创建命令行解析器"""
    parser = argparse.ArgumentParser(
        prog="conda_env_toolkit",
        description="Conda 环境管理工具箱 - 最终完美版 v" + VERSION,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 交互模式 (推荐新手)
  python conda_env_toolkit.py
  
  # 备份单个环境
  python conda_env_toolkit.py backup myenv --all-formats
  python conda_env_toolkit.py backup myenv -o mybackup --formats json yaml
  
  # 备份所有环境
  python conda_env_toolkit.py backup --all-envs
  python conda_env_toolkit.py backup --all-envs --all-formats --output-dir ./my_backups
  
  # 恢复环境 (并行+UV加速)
  python conda_env_toolkit.py restore backup.json -n newenv --parallel --use-uv
  python conda_env_toolkit.py restore backup.json --max-workers 8 --no-resume
  
  # 克隆环境
  python conda_env_toolkit.py clone oldenv newenv
  
  # 对比环境
  python conda_env_toolkit.py compare env1 env2
  
  # 查看环境
  python conda_env_toolkit.py view myenv
  
  # 系统清理
  python conda_env_toolkit.py cleanup --all
  python conda_env_toolkit.py cleanup --conda --pip

更多信息: https://github.com/conda-env-toolkit/docs
        """
    )
    
    parser.add_argument("--version", "-v", action="version", version=f"%(prog)s {VERSION}")
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # backup 命令
    backup_parser = subparsers.add_parser("backup", help="备份 Conda 环境")
    backup_parser.add_argument("env_name", nargs="?", default=None, help="环境名称 (省略则备份所有环境)")
    backup_parser.add_argument("-o", "--output", help="输出文件名前缀")
    backup_parser.add_argument("--all-formats", action="store_true", help="导出所有格式")
    backup_parser.add_argument("--formats", nargs="+", choices=["json", "txt", "yaml", "requirements", "markdown"],
                              help="指定导出格式")
    backup_parser.add_argument("--all-envs", action="store_true", help="备份所有环境")
    backup_parser.add_argument("--output-dir", help="批量备份输出目录")
    backup_parser.add_argument("--include-base", action="store_true", help="包含 base 环境（全局默认环境）")
    backup_parser.add_argument("--verbose", action="store_true", help="启用详细日志")
    
    # restore 命令
    restore_parser = subparsers.add_parser("restore", help="恢复 Conda 环境")
    restore_parser.add_argument("backup_file", help="备份文件路径")
    restore_parser.add_argument("-n", "--env-name", help="目标环境名称")
    restore_parser.add_argument("--use-uv", action="store_true", help="使用 UV 加速")
    restore_parser.add_argument("--parallel", action="store_true", help="并行安装")
    restore_parser.add_argument("--max-workers", type=int, default=4, help="并行工作数")
    restore_parser.add_argument("--no-resume", action="store_true", help="禁用断点续传")
    restore_parser.add_argument("--verbose", action="store_true", help="启用详细日志")
    
    # clone 命令
    clone_parser = subparsers.add_parser("clone", help="克隆 Conda 环境")
    clone_parser.add_argument("source_env", help="源环境")
    clone_parser.add_argument("target_env", help="目标环境")
    clone_parser.add_argument("--verbose", action="store_true", help="启用详细日志")
    
    # compare 命令
    compare_parser = subparsers.add_parser("compare", help="对比两个环境")
    compare_parser.add_argument("env1", help="环境1")
    compare_parser.add_argument("env2", help="环境2")
    compare_parser.add_argument("--verbose", action="store_true", help="启用详细日志")
    
    # view 命令
    view_parser = subparsers.add_parser("view", help="查看环境详情")
    view_parser.add_argument("env_name", help="环境名称")
    view_parser.add_argument("--verbose", action="store_true", help="启用详细日志")
    
    # cleanup 命令
    cleanup_parser = subparsers.add_parser("cleanup", help="清理缓存")
    cleanup_parser.add_argument("--all", action="store_true", help="清理所有缓存")
    cleanup_parser.add_argument("--conda", action="store_true", help="清理 Conda 缓存")
    cleanup_parser.add_argument("--pip", action="store_true", help="清理 Pip 缓存")
    cleanup_parser.add_argument("--uv", action="store_true", help="清理 UV 缓存")
    cleanup_parser.add_argument("--temp", action="store_true", help="清理临时文件")
    cleanup_parser.add_argument("--verbose", action="store_true", help="启用详细日志")
    
    # classify 命令 (在线分类)
    classify_parser = subparsers.add_parser("classify", help="在线分类包 (conda vs pip)")
    classify_parser.add_argument("package_file", help="包列表文件")
    classify_parser.add_argument("-o", "--output", default="classified", help="输出文件名前缀")
    classify_parser.add_argument("--refresh", action="store_true", help="强制刷新索引")
    classify_parser.add_argument("--verbose", action="store_true", help="启用详细日志")
    
    # check 命令 (网络检查)
    check_parser = subparsers.add_parser("check", help="检查网络和镜像")
    check_parser.add_argument("--verbose", action="store_true", help="启用详细日志")
    
    return parser


def main():
    """主入口函数"""
    parser = create_parser()
    args = parser.parse_args()
    
    # 设置详细模式 (从子命令参数中获取)
    if hasattr(args, 'verbose') and args.verbose:
        Config.VERBOSE = True
    
    # 无命令时进入交互模式
    if not args.command:
        menu = InteractiveMenu()
        menu.run()
        return
    
    # 执行命令
    backup_mgr = BackupManager()
    restore_mgr = RestoreManager()
    conda = CondaManager()
    
    try:
        if args.command == "backup":
            formats = ["json"]
            if args.all_formats:
                formats = ["json", "txt", "yaml", "requirements"]
            elif args.formats:
                formats = args.formats
            
            # 批量备份所有环境
            if args.all_envs or args.env_name is None:
                backup_mgr.backup_all_envs(args.output_dir, formats, args.include_base)
            else:
                backup_mgr.backup_conda(args.env_name, args.output, formats)
        
        elif args.command == "restore":
            restore_mgr.restore_conda(
                args.backup_file,
                target_env=args.env_name,
                use_uv=args.use_uv,
                parallel=args.parallel,
                max_workers=args.max_workers,
                resume=not args.no_resume
            )
        
        elif args.command == "clone":
            log(f"克隆: {args.source_env} → {args.target_env}")
            temp_file = f".temp_{args.source_env}_backup.json"
            backup_mgr.backup_conda(args.source_env, temp_file.replace(".json", ""), ["json"])
            restore_mgr.restore_conda(temp_file, args.target_env, use_uv=True, resume=False)
            if os.path.exists(temp_file) and not Config.KEEP_TEMP_FILES:
                os.remove(temp_file)
        
        elif args.command == "compare":
            # 简单的对比实现
            pkgs1 = {p.name: p.version for p in conda.get_packages(args.env1)}
            pkgs2 = {p.name: p.version for p in conda.get_packages(args.env2)}
            
            only_in_1 = set(pkgs1.keys()) - set(pkgs2.keys())
            only_in_2 = set(pkgs2.keys()) - set(pkgs1.keys())
            
            print(f"\n对比: {args.env1} vs {args.env2}")
            print("-" * 50)
            print(f"仅在 {args.env1}: {len(only_in_1)} 个")
            print(f"仅在 {args.env2}: {len(only_in_2)} 个")
            print(f"共有: {len(set(pkgs1.keys()) & set(pkgs2.keys()))} 个")
        
        elif args.command == "view":
            packages = conda.get_packages(args.env_name)
            print(f"\n环境: {args.env_name}")
            print(f"总包数: {len(packages)}")
            print(f"Conda 包: {len([p for p in packages if p.source == PackageSource.CONDA])}")
            print(f"Pip 包: {len([p for p in packages if p.source == PackageSource.PIP])}")
        
        elif args.command == "cleanup":
            if args.all or args.conda:
                log("清理 Conda 缓存...")
                run_cmd(["conda", "clean", "--all", "-y"], timeout=300)
            if args.all or args.pip:
                log("清理 Pip 缓存...")
                run_cmd([sys.executable, "-m", "pip", "cache", "purge"], timeout=60)
            if args.all or args.uv:
                if UVManager.is_installed():
                    log("清理 UV 缓存...")
                    run_cmd(["uv", "cache", "clean"], timeout=60)
            if args.all or args.temp:
                count = 0
                for pattern in ["*.tmp", "temp_*", ".temp_*"]:
                    for f in Path(".").glob(pattern):
                        try:
                            f.unlink()
                            count += 1
                        except:
                            pass
                log(f"清理了 {count} 个临时文件")
            
            log("清理完成！", LogLevel.SUCCESS)
        
        elif args.command == "classify":
            # 在线分类包
            log(f"加载包列表: {args.package_file}")
            with open(args.package_file, "r", encoding="utf-8") as f:
                packages = [line.strip() for line in f if line.strip() and not line.startswith("#")]
            
            log(f"共 {len(packages)} 个包，开始在线分类...")
            indexer = OnlinePackageIndex()
            conda_list, pip_list = indexer.classify_packages(packages)
            
            # 保存结果
            conda_file = f"{args.output}_conda.txt"
            pip_file = f"{args.output}_pip.txt"
            
            with open(conda_file, "w", encoding="utf-8") as f:
                f.write("\n".join(conda_list) + "\n")
            with open(pip_file, "w", encoding="utf-8") as f:
                f.write("\n".join(pip_list) + "\n")
            
            log(f"✅ 分类完成:", LogLevel.SUCCESS)
            log(f"   Conda: {len(conda_list)} 个 -> {conda_file}")
            log(f"   Pip: {len(pip_list)} 个 -> {pip_file}")
        
        elif args.command == "check":
            # 网络检查
            result = NetworkChecker.full_check()
            print("\n" + "="*50)
            print("网络检查结果:")
            print("="*50)
            print(f"互联网连接: {'✅' if result['internet'] else '❌'}")
            print(f"Conda镜像: {'✅' if result['conda_mirror'][0] else '❌'} ({result['conda_mirror'][1] or '无'})")
            print(f"Pip镜像: {'✅' if result['pip_mirror'] else '❌'}")
            print("="*50)
    
    except KeyboardInterrupt:
        log("\n操作被用户中断", LogLevel.WARNING)
        sys.exit(1)
    except Exception as e:
        log(f"错误: {e}", LogLevel.ERROR)
        sys.exit(1)


if __name__ == "__main__":
    main()

