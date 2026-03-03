# PyPI 镜像源配置

## ✅ 已配置的镜像源

**清华大学镜像源：** `https://pypi.tuna.tsinghua.edu.cn/simple/`

## 📁 配置文件位置

### 1. 全局配置（所有 Python 项目）
**位置：** `~/.config/pip/pip.conf`

```ini
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple/
trusted-host = pypi.tuna.tsinghua.edu.cn

[install]
timeout = 60
```

### 2. 项目虚拟环境配置
**位置：** `/mnt/f/latency_project/.venv/pip.conf`

```ini
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple/
trusted-host = pypi.tuna.tsinghua.edu.cn

[install]
timeout = 60
```

## 🔍 验证配置

```bash
# 查看当前 pip 配置
pip config list

# 测试下载速度（应该显示清华源）
pip install --dry-run requests
```

## 📦 其他常用镜像源

如果需要切换到其他镜像源：

### 阿里云
```ini
[global]
index-url = https://mirrors.aliyun.com/pypi/simple/
trusted-host = mirrors.aliyun.com
```

### 中国科技大学
```ini
[global]
index-url = https://pypi.mirrors.ustc.edu.cn/simple/
trusted-host = pypi.mirrors.ustc.edu.cn
```

### 豆瓣
```ini
[global]
index-url = https://pypi.douban.com/simple/
trusted-host = pypi.douban.com
```

## ⚙️ 临时使用镜像源

```bash
# 单次安装使用镜像源
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple/ package_name
```

## 🚀 加速效果对比

| 源 | 位置 | 速度 |
|------|------|------|
| PyPI 官方 | 国外 | 🐢 慢 |
| 清华大学 | 北京 | 🚀 快 |
| 阿里云 | 杭州 | 🚀 快 |
| 中科大 | 合肥 | 🚀 快 |

**预计加速比：** 5-20 倍
