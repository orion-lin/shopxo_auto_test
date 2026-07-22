import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from base.WebDriverBase import WebDriverBase
from utils.log_util import logger


class UserCenterPage:
    """
    个人中心页面对象类
    封装个人中心页面的元素定位和操作方法
    """

    # 页面元素定位器
    # ================================================
    # 个人中心菜单头部
    MENU_HD = (By.XPATH, "//div[@class='menu-hd ']")
    # 个人中心链接
    USER_CENTER_LINK = (By.XPATH, "//div[@class='menu-hd ']//a[@href='?s=user/index.html']")
    USER_CENTER_LINK_ALT = (By.XPATH, "//div[@class='menu-hd ']//a[contains(@href, 'user/index')]")
    
    # 个人中心页面标题
    USER_CENTER_TITLE = (By.XPATH, "//h1[contains(text(), '个人中心') or contains(text(), '用户中心')]")
    
    # 订单管理菜单项
    ORDER_MANAGEMENT_MENU = (By.XPATH, "//li[@class='am-active']//a[@href='?s=order/index.html']")
    ORDER_MANAGEMENT_MENU_ALT = (By.XPATH, "//li//a[@href='?s=order/index.html' and contains(text(), '订单管理')]")
    ORDER_MANAGEMENT_MENU_ALT2 = (By.XPATH, "//a[@href='?s=order/index.html' and contains(text(), '订单管理')]")
    
    # 订单管理菜单项（通过文本定位）
    ORDER_MANAGEMENT_TEXT = (By.XPATH, "//a[contains(text(), '订单管理')]")

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

    def click_user_center(self):
        """
        点击个人中心链接

        Returns:
            bool: 点击成功返回True，否则返回False
        """
        logger.info("点击个人中心链接")
        try:
            user_center_locators = [
                self.USER_CENTER_LINK,
                self.USER_CENTER_LINK_ALT,
                (By.XPATH, "//a[@href='?s=user/index.html']"),
                (By.XPATH, "//a[contains(text(), '个人中心')]"),
            ]

            for by, selector in user_center_locators:
                try:
                    wait = self._get_wait(timeout=3)
                    element = wait.until(EC.element_to_be_clickable((by, selector)))
                    self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
                    time.sleep(0.3)
                    element.click()
                    logger.info(f"个人中心链接点击成功，定位器: {selector}")
                    return True
                except TimeoutException:
                    continue
                except Exception as e:
                    logger.warning(f"尝试定位器 {selector} 失败: {str(e)}")
                    continue

            logger.error("所有定位器均未找到个人中心链接")
            return False
        except Exception as e:
            logger.error(f"点击个人中心链接失败: {str(e)}", exc_info=True)
            return False

    def is_user_center_page_displayed(self, timeout=5):
        """
        判断个人中心页面是否已显示

        Args:
            timeout (int): 超时时间，默认5秒

        Returns:
            bool: 个人中心页面已显示返回True，否则返回False
        """
        logger.info("判断个人中心页面是否已显示")
        try:
            page_locators = [
                self.USER_CENTER_TITLE,
                (By.XPATH, "//*[contains(text(), '个人中心')]"),
                (By.XPATH, "//div[@class='menu-hd ']"),
            ]

            for by, selector in page_locators:
                try:
                    wait = self._get_wait(timeout=timeout)
                    element = wait.until(EC.visibility_of_element_located((by, selector)))
                    logger.info(f"个人中心页面已显示，定位器: {selector}")
                    return True
                except TimeoutException:
                    continue

            current_url = self.driver.current_url
            if "user" in current_url.lower() and "index" in current_url.lower():
                logger.info(f"URL包含个人中心相关路径: {current_url}")
                return True

            logger.info(f"未跳转到个人中心页面，当前URL: {current_url}")
            return False
        except Exception as e:
            logger.error(f"判断个人中心页面状态失败: {str(e)}", exc_info=True)
            return False

    def click_order_management(self):
        """
        点击订单管理菜单

        Returns:
            bool: 点击成功返回True，否则返回False
        """
        logger.info("点击订单管理菜单")
        try:
            order_management_locators = [
                self.ORDER_MANAGEMENT_MENU,
                self.ORDER_MANAGEMENT_MENU_ALT,
                self.ORDER_MANAGEMENT_MENU_ALT2,
                self.ORDER_MANAGEMENT_TEXT,
                (By.XPATH, "//a[@href='?s=order/index.html']"),
            ]

            for by, selector in order_management_locators:
                try:
                    wait = self._get_wait(timeout=3)
                    element = wait.until(EC.element_to_be_clickable((by, selector)))
                    self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
                    time.sleep(0.3)
                    element.click()
                    logger.info(f"订单管理菜单点击成功，定位器: {selector}")
                    return True
                except TimeoutException:
                    continue
                except Exception as e:
                    logger.warning(f"尝试定位器 {selector} 失败: {str(e)}")
                    continue

            logger.error("所有定位器均未找到订单管理菜单")
            return False
        except Exception as e:
            logger.error(f"点击订单管理菜单失败: {str(e)}", exc_info=True)
            return False

    def open_user_center_page(self):
        """
        直接打开个人中心页面
        """
        base_url = self.env_config.get("base_url", "")
        user_center_url = f"{base_url}/?s=user/index.html"
        logger.info(f"打开个人中心页面: {user_center_url}")
        self.driver.get(user_center_url)

    def navigate_to_order_list(self):
        """
        从个人中心导航到订单列表页面

        Returns:
            bool: 导航成功返回True，否则返回False
        """
        logger.info("从个人中心导航到订单列表")
        try:
            self.click_order_management()
            time.sleep(2)
            logger.info("已从个人中心导航到订单列表页面")
            return True
        except Exception as e:
            logger.error(f"从个人中心导航到订单列表失败: {str(e)}", exc_info=True)
            return False