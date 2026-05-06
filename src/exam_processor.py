import hashlib
import json
import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple


APP_TIMEZONE = timezone(timedelta(hours=8), "Asia/Shanghai")


class ExamProcessor:
    """处理考试安排的获取、存储和增量通知。"""

    def __init__(self, env: Dict[str, Any]):
        self.env = env
        self.data_dir = "data"
        os.makedirs(self.data_dir, exist_ok=True)
        self.exam_file = os.path.join(self.data_dir, "exam_records.json")
        self._init_files()

    def _init_files(self):
        if not os.path.exists(self.exam_file):
            self._write_json_file(self.exam_file, [])

    def _write_json_file(self, path: str, data: Any):
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logging.error(f"写入文件 {path} 失败: {str(e)}")
            with open(path, "w", encoding="utf-8") as f:
                f.write("[]")

    def _read_json_file(self, path: str) -> Any:
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            logging.warning(f"文件 {path} 格式错误，返回空列表")
            return []
        except Exception as e:
            logging.error(f"读取文件 {path} 失败: {str(e)}")
            return []

    def _get_exam_query(self) -> Tuple[int, int]:
        env_year = self.env.get("exam_year")
        env_term = self.env.get("exam_term")
        now = datetime.now(APP_TIMEZONE)

        if env_year:
            year = int(env_year)
        else:
            year = now.year if now.month >= 9 else now.year - 1

        # 0 表示查询整个学年；用户可配置 1 或 2 缩小到指定学期。
        term = int(env_term) if env_term not in (None, "") else 0
        if term not in (0, 1, 2):
            raise ValueError("EXAM_TERM 必须是 0、1 或 2")

        return year, term

    def _format_query_name(self, year: int, term: int) -> str:
        term_name = "全年" if term == 0 else f"第{term}学期"
        return f"{year}-{year + 1}学年{term_name}"

    def _sanitize_exam(self, exam: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "course_id": exam.get("course_id"),
            "title": exam.get("title"),
            "time": exam.get("time"),
            "location": exam.get("location"),
            "campus": exam.get("xq"),
            "seat": exam.get("zwh"),
            "exam_name": exam.get("exam_name"),
            "teacher": exam.get("teacher"),
            "class_name": exam.get("class_name"),
            "college": exam.get("kkxy"),
            "credit": exam.get("credit"),
            "exam_method": exam.get("ksfs"),
            "paper_id": exam.get("sjbh"),
            "remark": exam.get("bz"),
            "retake_flag": exam.get("cxbj"),
        }

    def _get_exam_key(self, exam: Dict[str, Any]) -> str:
        content = {
            "course_id": exam.get("course_id"),
            "title": exam.get("title"),
            "exam_name": exam.get("exam_name"),
            "teacher": exam.get("teacher"),
            "class_name": exam.get("class_name"),
            "paper_id": exam.get("paper_id"),
            "retake_flag": exam.get("retake_flag"),
        }
        raw = json.dumps(content, ensure_ascii=False, sort_keys=True)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def _get_exam_detail_id(self, exam: Dict[str, Any]) -> str:
        content = {
            "course_id": exam.get("course_id"),
            "title": exam.get("title"),
            "time": exam.get("time"),
            "location": exam.get("location"),
            "seat": exam.get("seat"),
            "exam_name": exam.get("exam_name"),
            "paper_id": exam.get("paper_id"),
        }
        raw = json.dumps(content, ensure_ascii=False, sort_keys=True)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def _get_exam_changes(self, current_exams: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        sanitized_exams = [self._sanitize_exam(exam) for exam in current_exams]
        old_exams = self._read_json_file(self.exam_file)

        old_by_key = {self._get_exam_key(exam): exam for exam in old_exams}
        current_by_key = {self._get_exam_key(exam): exam for exam in sanitized_exams}

        added = []
        changed = []
        removed = []

        for exam_key, exam in current_by_key.items():
            old_exam = old_by_key.get(exam_key)
            if old_exam is None:
                added.append(exam)
            elif self._get_exam_detail_id(exam) != self._get_exam_detail_id(old_exam):
                changed.append(exam)

        for exam_key, exam in old_by_key.items():
            if exam_key not in current_by_key:
                removed.append(exam)

        sanitized_exams.sort(key=lambda item: item.get("time") or "", reverse=True)
        self._write_json_file(self.exam_file, sanitized_exams[:100])

        return {
            "added": added,
            "changed": changed,
            "removed": removed,
        }

    def _format_exam_item_markdown(self, exam: Dict[str, Any]) -> str:
        markdown = (
            f"课程名称：{exam.get('title') or '未知课程'}\n"
            f"考试名称：{exam.get('exam_name') or '未知考试'}\n"
            f"考试时间：{exam.get('time') or '未知时间'}\n"
            f"考试地点：{exam.get('location') or '未知地点'}\n"
            f"校区：{exam.get('campus') or '未知校区'}\n"
            f"座位号：{exam.get('seat') or '未公布'}\n"
            f"考试方式：{exam.get('exam_method') or '未公布'}\n"
            f"任课教师：{exam.get('teacher') or '未公布'}\n"
        )
        if exam.get("remark"):
            markdown += f"备注：{exam['remark']}\n"
        return markdown

    def _format_exam_markdown(self, exam_changes: Dict[str, List[Dict[str, Any]]]) -> str:
        if not any(exam_changes.values()):
            return ""

        markdown = "------\n**考试安排更新**\n"

        sections = [
            ("added", "新增考试安排"),
            ("changed", "变更考试安排"),
            ("removed", "取消或移除考试安排"),
        ]
        for key, title in sections:
            exams = exam_changes.get(key, [])
            if not exams:
                continue
            markdown += f"{title}：\n"
            for exam in exams:
                markdown += self._format_exam_item_markdown(exam)
                markdown += "------\n"

        return markdown

    def _get_workflow_info(self) -> str:
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

    def process(self, student_client: Any) -> Optional[Dict[str, Any]]:
        if self.env.get("exam_push_enabled") is False:
            return None

        result = {
            "title": "正方教务管理系统考试通知",
            "content": "",
            "has_error": False,
            "error_content": [],
            "has_new": False,
            "run_log": "",
        }

        try:
            year, term = self._get_exam_query()
            query_name = self._format_query_name(year, term)
            exam_response = student_client.get_exam_schedule(year, term)

            if not exam_response:
                exam_content = f"------\n考试安排：\n{query_name} 考试响应为空\n------"
                result["run_log"] += "考试响应为空\n"
            elif exam_response.get("code") == 1005:
                exam_changes = self._get_exam_changes([])
                if any(exam_changes.values()):
                    exam_content = self._format_exam_markdown(exam_changes)
                    result["has_new"] = True
                    result["run_log"] += f"{query_name} 考试安排已清空\n"
                else:
                    exam_content = f"------\n考试安排：\n{query_name} 暂无考试安排\n------"
                    result["run_log"] += "考试安排为空\n"
            elif exam_response.get("code") != 1000:
                result["has_error"] = True
                result["error_content"].append(exam_response.get("msg", "获取考试安排失败"))
                exam_content = (
                    f"------\n考试安排：\n获取 {query_name} 考试安排失败："
                    f"{exam_response.get('msg', '未知错误')}\n------"
                )
            else:
                exam_data = exam_response.get("data", {}).get("courses", [])
                exam_changes = self._get_exam_changes(exam_data)
                if any(exam_changes.values()):
                    exam_content = self._format_exam_markdown(exam_changes)
                    result["has_new"] = True
                    result["run_log"] += (
                        f"发现 {len(exam_changes['added'])} 条新增、"
                        f"{len(exam_changes['changed'])} 条变更、"
                        f"{len(exam_changes['removed'])} 条取消或移除考试安排\n"
                    )
                else:
                    exam_content = (
                        f"------\n考试安排：\n{query_name} 考试安排未更新\n"
                        f"当前考试数量：{len(exam_data)}\n------"
                    )
                    result["run_log"] += "考试安排未更新\n"
        except Exception as e:
            logging.error(f"处理考试安排时出错: {str(e)}")
            result["has_error"] = True
            result["error_content"].append("处理考试安排时发生错误")
            exam_content = "------\n考试安排：\n获取考试安排时发生错误\n------"

        workflow_info = self._get_workflow_info()
        copyright_text = "Copyright © 2025 nhirsama.\n[关于](https://github.com/nhirsama/ZFGetMessage/)"
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        result["content"] = (
            f"{exam_content}\n"
            f"{workflow_info if self.env.get('github_actions', False) else current_time}\n"
            f"{copyright_text}"
        )

        return result
