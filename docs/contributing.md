# 贡献指南

> 🤝 欢迎参与 Conda 环境管理工具箱的开发

## 如何贡献

### 报告问题

1. 访问 [GitHub Issues](https://github.com/daybydaymylove2009-max/conda-env-toolkit/issues)
2. 搜索是否已存在相同问题
3. 创建新 Issue，包含：
   - 问题描述
   - 复现步骤
   - 操作系统和版本
   - Python 版本
   - 错误信息

### 提交代码

1. **Fork 仓库**
   ```bash
   git clone https://github.com/your-username/conda-env-toolkit.git
   cd conda-env-toolkit
   ```

2. **创建分支**
   ```bash
   git checkout -b feature/your-feature
   ```

3. **提交更改**
   ```bash
   git add .
   git commit -m "feat: 添加新功能"
   ```

4. **推送并创建 PR**
   ```bash
   git push origin feature/your-feature
   ```

### 代码规范

- 遵循 PEP 8 规范
- 添加类型注解
- 编写文档字符串
- 保持向后兼容

## 开发环境

```bash
# 创建开发环境
conda create -n conda-toolkit-dev python=3.10
conda activate conda-toolkit-dev

# 安装开发依赖
pip install -r requirements.txt
pip install pytest black flake8

# 运行测试
pytest
```

## 联系方式

- GitHub Issues: [提交问题](https://github.com/daybydaymylove2009-max/conda-env-toolkit/issues)
- 邮件: your-email@example.com

---

*返回 [文档首页](index.md)*
