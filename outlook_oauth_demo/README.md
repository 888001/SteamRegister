# Outlook OAuth 邮件获取 Demo

这是一个独立的Outlook OAuth邮件获取演示程序，从SteamRegister项目中提取并优化了OAuth邮件功能。

## 功能特性

### 🔐 OAuth认证
- Microsoft OAuth 2.0认证流程
- 自动token刷新机制
- 完整的错误处理和重试逻辑

### 📧 多协议邮件获取
- **Graph API**: 使用Microsoft Graph REST API获取邮件
- **IMAP OAuth**: 使用OAuth认证的IMAP协议
- **POP3 OAuth**: 使用OAuth认证的POP3协议

### 🛠️ 功能亮点
- 模块化设计，易于扩展
- 完整的日志记录
- 交互式测试界面
- 虚拟环境支持
- 跨平台兼容

## 项目结构

```
outlook_oauth_demo/
├── config.py              # 配置管理模块
├── oauth_client.py        # OAuth认证客户端
├── email_client.py        # 邮件获取客户端
├── main.py               # 主程序和测试模块
├── requirements.txt      # Python依赖
├── outlook_token.txt     # OAuth配置文件
├── setup_and_test.bat    # Windows安装测试脚本
├── setup_and_test.sh     # Linux/Mac安装测试脚本
└── README.md            # 说明文档
```

## 快速开始

### 1. 克隆项目

```bash
git clone <repository-url>
cd outlook_oauth_demo
```

### 2. 配置Token文件

复制示例文件并填入您的信息：
```bash
cp outlook_token.example.txt outlook_token.txt
```

编辑 `outlook_token.txt`，格式：
```
your_email@outlook.com---your_password---your_refresh_token---your_access_token---expires_timestamp
```

### 3. 自动安装和测试

**Windows:**
```bash
setup_and_test.bat
```

**Linux/Mac:**
```bash
chmod +x setup_and_test.sh
./setup_and_test.sh
```

### 4. 手动安装

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 5. 运行测试

```bash
# 完整功能演示
python final_demo.py

# 交互式菜单
python main.py

# 验证Token
python main.py --test-token

# 测试Graph API
python main.py --test-graph

# 运行所有测试
python main.py --test-all
```

## 配置说明

### outlook_token.txt 格式
```
email---password---client_id---refresh_token---timestamp
```

示例：
```
user@outlook.com---password123---client_id_here---refresh_token_here---1756047705.258643
```

### 配置字段说明
- **email**: Outlook邮箱地址
- **password**: 邮箱密码（用于某些验证场景）
- **client_id**: Microsoft应用程序的Client ID
- **refresh_token**: OAuth刷新令牌
- **timestamp**: 时间戳（可选）

## 核心模块说明

### 1. OutlookConfig (config.py)
- 配置文件解析和管理
- Token更新和持久化
- 配置验证

### 2. OutlookOAuthClient (oauth_client.py)
- OAuth 2.0认证流程
- Access Token获取和刷新
- Token有效性验证

### 3. OutlookEmailClient (email_client.py)
- Graph API邮件获取
- IMAP OAuth邮件获取
- POP3 OAuth邮件获取
- 统一的邮件数据格式

### 4. 主程序 (main.py)
- 交互式测试界面
- 命令行参数支持
- 完整的测试套件

## API使用示例

### 基本使用
```python
from config import OutlookConfig
from oauth_client import OutlookOAuthClient
from email_client import OutlookEmailClient

# 加载配置
config = OutlookConfig("outlook_token.txt")
config.load_config()

# 初始化客户端
oauth_client = OutlookOAuthClient(config)
email_client = OutlookEmailClient(config, oauth_client)

# 获取邮件
emails = email_client.get_emails_graph_api(count=5)
for email in emails:
    print(f"主题: {email['subject']}")
    print(f"发件人: {email['from']}")
```

### Token验证
```python
# 验证Token有效性
result = oauth_client.test_token_validity()
if result['valid']:
    print("Token有效")
    print(f"用户: {result['token_info']['user_email']}")
else:
    print(f"Token无效: {result['error']}")
```

## 错误处理

程序包含完整的错误处理机制：

- **网络错误**: 自动重试和超时处理
- **认证错误**: Token刷新和错误提示
- **配置错误**: 详细的验证和错误信息
- **日志记录**: 所有操作都有详细日志

## 日志文件

程序会生成 `outlook_oauth.log` 文件，包含：
- 认证过程日志
- 邮件获取日志
- 错误信息和堆栈跟踪
- 性能统计信息

## 注意事项

1. **Token安全**: 请妥善保管outlook_token.txt文件，不要泄露给他人
2. **网络环境**: 确保网络可以访问Microsoft服务
3. **权限配置**: 确保Microsoft应用程序有正确的邮件读取权限
4. **频率限制**: 注意Microsoft API的调用频率限制

## 故障排除

### 常见问题

1. **Token验证失败**
   - 检查client_id和refresh_token是否正确
   - 确认Microsoft应用程序配置正确

2. **网络连接失败**
   - 检查网络连接
   - 确认防火墙设置

3. **邮件获取失败**
   - 检查邮箱权限设置
   - 确认协议支持情况

### 调试模式
修改config.py中的日志级别为DEBUG可获得更详细的调试信息：
```python
logging.basicConfig(level=logging.DEBUG, ...)
```

## 许可证

本项目仅供学习和研究使用，请遵守相关服务条款和法律法规。
