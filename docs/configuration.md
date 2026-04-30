# 配置指南

> ⚙️ Conda 环境管理工具箱的高级配置

## 配置文件

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

## 配置项说明

### AUTO_USE_UV

**类型：** `boolean`
**默认值：** `true`
**说明：** 是否自动使用 UV 加速安装

```json
{
  "AUTO_USE_UV": true
}
```

### AUTO_USE_MIRROR

**类型：** `boolean`
**默认值：** `true`
**说明：** 是否自动配置镜像源

```json
{
  "AUTO_USE_MIRROR": true
}
```

### KEEP_TEMP_FILES

**类型：** `boolean`
**默认值：** `false`
**说明：** 是否保留临时文件（用于调试）

```json
{
  "KEEP_TEMP_FILES": false
}
```

### VERBOSE

**类型：** `boolean`
**默认值：** `false`
**说明：** 是否显示详细输出和 Rich 进度条

```json
{
  "VERBOSE": true
}
```

### DEFAULT_MAX_WORKERS

**类型：** `integer`
**默认值：** `4`
**说明：** 并行安装的最大 workers 数

```json
{
  "DEFAULT_MAX_WORKERS": 4
}
```

## 配置方式

### 1. 交互菜单配置

选择菜单 **"12. 配置管理"**：

```
配置管理:
1. 自动使用 UV: 是
2. 自动使用镜像: 是
3. 保留临时文件: 否
4. 详细输出: 否
5. 最大并行数: 4
0. 返回主菜单
```

### 2. 手动编辑配置文件

```bash
# 编辑配置文件
nano .conda_env_toolkit_config.json

# 修改后保存，下次运行自动生效
```

### 3. 命令行覆盖

部分选项可以通过命令行参数覆盖：

```bash
# 启用详细输出
python conda_env_toolkit.py backup myenv --verbose

# 指定并行 workers
python conda_env_toolkit.py restore backup.json -n myenv --parallel --max-workers 8

# 强制使用/不使用 UV
python conda_env_toolkit.py restore backup.json -n myenv --use-uv
```

## 镜像源配置

### 自动配置

启用 `AUTO_USE_MIRROR` 后，工具会自动配置以下镜像：

- **Conda:** 清华大学镜像
- **Pip:** 清华大学 PyPI 镜像

### 手动配置

```bash
# 添加 Conda 镜像
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/
conda config --set show_channel_urls yes

# 添加 Pip 镜像
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

### 其他镜像源

| 名称 | URL |
|------|-----|
| 清华 | https://pypi.tuna.tsinghua.edu.cn/simple |
| 阿里云 | https://mirrors.aliyun.com/pypi/simple/ |
| 豆瓣 | http://pypi.douban.com/simple/ |
| 中科大 | https://pypi.mirrors.ustc.edu.cn/simple/ |

## 性能调优

### 并行安装

根据 CPU 核心数调整 workers：

```json
{
  "DEFAULT_MAX_WORKERS": 8
}
```

建议：
- 4 核 CPU：workers = 4
- 8 核 CPU：workers = 8
- 16 核 CPU：workers = 12-16

### UV 缓存

UV 使用全局缓存，可以定期清理：

```bash
# 清理 UV 缓存
uv cache clean

# 或清理所有缓存
python conda_env_toolkit.py cleanup --all
```

### 网络超时

如果遇到网络问题，可以增加超时时间：

```bash
# Pip 超时
pip install --default-timeout=100 <package>

# Conda 超时
conda config --set remote_connect_timeout_secs 40
conda config --set remote_read_timeout_secs 100
```

## 环境变量

部分配置可以通过环境变量设置：

```bash
# 代理设置
export HTTP_PROXY=http://proxy.company.com:8080
export HTTPS_PROXY=http://proxy.company.com:8080

# UV 配置
export UV_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple

# Python 编码
export PYTHONIOENCODING=utf-8
```

## 最佳实践

1. **开发环境**
   ```json
   {
     "VERBOSE": true,
     "KEEP_TEMP_FILES": true
   }
   ```

2. **生产环境**
   ```json
   {
     "VERBOSE": false,
     "AUTO_USE_UV": true,
     "DEFAULT_MAX_WORKERS": 8
   }
   ```

3. **CI/CD 环境**
   ```json
   {
     "VERBOSE": false,
     "AUTO_USE_UV": true,
     "AUTO_USE_MIRROR": true
   }
   ```

---

*返回 [文档首页](index.md)*
