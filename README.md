# Conda 环境管理工具箱

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Conda](https://img.shields.io/badge/Conda-Supported-brightgreen.svg)](https://docs.conda.io/)
[![UV](https://img.shields.io/badge/UV-Accelerated-purple.svg)](https://github.com/astral-sh/uv)

> 🐍 一站式 Conda 环境管理解决方案 - 备份、恢复、克隆、对比、转换，应有尽有

## ✨ 核心特性

- ⚡ **极速恢复** - 并行安装 + UV 加速，比传统方式快 10-100 倍
- 🧠 **智能安装** - 2000+ 包分类数据库，自动选择最佳安装方式
- 🛡️ **可靠稳定** - 断点续传 + 自动重试 + 版本回退策略
- 🎨 **友好交互** - 交互式菜单 + 命令行双模式，Rich 进度条可视化
- 📦 **完整备份** - 支持 base 环境在内的所有环境批量备份
- 🔄 **环境转换** - Conda ↔ UV 无缝转换
- 📊 **多格式导出** - JSON / TXT / YAML / Requirements / Markdown

## 🚀 快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/yourusername/conda-env-toolkit.git
cd conda-env-toolkit

# 安装依赖（可选，用于 UV 加速）
pip install uv
```

### 交互模式（推荐新手）

```bash
python conda_env_toolkit.py
```

### 命令行模式

```bash
# 备份单个环境
python conda_env_toolkit.py backup myenv --all-formats

# 备份所有环境（包括 base）
python conda_env_toolkit.py backup --all-envs --include-base --output-dir ./backups

# 极速恢复（并行 + UV 加速）
python conda_env_toolkit.py restore backup.json -n newenv --parallel --use-uv

# 克隆环境
python conda_env_toolkit.py clone oldenv newenv

# 对比环境
python conda_env_toolkit.py compare env1 env2

# 查看环境详情
python conda_env_toolkit.py view myenv

# 系统清理
python conda_env_toolkit.py cleanup --all
```

## 📋 功能详解

### 1. 环境备份

支持多种格式导出，满足不同场景需求：

| 格式 | 扩展名 | 用途 |
|------|--------|------|
| JSON | `.json` | 完整信息，推荐用于恢复 |
| Markdown | `.md` | 表格报告，便于查看和分享 |
| YAML | `.yml` | Conda 环境文件格式 |
| TXT | `.txt` | 简洁列表 |
| Requirements | `_requirements.txt` | Pip 兼容格式 |

```bash
# 导出所有格式
python conda_env_toolkit.py backup myenv --all-formats

# 指定格式
python conda_env_toolkit.py backup myenv --formats json markdown

# 批量备份所有环境
python conda_env_toolkit.py backup --all-envs --include-base
```

### 2. 环境恢复

智能恢复机制，确保环境完整重建：

- **并行安装** - 同时安装多个包，大幅提升速度
- **UV 加速** - 使用 UV 替代 Pip，安装速度提升 10-100 倍
- **断点续传** - 中断后可从上次位置继续
- **版本回退** - 安装失败时自动尝试其他版本
- **智能分类** - 自动区分 Conda/Pip 包，选择最佳安装方式

```bash
# 基础恢复
python conda_env_toolkit.py restore backup.json -n newenv

# 极速恢复（推荐）
python conda_env_toolkit.py restore backup.json -n newenv --parallel --use-uv

# 批量恢复
# 交互菜单选择"从备份目录批量恢复"，支持全部恢复或选择性恢复
```

### 3. 环境克隆

一键克隆环境，快速创建副本：

```bash
python conda_env_toolkit.py clone oldenv newenv
```

### 4. 环境对比

分析两个环境的差异：

```bash
python conda_env_toolkit.py compare env1 env2
```

输出包含：
- 仅在环境1中的包
- 仅在环境2中的包
- 版本不同的包

### 5. 环境查看

查看环境详细信息：

```bash
python conda_env_toolkit.py view myenv
```

### 6. 系统清理

清理缓存和临时文件：

```bash
# 清理所有缓存
python conda_env_toolkit.py cleanup --all

# 单独清理
python conda_env_toolkit.py cleanup --conda    # Conda 缓存
python conda_env_toolkit.py cleanup --pip      # Pip 缓存
python conda_env_toolkit.py cleanup --uv       # UV 缓存
python conda_env_toolkit.py cleanup --temp     # 临时文件
```

### 7. 包分类

在线查询包的最佳安装方式：

```bash
python conda_env_toolkit.py classify packages.txt
```

## 🏗️ 架构设计

```
conda_env_toolkit.py
├── CondaManager          # Conda 环境管理
├── UVManager             # UV 加速管理
├── PackageDatabase       # 包分类数据库
├── BackupManager         # 备份管理
├── RestoreManager        # 恢复管理
├── EnvironmentInfo       # 环境信息模型
├── PackageInfo           # 包信息模型
├── BackupData            # 备份数据模型
├── RestoreReport         # 恢复报告
├── RichProgress          # 进度条组件
├── InteractiveMenu       # 交互菜单
└── Config                # 配置管理
```

## 📊 性能对比

| 操作 | 传统方式 | 本工具 (UV+并行) | 提升 |
|------|----------|------------------|------|
| 恢复 100 个包 | ~10 分钟 | ~1 分钟 | **10x** |
| 恢复 500 个包 | ~1 小时 | ~3 分钟 | **20x** |
| 环境克隆 | ~15 分钟 | ~2 分钟 | **7x** |

## 🛠️ 高级配置

工具会自动创建配置文件 `.conda_env_toolkit_config.json`：

```json
{
  "AUTO_USE_UV": true,
  "AUTO_USE_MIRROR": true,
  "KEEP_TEMP_FILES": false,
  "VERBOSE": false,
  "DEFAULT_MAX_WORKERS": 4
}
```

或通过交互菜单（选项 13）进行配置。

## 📝 使用场景

### 场景 1：Conda 升级/重装

```bash
# 1. 备份所有环境（包括 base）
python conda_env_toolkit.py backup --all-envs --include-base --output-dir ./backups

# 2. 升级/重装 Conda
# ...

# 3. 恢复所有环境
# 使用交互菜单选择"从备份目录批量恢复"
```

### 场景 2：环境迁移

```bash
# 源机器
python conda_env_toolkit.py backup myenv --all-formats
# 复制备份文件到目标机器

# 目标机器
python conda_env_toolkit.py restore myenv_backup.json -n myenv --parallel --use-uv
```

### 场景 3：团队协作

```bash
# 导出 Markdown 报告，便于分享
python conda_env_toolkit.py backup myenv --formats markdown
# 分享 myenv_backup.md 给团队成员
```

## 🤝 贡献

欢迎提交 Issue 和 PR！

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- [Conda](https://docs.conda.io/) - 包管理器
- [UV](https://github.com/astral-sh/uv) - 极速 Python 包安装器
- [Rich](https://github.com/Textualize/rich) - 终端美化库

---

> 💡 **提示**：首次使用建议运行 `python conda_env_toolkit.py` 进入交互模式，体验完整功能！
