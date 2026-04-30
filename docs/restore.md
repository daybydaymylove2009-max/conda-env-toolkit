# 环境恢复功能详解

> 🔄 从备份快速重建 Conda 环境

## 功能概述

恢复功能可以从备份文件重建完整环境，包含：
- 智能包分类（Conda / Pip）
- 并行安装加速
- UV 加速支持
- 断点续传
- 智能跳过已安装包
- 实时进度显示
- 恢复后对比报告
- 失败包分析与日志导出

## 恢复流程

```
1. 读取备份文件
2. 检查目标环境
3. 智能分类包（Conda / Pip）
4. 检查已安装包（智能跳过）
5. 并行安装 Conda 包
6. UV/Pip 安装 Pip 包
7. 生成恢复报告
8. 输出失败包日志
```

## 使用方式

### 交互模式

选择菜单 **"2. 恢复环境"** 或 **"9. 从备份目录批量恢复"**

### 命令行模式

```bash
# 基础恢复
python conda_env_toolkit.py restore backup.json -n newenv

# 极速恢复（推荐）
python conda_env_toolkit.py restore backup.json -n newenv --parallel --use-uv

# 使用最新版本恢复
python conda_env_toolkit.py restore backup.json -n newenv --recovery-mode latest

# 使用指定镜像源恢复
python conda_env_toolkit.py restore backup.json -n newenv --mirror aliyun

# 批量恢复（从目录）
python conda_env_toolkit.py restore-all ./_backups --parallel --use-uv
```

## 恢复模式

支持两种恢复模式：

### 1. 备份版本恢复（默认）
严格按照备份文件中记录的版本号安装包，确保环境与备份时完全一致。

```bash
python conda_env_toolkit.py restore backup.json -n myenv
# 或显式指定
python conda_env_toolkit.py restore backup.json -n myenv --recovery-mode backup
```

**适用场景：**
- 需要完全复现备份时的环境
- 项目对版本有严格要求
- 避免因版本更新导致兼容性问题

### 2. 最新版本恢复
自动查询并安装各包的最新版本，适合需要更新环境的场景。

```bash
python conda_env_toolkit.py restore backup.json -n myenv --recovery-mode latest
```

**适用场景：**
- 重建开发环境并希望使用最新包
- 修复已知的安全漏洞
- 获取新功能和性能改进

**工作原理：**
1. 读取备份文件中的包列表
2. 查询 PyPI/Conda 获取每个包的最新版本
3. 更新版本号后执行安装
4. 显示版本变更摘要

## 恢复选项

| 选项 | 说明 | 默认值 |
|------|------|--------|
| `-n, --name` | 目标环境名称 | 备份中的原名 |
| `--parallel` | 并行安装 | False |
| `--use-uv` | 使用 UV 加速 | False |
| `--force` | 强制覆盖 | False |
| `--resume` | 断点续传 | True |
| `--max-workers` | 并行 workers | 4 |
| `--recovery-mode` | 恢复模式 (backup/latest) | backup |
| `--mirror` | 镜像源 (official/tsinghua/aliyun/ustc/tencent/huawei/douban) | tsinghua |

## 镜像源选择

支持多种镜像源，可根据网络环境选择：

| 镜像源 | 说明 | 适用场景 |
|--------|------|----------|
| `official` | 官方主站 (PyPI/Anaconda) | 海外用户或需要最新包 |
| `tsinghua` | 清华大学 TUNA | 国内默认推荐，教育网优选 |
| `aliyun` | 阿里云 | 国内通用，速度快 |
| `ustc` | 中国科学技术大学 | 华东地区优选 |
| `tencent` | 腾讯云 | 华南地区优选 |
| `huawei` | 华为云 | 企业用户优选 |
| `douban` | 豆瓣 | 稳定可靠 |

### 使用示例

```bash
# 使用官方主站（海外用户）
python conda_env_toolkit.py restore backup.json -n myenv --mirror official

# 使用阿里云镜像（国内推荐）
python conda_env_toolkit.py restore backup.json -n myenv --mirror aliyun

# 使用腾讯云镜像
python conda_env_toolkit.py restore backup.json -n myenv --mirror tencent
```

### 交互模式设置

在交互菜单中选择 **"13. 配置设置" → "6. 镜像源"** 进行切换。

## 智能跳过

恢复时会自动检查：
- 包是否已安装
- 已安装版本是否 ≥ 备份版本
- 满足条件则自动跳过

跳过信息会在恢复完成后显示：

```
⏭️  智能跳过的包 (已安装且版本相同或更新):
  • numpy: 已安装 1.26.0 >= 备份 1.24.0
  • pandas: 已安装 2.0.0 >= 备份 1.5.0
```

## 实时进度

恢复过程中显示百分比进度：

```
📊 Conda包进度: 50/150 (33.3%)
📊 Pip包进度: 25/50 (50.0%)
```

## 恢复报告

恢复完成后自动生成对比报告：

```
======================================================================
📊 恢复后环境对比报告
======================================================================
  目标环境: myenv
  备份包数: 150
  当前包数: 148
  差异: -2
----------------------------------------------------------------------

  ✅ 本次安装成功: 145 个
  ❌ 安装失败: 3 个
  ⏭️  智能跳过: 2 个

  ❌ 安装失败的包 (3 个):
----------------------------------------------------------------------
     • pytorch (备份版本: 2.0.0)
       原因: 大型包/深度学习框架下载超时或网络不稳定
       建议: 
         ① 使用国内镜像: pip install -i https://pypi.tuna.tsinghua.edu.cn/simple pytorch
         ② 手动下载whl文件从 https://download.pytorch.org/whl 安装
         ③ 使用conda安装: conda install pytorch torchvision -c pytorch

  📈 恢复完整度: 96.7%
  🎯 评价: 优秀 - 环境恢复非常完整
======================================================================
```

## 失败包日志

失败包会自动保存日志到 `_restore_logs/`：

```
_restore_logs/
└── myenv_failed_packages_20260501_120000.log
```

日志包含：
- 失败包列表
- 失败原因分析
- 针对性解决方案
- 手动安装命令
- 通用解决方案

## 批量恢复

### 从备份目录恢复

```bash
# 交互式选择
python conda_env_toolkit.py restore-all ./_backups

# 恢复所有环境
python conda_env_toolkit.py restore-all ./_backups --mode all

# 选择性恢复
python conda_env_toolkit.py restore-all ./_backups --mode select
```

### 多备份处理

如果同一环境有多份备份：
- 自动按时间排序
- 选择最新版本
- 提示用户存在多份备份

## 故障排除

### 恢复失败常见问题

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 包未找到 | 渠道中不存在 | 更换镜像源 |
| 版本冲突 | 依赖不兼容 | 创建新环境 |
| 网络超时 | 连接不稳定 | 配置代理或镜像 |
| 权限不足 | 无法写入 | 管理员权限运行 |
| 编译失败 | 缺少编译器 | 安装 build-essential |

### 手动修复失败包

```bash
# 查看日志获取具体命令
cat _restore_logs/myenv_failed_packages_*.log

# 手动安装
conda install -n myenv <package_name>
# 或
conda run -n myenv pip install <package_name>
```

## 最佳实践

1. **先备份再恢复** - 避免覆盖重要环境
2. **使用并行+UV** - 大幅提升恢复速度
3. **检查恢复报告** - 确认环境完整性
4. **查看失败日志** - 及时修复缺失包
5. **测试环境** - 恢复后验证关键功能

---

*返回 [文档首页](index.md)*
