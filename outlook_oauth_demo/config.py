"""
配置管理模块
解析和管理Outlook OAuth配置
"""
import os
import logging
from typing import Dict, Optional

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('outlook_oauth.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class OutlookConfig:
    """Outlook OAuth配置管理类"""

    def __init__(self, token_file: str = "outlook_token.txt"):
        self.token_file = token_file
        self.email = None
        self.password = None
        self.client_id = None  # 从文件中读取
        self.refresh_token = None
        self.access_token = None
        self.expires_timestamp = None
        self.logger = logging.getLogger(__name__)
        
    def load_config(self) -> bool:
        """
        从token文件加载配置
        格式: email---password---refresh_token---access_token---expires_timestamp---client_id
        """
        try:
            if not os.path.exists(self.token_file):
                self.logger.error(f"Token文件不存在: {self.token_file}")
                return False

            with open(self.token_file, 'r', encoding='utf-8') as f:
                line = f.readline().strip()

            if not line:
                self.logger.error("Token文件为空")
                return False

            parts = line.split('---')

            # 解析字段 (client_id在末尾)
            self.email = parts[0] if len(parts) > 0 else None
            self.password = parts[1] if len(parts) > 1 else None
            self.refresh_token = parts[2] if len(parts) > 2 else None
            self.access_token = parts[3] if len(parts) > 3 else None
            self.expires_timestamp = parts[4] if len(parts) > 4 else None
            self.client_id = parts[5] if len(parts) > 5 else "bb2aec70-3c74-48ab-9c37-13d36c32d99f"  # 默认值

            # 验证必要字段
            if not self.email or not self.refresh_token:
                self.logger.error("Token文件缺少必要字段（email或refresh_token）")
                return False

            self.logger.info(f"成功加载配置 - 邮箱: {self.email}")
            self.logger.info(f"Client ID: {self.client_id}")
            self.logger.info(f"字段数量: {len(parts)}")
            self.logger.info(f"有Access Token: {'是' if self.access_token else '否'}")
            self.logger.info(f"过期时间戳: {self.expires_timestamp}")

            return True

        except Exception as e:
            self.logger.error(f"加载配置失败: {e}")
            return False
    
    def get_email_data(self) -> Dict[str, str]:
        """获取邮箱数据字典"""
        return {
            'email': self.email,
            'password': self.password,
            'client_id': self.client_id,
            'refresh_token': self.refresh_token,
            'access_token': self.access_token
        }
    
    def update_tokens(self, new_refresh_token: str = None, new_access_token: str = None, expires_timestamp: str = None) -> bool:
        """更新tokens"""
        try:
            if new_refresh_token:
                self.refresh_token = new_refresh_token
            if new_access_token:
                self.access_token = new_access_token
            if expires_timestamp:
                self.expires_timestamp = expires_timestamp

            # 构建文件内容: email---password---refresh_token---access_token---expires_timestamp---client_id
            parts = [
                self.email or '',
                self.password or '',
                self.refresh_token or '',
                self.access_token or '',
                self.expires_timestamp or '',
                self.client_id or ''
            ]

            new_content = '---'.join(parts)

            with open(self.token_file, 'w', encoding='utf-8') as f:
                f.write(new_content + '\n')

            self.logger.info("Tokens已更新")
            return True

        except Exception as e:
            self.logger.error(f"更新tokens失败: {e}")
            return False

    def update_refresh_token(self, new_refresh_token: str) -> bool:
        """更新refresh_token (兼容旧接口)"""
        return self.update_tokens(new_refresh_token=new_refresh_token)
    
    def validate_config(self) -> bool:
        """验证配置完整性"""
        required_fields = [self.email, self.client_id, self.refresh_token]
        if not all(required_fields):
            self.logger.error("配置不完整，缺少必要字段（email、client_id、refresh_token）")
            return False

        if '@' not in self.email:
            self.logger.error("邮箱格式无效")
            return False

        # 验证client_id格式（UUID格式）
        if len(self.client_id) != 36 or self.client_id.count('-') != 4:
            self.logger.warning("Client ID格式可能不正确")

        return True
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"OutlookConfig(email={self.email}, client_id={self.client_id[:10]}...)"
