#!/usr/bin/env python3
"""
Selenium Cookie管理器
===================
专注于使用Selenium自动获取Cookie的简化版本

功能:
1. Selenium自动登录获取Cookie
2. Cookie验证和状态检查  
3. 定时刷新任务
4. 依赖检查和安装

使用方法:
    python selenium_cookie_manager.py                    # 显示菜单
    python selenium_cookie_manager.py --refresh          # 立即刷新
    python selenium_cookie_manager.py --check            # 检查状态
    python selenium_cookie_manager.py --setup            # 完整设置
"""

import json
import os
import sys
import time
import logging
import argparse
import subprocess
from datetime import datetime, timedelta
import urllib3

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 导入基础模块
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

# 检查可选模块
try:
    import schedule
    SCHEDULE_AVAILABLE = True
except ImportError:
    SCHEDULE_AVAILABLE = False

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.service import Service
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

# 检查webdriver-manager
try:
    from webdriver_manager.chrome import ChromeDriverManager
    WEBDRIVER_MANAGER_AVAILABLE = True
except ImportError:
    WEBDRIVER_MANAGER_AVAILABLE = False

# 配置常量
BASE_URL = "https://octane-prod.bmwgroup.net"
LOGIN_INFO_FILE = "login_info.txt"
COOKIE_FILE = "cookie.txt"
COOKIE_BACKUP_FILE = "cookie_backup.txt"
LOG_FILE = "selenium_cookie_manager.log"

