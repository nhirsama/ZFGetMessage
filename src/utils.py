import hashlib
import os

def encrypt_personal_info(info_str):
    """
    加密个人信息字符串
    保留名字的第一个字、班级汉字部分，其他部分用星号替换
    """
    lines = info_str.split('\n')
    encrypted_lines = []

    for line in lines:
        # 跳过空行
        if not line.strip():
            encrypted_lines.append(line)
            continue

        # 提取标签和值
        parts = line.split('：', 1)
        if len(parts) < 2:
            encrypted_lines.append(line)
            continue

        label, value = parts

        # 根据标签类型进行不同的加密处理
        if label == '姓名':
            # 保留第一个字，其余替换为星号
            if value:
                encrypted_value = value[0] + '*' * (len(value) - 1)
            else:
                encrypted_value = '***'
            encrypted_lines.append(f"{label}：{encrypted_value}")

        elif label == '班级':
            # 只保留汉字部分，非汉字替换为星号
            encrypted_value = ''.join(
                char if '\u4e00' <= char <= '\u9fff' else '*'
                for char in value
            )
            encrypted_lines.append(f"{label}：{encrypted_value}")

        elif label == '学号':
            # 学号全部替换为星号
            encrypted_value = '*' * len(value)
            encrypted_lines.append(f"{label}：{encrypted_value}")

        else:
            # 其他信息原样保留
            encrypted_lines.append(line)

    return '\n'.join(encrypted_lines)

def md5_encrypt(text):
    """MD5加密文本"""
    return hashlib.md5(text.encode('utf-8')).hexdigest()


class EnvVarMissingError(Exception):
    """当必需环境变量缺失时抛出此异常。"""
    pass


def get_env():
    env = {}
    keys = [
        "FORCE_PUSH_MESSAGE",
        "GITHUB_ACTIONS",
        "URL",
        "PUSH_URL",
        "USERNAME",
        "PASSWORD",
        "TOKEN",
        "GITHUB_REF_NAME",
        "GITHUB_EVENT_NAME",
        "GITHUB_ACTOR",
        "GITHUB_ACTOR_ID",
        "GITHUB_TRIGGERING_ACTOR",
        "REPOSITORY_NAME",
        "GITHUB_SHA",
        "GITHUB_WORKFLOW",
        "GITHUB_RUN_NUMBER",
        "GITHUB_RUN_ID",
        "BEIJING_TIME",
        "GITHUB_STEP_SUMMARY",
        "FORCE_PUSH_MESSAGE",
    ]
    for key in keys:
        val = os.getenv(key)
        if val is None:
            if key in ("URL", "USERNAME", "PASSWORD", "TOKEN"):
                # 对于这些关键字段缺失时，抛出异常
                raise EnvVarMissingError(f"缺少必需环境变量: {key}")
            env[key.lower()] = None  # 缺失时设为空
        else:
            # 将换将变量中的布尔相应转换为bool值，否则返回原始值。
            def if_bool(val: str):
                true_val = ['ok', 'true', 'yes']
                false_val = ['no', 'false']
                if val.lower() in true_val:
                    return True
                elif val.lower in false_val:
                    return False
                else:
                    return val

            val = if_bool(val)
            env[key.lower()] = val
    return env