"""
OAuth认证客户端
处理Microsoft OAuth 2.0认证流程
"""
import requests
import logging
import time
import urllib3
from typing import Optional, Dict, Any
from config import OutlookConfig

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class OutlookOAuthClient:
    """Outlook OAuth认证客户端"""
    
    # Microsoft OAuth 2.0端点
    TOKEN_ENDPOINT = "https://login.microsoftonline.com/consumers/oauth2/v2.0/token"
    GRAPH_SCOPE = "https://graph.microsoft.com/.default"
    
    def __init__(self, config: OutlookConfig):
        self.config = config
        self.access_token = config.access_token  # 从配置中加载已有的access_token
        self.token_expires_at = None
        if config.expires_timestamp:
            try:
                self.token_expires_at = float(config.expires_timestamp)
            except (ValueError, TypeError):
                self.token_expires_at = None
        self.logger = logging.getLogger(__name__)
        
    def get_access_token(self, protocol: str = "GRAPH", force_refresh: bool = False) -> Optional[str]:
        """
        获取访问令牌

        Args:
            protocol: 协议类型 (GRAPH, IMAP_OAUTH, POP3_OAUTH)
            force_refresh: 强制刷新token

        Returns:
            访问令牌字符串，失败返回None
        """
        # 检查现有token是否仍然有效
        if not force_refresh and self.access_token and self._is_token_valid():
            self.logger.info("使用现有的有效访问令牌")
            return self.access_token
            
        try:
            # 构建请求数据
            data = {
                'client_id': self.config.client_id,
                'refresh_token': self.config.refresh_token,
                'grant_type': 'refresh_token',
            }
            
            # 为Graph API添加scope
            if protocol == 'GRAPH':
                data['scope'] = self.GRAPH_SCOPE
                
            self.logger.info(f"正在获取{protocol}协议的访问令牌...")
            
            # 发送token请求
            response = requests.post(self.TOKEN_ENDPOINT, data=data, timeout=30, verify=False)
            
            if response.status_code == 200:
                result = response.json()
                self.access_token = result.get('access_token')
                
                # 处理新的refresh_token和过期时间
                new_refresh_token = result.get('refresh_token')
                expires_in = result.get('expires_in', 3600)
                self.token_expires_at = time.time() + expires_in - 300  # 提前5分钟过期

                # 更新配置文件中的tokens
                self.config.update_tokens(
                    new_refresh_token=new_refresh_token if new_refresh_token else None,
                    new_access_token=self.access_token,
                    expires_timestamp=str(self.token_expires_at)
                )

                if new_refresh_token and new_refresh_token != self.config.refresh_token:
                    self.logger.info("检测到新的refresh_token已更新")
                else:
                    self.logger.info("Access token已更新")
                
                self.logger.info("成功获取访问令牌")
                return self.access_token
                
            else:
                error_info = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
                self.logger.error(f"获取访问令牌失败: {response.status_code} - {error_info}")
                return None
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"网络请求失败: {e}")
            return None
        except Exception as e:
            self.logger.error(f"获取访问令牌时发生未知错误: {e}")
            return None
    
    def _is_token_valid(self) -> bool:
        """检查token是否仍然有效"""
        if not self.token_expires_at:
            return False
        return time.time() < self.token_expires_at
    
    def refresh_token(self, protocol: str = "GRAPH") -> bool:
        """
        强制刷新访问令牌
        
        Args:
            protocol: 协议类型
            
        Returns:
            刷新成功返回True，失败返回False
        """
        self.logger.info("强制刷新访问令牌...")
        token = self.get_access_token(protocol, force_refresh=True)
        return token is not None
    
    def test_token_validity(self) -> Dict[str, Any]:
        """
        测试token有效性
        
        Returns:
            包含测试结果的字典
        """
        result = {
            'valid': False,
            'error': None,
            'token_info': {}
        }
        
        try:
            # 尝试获取访问令牌
            access_token = self.get_access_token("GRAPH")
            if not access_token:
                result['error'] = "无法获取访问令牌"
                return result
            
            # 使用Graph API测试token
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            # 获取用户信息来验证token
            response = requests.get(
                'https://graph.microsoft.com/v1.0/me',
                headers=headers,
                timeout=30,
                verify=False
            )
            
            if response.status_code == 200:
                user_info = response.json()
                result['valid'] = True
                result['token_info'] = {
                    'user_email': user_info.get('mail', user_info.get('userPrincipalName')),
                    'display_name': user_info.get('displayName'),
                    'user_id': user_info.get('id')
                }
                self.logger.info("Token验证成功")
            else:
                result['error'] = f"Token验证失败: {response.status_code}"
                self.logger.error(result['error'])
                
        except Exception as e:
            result['error'] = f"Token验证时发生错误: {e}"
            self.logger.error(result['error'])
            
        return result
