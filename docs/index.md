# Conda 环境管理工具箱 - 文档中心

> 🐍 一站式 Conda 环境管理解决方案

## 📖 文档导航

### 快速入门
- [快速开始指南](quickstart.md) - 5分钟上手
- [安装与配置](installation.md) - 详细安装步骤
- [常见问题](faq.md) - 常见问题解答

### 功能指南
- [环境备份](backup.md) - 备份功能详解
- [环境恢复](restore.md) - 恢复功能详解
- [环境克隆](clone.md) - 克隆环境
- [环境对比](compare.md) - 对比分析
- [环境转换](convert.md) - Conda ↔ UV 转换

### 高级主题
- [配置文件](configuration.md) - 高级配置选项
- [故障排除](troubleshooting.md) - 常见错误解决
- [性能优化](performance.md) - 性能调优建议
- [API 参考](api.md) - 代码API文档

### 其他
- [更新日志](changelog.md) - 版本更新历史
- [贡献指南](contributing.md) - 如何参与贡献

## 🚀 快速开始

```bash
# 交互模式（推荐新手）
python conda_env_toolkit.py

# 备份环境
python conda_env_toolkit.py backup myenv --all-formats

# 恢复环境
python conda_env_toolkit.py restore backup.json -n newenv --parallel --use-uv
```

## 📦 核心功能

| 功能 | 说明 | 命令 |
|------|------|------|
| 备份 | 导出环境到多种格式 | `backup` |
| 恢复 | 从备份重建环境 | `restore` |
| 克隆 | 复制现有环境 | `clone` |
| 对比 | 分析环境差异 | `compare` |
| 转换 | Conda ↔ UV | `convert` |
| 清理 | 清理缓存 | `cleanup` |

## 🔗 相关链接

- [GitHub 仓库](https://github.com/daybydaymylove2009-max/conda-env-toolkit)
- [问题反馈](https://github.com/daybydaymylove2009-max/conda-env-toolkit/issues)
- [发布版本](https://github.com/daybydaymylove2009-max/conda-env-toolkit/releases)

---

*最后更新: 2026-05-01 | 版本: v0.2.0*
