# 安装指南

---

## 设置虚拟环境

使用虚拟环境非常重要，原因如下:

- 依赖隔离: 不同的项目可能需要不同版本的库和依赖。虚拟环境为每个项目创建独立的包管理环境，从而防止依赖项冲突。

- 简化的项目管理: 虚拟环境将每个项目的依赖项列表和配置分开，使开发、测试和部署更加容易。

- 避免系统污染: 在虚拟环境中安装软件包可防止对全局Python环境进行更改，避免全局软件包版本更改引起的问题。

- 可移植性: 虚拟环境使复制项目环境变得容易。通过导出和导入依赖关系列表，您可以确保在不同的开发和生产环境中保持一致的操作。

总之，虚拟环境通过隔离和管理依赖关系，使Python开发更加高效、可靠和可管理。

### 创建项目目录

```shell
$ mkdir visapi_project
$ cd visapi_project
```

### 创建虚拟环境

```shell
$ python -m venv .venv
```

### 激活虚拟环境

:::code-group

```shell [Windows]
$ .venv/Scripts/activate
```

```shell [MacOS]
$ source .venv/bin/activate
```

:::
---

## 安装VisAPI

```shell
$ pip install visapi
```

---


