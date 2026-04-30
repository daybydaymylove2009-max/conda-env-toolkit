# 环境备份功能详解

> 📦 完整备份 Conda 环境，支持多种格式

## 功能概述

备份功能可以导出环境的完整信息，包括：
- 环境名称和 Python 版本
- 所有已安装的包（名称、版本、渠道、构建号）
- 包分类信息（Conda / Pip）
- 创建时间和元数据

## 支持的格式

| 格式 | 扩展名 | 用途 | 特点 |
|------|--------|------|------|
| JSON | `.json` | 完整备份 | 信息最全，推荐用于恢复 |
| Markdown | `.md` | 报告查看 | 表格形式，便于阅读和分享 |
| YAML | `.yml` | Conda兼容 | 可直接用于 `conda env create` |
| TXT | `.txt` | 简洁列表 | 纯文本，简单明了 |
| Requirements | `_requirements.txt` | Pip兼容 | 可用于 `pip install -r` |

## 使用方式

### 交互模式

选择菜单 **"1. 备份环境"** 或 **"8. 批量备份所有环境"**

### 命令行模式

```bash
# 基础备份（默认JSON格式）
python conda_env_toolkit.py backup myenv

# 备份所有格式
python conda_env_toolkit.py backup myenv --all-formats

# 指定格式
python conda_env_toolkit.py backup myenv --formats json markdown

# 指定输出目录
python conda_env_toolkit.py backup myenv --output-dir ./backups

# 批量备份所有环境
python conda_env_toolkit.py backup --all-envs --output-dir ./_backups

# 包含 base 环境
python conda_env_toolkit.py backup --all-envs --include-base
```

## 备份文件结构

### JSON 格式

```json
{
  "version": "0.2.0",
  "created_at": "2026-05-01T12:00:00",
  "environment": {
    "name": "myenv",
    "python_version": "3.10.12",
    "packages": [
      {
        "name": "numpy",
        "version": "1.24.0",
        "channel": "conda-forge",
        "build": "py310h...",
        "source": "CONDA"
      }
    ]
  },
  "metadata": {
    "total_packages": 150,
    "conda_packages": 100,
    "pip_packages": 50
  }
}
```

### Markdown 格式

包含环境信息表格和包列表表格：

```markdown
# 环境备份报告 - myenv

## 环境信息

| 项目 | 值 |
|------|-----|
| 环境名称 | myenv |
| Python版本 | 3.10.12 |
| 包总数 | 150 |

## 包列表

| 序号 | 名称 | 版本 | 渠道 | 来源 |
|------|------|------|------|------|
| 1 | numpy | 1.24.0 | conda-forge | CONDA |
```

## 批量备份

### 备份所有环境

```bash
python conda_env_toolkit.py backup --all-envs --include-base --output-dir ./_backups
```

会自动为每个环境创建备份文件：

```
_backups/
├── base_backup.json
├── base_backup.md
├── env1_backup.json
├── env1_backup.md
└── env2_backup.json
```

### 备份文件命名

如果文件已存在，会自动重命名：

```
myenv_backup.json → myenv_backup-old-20260501-120000.json
```

## 备份完整性验证

备份完成后，工具会自动：
1. 计算文件 MD5 校验和
2. 验证包数量
3. 检查 JSON 格式有效性

## 最佳实践

1. **定期备份** - 建议每周或重大变更后备份
2. **多格式导出** - 至少导出 JSON 和 Markdown
3. **版本控制** - 将备份文件纳入版本控制
4. **异地存储** - 重要备份复制到云存储

---

*返回 [文档首页](index.md)*
