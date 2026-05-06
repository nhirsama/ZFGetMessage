# 必要的依赖库
import traceback
from datetime import datetime, timedelta, timezone

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from scripts.user_login import login
from src.utils import get_env
from src.grade_processor import GradeProcessor

from src.exam_processor import ExamProcessor
from src.message_processor import MessageProcessor
from src.push_message import PushMessage


APP_TIMEZONE = timezone(timedelta(hours=8), "Asia/Shanghai")


def run_task(env, grade_processor):
    print(f"[{datetime.now(APP_TIMEZONE).strftime('%Y-%m-%d %H:%M:%S')}] 开始执行任务...")
    try:
        # 每次重新登录以保证 Session 有效
        student_client = login(env["url"], env["username"], env["password"])
        result = grade_processor.process(student_client)
        print("成绩更新推送", PushMessage(env, result).check_message())
        result = ExamProcessor(env).process(student_client)
        if result:
            print("考试通知推送", PushMessage(env, result).check_message())
        result = MessageProcessor(env).process(student_client)
        print("通知推送", PushMessage(env, result).check_message())
        return True
    except SystemExit as e:
        print(f"任务执行中断: {e}")
        return False
    except Exception as e:
        print(f"任务执行出错: {e}")
        traceback.print_exc()
        return False


def main():
    env = get_env()
    grade_processor = GradeProcessor(env)

    cron_exp = env.get("cron_expression")
    interval = env.get("run_interval")

    if cron_exp or interval:
        scheduler = BlockingScheduler(timezone=APP_TIMEZONE)

        if cron_exp:
            print(f"检测到 Cron 模式，表达式: {cron_exp}")
            try:
                trigger = CronTrigger.from_crontab(cron_exp, timezone=APP_TIMEZONE)
            except ValueError as e:
                print(f"Cron 表达式格式错误: {e}")
                return
        elif interval:
            try:
                interval_sec = int(interval)
                if interval_sec <= 0:
                    raise ValueError
                print(f"检测到循环模式，间隔: {interval_sec}秒")
                trigger = IntervalTrigger(seconds=interval_sec, timezone=APP_TIMEZONE)
            except ValueError:
                print("RUN_INTERVAL 格式错误，必须是大于 0 的秒数")
                return

        scheduler.add_job(
            run_task,
            trigger,
            args=[env, grade_processor],
            coalesce=True,
            max_instances=1,
        )

        # 启动时先执行一次，确保服务正常且用户能立即看到结果
        run_task(env, grade_processor)

        print("调度器已启动，等待下次触发...")
        try:
            scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            print("停止调度")
    else:
        if not run_task(env, grade_processor):
            raise SystemExit(1)


if __name__ == "__main__":
    main()
