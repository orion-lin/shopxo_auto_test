from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from base.WebDriverBase import WebDriverBase
from utils.log_util import logger


class HomePage:
    """
    首页页面对象类
    封装首页的元素定位和操作方法
    """

    # 页面元素定位器
    # ================================================
    # 搜索框输入框 - 通过NAME或CLASS定位
    SEARCH_INPUT = (By.NAME, "wd")
    # 搜索按钮 - 通过TYPE和VALUE组合定位
    SEARCH_BTN = (By.XPATH, "//button[@type='submit' and contains(@class, 'am-btn-primary')]")
    # 搜索框表单 - 通过ID或CLASS定位
    SEARCH_FORM = (By.XPATH, "//form[@method='get' and contains(@action, 'search')]")
    # 导航栏首页按钮
    HOME_BTN = (By.XPATH, "//a[@href='/' and contains(@class, 'am-icon-home')]")

    def __init__(self, web_driver):
        """
        构造方法：接收已初始化的web_driver实例

        Args:
            web_driver (WebDriverBase): 已初始化的WebDriverBase实例
        """
        self.driver = web_driver.driver
        self.env_config = web_driver.env_config
        self.browser_config = web_driver.browser_config
        self._wait = None

    def _get_wait(self, timeout=None):
        """
        获取显式等待对象

        Args:
            timeout (int): 超时时间，默认为配置文件中的explicit_wait值

        Returns:
            WebDriverWait: 显式等待对象
        """
        wait_time = timeout or self.browser_config.get("explicit_wait", 15)
        poll_frequency = self.browser_config.get("poll_frequency", 500) / 1000

        self._wait = WebDriverWait(
            self.driver,
            timeout=wait_time,
            poll_frequency=poll_frequency,
            ignored_exceptions=[NoSuchElementException]
        )
        return self._wait

    def open_home_page(self):
        """
        打开商城首页
        """
        base_url = self.env_config.get("base_url", "")
        logger.info(f"打开商城首页: {base_url}")
        self.driver.get(base_url)

    def input_search_keyword(self, keyword):
        """
        在搜索框中输入关键词

        Args:
            keyword (str): 搜索关键词
        """
        logger.info(f"输入搜索关键词: {keyword}")
        try:
            wait = self._get_wait()
            element = wait.until(EC.visibility_of_element_located(self.SEARCH_INPUT))
            element.clear()
            element.send_keys(keyword)
            logger.info("搜索关键词输入成功")
        except TimeoutException:
            logger.error("搜索框等待超时")
            raise
        except Exception as e:
            logger.error(f"输入搜索关键词失败: {str(e)}", exc_info=True)
            raise

    def click_search_btn(self):
        """
        点击搜索按钮
        """
        logger.info("点击搜索按钮")
        try:
            wait = self._get_wait()
            element = wait.until(EC.element_to_be_clickable(self.SEARCH_BTN))
            element.click()
            logger.info("搜索按钮点击成功")
        except TimeoutException:
            logger.error("搜索按钮等待超时")
            raise
        except Exception as e:
            logger.error(f"点击搜索按钮失败: {str(e)}", exc_info=True)
            raise

    def search(self, keyword):
        """
        执行搜索操作（输入关键词并点击搜索）

        Args:
            keyword (str): 搜索关键词
        """
        logger.info(f"执行搜索操作: {keyword}")
        self.input_search_keyword(keyword)
        self.click_search_btn()

    def get_search_input_value(self):
        """
        获取搜索框当前输入的值

        Returns:
            str: 搜索框中的值，未找到返回空字符串
        """
        logger.info("获取搜索框当前值")
        try:
            wait = self._get_wait()
            element = wait.until(EC.visibility_of_element_located(self.SEARCH_INPUT))
            value = element.get_attribute("value")
            logger.info(f"搜索框当前值: {value}")
            return value or ""
        except TimeoutException:
            logger.warning("未找到搜索框")
            return ""
        except Exception as e:
            logger.error(f"获取搜索框值失败: {str(e)}", exc_info=True)
            return ""

    def is_search_input_displayed(self):
        """
        判断搜索框是否可见

        Returns:
            bool: 搜索框可见返回True，否则返回False
        """
        logger.info("判断搜索框是否可见")
        try:
            wait = self._get_wait(timeout=3)
            element = wait.until(EC.visibility_of_element_located(self.SEARCH_INPUT))
            logger.info("搜索框已可见")
            return True
        except TimeoutException:
            logger.info("搜索框不可见")
            return False
        except Exception as e:
            logger.error(f"判断搜索框状态失败: {str(e)}", exc_info=True)
            return False