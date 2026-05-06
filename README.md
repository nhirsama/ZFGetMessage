# 正方教务管理系统消息推送

<img src="https://raw.githubusercontent.com/xwy231321/ZFCheckScores/main/img/7.jpg" style="zoom:60%;" />

## 简介

**使用本项目前：**

早晨睡醒看一遍教务系统、上厕所看一遍教务系统、刷牙看一遍教务系统、洗脸看一遍教务系统、吃早餐看一遍教务系统、吃午饭看一遍教务系统、睡午觉前看一遍教务系统、午觉醒来看一遍教务系统、出门前看一遍教务系统、吃晚饭看一遍教务系统、洗澡看一遍教务系统、睡觉之前看一遍教务系统

**使用本项目后：**

教务有通知后**自动发通知到微信**以节省您宝贵的时间

## 测试环境
### 1.教务环境
正方教务管理系统 版本 V8.0、V9.0

如果你的教务系统页面与下图所示的页面**完全一致**或**几乎一致**，则代表你可以使用本项目。

<img src="https://raw.githubusercontent.com/xwy231321/ZFCheckScores/main/img/9.png" style="zoom:60%;" />

### 2.本地环境
操作系统: Arch Linux  
IDE: CLion 2025.1  
解释器: Python 3.12  

### 3.服务器环境
操作系统: Ubuntu 24.04 64位  
容器: podman version 4.9.3

## 目前支持的功能

1. 主要功能

   1. 每隔三小时自动检测一次教务是否有新通知，若有更新，将通过微信推送及时通知用户。

2. 相较于教务系统增加了哪些功能？

   1. 显示成绩提交时间，即成绩何时被录入教务系统。
   2. 显示成绩提交人姓名，即成绩由谁录入进教务系统。
   3. 计算 `GPA`
   4. 计算百分制 `GPA`
   5. 对于没有分数仅有级别的成绩，例如”及格、良好、优秀“，可以强制显示数字分数。
   6. 消息分类推送,分为`成绩推送`、`消息通知`两种。
   7. 考试安排变更推送。
   8. 增量更新, 除第一次为全量推送以外,只推送新增的信息。

   
## 使用方法一: docker-compose(推荐)
`docker-compose` 是管理容器化应用的最便捷方式，本项目已完美适配。
### 1. 安装 Docker 与 Docker Compose
请确保您的服务器已安装 Docker。
* 对于 Debian/Ubuntu 系列：
  ```bash
  sudo apt update
  sudo apt install -y docker.io docker-compose-v2 git
  ```
### 2. Clone 此项目
```bash
git clone https://github.com/nhirsama/ZFGetMessage
cd ZFGetMessage
```
然后创建 `env.txt` 文件并输入配置信息：
```bash
nano env.txt
```
配置示例（请保护好您的个人隐私信息）：
```txt
PASSWORD=修改为你的密码
# 若你使用其他的推送服务，请修改下面的PUSH_URL
PUSH_URL=https://push.showdoc.com.cn/server/api/push/
TOKEN=修改为你的推送token
URL=修改为你的教务url
# username 为你的教务登陆用户名，一般情况下为学号
USERNAME=修改为你的学号

# 调度配置：
# 如果设置了 CRON_EXPRESSION，程序将使用 Cron 逻辑调度（推荐）。
# 如果仅设置了 RUN_INTERVAL（秒），程序将使用简单的间隔循环。
# 示例：每 3 小时整点运行一次
# RUN_INTERVAL=10800
CRON_EXPRESSION="0 */3 * * *"

# 考试通知配置：
# 默认启用考试通知，并自动查询当前学年全年考试安排。
# 如需指定学年或学期，可取消下面注释；EXAM_TERM 可填 0（全年）、1、2。
# EXAM_YEAR=2025
# EXAM_TERM=0
# EXAM_PUSH_ENABLED=true
```
### 3. 运行容器
无需运行额外脚本，直接使用 Docker Compose 启动服务：
```bash
# 构建并后台运行
docker compose up -d --build
```
### 4. 查看日志
由于服务在后台运行，您可以随时通过以下命令查看实时运行日志：
```bash
docker compose logs -f
```

