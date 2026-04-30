# 故障排除指南

> 🔧 解决使用过程中的常见问题

## 安装问题

### 1. Conda 命令未找到

**症状：**
```
'conda' 不是内部或外部命令
```

**解决方案：**
```bash
# 检查 Conda 安装
conda --version

# 如果未找到，添加环境变量
# Windows: 添加 C:\Users\<用户名>\Anaconda3\Scripts 到 PATH
# Linux/macOS: export PATH="$HOME/anaconda3/bin:$PATH"
```

### 2. UV 安装失败

**症状：**
```
UVManager.is_installed() 返回 False
```

**解决方案：**
```bash
# 手动安装 UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# 验证
uv --version
```

## 备份问题

### 3. 备份文件为空

**症状：**
```
备份文件大小为 0 字节或内容为空
```

**原因：**
- Conda 环境列表解析错误
- 环境不存在

**解决方案：**
```bash
# 检查环境是否存在
conda env list

# 手动测试
conda list -n myenv --json
```

### 4. 备份时提示 "环境不存在"

**症状：**
```
ERROR: 环境不存在: myenv
```

**解决方案：**
```bash
# 列出所有环境
conda env list

# 检查拼写
# 注意区分大小写
```

## 恢复问题

### 5. 恢复时包安装失败

**症状：**
```
❌ 安装失败: 5 个
```

**查看日志：**
```bash
# 查看最新日志
ls -la _restore_logs/
cat _restore_logs/*_failed_packages_*.log
```

**常见解决方案：**

#### 5.1 网络问题
```bash
# 配置镜像源
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/

# 使用国内 PyPI 镜像
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple <package>
```

#### 5.2 版本冲突
```bash
# 创建新环境
conda create -n newenv python=3.10

# 在新环境中恢复
python conda_env_toolkit.py restore backup.json -n newenv
```

#### 5.3 编译失败
```bash
# Windows: 安装 Visual C++ Build Tools
# Linux:
sudo apt-get update
sudo apt-get install build-essential python3-dev

# macOS:
xcode-select --install
```

### 6. 恢复后环境不完整

**症状：**
```
恢复完整度: 60%
评价: 较差
```

**解决方案：**
1. 查看失败日志
2. 手动安装失败包
3. 检查网络连接
4. 尝试更换镜像源

### 7. 断点续传不工作

**症状：**
```
恢复中断后从头开始
```

**解决方案：**
```bash
# 检查状态文件
ls -la *.state.json

# 手动清理状态（如果损坏）
rm *.state.json

# 重新恢复
python conda_env_toolkit.py restore backup.json -n myenv --resume
```

## 性能问题

### 8. 恢复速度很慢

**症状：**
```
恢复 100 个包需要 30 分钟以上
```

**优化方案：**
```bash
# 启用并行和 UV
python conda_env_toolkit.py restore backup.json -n myenv --parallel --use-uv

# 增加 workers
python conda_env_toolkit.py restore backup.json -n myenv --parallel --max-workers 8
```

### 9. 内存不足

**症状：**
```
MemoryError
或系统卡顿
```

**解决方案：**
```bash
# 减少并行 workers
python conda_env_toolkit.py restore backup.json -n myenv --parallel --max-workers 2

# 关闭其他程序
# 增加虚拟内存/交换分区
```

## 权限问题

### 10. 无法写入备份目录

**症状：**
```
PermissionError: [Errno 13] Permission denied
```

**解决方案：**
```bash
# Windows: 以管理员身份运行终端
# Linux/macOS:
sudo chmod 755 <目录>

# 或更换输出目录
python conda_env_toolkit.py backup myenv --output-dir ~/backups
```

### 11. 无法修改 Conda 环境

**症状：**
```
NotWritableError: The current user does not have write permissions
```

**解决方案：**
```bash
# 使用用户目录
conda create --prefix ~/myenv python=3.10

# 或修改 Conda 目录权限
sudo chown -R $USER:$USER ~/anaconda3
```

## 其他问题

### 12. JSON 解析错误

**症状：**
```
json.decoder.JSONDecodeError
```

**解决方案：**
```bash
# 检查备份文件完整性
python -m json.tool backup.json

# 重新备份
python conda_env_toolkit.py backup myenv --formats json
```

### 13. 编码错误

**症状：**
```
UnicodeDecodeError
```

**解决方案：**
```bash
# 设置 UTF-8 编码
# Windows:
chcp 65001

# Linux/macOS:
export LANG=en_US.UTF-8
```

### 14. 工具崩溃/无响应

**症状：**
```
程序卡住或异常退出
```

**解决方案：**
1. 检查 Python 版本：`python --version`（需要 3.8+）
2. 更新工具：`git pull`
3. 检查依赖：`pip install -r requirements.txt`
4. 查看错误日志

## 获取帮助

如果以上方案无法解决问题：

1. **查看日志文件**
   ```bash
   ls -la _restore_logs/
   cat _restore_logs/*.log
   ```

2. **启用详细输出**
   ```bash
   python conda_env_toolkit.py restore backup.json -n myenv --verbose
   ```

3. **提交 Issue**
   - 访问 [GitHub Issues](https://github.com/daybydaymylove2009-max/conda-env-toolkit/issues)
   - 提供：操作系统、Python 版本、错误信息、复现步骤

---

*返回 [文档首页](index.md)*
