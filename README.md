# 正方教务管理系统成绩推送

<img src="https://raw.githubusercontent.com/xwy231321/ZFCheckScores/main/img/7.jpg" style="zoom:60%;" />

## 简介

**使用本项目前：**

早晨睡醒看一遍教务系统、上厕所看一遍教务系统、刷牙看一遍教务系统、洗脸看一遍教务系统、吃早餐看一遍教务系统、吃午饭看一遍教务系统、睡午觉前看一遍教务系统、午觉醒来看一遍教务系统、出门前看一遍教务系统、吃晚饭看一遍教务系统、洗澡看一遍教务系统、睡觉之前看一遍教务系统

**使用本项目后：**

成绩更新后**自动发通知到微信** 以节省您宝贵的时间

本项目在由 [xwy231321](https://github.com/xwy231321/ZFCheckScores) 
修改的开源项目 [ZFCheckScores](https://github.com/NianBroken/ZFCheckScores/) 
的基础上添加推送教务系统通知而来，本项目将依照 [NianBroken](https://github.com/NianBroken) 
的开源许可证[Apache-2.0](https://www.apache.org/licenses/LICENSE-2.0 "Apache-2.0")进行修改与二次开源。
## 测试环境

正方教务管理系统 版本 V8.0、V9.0

如果你的教务系统页面与下图所示的页面**完全一致**或**几乎一致**，则代表你可以使用本项目。

<img src="https://raw.githubusercontent.com/xwy231321/ZFCheckScores/main/img/9.png" style="zoom:60%;" />

## 目前支持的功能

1. 主要功能

   1. 每隔 30 分钟自动检测一次成绩是否有更新，若有更新，将通过微信推送及时通知用户。

2. 相较于教务系统增加了哪些功能？

   1. 显示成绩提交时间，即成绩何时被录入教务系统。
   2. 显示成绩提交人姓名，即成绩由谁录入进教务系统。
   3. 成绩信息按时间降序排序，确保最新的成绩始终在最上方，提升用户查阅效率。
   4. 计算 `GPA`
   5. 计算百分制 `GPA`
   6. 对于没有分数仅有级别的成绩，例如”及格、良好、优秀“，可以强制显示数字分数。
   7. 显示未公布成绩的课程，即已选课但尚未出成绩的课程。

## 使用方法一：GitHub Actions

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
sudo docker run -dit -e URL=<你所在大学的教务url> -e USERNAME=<你的学号> -e PASSWORD=<你的密码> -e TOKEN=<你的token> zfcheckscores
```
注1： `sudo`命令用于在Ubuntu等Linux发行版中使用管理员权限运行命令，管理员账户则不需要此命令。  

注2： docker容器中环境变量信息使用明文存储，因此请确保服务器信息安全！

## 程序逻辑

1. 清空文件 B 中的内容
2. 将文件 A 中的内容写入到文件 B
3. 清空文件 A 中的内容
4. 将获取到的成绩进行 MD5 加密
5. 将加密后的成绩写入到文件 A
6. 比对文件 A 与文件 B 的内容是否一致
7. 若一致则表示成绩未更新，若不一致则表示成绩已更新

_若是第一次运行程序，上述步骤会执行两遍_

## 许可证

`Copyright © 2024 NianBroken. All rights reserved.`

本项目采用 [Apache-2.0](https://www.apache.org/licenses/LICENSE-2.0 "Apache-2.0") 许可证。简而言之，你可以自由使用、修改和分享本项目的代码，但前提是在其衍生作品中必须保留原始许可证和版权信息，并且必须以相同的许可证发布所有修改过的代码。

## 特别感谢

[openschoolcn/zfn_api](https://github.com/openschoolcn/zfn_api "openschoolcn/zfn_api")

[https://github.com/NianBroken/ZFCheckScores](https://github.com/NianBroken/ZFCheckScores)

[https://github.com/xwy231321/ZFCheckScores](https://github.com/xwy231321/ZFCheckScores)
## 其他

欢迎提交 `Issues` 和 `Pull requests`