## 使用方法二: podman容器
`podman` 是一款完全兼容 Docker 的现代化容器。
### 1. 安装 podman 
```bash
sudo apt install -y podman git podman-compose
```
### 2. 配置与运行
配置方式与 `docker-compose` 完全一致。创建好 `env.txt` 后，直接运行：
```bash
# 使用 podman-compose (如果安装了)
podman-compose up -d --build

# 或者使用 podman 直接运行 (如果不使用 compose)
# 注意：这需要手动处理挂载和环境变量，建议安装 podman-compose
```


## 使用方法三：GitHub Actions

**注:此方法来自原存储库,重构时并未特意编写 GitHub Actions 相关内容,可能完全不可用.**

### 1. [Fork](https://github.com/xwy231321/ZFCheckScores/fork "Fork") 本仓库

`Fork` → `Create fork`

### 2. 开启 工作流读写权限

`Settings` → `Actions` → `General` → `Workflow permissions` →`Read and write permissions` →`Save`

### 3. 添加 Secrets

`Settings` → `Secrets and variables` → `Actions` → `Secrets` → `Repository secrets` → `New repository secret` → `Add secret`

> Name = Name，Secret = 例子

| Name     | 例子                      | 说明                                                                      |
|----------|-------------------------|-------------------------------------------------------------------------|
| URL      | 对应的教务管理系统url            | 教务系统地址                                                                  |
| USERNAME | 学号                      | 教务系统用户名                                                                 |
| PASSWORD | 对应的密码                   | 教务系统密码                                                                  |
| TOKEN    | "server/api/push/"后面的内容 | [Showdoc 的 token](https://push.showdoc.com.cn/#/push "Showdoc 的 token") |

### 4. 开启 Actions

`Actions` → `I understand my workflows, go ahead and enable them` → `CheckScores` → `Enable workflow`

### 5. 运行 程序

`Actions` → `CheckScores` → `Run workflow`

_若你的程序正常运行且未报错，那么在此之后，程序将会每隔 30 分钟自动检测一次成绩是否有更新_

_若你看不懂上述使用方法，你可以查看[详细使用方法](https://nianbroken.github.io/ZFCheckScores/ "详细使用方法")_
## 程序逻辑

1. 读取对应 json 文件中的内容
2. 通过 api 获取通知和成绩信息
3. 通过关键信息查找新增的通知
4. 修改 json 并推送

## 更新
 - 在 [2026年1月26日](https://github.com/nhirsama/ZFGetMessage/commit/de2ed15fa55cf37469d6287d818e7ee49a0f22e3) 的提交中优化了项目的运行方式，避免多次构建 docker 镜像导致项目占用空间快速膨胀。

 - 在 [2025年6月19日](https://github.com/nhirsama/ZFGetMessage/commit/0246abd99cd5980e1df87d73ba6f92f26a4d2989) 的提交中重构了主体模块的实现。  
本项目在由 [xwy231321](https://github.com/xwy231321/ZFCheckScores) 
修改的开源项目 [ZFCheckScores](https://github.com/NianBroken/ZFCheckScores/) 
的基础上添加教务系统通知推送而来，本项目将依照 [NianBroken](https://github.com/NianBroken) 
的开源许可证[Apache-2.0](https://www.apache.org/licenses/LICENSE-2.0 "Apache-2.0")进行修改与二次开源。

## 许可证 
`Copyright © 2025-2026 nhirsama.`  
`Copyright © 2024 NianBroken. All rights reserved.`

本项目采用 [Apache-2.0](https://www.apache.org/licenses/LICENSE-2.0 "Apache-2.0") 许可证。简而言之，你可以自由使用、修改和分享本项目的代码，但前提是在其衍生作品中必须保留原始许可证和版权信息，并且必须以相同的许可证发布所有修改过的代码。

## 特别感谢

[openschoolcn/zfn_api](https://github.com/openschoolcn/zfn_api "openschoolcn/zfn_api")

[https://github.com/NianBroken/ZFCheckScores](https://github.com/NianBroken/ZFCheckScores)

[https://github.com/xwy231321/ZFCheckScores](https://github.com/xwy231321/ZFCheckScores)
## 其他

欢迎提交 `Issues` 和 `Pull requests`
