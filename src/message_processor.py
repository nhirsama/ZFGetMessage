import os
import json
import hashlib
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

class MessageProcessor:
    """处理教务通知的获取、存储"""

    def __init__(self, env: Dict[str, Any]):
        """
        初始化消息处理器
        :param env: 环境变量字典
        """
        self.env = env
        self.data_dir = 'data'
        os.makedirs(self.data_dir, exist_ok=True)
        self.message_file = os.path.join(self.data_dir, "message_records.json")

        # 初始化必要文件
        self._init_files()

    def _init_files(self):
        """初始化必要的存储文件"""
        if not os.path.exists(self.message_file):
            self._write_json_file(self.message_file, [])

    def _write_json_file(self, path: str, data: Any):
        """安全写入JSON文件，使用UTF-8编码"""
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logging.error(f"写入文件 {path} 失败: {str(e)}")
            # 创建空文件作为后备
            with open(path, 'w', encoding='utf-8') as f:
                f.write('[]')

    def _read_json_file(self, path: str) -> Any:
        """安全读取JSON文件"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            logging.warning(f"文件 {path} 格式错误，返回空列表")
            return []
        except Exception as e:
            logging.error(f"读取文件 {path} 失败: {str(e)}")
            return []

    def _get_message_id(self, message: Dict[str, Any]) -> str:
        """
        生成通知的唯一标识
        :param message: 通知字典
        :return: SHA256哈希值
        """
        # 使用创建时间和内容生成唯一ID
        content_str = f"{message.get('create_time', '')}_{message.get('content', '')}"
        return hashlib.sha256(content_str.encode('utf-8')).hexdigest()

    def _get_new_messages(self, current_messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        获取新通知
        :param current_messages: 当前获取的通知列表
        :return: 新通知列表
        """
        # 读取历史记录
        old_messages = self._read_json_file(self.message_file)

        # 创建唯一标识集合
        old_message_ids = set()
        for msg in old_messages:
            try:
                # 使用消息ID作为唯一标识
                msg_id = self._get_message_id(msg)
                old_message_ids.add(msg_id)
            except KeyError:
                continue

        # 找出新通知
        new_messages = []
        for msg in current_messages:
            try:
                msg_id = self._get_message_id(msg)
                if msg_id not in old_message_ids:
                    new_messages.append(msg)
            except KeyError:
                continue

        # 更新历史记录
        if current_messages:
            # 合并新旧记录，去除重复
            all_messages = current_messages + old_messages
            unique_messages = []
            seen_ids = set()

            for msg in all_messages:
                try:
                    msg_id = self._get_message_id(msg)
                    if msg_id not in seen_ids:
                        seen_ids.add(msg_id)
                        unique_messages.append(msg)
                except KeyError:
                    continue

            # 按创建时间排序（最新的在前）
            try:
                # 健壮的排序方法
                unique_messages.sort(
                    key=lambda x: (
                        datetime.strptime(x['create_time'], '%Y-%m-%d %H:%M:%S')
                        if x.get('create_time') and isinstance(x['create_time'], str)
                        else datetime.min
                    ),
                    reverse=True
                )
            except Exception as e:
                logging.warning(f"排序失败，使用备用排序方法: {str(e)}")
                # 备用排序方法：使用字符串比较
                unique_messages.sort(
                    key=lambda x: x.get('create_time', '') or '',
                    reverse=True
                )

            # 保存更新后的记录（最多保留100条）
            self._write_json_file(self.message_file, unique_messages[:100])

        return new_messages

    def _format_message_markdown(self, message_list: List[Dict[str, Any]]) -> str:
        """
        将通知列表格式化为Markdown字符串
        :param message_list: 通知列表
        :return: Markdown格式的字符串
        """
        if not message_list:
            return ""

        markdown = "------\n**新通知**\n"

        for msg in message_list:
            # 格式化创建时间
            try:
                create_time = datetime.strptime(msg['create_time'], '%Y-%m-%d %H:%M:%S')
                formatted_time = create_time.strftime("%Y年%m月%d日 %H:%M")
            except:
                formatted_time = msg.get('create_time', '未知时间')

            # 截断过长的内容
            content = msg.get('content', '')
            if len(content) > 200:
                content = content[:200] + "..."

            markdown += (
                f"类型：{msg.get('type', '通知')}\n"
                f"时间：{formatted_time}\n"
                f"内容：{content}\n"
                f"------\n"
            )

        return markdown

    def _get_workflow_info(self) -> str:
        """获取工作流信息"""
        return (
            f"------\n"
            f"工作流信息：\n"
            f"Force Push Message：{self.env.get('force_push_message', '')}\n"
            f"Branch Name：{self.env.get('github_ref_name', '')}\n"
            f"Triggered By：{self.env.get('github_event_name', '')}\n"
            f"Initial Run By：{self.env.get('github_actor', '')}\n"
            f"Initial Run By ID：{self.env.get('github_actor_id', '')}\n"
            f"Initiated Run By：{self.env.get('github_triggering_actor', '')}\n"
            f"Repository Name：{self.env.get('repository_name', '')}\n"
            f"Commit SHA：{self.env.get('github_sha', '')}\n"
            f"Workflow Name：{self.env.get('github_workflow', '')}\n"
            f"Workflow Number：{self.env.get('github_run_number', '')}\n"
            f"Workflow ID：{self.env.get('github_run_id', '')}\n"
            f"Beijing Time：{self.env.get('beijing_time', '')}"
        )

    def process(self, student_client: Any, user_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        处理通知获取和推送生成
        :param student_client: 学生客户端对象
        :param user_info: 用户个人信息（可选）
        :return: 包含通知信息的字典
        """
        result = {
            'title': "正方教务管理系统消息通知",
            'content': "",
            'has_error': False,
            'error_content': [],
            'has_new': False,
            'run_log': ""
        }

        try:
            # 获取通知
            message_response = student_client.get_notifications()

            if not message_response or 'data' not in message_response:
                result['run_log'] += "通知响应为空\n"
                message_content = "------\n消息通知：\n暂无新通知\n------"
            else:
                # 获取通知数据
                message_data = message_response.get('data', [])

                if not message_data:
                    result['run_log'] += "通知列表为空\n"
                    message_content = "------\n消息通知：\n暂无新通知\n------"
                else:
                    # 获取新通知
                    new_messages = self._get_new_messages(message_data)

                    if new_messages:
                        # 格式化新通知
                        message_content = self._format_message_markdown(new_messages)
                        result['has_new'] = True
                        result['run_log'] += f"发现 {len(new_messages)} 条新通知\n"
                    else:
                        # 获取最新通知时间
                        latest_time = message_data[0].get('create_time', '未知时间')
                        message_content = f"------\n消息通知：\n通知未更新\n最近一次更新时间：{latest_time}\n------"
                        result['run_log'] += "通知未更新\n"
        except Exception as e:
            logging.error(f"处理通知时出错: {str(e)}")
            result['has_error'] = True
            result['error_content'].append("处理通知时发生错误")
            message_content = "------\n消息通知：\n获取通知时发生错误\n------"

        # 获取个人信息（如果提供）
        personal_info = ""

        # 工作流信息
        workflow_info = self._get_workflow_info()
        copyright_text = "Copyright © 2025 nhirsama.\n[关于](https://github.com/nhirsama/ZFGetMessage/)"
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 整合所有信息
        result['content'] = (
            f"{personal_info}"
            f"{message_content}\n"
            f"{workflow_info if self.env.get('github_actions', False) else current_time}\n"
            f"{copyright_text}"
        )

        return result