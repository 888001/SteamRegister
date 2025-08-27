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
        self.client_id = None
        self.refresh_token = None
        self.timestamp = None
        self.logger = logging.getLogger(__name__)
        
    def load_config(self) -> bool:
        """
        从token文件加载配置
        格式: email---password---client_id---refresh_token---timestamp
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
            if len(parts) < 4:
                self.logger.error(f"Token文件格式错误，期望至少4个部分，实际{len(parts)}个")
                return False
                
            self.email = parts[0]
            self.password = parts[1]
            self.client_id = parts[2]
            self.refresh_token = parts[3]
            self.timestamp = parts[4] if len(parts) > 4 else None
            
            self.logger.info(f"成功加载配置 - 邮箱: {self.email}")
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
            'refresh_token': self.refresh_token
        }
    
    def update_refresh_token(self, new_refresh_token: str) -> bool:
        """更新refresh_token"""
        try:
            self.refresh_token = new_refresh_token
            
            # 重新构建文件内容
            parts = [self.email, self.password, self.client_id, new_refresh_token]
            if self.timestamp:
                parts.append(self.timestamp)
                
            new_content = '---'.join(parts)
            
            with open(self.token_file, 'w', encoding='utf-8') as f:
                f.write(new_content + '\n')
                
            self.logger.info("Refresh token已更新")
            return True
            
        except Exception as e:
            self.logger.error(f"更新refresh token失败: {e}")
            return False
    
    def validate_config(self) -> bool:
        """验证配置完整性"""
        required_fields = [self.email, self.client_id, self.refresh_token]
        if not all(required_fields):
            self.logger.error("配置不完整，缺少必要字段")
            return False
            
        if '@' not in self.email:
            self.logger.error("邮箱格式无效")
            return False
            
        return True
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"OutlookConfig(email={self.email}, client_id={self.client_id[:10]}...)"
