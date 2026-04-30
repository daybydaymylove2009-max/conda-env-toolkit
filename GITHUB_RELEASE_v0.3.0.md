# v0.3.0 - Mirror & Insight Edition

## ✨ 新增功能

### 多镜像源支持
- 支持 **官方主站 + 6 大国内镜像源**：
  - `official` - 官方主站 (PyPI/Anaconda)
  - `tsinghua` - 清华大学 TUNA（默认）
  - `aliyun` - 阿里云
  - `ustc` - 中国科学技术大学
  - `tencent` - 腾讯云
  - `huawei` - 华为云
  - `douban` - 豆瓣

### 镜像源动态切换
- **命令行支持**：`--mirror` 参数
  ```bash
  python conda_env_toolkit.py restore backup.json -n myenv --mirror aliyun
  ```
- **交互式菜单**：恢复时选择镜像源（序号 1-7）
- **配置持久化**：设置后保存到配置文件

### 实时失败原因分析
安装失败时立即显示具体原因：
- **系统库/开发包识别**（70+ 常见库）：
  - `libasprintf`, `libblas`, `libcblas`, `libgcc`, `libgomp`
  - `libintl`, `liblapack`, `libsqlite`, `libwinpthread`, `libxcb`
  - `libfreetype`, `libpng`, `libjpeg`, `libxml2`, `libxslt`
  - `libcurl`, `libssh2`, `libhdf5`, `libnetcdf`, `libarrow`
  - `libopenblas`, `libmkl`, `libomp`, `libllvm`, `libclang`
  - `gettext` 等
- 网络问题（超时、连接失败）
- SSL 证书验证失败
- 依赖冲突
- 权限不足
- 磁盘空间不足
- 内存不足
- Python 版本不兼容
- 包在渠道中未找到

### 并行安装进度显示
- 批量安装时显示实时百分比进度
- 每 5 个包更新一次进度
- 安装完成后显示失败包汇总

## 🔧 改进

- 优化交互式菜单镜像源选择界面，使用序号选择（1-7）
- 改进失败包日志，包含具体失败原因
- **增强包名特征识别算法**（新增 70+ 系统库/开发包识别模式）

## 📖 使用示例

### 命令行使用镜像源
```bash
# 使用官方主站（海外用户推荐）
python conda_env_toolkit.py restore backup.json -n myenv --mirror official

# 使用阿里云镜像（国内推荐）
python conda_env_toolkit.py restore backup.json -n myenv --mirror aliyun

# 使用腾讯云镜像
python conda_env_toolkit.py restore backup.json -n myenv --mirror tencent
```

### 交互式菜单使用
```
镜像源选择:
  1. 官方主站
  2. 清华大学 (TUNA) (当前默认)
  3. 阿里云
  4. 中国科学技术大学 (USTC)
  5. 腾讯云
  6. 华为云
  7. 豆瓣
选择镜像源 [1-7] (直接回车使用当前默认): 3
[INFO] 已切换到: 阿里云
```

## 🐛 修复

- 修复交互式菜单镜像源选择提示不一致的问题
- 修复并行安装无进度显示的问题
- **修复系统库/开发包识别不全的问题**（新增 70+ 识别模式，解决 `gettext`, `libintl`, `liblapack` 等常见库显示"未知错误"的问题）

## 📦 安装

```bash
# 克隆仓库
git clone https://github.com/daybydaymylove2009-max/conda-env-toolkit.git
cd conda-env-toolkit

# 安装依赖
pip install -r requirements.txt

# 运行
python conda_env_toolkit.py
```

## 📝 完整文档

- [恢复功能详解](docs/restore.md)
- [更新日志](docs/changelog.md)
- [GitHub 仓库](https://github.com/daybydaymylove2009-max/conda-env-toolkit)

---

**Full Changelog**: [v0.2.0...v0.3.0](https://github.com/daybydaymylove2009-max/conda-env-toolkit/compare/v0.2.0...v0.3.0)