def setup_logging():
    """设置日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

class SeleniumCookieManager:
    def __init__(self):
        self.login_info = None
        self.running = False
        setup_logging()
        
    def check_dependencies(self):
        """检查依赖"""
        print("=== 依赖检查 ===")
        
        deps = {
            "requests": REQUESTS_AVAILABLE,
            "selenium": SELENIUM_AVAILABLE,
            "webdriver-manager": WEBDRIVER_MANAGER_AVAILABLE,
            "schedule": SCHEDULE_AVAILABLE
        }
        
        all_ok = True
        for module, available in deps.items():
            status = "✓" if available else "✗"
            if module in ["requests", "selenium"]:
                required = "(必需)"
            elif module == "webdriver-manager":
                required = "(强烈推荐)"
            else:
                required = "(可选)"
            print(f"  {status} {module} {required}")
            if not available and module in ["requests", "selenium"]:
                all_ok = False
        
        return all_ok
    
    def install_dependencies(self):
        """自动安装依赖"""
        print("=== 安装依赖 ===")
        
        packages_to_install = []
        
        if not REQUESTS_AVAILABLE:
            packages_to_install.append("requests")
        if not SELENIUM_AVAILABLE:
            packages_to_install.append("selenium")
        if not WEBDRIVER_MANAGER_AVAILABLE:
            packages_to_install.append("webdriver-manager")
        if not SCHEDULE_AVAILABLE:
            packages_to_install.append("schedule")
            
        if packages_to_install:
            print(f"需要安装: {', '.join(packages_to_install)}")
            try:
                for package in packages_to_install:
                    print(f"安装 {package}...")
                    subprocess.run([sys.executable, "-m", "pip", "install", package], 
                                 check=True, capture_output=True)
                    print(f"✓ {package} 安装成功")
                print("\n请重新启动脚本以使用新安装的模块")
                return True
            except subprocess.CalledProcessError as e:
                print(f"✗ 安装失败: {e}")
                return False
        else:
            print("✓ 所有依赖已满足")
            return True
    
    def load_login_info(self):
        """加载登录信息"""
        try:
            if not os.path.exists(LOGIN_INFO_FILE):
                logging.error(f"登录信息文件 {LOGIN_INFO_FILE} 不存在")
                return False
                
            with open(LOGIN_INFO_FILE, 'r', encoding='utf-8') as f:
                self.login_info = json.load(f)
                
            if not self.login_info.get('username') or not self.login_info.get('password'):
                logging.error("登录信息文件中缺少用户名或密码")
                return False
                
            logging.info("成功加载登录信息")
            return True
            
        except Exception as e:
            logging.error(f"加载登录信息失败: {e}")
            return False
    
    def get_cookie_via_selenium(self):
        """使用Selenium自动获取Cookie"""
        if not SELENIUM_AVAILABLE:
            logging.error("Selenium模块不可用，请安装: pip install selenium")
            return None
            
        if not self.load_login_info():
            return None
        
        try:
            logging.info("启动浏览器进行自动登录...")
            
            # 配置Chrome选项
            chrome_options = Options()
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--disable-features=VizDisplayCompositor")
            chrome_options.add_argument("--ignore-certificate-errors")
            chrome_options.add_argument("--ignore-ssl-errors")
            chrome_options.add_argument("--allow-running-insecure-content")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            
            # 可选：无头模式（如果需要后台运行）
            # chrome_options.add_argument("--headless")
            
            # 尝试使用webdriver-manager自动管理驱动
            try:
                if WEBDRIVER_MANAGER_AVAILABLE:
                    from webdriver_manager.chrome import ChromeDriverManager
                    service = Service(ChromeDriverManager().install())
                    driver = webdriver.Chrome(service=service, options=chrome_options)
                    logging.info("使用webdriver-manager成功启动Chrome")
                else:
                    # 回退到系统PATH中的chromedriver
                    driver = webdriver.Chrome(options=chrome_options)
                    logging.info("使用系统PATH中的chromedriver启动Chrome")
            except Exception as driver_error:
                logging.error(f"Chrome启动失败: {driver_error}")
                # 提供解决方案
                print("\n🔧 Chrome驱动问题解决方案:")
                print("1. 安装webdriver-manager: pip install webdriver-manager")
                print("2. 或手动下载ChromeDriver:")
                print("   - 访问: https://chromedriver.chromium.org/")
                print("   - 下载对应Chrome版本的驱动")
                print("   - 将驱动放入系统PATH中")
                return None
            
            driver.set_page_load_timeout(30)
            
            try:
                # 访问登录页面
                logging.info(f"访问登录页面: {BASE_URL}")
                driver.get(BASE_URL)
                
                # 等待页面加载
                time.sleep(3)
                
                # 调试信息：检查当前页面
                current_url = driver.current_url
                page_title = driver.title
                logging.info(f"当前URL: {current_url}")
                logging.info(f"页面标题: {page_title}")
                
                # 检查是否被重定向到其他认证页面
                if "octane-prod.bmwgroup.net" not in current_url:
                    logging.warning(f"页面被重定向到: {current_url}")
                    logging.info("可能需要通过SSO或其他认证流程")
                
                # 保存页面截图用于调试
                try:
                    screenshot_path = "debug_login_page.png"
                    driver.save_screenshot(screenshot_path)
                    logging.info(f"页面截图已保存: {screenshot_path}")
                except:
                    pass
                
                # 查找用户名输入框（可能有多种可能的选择器）
                username_selectors = [
                    "input[name='username']",
                    "input[id='username']", 
                    "input[type='text']",
                    "#username",
                    ".username"
                ]
                
                username_field = None
                for selector in username_selectors:
                    try:
                        username_field = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                        )
                        logging.info(f"找到用户名输入框: {selector}")
                        break
                    except:
                        continue
                
                if not username_field:
                    logging.error("未找到用户名输入框")
                    return None
                
                # 输入用户名
                username_field.clear()
                username_field.send_keys(self.login_info['username'])
                logging.info("已输入用户名")
                
                # 查找密码输入框
                password_selectors = [
                    "input[name='password']",
                    "input[id='password']",
                    "input[type='password']",
                    "#password",
                    ".password"
                ]
                
                password_field = None
                for selector in password_selectors:
                    try:
                        password_field = driver.find_element(By.CSS_SELECTOR, selector)
                        logging.info(f"找到密码输入框: {selector}")
                        break
                    except:
                        continue
                
                if not password_field:
                    logging.error("未找到密码输入框")
                    return None
                
                # 输入密码
                password_field.clear()
                password_field.send_keys(self.login_info['password'])
                logging.info("已输入密码")
                
                # 查找登录按钮
                login_selectors = [
                    "button[type='submit']",
                    "input[type='submit']",
                    "button:contains('Login')",
                    "button:contains('Sign in')",
                    ".login-button",
                    "#login-button"
                ]
                
                login_button = None
                for selector in login_selectors:
                    try:
                        if ":contains(" in selector:
                            # 使用XPath处理包含文本的选择器
                            xpath = f"//button[contains(text(), 'Login') or contains(text(), 'Sign in')]"
                            login_button = driver.find_element(By.XPATH, xpath)
                        else:
                            login_button = driver.find_element(By.CSS_SELECTOR, selector)
                        logging.info(f"找到登录按钮: {selector}")
                        break
                    except:
                        continue
                
                if not login_button:
                    logging.error("未找到登录按钮")
                    return None
                
                # 点击登录按钮
                login_button.click()
                logging.info("已点击登录按钮")
                
                # 等待登录完成（等待URL变化或特定元素出现）
                try:
                    # 等待URL包含目标域名或出现登录成功的标志
                    WebDriverWait(driver, 30).until(
                        lambda d: "octane-prod.bmwgroup.net" in d.current_url and "/login" not in d.current_url.lower()
                    )
                    logging.info("登录成功")
                except:
                    logging.warning("登录状态不确定，继续尝试获取Cookie")
                
                # 等待额外时间确保Cookie设置完成
                time.sleep(5)
                
                # 获取所有Cookie
                cookies = driver.get_cookies()
                if not cookies:
                    logging.error("未获取到任何Cookie")
                    return None
                
                # 格式化Cookie字符串
                cookie_string = "; ".join([f"{cookie['name']}={cookie['value']}" for cookie in cookies])
                
                logging.info(f"成功获取Cookie，包含{len(cookies)}个条目")
                return cookie_string
                
            finally:
                driver.quit()
                logging.info("浏览器已关闭")
                
        except Exception as e:
            logging.error(f"Selenium获取Cookie失败: {e}")
            return None
    
    def save_cookie(self, cookie_string):
        """保存Cookie"""
        try:
            # 备份旧Cookie
            if os.path.exists(COOKIE_FILE):
                with open(COOKIE_FILE, 'r', encoding='utf-8') as f:
                    old_cookie = f.read().strip()
                if old_cookie:
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    backup_name = f"{COOKIE_BACKUP_FILE}.{timestamp}"
                    with open(backup_name, 'w', encoding='utf-8') as f:
                        f.write(old_cookie)
                    logging.info(f"已备份旧Cookie: {backup_name}")
            
            # 保存新Cookie
            with open(COOKIE_FILE, 'w', encoding='utf-8') as f:
                f.write(cookie_string)
            
            logging.info(f"Cookie已保存到: {COOKIE_FILE}")
            return True
            
        except Exception as e:
            logging.error(f"保存Cookie失败: {e}")
            return False
    
    def validate_cookie(self, cookie_string=None):
        """验证Cookie有效性"""
        if not REQUESTS_AVAILABLE:
            logging.error("需要requests模块进行验证")
            return False
            
        if not cookie_string:
            if os.path.exists(COOKIE_FILE):
                with open(COOKIE_FILE, 'r', encoding='utf-8') as f:
                    cookie_string = f.read().strip()
            else:
                logging.warning("没有找到Cookie文件")
                return False
        
        if not cookie_string:
            return False
            
        try:
            session = requests.Session()
            session.verify = False
            session.headers.update({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
                "Cookie": cookie_string
            })
            
            test_url = f"{BASE_URL}/api/shared_spaces/1002/workspaces/2001/defects"
            response = session.get(test_url, params={"limit": 1}, timeout=10)
            
            if response.status_code == 200:
                logging.info("Cookie验证成功")
                return True
            elif response.status_code == 401:
                logging.warning("Cookie已过期或无效")
                return False
            else:
                logging.warning(f"Cookie验证失败，状态码: {response.status_code}")
                return False
                
        except Exception as e:
            logging.error(f"Cookie验证出错: {e}")
            return False
    
    def check_cookie_status(self):
        """检查Cookie状态"""
        print("=== Cookie状态检查 ===")
        
        if not os.path.exists(COOKIE_FILE):
            print("✗ Cookie文件不存在")
            return False
        
        # 文件信息
        file_time = datetime.fromtimestamp(os.path.getmtime(COOKIE_FILE))
        time_diff = datetime.now() - file_time
        file_size = os.path.getsize(COOKIE_FILE)
        
        print(f"文件路径: {os.path.abspath(COOKIE_FILE)}")
        print(f"文件大小: {file_size} 字节")
        print(f"修改时间: {file_time}")
        print(f"距离现在: {time_diff}")
        
        # 验证有效性
        if self.validate_cookie():
            print("✓ Cookie状态: 有效")
            return True
        else:
            print("✗ Cookie状态: 无效")
            return False
    
    def refresh_cookie(self):
        """刷新Cookie"""
        print("=== Selenium自动获取Cookie ===")
        
        # 检查依赖
        if not SELENIUM_AVAILABLE:
            print("✗ Selenium模块不可用")
            print("请安装: pip install selenium")
            return False
        
        if not self.load_login_info():
            print("✗ 需要login_info.txt文件包含用户名和密码")
            print("文件格式:")
            print('{"username": "your_username", "password": "your_password"}')
            return False
        
        # 先检查当前Cookie是否有效
        if self.validate_cookie():
            print("当前Cookie仍然有效，是否强制刷新？(y/N): ", end="")
            if input().lower() != 'y':
                print("取消刷新")
                return True
        
        # 使用Selenium获取新Cookie
        new_cookie = self.get_cookie_via_selenium()
        
        if not new_cookie:
            print("✗ 获取Cookie失败")
            return False
        
        # 验证新Cookie
        if not self.validate_cookie(new_cookie):
            print("✗ 新Cookie验证失败")
            return False
        
        # 保存新Cookie
        if self.save_cookie(new_cookie):
            print("✓ Cookie刷新成功")
            return True
        else:
            print("✗ Cookie保存失败")
            return False
    
    def setup_automation(self):
        """设置自动化定时任务"""
        print("=== 设置定时刷新 ===")
        
        if not SCHEDULE_AVAILABLE:
            print("需要安装schedule模块: pip install schedule")
            return False
        
        print("设置定时刷新任务...")
        print("注意: 这将启动一个持续运行的进程")
        print("建议使用系统任务计划程序代替")
        
        import schedule
        
        def scheduled_refresh():
            print(f"\n[{datetime.now()}] 定时刷新开始...")
            if self.refresh_cookie():
                print("定时刷新成功")
            else:
                print("定时刷新失败")
        
        # 设置定时任务
        schedule.every().day.at("09:00").do(scheduled_refresh)
        schedule.every().day.at("15:00").do(scheduled_refresh)
        
        print("已设置定时任务: 每天9:00和15:00")
        print("按Ctrl+C停止")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)
        except KeyboardInterrupt:
            print("\n定时任务已停止")
            return True
    
    def test_connection(self):
        """测试网络连接"""
        print("=== 网络连接测试 ===")
        
        if not REQUESTS_AVAILABLE:
            print("需要requests模块")
            return False
        
        try:
            print(f"测试连接: {BASE_URL}")
            response = requests.get(BASE_URL, timeout=10, verify=False, allow_redirects=True)
            print(f"✓ HTTP状态码: {response.status_code}")
            print(f"✓ 最终URL: {response.url}")
            print(f"✓ 响应大小: {len(response.content)} 字节")
            
            # 检查是否被重定向
            if response.url != BASE_URL:
                print(f"⚠️  页面被重定向到: {response.url}")
                if "login" in response.url.lower() or "auth" in response.url.lower():
                    print("✓ 这是正常的，需要登录认证")
                else:
                    print("⚠️  可能需要VPN或内网访问")
            
            # 检查页面内容
            content = response.text.lower()
            if "login" in content or "username" in content or "password" in content:
                print("✓ 发现登录表单，网站可访问")
                return True
            elif "unauthorized" in content or "access denied" in content:
                print("✗ 访问被拒绝，可能需要VPN或权限")
                return False
            else:
                print("⚠️  页面内容异常，请检查网络环境")
                return False
                
        except requests.exceptions.ConnectTimeout:
            print("✗ 连接超时，请检查网络连接")
            return False
        except requests.exceptions.ConnectionError as e:
            print(f"✗ 连接失败: {e}")
            print("可能原因:")
            print("  1. 需要连接BMW内网VPN")
            print("  2. 网络防火墙阻止访问")
            print("  3. 代理设置问题")
            return False
        except Exception as e:
            print(f"✗ 其他错误: {e}")
            return False
    
    def show_main_menu(self):
        """显示主菜单"""
        while True:
            print("\n" + "="*50)
            print("        Selenium Cookie管理器")
            print("="*50)
            print("1. 检查Cookie状态")
            print("2. 刷新Cookie (Selenium自动)")
            print("3. 检查/安装依赖")
            print("4. 设置定时任务")
            print("5. 测试网络连接")
            print("0. 退出")
            print("-"*50)
            
            choice = input("请选择功能 (0-5): ").strip()
            
            if choice == "0":
                print("再见!")
                break
            elif choice == "1":
                self.check_cookie_status()
            elif choice == "2":
                self.refresh_cookie()
            elif choice == "3":
                self.check_dependencies()
                if input("\n是否安装缺失的依赖？(y/N): ").lower() == 'y':
                    self.install_dependencies()
            elif choice == "4":
                self.setup_automation()
            elif choice == "5":
                self.test_connection()
            else:
                print("无效选择")
            
            input("\n按回车继续...")

def main():
    parser = argparse.ArgumentParser(description="Selenium Cookie管理器")
    parser.add_argument("--refresh", action="store_true", help="立即刷新Cookie")
    parser.add_argument("--check", action="store_true", help="检查Cookie状态")
    parser.add_argument("--setup", action="store_true", help="完整设置向导")
    
    args = parser.parse_args()
    
    manager = SeleniumCookieManager()
    
    # 快速模式
    if args.refresh:
        success = manager.refresh_cookie()
        sys.exit(0 if success else 1)
    elif args.check:
        success = manager.check_cookie_status()
        sys.exit(0 if success else 1)
    elif args.setup:
        manager.check_dependencies()
        manager.install_dependencies()
        manager.refresh_cookie()
        sys.exit(0)
    else:
        # 交互模式
        manager.show_main_menu()

if __name__ == "__main__":
    main()