# 项目结构说明

## 📁 核心文件

### 🔧 配置和认证
- `config.py` - 配置管理，解析token文件
- `oauth_client.py` - OAuth认证客户端，处理token获取和刷新
- `outlook_token.example.txt` - Token文件模板

### 📧 邮件功能
- `email_client.py` - 邮件客户端，支持Graph API/IMAP/POP3
- `main.py` - 交互式主程序
- `final_demo.py` - 完整功能演示

### 🛠️ 工具和设置
- `oauth_setup.py` - OAuth设置助手，帮助获取新token
- `requirements.txt` - Python依赖列表
- `setup_and_test.bat` / `setup_and_test.sh` - 自动安装脚本

### 📚 文档
- `README.md` - 详细使用说明
- `项目分析总结.md` - 原项目功能分析
- `项目总结.md` - Demo实现总结

## 🚀 快速开始

1. **配置Token**：
   ```bash
   cp outlook_token.example.txt outlook_token.txt
   # 编辑 outlook_token.txt 填入您的信息
   ```

2. **安装依赖**：
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```

3. **运行Demo**：
   ```bash
   python final_demo.py  # 完整演示
   python main.py        # 交互式菜单
   ```

## 🔑 Token格式

```
email@outlook.com---password---refresh_token---access_token---expires_timestamp---client_id
```

## 📋 功能特性

- ✅ Microsoft OAuth 2.0认证
- ✅ Graph API邮件获取
- ✅ IMAP/POP3 OAuth支持
- ✅ 自动token刷新
- ✅ 完整错误处理
- ✅ 模块化设计
