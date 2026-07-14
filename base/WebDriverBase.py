import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    ElementNotVisibleException,
    ElementNotInteractableException,
    StaleElementReferenceException,
    WebDriverException
)
from utils.yaml_util import YamlUtil
from utils.log_util import logger


class WebDriverBase:
    """
    WebDriver基础操作封装类
    提供浏览器初始化、显式等待、元素通用操作、窗口管理、关闭驱动等功能
    无业务逻辑，仅提供通用能力
    """

    def __init__(self):
        """
        初始化WebDriver基础类
        加载浏览器配置，准备初始化驱动
        """
        self.driver = None
        self.browser_config = YamlUtil.read_conf("browser.yaml")
        self.env_config = YamlUtil.read_conf("env.yaml")
        self._wait = None

    def _get_wait(self, timeout=None):
        """
        获取显式等待对象

        Args:
            timeout (int): 超时时间，默认为配置文件中的explicit_wait值

        Returns:
            WebDriverWait: 显式等待对象
        """
        if not self.driver:
            logger.error("WebDriver未初始化")
            raise WebDriverException("WebDriver未初始化")

        wait_time = timeout or self.browser_config.get("explicit_wait", 15)
        poll_frequency = self.browser_config.get("poll_frequency", 500) / 1000

        self._wait = WebDriverWait(
            self.driver,
            timeout=wait_time,
            poll_frequency=poll_frequency,
            ignored_exceptions=[
                NoSuchElementException,
                StaleElementReferenceException
            ]
        )
        return self._wait

    def init_driver(self):
        """
        初始化浏览器驱动
        根据配置文件选择本地驱动或webdriver-manager自动下载
        """
        try:
            browser_type = self.browser_config.get("browser", "chrome")
            driver_mode = self.browser_config.get("driver_mode", "local")

            if browser_type.lower() != "chrome":
                logger.warning(f"当前仅支持Chrome浏览器，配置文件中指定为: {browser_type}")

            options = webdriver.ChromeOptions()

            # 页面加载策略
            load_strategy = self.browser_config.get("load_strategy", "normal")
            options.page_load_strategy = load_strategy

            # 无头模式
            if self.browser_config.get("headless", False):
                options.add_argument("--headless=new")
                options.add_argument("--disable-gpu")
                logger.info("已启用无头模式")

            # 禁用图片加载（加速）
            if self.browser_config.get("disable_images", False):
                prefs = {"profile.managed_default_content_settings.images": 2}
                options.add_experimental_option("prefs", prefs)
                logger.info("已禁用图片加载")

            # 浏览器语言
            language = self.browser_config.get("language", "zh-CN")
            options.add_argument(f"--lang={language}")

            # 用户代理
            user_agent = self.browser_config.get("user_agent", "")
            if user_agent:
                options.add_argument(f"--user-agent={user_agent}")

            # 下载路径
            download_path = self.browser_config.get("download_path", "")
            if download_path:
                prefs = {"download.default_directory": download_path}
                options.add_experimental_option("prefs", prefs)

            # 其他通用配置
            options.add_argument("--start-maximized")
            options.add_argument("--disable-infobars")
            options.add_argument("--disable-extensions")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")

            # 根据驱动模式初始化
            if driver_mode.lower() == "local":
                # 使用本地指定驱动
                driver_path = self.browser_config.get("driver_path")
                if not driver_path:
                    logger.error("本地驱动模式下，driver_path配置为空")
                    raise ValueError("本地驱动模式下，driver_path配置为空")

                logger.info(f"使用本地驱动: {driver_path}")
                service = Service(driver_path)
                self.driver = webdriver.Chrome(
                    service=service,
                    options=options
                )
            else:
                # 使用webdriver-manager自动下载驱动
                logger.info("使用webdriver-manager自动下载驱动")
                from webdriver_manager.chrome import ChromeDriverManager
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(
                    service=service,
                    options=options
                )

            # 设置页面加载超时
            page_load_timeout = self.browser_config.get("page_load_timeout", 30)
            self.driver.set_page_load_timeout(page_load_timeout)

            # 设置隐式等待
            implicit_wait = self.browser_config.get("implicit_wait", 10)
            self.driver.implicitly_wait(implicit_wait)

            logger.info("WebDriver初始化成功")

        except Exception as e:
            logger.error(f"WebDriver初始化失败: {str(e)}", exc_info=True)
            raise

    def open_url(self, url=None):
        """
        打开指定URL

        Args:
            url (str): 要打开的URL，默认为配置文件中的base_url
        """
        try:
            target_url = url or self.env_config.get("base_url", "")
            if not target_url:
                logger.error("URL为空，请检查配置文件")
                raise ValueError("URL为空，请检查配置文件")

            logger.info(f"打开URL: {target_url}")
            self.driver.get(target_url)

        except Exception as e:
            logger.error(f"打开URL失败: {str(e)}", exc_info=True)
            raise

    def wait_element(self, locator, timeout=None):
        """
        显式等待元素可见

        Args:
            locator (tuple): 元素定位器，格式为(By.ID, "element_id")
            timeout (int): 超时时间（可选）

        Returns:
            WebElement: 定位到的元素

        Raises:
            TimeoutException: 超时未找到元素
        """
        try:
            logger.info(f"等待元素可见: {locator}")
            wait = self._get_wait(timeout)
            element = wait.until(EC.visibility_of_element_located(locator))
            logger.info(f"元素已找到: {locator}")
            return element

        except TimeoutException:
            logger.error(f"等待元素超时: {locator}")
            raise
        except Exception as e:
            logger.error(f"等待元素失败: {str(e)}", exc_info=True)
            raise

    def wait_element_clickable(self, locator, timeout=None):
        """
        显式等待元素可点击

        Args:
            locator (tuple): 元素定位器
            timeout (int): 超时时间（可选）

        Returns:
            WebElement: 定位到的元素

        Raises:
            TimeoutException: 超时元素不可点击
        """
        try:
            logger.info(f"等待元素可点击: {locator}")
            wait = self._get_wait(timeout)
            element = wait.until(EC.element_to_be_clickable(locator))
            logger.info(f"元素可点击: {locator}")
            return element

        except TimeoutException:
            logger.error(f"等待元素可点击超时: {locator}")
            raise
        except Exception as e:
            logger.error(f"等待元素可点击失败: {str(e)}", exc_info=True)
            raise

    def wait_element_invisible(self, locator, timeout=None):
        """
        显式等待元素不可见

        Args:
            locator (tuple): 元素定位器
            timeout (int): 超时时间（可选）

        Returns:
            bool: 元素不可见返回True

        Raises:
            TimeoutException: 超时元素仍可见
        """
        try:
            logger.info(f"等待元素不可见: {locator}")
            wait = self._get_wait(timeout)
            result = wait.until(EC.invisibility_of_element_located(locator))
            logger.info(f"元素已不可见: {locator}")
            return result

        except TimeoutException:
            logger.error(f"等待元素不可见超时: {locator}")
            raise
        except Exception as e:
            logger.error(f"等待元素不可见失败: {str(e)}", exc_info=True)
            raise

    def find_element(self, locator):
        """
        查找单个元素

        Args:
            locator (tuple): 元素定位器

        Returns:
            WebElement: 定位到的元素

        Raises:
            NoSuchElementException: 未找到元素
        """
        try:
            logger.debug(f"查找元素: {locator}")
            element = self.driver.find_element(*locator)
            return element

        except NoSuchElementException:
            logger.error(f"未找到元素: {locator}")
            raise
        except Exception as e:
            logger.error(f"查找元素失败: {str(e)}", exc_info=True)
            raise

    def find_elements(self, locator):
        """
        查找多个元素

        Args:
            locator (tuple): 元素定位器

        Returns:
            list[WebElement]: 定位到的元素列表
        """
        try:
            logger.debug(f"查找元素列表: {locator}")
            elements = self.driver.find_elements(*locator)
            logger.info(f"找到元素数量: {len(elements)}")
            return elements

        except Exception as e:
            logger.error(f"查找元素列表失败: {str(e)}", exc_info=True)
            raise

    def click(self, locator, timeout=None):
        """
        点击元素

        Args:
            locator (tuple): 元素定位器
            timeout (int): 等待超时时间（可选）
        """
        try:
            element = self.wait_element_clickable(locator, timeout)
            logger.info(f"点击元素: {locator}")
            element.click()

        except Exception as e:
            logger.error(f"点击元素失败: {str(e)}", exc_info=True)
            raise

    def send_keys(self, locator, text, timeout=None, clear_first=True):
        """
        向输入框发送文本

        Args:
            locator (tuple): 元素定位器
            text (str): 要输入的文本
            timeout (int): 等待超时时间（可选）
            clear_first (bool): 是否先清空输入框，默认为True
        """
        try:
            element = self.wait_element(locator, timeout)

            if clear_first:
                element.clear()
                logger.debug(f"已清空输入框: {locator}")

            logger.info(f"向元素输入文本: {locator}, 文本: {text}")
            element.send_keys(text)

        except Exception as e:
            logger.error(f"向元素输入文本失败: {str(e)}", exc_info=True)
            raise

    def get_text(self, locator, timeout=None):
        """
        获取元素文本

        Args:
            locator (tuple): 元素定位器
            timeout (int): 等待超时时间（可选）

        Returns:
            str: 元素文本内容
        """
        try:
            element = self.wait_element(locator, timeout)
            text = element.text
            logger.info(f"获取元素文本: {locator}, 文本: {text}")
            return text

        except Exception as e:
            logger.error(f"获取元素文本失败: {str(e)}", exc_info=True)
            raise

    def get_attribute(self, locator, attribute_name, timeout=None):
        """
        获取元素属性值

        Args:
            locator (tuple): 元素定位器
            attribute_name (str): 属性名称
            timeout (int): 等待超时时间（可选）

        Returns:
            str: 属性值
        """
        try:
            element = self.wait_element(locator, timeout)
            attribute_value = element.get_attribute(attribute_name)
            logger.info(f"获取元素属性: {locator}, 属性: {attribute_name}, 值: {attribute_value}")
            return attribute_value

        except Exception as e:
            logger.error(f"获取元素属性失败: {str(e)}", exc_info=True)
            raise

    def scroll_to_element(self, locator, timeout=None):
        """
        滚动页面到元素可见位置

        Args:
            locator (tuple): 元素定位器
            timeout (int): 等待超时时间（可选）
        """
        try:
            element = self.wait_element(locator, timeout)
            logger.info(f"滚动到元素: {locator}")
            element.scroll_into_view()

        except Exception as e:
            logger.error(f"滚动到元素失败: {str(e)}", exc_info=True)
            raise

    def execute_script(self, script, *args):
        """
        执行JavaScript脚本

        Args:
            script (str): JavaScript脚本
            *args: 脚本参数

        Returns:
            任意类型: 脚本执行结果
        """
        try:
            logger.info(f"执行JavaScript脚本: {script[:50]}...")
            result = self.driver.execute_script(script, *args)
            return result

        except Exception as e:
            logger.error(f"执行JavaScript脚本失败: {str(e)}", exc_info=True)
            raise

    def get_title(self):
        """
        获取当前页面标题

        Returns:
            str: 页面标题
        """
        try:
            title = self.driver.title
            logger.info(f"当前页面标题: {title}")
            return title

        except Exception as e:
            logger.error(f"获取页面标题失败: {str(e)}", exc_info=True)
            raise

    def get_current_url(self):
        """
        获取当前页面URL

        Returns:
            str: 当前页面URL
        """
        try:
            url = self.driver.current_url
            logger.info(f"当前页面URL: {url}")
            return url

        except Exception as e:
            logger.error(f"获取页面URL失败: {str(e)}", exc_info=True)
            raise

    def switch_to_window(self, index=0):
        """
        切换到指定索引的窗口

        Args:
            index (int): 窗口索引，从0开始，默认为第一个窗口
        """
        try:
            windows = self.driver.window_handles
            if index >= len(windows):
                logger.error(f"窗口索引超出范围: {index}, 总窗口数: {len(windows)}")
                raise IndexError(f"窗口索引超出范围")

            logger.info(f"切换到窗口: {index}")
            self.driver.switch_to.window(windows[index])

        except Exception as e:
            logger.error(f"切换窗口失败: {str(e)}", exc_info=True)
            raise

    def switch_to_frame(self, locator=None, index=None):
        """
        切换到iframe

        Args:
            locator (tuple): iframe定位器（可选）
            index (int): iframe索引（可选）
        """
        try:
            if locator:
                element = self.wait_element(locator)
                logger.info(f"切换到iframe: {locator}")
                self.driver.switch_to.frame(element)
            elif index is not None:
                logger.info(f"切换到iframe索引: {index}")
                self.driver.switch_to.frame(index)
            else:
                logger.error("必须提供locator或index参数")
                raise ValueError("必须提供locator或index参数")

        except Exception as e:
            logger.error(f"切换iframe失败: {str(e)}", exc_info=True)
            raise

    def switch_to_default_content(self):
        """
        切换回主文档
        """
        try:
            logger.info("切换回主文档")
            self.driver.switch_to.default_content()

        except Exception as e:
            logger.error(f"切换回主文档失败: {str(e)}", exc_info=True)
            raise

    def refresh(self):
        """
        刷新当前页面
        """
        try:
            logger.info("刷新页面")
            self.driver.refresh()

        except Exception as e:
            logger.error(f"刷新页面失败: {str(e)}", exc_info=True)
            raise

    def back(self):
        """
        返回上一页
        """
        try:
            logger.info("返回上一页")
            self.driver.back()

        except Exception as e:
            logger.error(f"返回上一页失败: {str(e)}", exc_info=True)
            raise

    def forward(self):
        """
        前进到下一页
        """
        try:
            logger.info("前进到下一页")
            self.driver.forward()

        except Exception as e:
            logger.error(f"前进到下一页失败: {str(e)}", exc_info=True)
            raise

    def close_window(self):
        """
        关闭当前窗口
        """
        try:
            logger.info("关闭当前窗口")
            self.driver.close()

        except Exception as e:
            logger.error(f"关闭窗口失败: {str(e)}", exc_info=True)
            raise

    def quit(self):
        """
        关闭浏览器并退出驱动
        """
        try:
            if self.driver:
                logger.info("关闭浏览器")
                self.driver.quit()
                self.driver = None
            else:
                logger.warning("WebDriver未初始化，无需关闭")

        except Exception as e:
            logger.error(f"关闭浏览器失败: {str(e)}", exc_info=True)
            raise

    def maximize_window(self):
        """
        最大化浏览器窗口
        """
        try:
            logger.info("最大化浏览器窗口")
            self.driver.maximize_window()

        except Exception as e:
            logger.error(f"最大化窗口失败: {str(e)}", exc_info=True)
            raise

    def set_window_size(self, width, height):
        """
        设置浏览器窗口大小

        Args:
            width (int): 窗口宽度
            height (int): 窗口高度
        """
        try:
            logger.info(f"设置窗口大小: {width}x{height}")
            self.driver.set_window_size(width, height)

        except Exception as e:
            logger.error(f"设置窗口大小失败: {str(e)}", exc_info=True)
            raise

    def get_window_size(self):
        """
        获取当前窗口大小

        Returns:
            dict: 窗口大小，包含width和height
        """
        try:
            size = self.driver.get_window_size()
            logger.info(f"当前窗口大小: {size['width']}x{size['height']}")
            return size

        except Exception as e:
            logger.error(f"获取窗口大小失败: {str(e)}", exc_info=True)
            raise

    def screenshot(self, filename=None):
        """
        截图并保存

        Args:
            filename (str): 自定义文件名（可选）

        Returns:
            str: 截图文件路径
        """
        try:
            from utils.screenshot_util import ScreenshotUtil
            screenshot_path = ScreenshotUtil.capture_screenshot(self.driver, filename)
            return screenshot_path

        except Exception as e:
            logger.error(f"截图失败: {str(e)}", exc_info=True)
            raise

    def hover(self, locator, timeout=None):
        """
        鼠标悬停在元素上

        Args:
            locator (tuple): 元素定位器
            timeout (int): 等待超时时间（可选）
        """
        try:
            element = self.wait_element(locator, timeout)
            logger.info(f"鼠标悬停在元素上: {locator}")
            ActionChains(self.driver).move_to_element(element).perform()

        except Exception as e:
            logger.error(f"鼠标悬停失败: {str(e)}", exc_info=True)
            raise

    def double_click(self, locator, timeout=None):
        """
        双击元素

        Args:
            locator (tuple): 元素定位器
            timeout (int): 等待超时时间（可选）
        """
        try:
            element = self.wait_element(locator, timeout)
            logger.info(f"双击元素: {locator}")
            ActionChains(self.driver).double_click(element).perform()

        except Exception as e:
            logger.error(f"双击元素失败: {str(e)}", exc_info=True)
            raise

    def right_click(self, locator, timeout=None):
        """
        右键点击元素

        Args:
            locator (tuple): 元素定位器
            timeout (int): 等待超时时间（可选）
        """
        try:
            element = self.wait_element(locator, timeout)
            logger.info(f"右键点击元素: {locator}")
            ActionChains(self.driver).context_click(element).perform()

        except Exception as e:
            logger.error(f"右键点击元素失败: {str(e)}", exc_info=True)
            raise

    def press_key(self, key):
        """
        按下键盘按键

        Args:
            key (str): 按键名称，如"ENTER", "TAB", "ESC"等
        """
        try:
            key_map = {
                "ENTER": Keys.ENTER,
                "TAB": Keys.TAB,
                "ESC": Keys.ESCAPE,
                "SPACE": Keys.SPACE,
                "BACKSPACE": Keys.BACKSPACE,
                "DELETE": Keys.DELETE,
                "UP": Keys.UP,
                "DOWN": Keys.DOWN,
                "LEFT": Keys.LEFT,
                "RIGHT": Keys.RIGHT,
                "F5": Keys.F5,
                "F12": Keys.F12,
                "CTRL": Keys.CONTROL,
                "ALT": Keys.ALT,
                "SHIFT": Keys.SHIFT
            }

            if key.upper() in key_map:
                logger.info(f"按下按键: {key}")
                ActionChains(self.driver).send_keys(key_map[key.upper()]).perform()
            else:
                logger.warning(f"不支持的按键: {key}")

        except Exception as e:
            logger.error(f"按下按键失败: {str(e)}", exc_info=True)
            raise

    def wait_for_page_load(self, timeout=None):
        """
        等待页面加载完成

        Args:
            timeout (int): 超时时间（可选）

        Returns:
            bool: 加载成功返回True
        """
        try:
            wait_time = timeout or self.env_config.get("page_load_timeout", 30)
            logger.info("等待页面加载完成")

            def page_loaded(driver):
                return driver.execute_script("return document.readyState") == "complete"

            wait = WebDriverWait(self.driver, wait_time)
            wait.until(page_loaded)
            logger.info("页面加载完成")
            return True

        except TimeoutException:
            logger.error("页面加载超时")
            raise
        except Exception as e:
            logger.error(f"等待页面加载失败: {str(e)}", exc_info=True)
            raise

    def is_element_displayed(self, locator):
        """
        判断元素是否可见

        Args:
            locator (tuple): 元素定位器

        Returns:
            bool: 可见返回True，不可见或不存在返回False
        """
        try:
            element = self.find_element(locator)
            return element.is_displayed()

        except NoSuchElementException:
            logger.debug(f"元素不存在: {locator}")
            return False
        except Exception as e:
            logger.error(f"判断元素可见性失败: {str(e)}", exc_info=True)
            return False

    def is_element_enabled(self, locator):
        """
        判断元素是否可用

        Args:
            locator (tuple): 元素定位器

        Returns:
            bool: 可用返回True，不可用或不存在返回False
        """
        try:
            element = self.find_element(locator)
            return element.is_enabled()

        except NoSuchElementException:
            logger.debug(f"元素不存在: {locator}")
            return False
        except Exception as e:
            logger.error(f"判断元素可用性失败: {str(e)}", exc_info=True)
            return False

    def get_cookies(self):
        """
        获取当前页面所有cookie

        Returns:
            list[dict]: cookie列表
        """
        try:
            cookies = self.driver.get_cookies()
            logger.info(f"获取到cookie数量: {len(cookies)}")
            return cookies

        except Exception as e:
            logger.error(f"获取cookie失败: {str(e)}", exc_info=True)
            raise

    def add_cookie(self, cookie_dict):
        """
        添加cookie

        Args:
            cookie_dict (dict): cookie字典，包含name, value等键
        """
        try:
            logger.info(f"添加cookie: {cookie_dict.get('name')}")
            self.driver.add_cookie(cookie_dict)

        except Exception as e:
            logger.error(f"添加cookie失败: {str(e)}", exc_info=True)
            raise

    def delete_cookie(self, name):
        """
        删除指定cookie

        Args:
            name (str): cookie名称
        """
        try:
            logger.info(f"删除cookie: {name}")
            self.driver.delete_cookie(name)

        except Exception as e:
            logger.error(f"删除cookie失败: {str(e)}", exc_info=True)
            raise

    def delete_all_cookies(self):
        """
        删除所有cookie
        """
        try:
            logger.info("删除所有cookie")
            self.driver.delete_all_cookies()

        except Exception as e:
            logger.error(f"删除所有cookie失败: {str(e)}", exc_info=True)
            raise
