"""
Outlook OAuth 邮件获取 - 最终完整Demo
从SteamRegister项目提取的OAuth邮件功能
"""
import sys
import time
import logging
from typing import List, Dict, Any
from config import OutlookConfig
from oauth_client import OutlookOAuthClient
from email_client import OutlookEmailClient

def setup_logging():
    """设置日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('outlook_oauth_final.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

def print_header():
    """打印程序头部"""
    print("=" * 70)
    print("🔐 Outlook OAuth 邮件获取 Demo".center(70))
    print("从SteamRegister项目提取的完整OAuth功能".center(70))
    print("=" * 70)
    print()

def display_config_info(config: OutlookConfig):
    """显示配置信息"""
    print("📋 配置信息:")
    print(f"   邮箱地址: {config.email}")
    print(f"   Client ID: {config.client_id}")
    print(f"   有Refresh Token: {'✅' if config.refresh_token else '❌'}")
    print(f"   有Access Token: {'✅' if config.access_token else '❌'}")
    
    if config.expires_timestamp:
        try:
            expires_time = float(config.expires_timestamp)
            current_time = time.time()
            if expires_time > current_time:
                remaining_hours = (expires_time - current_time) / 3600
                print(f"   Token状态: ✅ 有效 (剩余 {remaining_hours:.1f} 小时)")
            else:
                print(f"   Token状态: ⚠️ 已过期，将自动刷新")
        except:
            print(f"   Token状态: ❓ 时间戳格式错误")
    print()

def test_oauth_authentication(oauth_client: OutlookOAuthClient) -> bool:
    """测试OAuth认证"""
    print("🔑 OAuth认证测试:")
    
    # 获取access_token
    access_token = oauth_client.get_access_token("GRAPH")
    if not access_token:
        print("   ❌ 获取Access Token失败")
        return False
    
    print(f"   ✅ Access Token: {access_token[:30]}...")
    
    # 验证token
    result = oauth_client.test_token_validity()
    if result['valid']:
        token_info = result['token_info']
        print(f"   ✅ 用户验证成功")
        print(f"      用户邮箱: {token_info.get('user_email', '未知')}")
        print(f"      显示名称: {token_info.get('display_name', '未知')}")
        return True
    else:
        print(f"   ❌ Token验证失败: {result['error']}")
        return False

def display_emails(emails: List[Dict[str, Any]], protocol: str):
    """显示邮件列表"""
    if not emails:
        print(f"   ❌ 未获取到邮件")
        return
    
    print(f"   ✅ 成功获取 {len(emails)} 封邮件 (协议: {protocol})")
    print()
    
    for i, email_data in enumerate(emails, 1):
        print(f"   📧 邮件 {i}:")
        print(f"      主题: {email_data.get('subject', '无主题')}")
        print(f"      发件人: {email_data.get('from', '未知发件人')}")
        print(f"      时间: {email_data.get('received_time', '未知时间')}")
        
        if 'is_read' in email_data:
            print(f"      状态: {'已读' if email_data['is_read'] else '未读'}")
        if 'has_attachments' in email_data:
            print(f"      附件: {'有' if email_data['has_attachments'] else '无'}")
        
        # 显示邮件正文预览
        body = email_data.get('body', '')
        if body:
            # 清理HTML标签和换行符
            import re
            clean_body = re.sub(r'<[^>]+>', '', body)
            clean_body = clean_body.replace('\n', ' ').replace('\r', ' ').strip()
            if clean_body:
                preview = clean_body[:80] + "..." if len(clean_body) > 80 else clean_body
                print(f"      预览: {preview}")
        
        print()

def test_email_protocols(email_client: OutlookEmailClient):
    """测试不同的邮件协议"""
    print("📧 邮件获取测试:")
    
    # 1. Graph API
    print("\n   🌐 Graph API 测试:")
    try:
        emails = email_client.get_emails_graph_api(count=3)
        display_emails(emails, "Graph API")
    except Exception as e:
        print(f"   ❌ Graph API 失败: {e}")
    
    # 2. IMAP OAuth (可能需要特殊权限)
    print("   📨 IMAP OAuth 测试:")
    try:
        emails = email_client.get_emails_imap_oauth(count=3)
        display_emails(emails, "IMAP OAuth")
    except Exception as e:
        print(f"   ⚠️ IMAP OAuth 失败: {e}")
    
    # 3. POP3 OAuth (可能需要特殊权限)
    print("   📬 POP3 OAuth 测试:")
    try:
        emails = email_client.get_emails_pop3_oauth(count=3)
        display_emails(emails, "POP3 OAuth")
    except Exception as e:
        print(f"   ⚠️ POP3 OAuth 失败: {e}")

def main():
    """主函数"""
    setup_logging()
    print_header()
    
    # 1. 加载配置
    print("🔧 初始化配置...")
    config = OutlookConfig("outlook_token.txt")
    
    if not config.load_config():
        print("❌ 配置加载失败，请检查 outlook_token.txt 文件")
        return False
    
    display_config_info(config)
    
    # 2. 初始化OAuth客户端
    print("🔐 初始化OAuth客户端...")
    oauth_client = OutlookOAuthClient(config)
    print()
    
    # 3. 测试OAuth认证
    if not test_oauth_authentication(oauth_client):
        print("❌ OAuth认证失败，无法继续")
        return False
    print()
    
    # 4. 初始化邮件客户端
    print("📧 初始化邮件客户端...")
    email_client = OutlookEmailClient(config, oauth_client)
    print()
    
    # 5. 测试邮件获取
    test_email_protocols(email_client)
    
    # 6. 显示总结
    print("=" * 70)
    print("✅ Demo 执行完成!".center(70))
    print()
    print("📝 功能总结:")
    print("   ✅ OAuth 2.0 认证流程")
    print("   ✅ Access Token 自动刷新")
    print("   ✅ Microsoft Graph API 邮件获取")
    print("   ✅ IMAP/POP3 OAuth 支持")
    print("   ✅ 完整的错误处理和日志记录")
    print()
    print("📁 相关文件:")
    print("   📄 outlook_token.txt - OAuth配置文件")
    print("   📄 outlook_oauth_final.log - 详细日志")
    print("=" * 70)
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n👋 用户中断，程序退出")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ 程序异常: {e}")
        sys.exit(1)
