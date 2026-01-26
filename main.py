# 必要的依赖库
import traceback
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from scripts.user_login import login
from src.utils import get_env
from src.grade_processor import GradeProcessor

from scripts.get_message import get_message
from src.message_processor import MessageProcessor
from src.push_message import PushMessage

def run_task(env, grade_processor):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始执行任务...")
    try:
        #调用教务系统api (每次重新登录以保证Session有效)
        student_client = login(env["url"], env["username"], env["password"])
        #获取增量成绩
        result = grade_processor.process(student_client)
        print("成绩更新推送",PushMessage(env,result).check_message())
        result = MessageProcessor(env).process(student_client)
        print("通知推送",PushMessage(env,result).check_message())
    except Exception as e:
        print(f"任务执行出错: {e}")
        traceback.print_exc()

def main():
    #获取环境变量
    env = get_env()
    #定义成绩获取类
    grade_processor = GradeProcessor(env)
    
    cron_exp = env.get("cron_expression")
    interval = env.get("run_interval")

    if cron_exp or interval:
        # 使用 BlockingScheduler，默认时区设为上海
        # 注意：Docker 容器内可能需要设置时区或安装 tzdata，这里由 APScheduler 处理 Python 层面的时区
        scheduler = BlockingScheduler(timezone="Asia/Shanghai")
        
        # 启动时先执行一次，确保服务正常且用户能立即看到结果
        run_task(env, grade_processor)

        if cron_exp:
            print(f"检测到 Cron 模式，表达式: {cron_exp}")
            try:
                trigger = CronTrigger.from_crontab(cron_exp)
                scheduler.add_job(run_task, trigger, args=[env, grade_processor])
            except ValueError as e:
                print(f"Cron 表达式格式错误: {e}")
                return
        elif interval:
            try:
                interval_sec = int(interval)
                print(f"检测到循环模式，间隔: {interval_sec}秒")
                trigger = IntervalTrigger(seconds=interval_sec)
                scheduler.add_job(run_task, trigger, args=[env, grade_processor])
            except ValueError:
                print("RUN_INTERVAL 格式错误，仅执行一次")
                return

        print(f"调度器已启动，等待下次触发...")
        try:
            scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            print("停止调度")
    else:
        # 无任何调度配置，仅运行一次
        run_task(env, grade_processor)

if __name__ == "__main__":
    main()
