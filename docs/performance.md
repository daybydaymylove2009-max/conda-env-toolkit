# 性能优化指南

> ⚡ 提升 Conda 环境管理工具箱的性能

## 安装速度优化

### 1. 使用 UV 加速

UV 比传统 Pip 快 10-100 倍：

```bash
# 安装 UV
pip install uv

# 恢复时启用 UV
python conda_env_toolkit.py restore backup.json -n myenv --use-uv
```

### 2. 并行安装

同时安装多个包：

```bash
# 启用并行安装
python conda_env_toolkit.py restore backup.json -n myenv --parallel --max-workers 8
```

### 3. 配置镜像源

使用国内镜像加速下载：

```bash
# 配置清华镜像
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

## 性能对比

| 操作 | 传统方式 | 优化后 | 提升 |
|------|----------|--------|------|
| 恢复 100 个包 | ~10 分钟 | ~1 分钟 | **10x** |
| 恢复 500 个包 | ~1 小时 | ~3 分钟 | **20x** |
| 环境克隆 | ~15 分钟 | ~2 分钟 | **7x** |

## 系统优化

### 1. 清理缓存

定期清理缓存释放空间：

```bash
python conda_env_toolkit.py cleanup --all
```

### 2. 增加交换空间

如果内存不足：

```bash
# Linux
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### 3. SSD 优化

将 Conda 目录移动到 SSD：

```bash
# 查看当前位置
conda info

# 修改配置
conda config --add envs_dirs /ssd/conda/envs
conda config --add pkgs_dirs /ssd/conda/pkgs
```

## 网络优化

### 1. 配置代理

```bash
export HTTP_PROXY=http://proxy.company.com:8080
export HTTPS_PROXY=http://proxy.company.com:8080
```

### 2. 增加超时时间

```bash
# Conda
conda config --set remote_connect_timeout_secs 40
conda config --set remote_read_timeout_secs 100

# Pip
pip install --default-timeout=100 <package>
```

## 最佳实践

1. **使用 SSD** - 将 Conda 目录放在 SSD 上
2. **定期清理** - 每周清理一次缓存
3. **使用 UV** - 始终启用 UV 加速
4. **配置镜像** - 使用最近的镜像源
5. **并行安装** - 根据 CPU 核心数调整 workers

---

*返回 [文档首页](index.md)*
