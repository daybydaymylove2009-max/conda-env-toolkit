# 环境对比功能

> 🔍 分析两个 Conda 环境的差异

## 功能概述

对比功能可以分析两个环境的差异，包括：
- 仅存在于环境1的包
- 仅存在于环境2的包
- 版本不同的包

## 使用方式

### 交互模式

选择菜单 **"4. 对比环境"**

### 命令行模式

```bash
# 对比两个环境
python conda_env_toolkit.py compare env1 env2

# 导出对比报告
python conda_env_toolkit.py compare env1 env2 --output report.md
```

## 输出示例

```
环境对比报告: env1 vs env2
=====================================

仅在 env1 中的包 (5 个):
  • package-a (1.0.0)
  • package-b (2.0.0)

仅在 env2 中的包 (3 个):
  • package-c (1.5.0)
  • package-d (3.0.0)

版本不同的包 (2 个):
  • numpy: 1.24.0 (env1) vs 1.26.0 (env2)
  • pandas: 1.5.0 (env1) vs 2.0.0 (env2)
```

## 应用场景

- 检查开发环境和生产环境差异
- 验证克隆是否成功
- 追踪环境变更

---

*返回 [文档首页](index.md)*
