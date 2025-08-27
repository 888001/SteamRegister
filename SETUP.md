# SteamRegister 配置说明

## 🚀 快速开始

### 1. 复制示例配置文件

```bash
# 复制配置文件
cp config.example.json config.json
cp email_password.example.txt email_password.txt
cp proxy_ips.example.txt proxy_ips.txt
```

### 2. 编辑配置文件

#### config.json
编辑主配置文件，设置：
- `captcha_api_key`: 验证码服务API密钥
- `threads`: 并发线程数
- `proxy_type`: 代理类型 (http/socks5)
- 其他注册参数

#### email_password.txt
配置邮箱信息：

**普通邮箱格式：**
```
email@example.com----password
```

**Graph API邮箱格式（推荐）：**
```
email@outlook.com----password----refresh_token----access_token----expires_timestamp----client_id
```

#### proxy_ips.txt
配置代理服务器：
```
ip:port:username:password
```

### 3. 运行程序

```bash
python steamrg.py
```

## 🔐 安全注意事项

- ⚠️ **绝不要**将包含真实信息的配置文件提交到Git
- ✅ 只编辑本地的配置文件
- ✅ 使用高质量的代理服务
- ✅ 定期更新API密钥和token

## 📁 文件说明

| 文件 | 用途 | 是否提交Git |
|------|------|-------------|
| `config.example.json` | 配置模板 | ✅ 是 |
| `config.json` | 实际配置 | ❌ 否 |
| `email_password.example.txt` | 邮箱模板 | ✅ 是 |
| `email_password.txt` | 实际邮箱 | ❌ 否 |
| `proxy_ips.example.txt` | 代理模板 | ✅ 是 |
| `proxy_ips.txt` | 实际代理 | ❌ 否 |

## 🛠️ OAuth邮件功能

如需使用Outlook OAuth邮件功能，请参考 `outlook_oauth_demo/` 目录中的详细说明。

## ❓ 常见问题

**Q: 如何获取Outlook的refresh_token？**
A: 使用 `outlook_oauth_demo/oauth_setup.py` 工具获取。

**Q: 代理不工作怎么办？**
A: 检查代理格式和网络连接，建议使用付费代理服务。

**Q: 验证码识别失败？**
A: 检查验证码服务API密钥和余额。
