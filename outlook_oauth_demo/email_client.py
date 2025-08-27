"""
邮件客户端
支持Graph API、IMAP OAuth、POP3 OAuth三种方式获取邮件
"""
import base64
import imaplib
import poplib
import email
import requests
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from oauth_client import OutlookOAuthClient
from config import OutlookConfig

class OutlookEmailClient:
    """Outlook邮件客户端"""
    
    # 服务器配置
    IMAP_SERVER = "outlook.office365.com"
    IMAP_PORT = 993
    POP3_SERVER = "outlook.office365.com"
    POP3_PORT = 995
    GRAPH_API_BASE = "https://graph.microsoft.com/v1.0"
    
    def __init__(self, config: OutlookConfig, oauth_client: OutlookOAuthClient):
        self.config = config
        self.oauth_client = oauth_client
        self.logger = logging.getLogger(__name__)
    
    def get_emails_graph_api(self, count: int = 5) -> Optional[List[Dict[str, Any]]]:
        """
        使用Graph API获取邮件
        
        Args:
            count: 获取邮件数量
            
        Returns:
            邮件列表，失败返回None
        """
        try:
            access_token = self.oauth_client.get_access_token("GRAPH")
            if not access_token:
                self.logger.error("无法获取Graph API访问令牌")
                return None
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            params = {
                '$top': count,
                '$select': 'subject,body,receivedDateTime,from,hasAttachments,isRead',
                '$orderby': 'receivedDateTime desc'
            }
            
            self.logger.info(f"正在通过Graph API获取最新{count}封邮件...")
            
            response = requests.get(
                f'{self.GRAPH_API_BASE}/me/messages',
                headers=headers,
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                emails = response.json().get('value', [])
                self.logger.info(f"成功获取{len(emails)}封邮件")
                return self._format_graph_emails(emails)
            else:
                self.logger.error(f"Graph API请求失败: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.logger.error(f"Graph API获取邮件失败: {e}")
            return None
    
    def get_emails_imap_oauth(self, count: int = 5, folder: str = "INBOX") -> Optional[List[Dict[str, Any]]]:
        """
        使用IMAP OAuth获取邮件
        
        Args:
            count: 获取邮件数量
            folder: 邮件文件夹
            
        Returns:
            邮件列表，失败返回None
        """
        try:
            access_token = self.oauth_client.get_access_token("IMAP_OAUTH")
            if not access_token:
                self.logger.error("无法获取IMAP OAuth访问令牌")
                return None
            
            # 构建XOAUTH2认证字符串
            auth_string = f"user={self.config.email}\x01auth=Bearer {access_token}\x01\x01"
            
            self.logger.info(f"正在通过IMAP OAuth连接到{self.IMAP_SERVER}...")
            
            # 连接到IMAP服务器
            mail = imaplib.IMAP4_SSL(self.IMAP_SERVER, self.IMAP_PORT)
            mail.authenticate('XOAUTH2', lambda x: auth_string)
            
            # 选择文件夹
            mail.select(folder)
            
            # 搜索邮件
            _, message_ids = mail.search(None, 'ALL')
            message_ids = message_ids[0].split()
            
            # 获取最新的邮件
            latest_ids = message_ids[-count:] if len(message_ids) >= count else message_ids
            emails = []
            
            for msg_id in reversed(latest_ids):  # 倒序获取最新邮件
                _, msg_data = mail.fetch(msg_id, '(RFC822)')
                email_body = msg_data[0][1]
                email_message = email.message_from_bytes(email_body)
                emails.append(self._format_imap_email(email_message))
            
            mail.logout()
            self.logger.info(f"成功通过IMAP获取{len(emails)}封邮件")
            return emails
            
        except Exception as e:
            self.logger.error(f"IMAP OAuth获取邮件失败: {e}")
            return None
    
    def get_emails_pop3_oauth(self, count: int = 5) -> Optional[List[Dict[str, Any]]]:
        """
        使用POP3 OAuth获取邮件
        
        Args:
            count: 获取邮件数量
            
        Returns:
            邮件列表，失败返回None
        """
        try:
            access_token = self.oauth_client.get_access_token("POP3_OAUTH")
            if not access_token:
                self.logger.error("无法获取POP3 OAuth访问令牌")
                return None
            
            # 构建XOAUTH2认证字符串
            auth_string = f"user={self.config.email}\x01auth=Bearer {access_token}\x01\x01"
            auth_bytes = auth_string.encode('ascii')
            auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
            
            self.logger.info(f"正在通过POP3 OAuth连接到{self.POP3_SERVER}...")
            
            # 连接到POP3服务器
            mail = poplib.POP3_SSL(self.POP3_SERVER, self.POP3_PORT)
            mail._shortcmd('AUTH XOAUTH2')
            mail._shortcmd(auth_b64)
            
            # 获取邮件数量
            num_messages = len(mail.list()[1])
            
            # 获取最新的邮件
            start_index = max(1, num_messages - count + 1)
            emails = []
            
            for i in range(start_index, num_messages + 1):
                _, lines, _ = mail.retr(i)
                email_content = b'\n'.join(lines)
                email_message = email.message_from_bytes(email_content)
                emails.append(self._format_pop3_email(email_message))
            
            mail.quit()
            self.logger.info(f"成功通过POP3获取{len(emails)}封邮件")
            return emails
            
        except Exception as e:
            self.logger.error(f"POP3 OAuth获取邮件失败: {e}")
            return None
    
    def _format_graph_emails(self, emails: List[Dict]) -> List[Dict[str, Any]]:
        """格式化Graph API邮件数据"""
        formatted_emails = []
        for email_data in emails:
            formatted_email = {
                'protocol': 'GRAPH',
                'subject': email_data.get('subject', '无主题'),
                'from': email_data.get('from', {}).get('emailAddress', {}).get('address', '未知发件人'),
                'received_time': email_data.get('receivedDateTime', ''),
                'is_read': email_data.get('isRead', False),
                'has_attachments': email_data.get('hasAttachments', False),
                'body': email_data.get('body', {}).get('content', '')[:500] + '...' if len(email_data.get('body', {}).get('content', '')) > 500 else email_data.get('body', {}).get('content', '')
            }
            formatted_emails.append(formatted_email)
        return formatted_emails
    
    def _format_imap_email(self, email_message) -> Dict[str, Any]:
        """格式化IMAP邮件数据"""
        return {
            'protocol': 'IMAP_OAUTH',
            'subject': email_message.get('Subject', '无主题'),
            'from': email_message.get('From', '未知发件人'),
            'received_time': email_message.get('Date', ''),
            'body': self._extract_email_body(email_message)
        }
    
    def _format_pop3_email(self, email_message) -> Dict[str, Any]:
        """格式化POP3邮件数据"""
        return {
            'protocol': 'POP3_OAUTH',
            'subject': email_message.get('Subject', '无主题'),
            'from': email_message.get('From', '未知发件人'),
            'received_time': email_message.get('Date', ''),
            'body': self._extract_email_body(email_message)
        }
    
    def _extract_email_body(self, email_message) -> str:
        """提取邮件正文"""
        try:
            if email_message.is_multipart():
                for part in email_message.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True)
                        if body:
                            return body.decode('utf-8', errors='ignore')[:500] + '...'
            else:
                body = email_message.get_payload(decode=True)
                if body:
                    return body.decode('utf-8', errors='ignore')[:500] + '...'
        except Exception as e:
            self.logger.warning(f"提取邮件正文失败: {e}")
        return "无法提取邮件正文"
