# 快速开始指南

> ⏱️ 5分钟上手 Conda 环境管理工具箱

## 1. 安装

### 前提条件
- Python 3.8+
- Conda 已安装

### 安装工具

```bash
# 克隆仓库
git clone https://github.com/daybydaymylove2009-max/conda-env-toolkit.git
cd conda-env-toolkit

# 安装依赖（可选，用于 UV 加速）
pip install uv
```

## 2. 首次运行

### 交互模式（推荐）

```bash
python conda_env_toolkit.py
```

会看到交互式菜单：

```
╔══════════════════════════════════════════════════════════════╗
║           Conda 环境管理工具箱 - v0.2.0                      ║
╠══════════════════════════════════════════════════════════════╣
║  1.  备份环境                                                ║
║  2.  恢复环境                                                ║
║  3.  克隆环境                                                ║
║  4.  对比环境                                                ║
║  5.  查看环境详情                                            ║
║  6.  系统清理                                                ║
║  7.  环境转换 (Conda ↔ UV)                                  ║
║  8.  批量备份所有环境                                        ║
║  9.  从备份目录批量恢复                                      ║
║  10. 包分类查询                                              ║
║  11. 导出环境报告                                            ║
║  12. 配置管理                                                ║
║  0.  退出                                                    ║
╚══════════════════════════════════════════════════════════════╝
```

### 命令行模式

```bash
# 查看帮助
python conda_env_toolkit.py --help
```

## 3. 基本操作

### 备份环境

```bash
# 备份单个环境（所有格式）
python conda_env_toolkit.py backup myenv --all-formats

# 备份到指定目录
python conda_env_toolkit.py backup myenv --output-dir ./my-backups
```

### 恢复环境

```bash
# 基础恢复
python conda_env_toolkit.py restore myenv_backup.json -n newenv

# 极速恢复（推荐）
python conda_env_toolkit.py restore myenv_backup.json -n newenv --parallel --use-uv
```

### 批量备份所有环境

```bash
# 备份所有环境，包括 base
python conda_env_toolkit.py backup --all-envs --include-base --output-dir ./_backups
```

## 4. 查看结果

备份完成后，会在指定目录生成以下文件：

```
_backups/
├── myenv_backup.json          # 完整备份数据
├── myenv_backup.md            # Markdown 报告
├── myenv_backup.yml           # Conda 环境文件
├── myenv_backup.txt           # 简洁列表
└── myenv_backup_requirements.txt  # Pip 格式
```

## 5. 下一步

- 📖 阅读 [完整功能指南](backup.md)
- ⚙️ 了解 [配置选项](configuration.md)
- 🔧 查看 [故障排除](troubleshooting.md)

---

*有问题？查看 [FAQ](faq.md) 或提交 [Issue](https://github.com/daybydaymylove2009-max/conda-env-toolkit/issues)*
