# 安装指南

## 安装需求

Vank 需要比较新的Python和Python包管理器安装在你的电脑上
你可以通过以下命令检查你的版本(不要带上`>`符号)

```shell
> python --version
Python 3.8.2

> pip --version
pip 22.2.2 from /usr/local/lib/python3.8/site-packages/pip
```

如果你已经安装了这些软件包,则可以往下继续

## 安装Vank
### 创建虚拟环境

在安装`Vank`之前,我建议你先创建一个虚拟环境(virtual environment)

```shell
> mkdir mysite
> cd mysite
> python -m venv venv
```

这里你创建了一个文件夹叫做`mysite`,然后进入`mysite`并使用了
python的内置库[venv](https://docs.python.org/3.8/library/venv.html)创建了一个名为venv的虚拟环境
***
### 激活虚拟环境  

接下来你需要激活虚拟环境  
=== "Windows"
    ```shell
    > venv/Scripts/activate
    ```
=== "Mac OS"
    ```shell
    > source venv/bin/activate
    ```
***
### 安装  

你可以使用`pip`包管理器安装`vank`

```shell
> pip install vank
```
***
### 校验安装
你可以在命令行中输入`vank`查看Vank是否安装成功
```shell
> vank
The currently available commands are:
- init                     Initialize the project through this command
- subapp                   You can create a sub application through this command

You can view usage through python -m vank <command> -h
```