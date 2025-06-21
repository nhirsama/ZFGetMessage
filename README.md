# 正方教务管理系统消息推送

<img src="https://raw.githubusercontent.com/xwy231321/ZFCheckScores/main/img/7.jpg" style="zoom:60%;" />

## 简介

**使用本项目前：**

早晨睡醒看一遍教务系统、上厕所看一遍教务系统、刷牙看一遍教务系统、洗脸看一遍教务系统、吃早餐看一遍教务系统、吃午饭看一遍教务系统、睡午觉前看一遍教务系统、午觉醒来看一遍教务系统、出门前看一遍教务系统、吃晚饭看一遍教务系统、洗澡看一遍教务系统、睡觉之前看一遍教务系统

**使用本项目后：**

教务有通知后**自动发通知到微信** 以节省您宝贵的时间

本项目在由 [xwy231321](https://github.com/xwy231321/ZFCheckScores) 
修改的开源项目 [ZFCheckScores](https://github.com/NianBroken/ZFCheckScores/) 
的基础上添加推送教务系统通知而来，本项目将依照 [NianBroken](https://github.com/NianBroken) 
的开源许可证[Apache-2.0](https://www.apache.org/licenses/LICENSE-2.0 "Apache-2.0")进行修改与二次开源。
## 测试环境
### 1.教务环境
正方教务管理系统 版本 V8.0、V9.0

如果你的教务系统页面与下图所示的页面**完全一致**或**几乎一致**，则代表你可以使用本项目。

<img src="https://raw.githubusercontent.com/xwy231321/ZFCheckScores/main/img/9.png" style="zoom:60%;" />

### 2.本地环境
操作系统: Linux Mint 22.1 Cinnamon  
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
   7. 增量更新, 除第一次为全量推送以外,只推送新增的信息。

   
## 使用方法一: podman容器(推荐)
`podman` 是一款完全兼容 Docker 的现代化容器,可以直接运行 Docker 项目.
### 1. 安装 podman 容器  
* 对于 Debian/Ubuntu 系列，一般：

  ```bash
  sudo apt update
  sudo apt install -y podman git
  ```
* 对于 RHEL/CentOS/Fedora 系列，一般：

  ```bash
  sudo dnf install -y podman git
  ```
* 确认安装成功：

  ```bash
  podman --version
  ```
### 2. Clone 此项目
```bash
git clone https://github.com/nhirsama/ZFCheckScores
```
然后创建 `ven.txt` 文件.
```bash
nano ven.txt
```
按照下面要求输入必要的信息.  
因必要信息是明文存储在服务器中,请保护好个人信息.
```txt
PASSWORD=修改为你的密码
# 若你使用其他的推送服务，请修改下面的PUSH_URL
PUSH_URL=https://push.showdoc.com.cn/server/api/push/
TOKEN=修改为你的推送token
URL=修改为你的教务url
# username 为你的教务登陆用户名，一般情况下为学号
USERNAME=修改为你的学号
```
### 3. 运行一键脚本
给脚本添加可执行权限,并运行一次.  
若前面配置完全正确,此时应该会给你推送两条信息.  
若没有收到推送信息,请查看 `run.log` 日志查找问题.

```bash
cd ZFGetMessage
chmod +x ./start.sh
./start
```
### 4. 使用 `Cron` 定时执行脚本任务
1. 编辑要运行脚本的用户的 crontab，例如以 root 或特定用户身份：

   ```bash
   crontab -e
   ```
   2. 添加：  
       假设 `path` 为脚本所在位置的绝对目录,若不知道可以使用```pwd```命令查看当前位置
      ```
      0 */3 * * * path/start.sh
      ```

       * 上述在每隔 3 小时的整点（0:00、3:00、6:00…）执行一次。
       * 日志已在脚本内重定向，无需在 cron 再加重定向。若希望将 cron 错误输出也记录，可修改为：

         ```
         0 */3 * * * path/start.sh >> path/cron.log 2>&1
         ```
       * 可以自行修改 cron 命令以自定义检测间隔时间。例如下面为每天九点整运行此项目。
         ``` cron
         0 9 * * * path/start.sh >> path/cron.log 2>&1
         ```
3. 保存后生效。可通过检查 `path/run.log` 或 `pathcron.log` 来确认执行情况。

## 使用方法二：Docker容器

### 1. 克隆本项目

在控制台中输入下列指令克隆该项目。  
```bash
git clone https://github.com/nhirsama/ZFCheckScores
```
### 2. 创建容器
输入下列指令以创建名为`zfcheckscores`的容器。  

```bash
cd ZFCheckScores
```
```bash
sudo docker build -t zfcheckscores .
```
### 3. 运行容器并设置环境变量
输入下列指令，并应将'<>'所引的内容改为正确内容。  
```bash
sudo docker run -dit -e URL=<你所在大学的教务url> -e USERNAME=<你的学号> -e PASSWORD=<你的密码> -e TOKEN=<你的token> -e PUSH=https://push.showdoc.com.cn/server/api/push/ zfcheckscores
```
注1： `sudo`命令用于在Ubuntu等Linux发行版中使用管理员权限运行命令，管理员账户则不需要此命令。  

注2： docker容器中环境变量信息使用明文存储，因此请确保服务器信息安全！


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


## 许可证 
`Copyright © 2025 nhirsama.`  
`Copyright © 2024 NianBroken. All rights reserved.`

本项目采用 [Apache-2.0](https://www.apache.org/licenses/LICENSE-2.0 "Apache-2.0") 许可证。简而言之，你可以自由使用、修改和分享本项目的代码，但前提是在其衍生作品中必须保留原始许可证和版权信息，并且必须以相同的许可证发布所有修改过的代码。

## 特别感谢

[openschoolcn/zfn_api](https://github.com/openschoolcn/zfn_api "openschoolcn/zfn_api")

[https://github.com/NianBroken/ZFCheckScores](https://github.com/NianBroken/ZFCheckScores)

[https://github.com/xwy231321/ZFCheckScores](https://github.com/xwy231321/ZFCheckScores)
## 其他

欢迎提交 `Issues` 和 `Pull requests`