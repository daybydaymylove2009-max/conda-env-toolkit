# 常见问题解答 (FAQ)

> ❓ 使用 Conda 环境管理工具箱时的常见问题

## 一般问题

### Q: 这个工具支持哪些操作系统？
**A:** 支持 Windows、macOS 和 Linux。但某些功能（如 UV 加速）在 Windows 上可能需要额外配置。

### Q: 需要安装哪些依赖？
**A:** 基础功能只需要 Python 3.8+ 和 Conda。可选依赖：
- `uv` - 用于加速安装（推荐）
- `rich` - 用于美化输出（已内置兼容）

### Q: 工具是否收费？
**A:** 完全免费，基于 MIT 协议开源。

## 备份相关问题

### Q: 备份文件会很大吗？
**A:** 备份文件只包含包列表和元数据，不包含实际的包文件。通常几百 KB 到几 MB。

### Q: 可以备份 base 环境吗？
**A:** 可以！使用 `--include-base` 选项即可。

```bash
python conda_env_toolkit.py backup --all-envs --include-base
```

### Q: 备份文件可以跨平台使用吗？
**A:** JSON 格式的备份文件可以跨平台使用。但某些平台特定的包可能需要手动调整。

### Q: 如何查看备份内容？
**A:** 推荐使用 Markdown 格式的备份文件，可以直接用浏览器或 Markdown 编辑器查看。

## 恢复相关问题

### Q: 恢复会覆盖现有环境吗？
**A:** 默认不会。如果环境已存在，会提示错误。使用 `--force` 可以强制覆盖。

### Q: 恢复过程中断怎么办？
**A:** 支持断点续传！重新运行相同的恢复命令即可从上次位置继续。

### Q: 为什么有些包恢复失败？
**A:** 常见原因：
- 包已从 PyPI/Conda 移除
- 网络连接问题
- 版本冲突
- 缺少系统依赖

查看 `_restore_logs/` 目录下的日志文件获取详细信息和解决方案。

### Q: UV 加速和不用 UV 有什么区别？
**A:** 安装结果完全相同，但 UV 速度更快（10-100 倍）。UV 使用全局缓存，减少重复下载。

### Q: 智能跳过是什么意思？
**A:** 如果环境中已安装相同或更新版本的包，会自动跳过安装，避免重复工作和版本降级。

## 性能问题

### Q: 恢复 500 个包需要多久？
**A:** 取决于网络速度和选项：
- 传统方式：约 1 小时
- 并行+UV：约 3 分钟

### Q: 并行安装会冲突吗？
**A:** Conda 包使用内部并行，Pip 包使用 UV 批量安装，不会冲突。

## 错误处理

### Q: 遇到 "包未找到" 错误怎么办？
**A:** 
1. 检查包名拼写
2. 尝试其他渠道：`conda install -c conda-forge <package>`
3. 使用 pip 安装：`pip install <package>`

### Q: 遇到 "权限 denied" 怎么办？
**A:**
- Windows：以管理员身份运行终端
- Linux/macOS：使用 `sudo` 或检查目录权限

### Q: SSL 证书错误如何解决？
**A:**
```bash
# 更新证书
pip install --upgrade certifi

# 或临时跳过验证
pip install --trusted-host pypi.org <package>
```

## 高级用法

### Q: 如何配置镜像源？
**A:** 通过交互菜单（选项 12）或手动编辑配置文件：

```bash
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/
```

### Q: 可以集成到 CI/CD 吗？
**A:** 可以！使用命令行模式：

```bash
python conda_env_toolkit.py backup myenv --formats json
python conda_env_toolkit.py restore backup.json -n myenv --parallel
```

### Q: 如何导出环境报告？
**A:**
```bash
python conda_env_toolkit.py backup myenv --formats markdown
```

## 其他问题

### Q: 如何更新工具？
**A:**
```bash
git pull origin main
```

### Q: 如何提交 bug 报告？
**A:** 访问 [GitHub Issues](https://github.com/daybydaymylove2009-max/conda-env-toolkit/issues) 提交。

### Q: 可以贡献代码吗？
**A:** 欢迎！请查看 [贡献指南](contributing.md)。

---

*还有其他问题？提交 [Issue](https://github.com/daybydaymylove2009-max/conda-env-toolkit/issues) 或查看 [故障排除](troubleshooting.md)*
