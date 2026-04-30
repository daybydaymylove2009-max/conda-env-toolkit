# 环境转换功能

> 🔄 Conda 环境与 UV 环境的相互转换

## 功能概述

转换功能可以在 Conda 环境和 UV 虚拟环境之间无缝切换。

## Conda → UV

### 交互模式

选择菜单 **"7. 环境转换 (Conda ↔ UV)"**

### 命令行模式

```bash
# 将 Conda 环境转换为 UV 环境
python conda_env_toolkit.py convert --from-conda myenv --to-uv ./myenv-uv
```

### 转换流程

1. 导出 Conda 环境包列表
2. 创建 UV 虚拟环境
3. 使用 UV 安装相同包
4. 验证转换结果

## UV → Conda

```bash
# 将 UV 环境转换为 Conda 环境
python conda_env_toolkit.py convert --from-uv ./myenv-uv --to-conda myenv-new
```

## 注意事项

- UV 环境是虚拟环境，不包含 Python 解释器
- 某些 Conda 特定的包可能无法在 UV 中安装
- 转换后建议验证关键功能

---

*返回 [文档首页](index.md)*
