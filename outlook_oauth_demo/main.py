"""
Outlook OAuth邮件获取Demo
主程序和测试模块
"""
import sys
import json
import logging
from typing import List, Dict, Any
from config import OutlookConfig
from oauth_client import OutlookOAuthClient
from email_client import OutlookEmailClient

def print_separator(title: str = ""):
    """打印分隔线"""
    print("=" * 60)
    if title:
        print(f" {title} ".center(60, "="))
        print("=" * 60)

def print_email_info(emails: List[Dict[str, Any]]):
    """打印邮件信息"""
    if not emails:
        print("没有获取到邮件")
        return
    
    for i, email_data in enumerate(emails, 1):
        print(f"\n📧 邮件 {i}:")
        print(f"   协议: {email_data.get('protocol', 'Unknown')}")
        print(f"   主题: {email_data.get('subject', '无主题')}")
        print(f"   发件人: {email_data.get('from', '未知')}")
        print(f"   接收时间: {email_data.get('received_time', '未知')}")
        
        if 'is_read' in email_data:
            print(f"   已读: {'是' if email_data['is_read'] else '否'}")
        if 'has_attachments' in email_data:
            print(f"   有附件: {'是' if email_data['has_attachments'] else '否'}")
            
        body = email_data.get('body', '')
        if body:
            print(f"   正文预览: {body[:100]}...")
        print("-" * 50)

def test_oauth_token(oauth_client: OutlookOAuthClient):
    """测试OAuth token有效性"""
    print_separator("OAuth Token 验证测试")
    
    result = oauth_client.test_token_validity()
    
    if result['valid']:
        print("✅ Token验证成功!")
        token_info = result['token_info']
        print(f"   用户邮箱: {token_info.get('user_email', '未知')}")
        print(f"   显示名称: {token_info.get('display_name', '未知')}")
        print(f"   用户ID: {token_info.get('user_id', '未知')}")
    else:
        print("❌ Token验证失败!")
        print(f"   错误信息: {result['error']}")
    
    return result['valid']

def test_graph_api(email_client: OutlookEmailClient):
    """测试Graph API邮件获取"""
    print_separator("Graph API 邮件获取测试")
    
    try:
        emails = email_client.get_emails_graph_api(count=3)
        if emails:
            print(f"✅ 成功通过Graph API获取到{len(emails)}封邮件")
            print_email_info(emails)
        else:
            print("❌ Graph API邮件获取失败")
    except Exception as e:
        print(f"❌ Graph API测试异常: {e}")

def test_imap_oauth(email_client: OutlookEmailClient):
    """测试IMAP OAuth邮件获取"""
    print_separator("IMAP OAuth 邮件获取测试")
    
    try:
        emails = email_client.get_emails_imap_oauth(count=3)
        if emails:
            print(f"✅ 成功通过IMAP OAuth获取到{len(emails)}封邮件")
            print_email_info(emails)
        else:
            print("❌ IMAP OAuth邮件获取失败")
    except Exception as e:
        print(f"❌ IMAP OAuth测试异常: {e}")

def test_pop3_oauth(email_client: OutlookEmailClient):
    """测试POP3 OAuth邮件获取"""
    print_separator("POP3 OAuth 邮件获取测试")
    
    try:
        emails = email_client.get_emails_pop3_oauth(count=3)
        if emails:
            print(f"✅ 成功通过POP3 OAuth获取到{len(emails)}封邮件")
            print_email_info(emails)
        else:
            print("❌ POP3 OAuth邮件获取失败")
    except Exception as e:
        print(f"❌ POP3 OAuth测试异常: {e}")

def interactive_menu(email_client: OutlookEmailClient, oauth_client: OutlookOAuthClient):
    """交互式菜单"""
    while True:
        print_separator("Outlook OAuth 邮件获取 Demo")
        print("请选择测试项目:")
        print("1. 验证OAuth Token")
        print("2. Graph API 邮件获取")
        print("3. IMAP OAuth 邮件获取")
        print("4. POP3 OAuth 邮件获取")
        print("5. 运行所有测试")
        print("6. 刷新Access Token")
        print("0. 退出")
        print("-" * 60)
        
        choice = input("请输入选择 (0-6): ").strip()
        
        if choice == '0':
            print("👋 再见!")
            break
        elif choice == '1':
            test_oauth_token(oauth_client)
        elif choice == '2':
            test_graph_api(email_client)
        elif choice == '3':
            test_imap_oauth(email_client)
        elif choice == '4':
            test_pop3_oauth(email_client)
        elif choice == '5':
            run_all_tests(email_client, oauth_client)
        elif choice == '6':
            print("🔄 正在刷新Access Token...")
            if oauth_client.refresh_token():
                print("✅ Access Token刷新成功")
            else:
                print("❌ Access Token刷新失败")
        else:
            print("❌ 无效选择，请重新输入")
        
        input("\n按回车键继续...")

def run_all_tests(email_client: OutlookEmailClient, oauth_client: OutlookOAuthClient):
    """运行所有测试"""
    print_separator("运行所有测试")
    
    # 1. Token验证
    if not test_oauth_token(oauth_client):
        print("❌ Token验证失败，跳过邮件获取测试")
        return
    
    # 2. Graph API测试
    test_graph_api(email_client)
    
    # 3. IMAP OAuth测试
    test_imap_oauth(email_client)
    
    # 4. POP3 OAuth测试
    test_pop3_oauth(email_client)
    
    print_separator("所有测试完成")

def main():
    """主函数"""
    print_separator("Outlook OAuth 邮件获取 Demo 启动")
    
    # 1. 加载配置
    config = OutlookConfig("outlook_token.txt")
    if not config.load_config():
        print("❌ 配置加载失败，请检查outlook_token.txt文件")
        return
    
    if not config.validate_config():
        print("❌ 配置验证失败，请检查配置完整性")
        return
    
    print(f"✅ 配置加载成功: {config}")
    
    # 2. 初始化OAuth客户端
    oauth_client = OutlookOAuthClient(config)
    
    # 3. 初始化邮件客户端
    email_client = OutlookEmailClient(config, oauth_client)
    
    # 4. 检查命令行参数
    if len(sys.argv) > 1:
        if sys.argv[1] == '--test-all':
            run_all_tests(email_client, oauth_client)
            return
        elif sys.argv[1] == '--test-token':
            test_oauth_token(oauth_client)
            return
        elif sys.argv[1] == '--test-graph':
            test_graph_api(email_client)
            return
    
    # 5. 启动交互式菜单
    interactive_menu(email_client, oauth_client)

if __name__ == "__main__":
    main()
