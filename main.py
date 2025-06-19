# 必要的依赖库
from scripts.user_login import login
from src.utils import get_env
from src.grade_processor import GradeProcessor

from scripts.get_message import get_message
from src.message_processor import MessageProcessor
from src.push_message import PushMessage
def main():
    #获取环境变量
    env = get_env()
    #定义成绩获取类
    grade_processor = GradeProcessor(env)
    #调用教务系统api
    student_client = login(env["url"], env["username"], env["password"])
    #获取增量成绩
    result = grade_processor.process(student_client)
    print("成绩更新推送",PushMessage(env,result).check_message())
    result = MessageProcessor(env).process(student_client)
    print("通知推送",PushMessage(env,result).check_message())

if __name__ == "__main__":
    main()
