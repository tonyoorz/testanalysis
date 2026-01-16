# Selenium Cookie管理器

## 🎯 专注于Selenium自动化的Cookie管理

这是一个专门使用Selenium自动化浏览器获取Cookie的简化版本。

## 🚀 使用方法

### 1. 交互式菜单
```cmd
python selenium_cookie_manager.py
```

### 2. 快速命令
```cmd
# 检查Cookie状态
python selenium_cookie_manager.py --check

# 立即刷新Cookie
python selenium_cookie_manager.py --refresh

# 完整设置（安装依赖+刷新Cookie）
python selenium_cookie_manager.py --setup
```

## ⚙️ 首次设置

### 1. 准备登录信息文件
创建 `login_info.txt` 文件：
```json
{
    "username": "你的用户名",
    "password": "你的密码"
}
```

### 2. 安装依赖
```cmd
# 自动检查和安装（推荐）
python selenium_cookie_manager.py --setup

# 或手动安装
pip install selenium requests schedule webdriver-manager
```

### 3. Chrome浏览器和驱动
- **安装Chrome浏览器** (如果没有的话)
- **自动驱动管理** - 脚本会自动下载匹配的ChromeDriver

## 🔧 功能特点

- ✅ **Selenium自动化** - 模拟真实浏览器操作
- ✅ **智能元素查找** - 自动适配不同的登录页面结构
- ✅ **Cookie验证** - 自动验证获取的Cookie有效性
- ✅ **自动备份** - 每次更新前自动备份旧Cookie
- ✅ **定时刷新** - 支持设置定时任务自动刷新
- ✅ **详细日志** - 完整的操作日志记录

## 📋 工作流程

1. **启动Chrome浏览器** (可见或无头模式)
2. **访问登录页面** (https://octane-prod.bmwgroup.net)
3. **自动填写用户名密码** (从login_info.txt读取)
4. **点击登录按钮** (智能查找登录元素)
5. **等待登录完成** (检测URL变化)
6. **提取所有Cookie** (获取完整Cookie信息)
7. **验证Cookie有效性** (API测试)
8. **保存到文件** (覆盖cookie.txt)

## 🛠️ 故障排除

### 问题：Chrome驱动错误
**错误**: `Unable to obtain driver for chrome`
**解决方案**:
```cmd
# 方法1: 安装webdriver-manager（推荐）
pip install webdriver-manager

# 方法2: 手动下载ChromeDriver
# 1. 检查Chrome版本: chrome://version/
# 2. 下载对应版本: https://chromedriver.chromium.org/
# 3. 放入系统PATH中
```

### 问题：找不到登录元素
- 脚本会尝试多种选择器自动适配
- 检查网页结构是否有变化

### 问题：登录失败
- 检查用户名密码是否正确
- 确认网络连接正常
- 查看是否有验证码或额外验证步骤

### 问题：Cookie验证失败
- 可能需要手动登录一次完成额外验证
- 检查API接口是否有变化

## 📅 定时任务设置

### Windows任务计划
```cmd
schtasks /create /tn "Selenium_Cookie_Refresh" /tr "python selenium_cookie_manager.py --refresh" /sc daily /st 09:00
```

### 脚本内置定时器
```cmd
python selenium_cookie_manager.py
# 选择功能4 - 设置定时任务
```

## 📝 日志文件

运行日志保存在 `selenium_cookie_manager.log` 文件中，包含详细的操作记录。

---

**注意**: 这是一个自动化工具，请确保符合你所在组织的安全政策和使用条款。