"""
OAuth设置助手
帮助用户获取正确的refresh_token
"""
import urllib.parse
import webbrowser
import requests
import json
import urllib3
from typing import Dict, Any

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class OAuthSetup:
    """OAuth设置助手"""
    
    def __init__(self, client_id: str):
        self.client_id = client_id
        self.redirect_uri = "http://localhost:8080/callback"  # 本地回调地址
        self.scope = "https://graph.microsoft.com/Mail.Read offline_access"
        self.auth_url = "https://login.microsoftonline.com/consumers/oauth2/v2.0/authorize"
        self.token_url = "https://login.microsoftonline.com/consumers/oauth2/v2.0/token"
    
    def get_authorization_url(self) -> str:
        """生成授权URL"""
        params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'redirect_uri': self.redirect_uri,
            'scope': self.scope,
            'response_mode': 'query',
            'state': 'outlook_oauth_demo'
        }
        
        url = f"{self.auth_url}?{urllib.parse.urlencode(params)}"
        return url
    
    def exchange_code_for_tokens(self, authorization_code: str) -> Dict[str, Any]:
        """用授权码换取tokens"""
        data = {
            'client_id': self.client_id,
            'code': authorization_code,
            'redirect_uri': self.redirect_uri,
            'grant_type': 'authorization_code',
            'scope': self.scope
        }
        
        try:
            response = requests.post(self.token_url, data=data, verify=False, timeout=30)
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'data': response.json()
                }
            else:
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}: {response.text}"
                }
        except Exception as e:
            return {
                'success': False,
                'error': f"请求失败: {e}"
            }
    
    def test_refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """测试refresh_token是否有效"""
        data = {
            'client_id': self.client_id,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
            'scope': 'https://graph.microsoft.com/.default'
        }
        
        try:
            response = requests.post(self.token_url, data=data, verify=False, timeout=30)
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'data': response.json()
                }
            else:
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}: {response.text}"
                }
        except Exception as e:
            return {
                'success': False,
                'error': f"请求失败: {e}"
            }

def main():
    """主函数"""
    client_id = "bb2aec70-3c74-48ab-9c37-13d36c32d99f"
    
    print("=" * 60)
    print("Outlook OAuth 设置助手")
    print("=" * 60)
    print(f"Client ID: {client_id}")
    print()
    
    oauth_setup = OAuthSetup(client_id)
    
    while True:
        print("请选择操作:")
        print("1. 生成授权URL（获取新的refresh_token）")
        print("2. 用授权码换取tokens")
        print("3. 测试现有refresh_token")
        print("4. 退出")
        print("-" * 40)
        
        choice = input("请输入选择 (1-4): ").strip()
        
        if choice == '1':
            print("\n生成授权URL...")
            auth_url = oauth_setup.get_authorization_url()
            print(f"授权URL: {auth_url}")
            print()
            print("请按照以下步骤操作:")
            print("1. 复制上面的URL到浏览器中打开")
            print("2. 登录您的Outlook账号并授权")
            print("3. 授权后会跳转到localhost页面（可能显示无法访问）")
            print("4. 从地址栏复制完整的回调URL")
            print("5. 提取URL中的'code='参数值")
            print()
            
            # 尝试自动打开浏览器
            try:
                webbrowser.open(auth_url)
                print("✅ 已自动打开浏览器")
            except:
                print("❌ 无法自动打开浏览器，请手动复制URL")
        
        elif choice == '2':
            print("\n用授权码换取tokens...")
            code = input("请输入授权码: ").strip()
            
            if not code:
                print("❌ 授权码不能为空")
                continue
            
            result = oauth_setup.exchange_code_for_tokens(code)
            
            if result['success']:
                data = result['data']
                print("✅ 成功获取tokens!")
                print(f"Access Token: {data.get('access_token', '')[:50]}...")
                print(f"Refresh Token: {data.get('refresh_token', '')[:50]}...")
                print(f"Expires In: {data.get('expires_in', 0)} 秒")
                
                # 保存到文件
                email = input("请输入邮箱地址: ").strip()
                password = input("请输入邮箱密码: ").strip()
                
                if email and password:
                    token_content = f"{email}---{password}---{data.get('refresh_token', '')}---{data.get('access_token', '')}---{data.get('expires_in', 3600)}"
                    
                    with open('outlook_token_new.txt', 'w', encoding='utf-8') as f:
                        f.write(token_content + '\n')
                    
                    print("✅ Token已保存到 outlook_token_new.txt")
            else:
                print(f"❌ 获取tokens失败: {result['error']}")
        
        elif choice == '3':
            print("\n测试现有refresh_token...")
            refresh_token = input("请输入refresh_token: ").strip()
            
            if not refresh_token:
                print("❌ Refresh token不能为空")
                continue
            
            result = oauth_setup.test_refresh_token(refresh_token)
            
            if result['success']:
                data = result['data']
                print("✅ Refresh token有效!")
                print(f"新的Access Token: {data.get('access_token', '')[:50]}...")
                if data.get('refresh_token'):
                    print(f"新的Refresh Token: {data.get('refresh_token', '')[:50]}...")
            else:
                print(f"❌ Refresh token无效: {result['error']}")
        
        elif choice == '4':
            print("👋 再见!")
            break
        
        else:
            print("❌ 无效选择，请重新输入")
        
        print()

if __name__ == "__main__":
    main()
