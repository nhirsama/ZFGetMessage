import os
import json
import re

from datetime import datetime
from scripts.get_user_info import get_user_info
from src.utils import encrypt_personal_info
from scripts.get_grade import get_grade

class GradeProcessor:
    def __init__(self, env):
        self.env = env
        self.data_dir = 'data'
        os.makedirs(self.data_dir, exist_ok=True)
        self.grade_file = os.path.join(self.data_dir, "grade_records.json")
        self.notice_file = os.path.join(self.data_dir, "notice_records.json")

        # 初始化文件
        self._init_files()

    def _init_files(self):
        """初始化必要的存储文件"""
        if not os.path.exists(self.grade_file):
            with open(self.grade_file, 'w') as f:
                json.dump([], f)
        if not os.path.exists(self.notice_file):
            with open(self.notice_file, 'w') as f:
                json.dump([], f)

    def _sanitize_grade(self, grade):
        """清理成绩记录中的敏感信息"""
        return {
            'class_id': grade.get('class_id'),
            'class_name': grade.get('class_name'),
            'credit': grade.get('credit'),
            'grade': grade.get('grade'),
            'grade_point': grade.get('grade_point'),
            'percentage_grades': grade.get('percentage_grades'),
            'submission_time': grade.get('submission_time'),
            'teacher': grade.get('teacher'),
            'title': grade.get('title'),
            'xfjd': grade.get('xfjd')
        }

    def _get_new_grades(self, current_grades):
        """
        获取新增成绩
        :param current_grades: 当前获取的成绩列表
        :return: 新增成绩列表
        """
        # 清理当前成绩记录
        sanitized_grades = [self._sanitize_grade(g) for g in current_grades]

        # 读取历史记录
        try:
            with open(self.grade_file, 'r') as f:
                old_grades = json.load(f)
        except:
            old_grades = []

        # 创建唯一标识集合
        old_grade_ids = {f"{g['class_id']}_{g['submission_time']}" for g in old_grades}

        # 找出新增成绩
        new_grades = []
        for grade in sanitized_grades:
            grade_id = f"{grade['class_id']}_{grade['submission_time']}"
            if grade_id not in old_grade_ids:
                new_grades.append(grade)

        # 更新历史记录
        if sanitized_grades:
            # 合并新旧记录，去重
            all_grades = sanitized_grades + old_grades
            unique_grades = []
            seen_ids = set()

            for grade in all_grades:
                grade_id = f"{grade['class_id']}_{grade['submission_time']}"
                if grade_id not in seen_ids:
                    seen_ids.add(grade_id)
                    unique_grades.append(grade)

            # 按提交时间排序（最新的在前）
            #unique_grades.sort(key=lambda x: x.get('submission_time', ''), reverse=True)

            # 保存更新后的记录
            with open(self.grade_file, 'w') as f:
                json.dump(unique_grades[:100], f, ensure_ascii=False, indent=2)

        return new_grades

    def _format_grade_markdown(self, grade_list):
        """
        将成绩列表格式化为Markdown字符串
        :param grade_list: 成绩列表
        :return: Markdown格式的字符串
        """
        if not grade_list:
            return ""

        markdown = "------\n**新增成绩**\n"

        for grade in grade_list:
            # 处理教师字段：用全角逗号分隔
            teachers = grade.get('teacher', '')
            if ';' in teachers:
                teachers = teachers.replace(';', '，')  # 全角逗号

            # 格式化提交时间
            try:
                submission_time = datetime.strptime(grade['submission_time'], '%Y-%m-%d %H:%M:%S')
                formatted_time = submission_time.strftime("%Y年%m月%d日 %H:%M")
            except:
                formatted_time = grade['submission_time']

            markdown += (
                f"课程名称：{grade['title']}\n"
                f"教师：{teachers}\n"
                f"成绩：{grade['grade']}\n"
                f"绩点：{grade['grade_point']}\n"
                f"学分：{grade['credit']}\n"
                f"提交时间：{formatted_time}\n"
                f"------\n"
            )

        return markdown

    def _get_workflow_info(self):
        """获取工作流信息"""
        return (
            f"------\n"
            f"工作流信息：\n"
            f"Force Push Message：{self.env['force_push_message']}\n"
            f"Branch Name：{self.env['github_ref_name']}\n"
            f"Triggered By：{self.env['github_event_name']}\n"
            f"Initial Run By：{self.env['github_actor']}\n"
            f"Initial Run By ID：{self.env['github_actor_id']}\n"
            f"Initiated Run By：{self.env['github_triggering_actor']}\n"
            f"Repository Name：{self.env['repository_name']}\n"
            f"Commit SHA：{self.env['github_sha']}\n"
            f"Workflow Name：{self.env['github_workflow']}\n"
            f"Workflow Number：{self.env['github_run_number']}\n"
            f"Workflow ID：{self.env['github_run_id']}\n"
            f"Beijing Time：{self.env['beijing_time']}"
        )

    def process(self, student_client):
        """
        处理成绩获取和通知生成
        :param student_client: 学生客户端对象
        :return: 包含通知信息的字典
        """
        result = {
            'title': "正方教务管理系统成绩推送",
            'content': "",
            'has_error': False,
            'error_content': [],
            'has_new_grades': False,
            'run_log': ""
        }

        # 获取个人信息
        info = get_user_info(student_client, output_type="info")
        integrated_info = get_user_info(student_client, output_type="integrated_info")

        # 加密个人信息
        info = encrypt_personal_info(info)
        integrated_info = encrypt_personal_info(integrated_info)

        # 错误处理
        if not info or not integrated_info:
            result['error_content'].append("个人信息为空")
            result['has_error'] = True
        elif "获取个人信息时出错" in info or "获取个人信息时出错" in integrated_info:
            result['error_content'].append("获取个人信息时出错")
            result['has_error'] = True

        # 获取成绩信息
        grade_data = get_grade(student_client, output_type="grade")
        integrated_grade_info = ""

        if not grade_data:
            integrated_grade_info = "------\n成绩信息：\n成绩为空\n------"
            result['run_log'] += "成绩为空\n"
        elif "获取成绩时出错" in grade_data:
            integrated_grade_info = "------\n成绩信息：\n获取成绩时出错\n------"
            result['error_content'].append("获取成绩时出错")
            result['has_error'] = True
        else:
            # 获取新增成绩
            new_grades = self._get_new_grades(grade_data)

            if new_grades:
                # 格式化新增成绩
                integrated_grade_info = self._format_grade_markdown(new_grades)
                result['has_new_grades'] = True
            else:
                last_submission_time = get_grade(student_client, output_type="last_submission_time")
                integrated_grade_info = f"------\n成绩信息：\n成绩未更新\n最近一次更新时间：{last_submission_time}\n------"

        # 工作流信息
        workflow_info = self._get_workflow_info()
        copyright_text = "Copyright © 2024 NianBroken. All rights reserved."
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 整合所有信息
        result['content'] = (
            f"{integrated_info}\n"
            f"{integrated_grade_info}\n"
            f"{workflow_info if self.env['github_actions'] else current_time}\n"
            f"{copyright_text}"
        )

        return result
