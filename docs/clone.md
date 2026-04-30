# 环境克隆功能

> 🔄 一键克隆 Conda 环境

## 功能概述

克隆功能可以快速复制现有环境，创建完全相同的副本。

## 使用方式

### 交互模式

选择菜单 **"3. 克隆环境"**

### 命令行模式

```bash
# 基础克隆
python conda_env_toolkit.py clone oldenv newenv

# 克隆并导出报告
python conda_env_toolkit.py clone oldenv newenv --export
```

## 克隆流程

1. 导出源环境包列表
2. 创建新环境
3. 安装相同版本的包
4. 验证克隆结果

## 示例

```bash
# 克隆生产环境到测试环境
python conda_env_toolkit.py clone production test-env

# 克隆并导出对比报告
python conda_env_toolkit.py clone myenv myenv-copy --export
```

## 注意事项

- 克隆会创建全新的环境，不共享包文件
- 克隆时间取决于包数量和大小
- 建议使用 `--parallel` 加速

---

*返回 [文档首页](index.md)*
