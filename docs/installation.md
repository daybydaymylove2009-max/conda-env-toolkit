# 安装指南

> 📥 Conda 环境管理工具箱的安装说明

## 系统要求

- **操作系统**: Windows 10+, macOS 10.15+, Linux (Ubuntu 18.04+)
- **Python**: 3.8 或更高版本
- **Conda**: Anaconda 或 Miniconda 已安装

## 安装步骤

### 1. 克隆仓库

```bash
git clone https://github.com/daybydaymylove2009-max/conda-env-toolkit.git
cd conda-env-toolkit
```

### 2. 安装依赖（可选）

```bash
# 安装 UV（推荐，用于加速）
pip install uv

# 或安装所有依赖
pip install -r requirements.txt
```

### 3. 验证安装

```bash
python conda_env_toolkit.py --help
```

## 可选依赖

### UV 加速

UV 可以大幅提升包安装速度（10-100 倍）：

```bash
# 安装 UV
curl -LsSf https://astral.sh/uv/install.sh | sh  # Linux/macOS
# 或
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"  # Windows

# 验证
uv --version
```

### Rich 终端美化

用于进度条和彩色输出（已内置兼容）：

```bash
pip install rich
```

## 平台特定说明

### Windows

1. **安装 Visual C++ Build Tools**（如果需要编译包）
   - 下载地址：https://visualstudio.microsoft.com/visual-cpp-build-tools/
   - 安装 "C++ 生成工具"

2. **PowerShell 执行策略**
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

### macOS

1. **安装 Xcode 命令行工具**
   ```bash
   xcode-select --install
   ```

2. **Homebrew 安装（可选）**
   ```bash
   brew install uv
   ```

### Linux

1. **安装编译工具**
   ```bash
   sudo apt-get update
   sudo apt-get install build-essential python3-dev
   ```

2. **Ubuntu/Debian**
   ```bash
   sudo apt-get install python3-pip
   ```

## 升级

```bash
# 拉取最新代码
git pull origin main

# 更新依赖
pip install -r requirements.txt --upgrade
```

## 卸载

```bash
# 直接删除目录
rm -rf conda-env-toolkit

# 清理配置文件
rm ~/.conda_env_toolkit_config.json
```

## 验证安装

运行以下命令验证安装：

```bash
# 查看版本
python conda_env_toolkit.py --version

# 进入交互模式
python conda_env_toolkit.py

# 测试备份
python conda_env_toolkit.py backup base --formats json
```

## 常见问题

### Q: 提示 "python" 命令未找到？
**A:** 确保 Python 已添加到系统 PATH，或使用 `python3` 命令。

### Q: 提示 "conda" 命令未找到？
**A:** 确保 Conda 已正确安装并初始化，运行 `conda init`。

### Q: UV 安装失败？
**A:** UV 是可选依赖，不影响基础功能。可以稍后手动安装。

---

*返回 [文档首页](index.md)*
