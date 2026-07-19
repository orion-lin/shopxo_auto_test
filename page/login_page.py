import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from base.WebDriverBase import WebDriverBase
from utils.log_util import logger
import ddddocr


class LoginPage:
    """
    登录页面对象类
    封装登录页面的元素定位和操作方法
    """

    # 页面元素定位器（已通过F12确认）
    # ================================================
    # 用户名输入框 - 通过NAME定位
    USERNAME_INPUT = (By.NAME, "accounts")
    # 密码输入框 - 通过NAME定位
    PASSWORD_INPUT = (By.NAME, "pwd")
    # 验证码输入框 - 通过NAME定位（实际名称为verify）
    CAPTCHA_INPUT = (By.NAME, "verify")
    # 验证码图片 - 通过ID定位
    CAPTCHA_IMAGE = (By.ID, "form-verify-img")
    # 登录按钮 - 通过type和class组合定位
    LOGIN_BTN = (By.XPATH, "//button[@type='submit' and contains(@class, 'am-btn-primary') and contains(text(), '登录')]")
    # 错误提示框 - 通过class组合定位
    ERROR_MSG = (By.XPATH, "//div[contains(@class, 'common-prompt') and contains(@class, 'am-alert-danger')]//p[@class='prompt-msg']")
    # 成功提示框 - 通过class组合定位
    SUCCESS_MSG = (By.XPATH, "//div[contains(@class, 'common-prompt') and contains(@class, 'am-alert-success')]//p[@class='prompt-msg']")
    # 用户头像元素 - 登录成功后右上角显示用户头像的元素（支持多种定位方式）
    USER_AVATAR = (By.XPATH, "//div[contains(@class, 'm-baseinfo')]//img[@class='user-avatar']")
    # 首页购物车按钮 - 通过文本和href组合定位
    CART_BTN = (By.XPATH, "//a[contains(text(), '购物车') or contains(@href, 'cart')]")
    # 错误提示框关闭按钮
    ERROR_CLOSE_BTN = (By.XPATH, "//div[contains(@class, 'common-prompt')]//button[@class='am-close']")
    # 首页登录链接按钮 - 通过文本和href定位（支持多种定位方式）
    HOME_LOGIN_LINK = (By.XPATH, "//a[contains(@href, 'login') and contains(text(), '登录')]")

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

    def open_login_page(self):
        """
        打开登录页面
        """
        base_url = self.env_config.get("base_url", "")
        login_url = f"{base_url}/?s=user/loginInfo.html"
        logger.info(f"打开登录页面: {login_url}")
        self.driver.get(login_url)

    def open_home_page(self):
        """
        打开商城首页
        """
        base_url = self.env_config.get("base_url", "")
        logger.info(f"打开商城首页: {base_url}")
        self.driver.get(base_url)

    def input_username(self, username):
        """
        输入用户名

        Args:
            username (str): 用户名
        """
        logger.info(f"输入用户名: {username}")
        try:
            wait = self._get_wait()
            element = wait.until(EC.visibility_of_element_located(self.USERNAME_INPUT))
            element.clear()
            element.send_keys(username)
        except TimeoutException:
            logger.error("用户名输入框等待超时")
            raise
        except Exception as e:
            logger.error(f"输入用户名失败: {str(e)}", exc_info=True)
            raise

    def input_password(self, password):
        """
        输入密码

        Args:
            password (str): 密码
        """
        logger.info(f"输入密码: ******")
        try:
            wait = self._get_wait()
            element = wait.until(EC.visibility_of_element_located(self.PASSWORD_INPUT))
            element.clear()
            element.send_keys(password)
        except TimeoutException:
            logger.error("密码输入框等待超时")
            raise
        except Exception as e:
            logger.error(f"输入密码失败: {str(e)}", exc_info=True)
            raise

    def input_captcha(self, captcha):
        """
        输入验证码（支持多种定位方式）

        Args:
            captcha (str): 验证码
        """
        logger.info(f"输入验证码: {captcha}")
        try:
            wait = self._get_wait(timeout=3)
            element = wait.until(EC.presence_of_element_located(self.CAPTCHA_INPUT))

            if element.is_displayed():
                element.clear()
                element.send_keys(captcha)
            else:
                logger.info("验证码输入框不可见，尝试使用JavaScript输入")
                self.driver.execute_script(f"document.querySelector('input[name=\"verify\"]').value = '{captcha}';")
                self.driver.execute_script("document.querySelector('input[name=\"verify\"]').dispatchEvent(new Event('input'));")

            logger.info("验证码输入成功")
        except TimeoutException:
            logger.warning("验证码输入框等待超时，尝试直接查找")
            try:
                elements = self.driver.find_elements(By.NAME, "verifycode")
                if elements:
                    element = elements[0]
                    if element.is_displayed():
                        element.clear()
                        element.send_keys(captcha)
                    else:
                        self.driver.execute_script(f"document.querySelector('input[name=\"verify\"]').value = '{captcha}';")
                else:
                    logger.error("未找到验证码输入框")
                    raise
            except Exception as e:
                logger.error(f"输入验证码失败: {str(e)}", exc_info=True)
                raise
        except Exception as e:
            logger.error(f"输入验证码失败: {str(e)}", exc_info=True)
            raise

    def click_login(self):
        """
        点击登录按钮
        """
        logger.info("点击登录按钮")
        try:
            wait = self._get_wait()
            element = wait.until(EC.element_to_be_clickable(self.LOGIN_BTN))
            element.click()
        except TimeoutException:
            logger.error("登录按钮等待超时")
            raise
        except Exception as e:
            logger.error(f"点击登录按钮失败: {str(e)}", exc_info=True)
            raise

    def click_cart_btn(self):
        """
        点击首页购物车按钮
        未登录状态下点击会弹出登录弹窗，而不是跳转登录页
        """
        logger.info("点击首页购物车按钮")
        try:
            time.sleep(2)
            
            cart_selectors = [
                (By.XPATH, "//div[@class='menu-hd login-event']//a[contains(text(), '购物车')]"),
                (By.XPATH, "//div[contains(@class, 'menu-hd') and contains(@class, 'login-event')]//a"),
                (By.XPATH, "//a[contains(text(), '购物车') and @href='javascript:;']"),
            ]
            
            for by, selector in cart_selectors:
                try:
                    elements = self.driver.find_elements(by, selector)
                    if elements:
                        element = elements[0]
                        self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
                        time.sleep(0.5)
                        self.driver.execute_script("arguments[0].click();", element)
                        logger.info(f"购物车按钮点击成功，定位器: {selector}")
                        return
                except Exception:
                    logger.info(f"定位器 {selector} 未找到元素")
            
            logger.error("未找到购物车按钮")
            raise NoSuchElementException("未找到购物车按钮")
        except NoSuchElementException:
            raise
        except Exception as e:
            logger.error(f"点击购物车按钮失败: {str(e)}", exc_info=True)
            raise

    def click_home_login_link(self):
        """
        点击首页的登录链接按钮，跳转到登录页面
        支持多重定位器容错：优先使用主定位器，失败后尝试备用定位器
        """
        logger.info("点击首页登录链接按钮")
        try:
            login_selectors = [
                self.HOME_LOGIN_LINK,
                (By.XPATH, "//div[@class='member-login']//a[@class='am-btn-primary']"),
                (By.XPATH, "//a[@href='?s=user/loginInfo.html']"),
                (By.XPATH, "//a[contains(@href, 'loginInfo')]"),
                (By.XPATH, "//a[contains(@class, 'am-btn-primary') and contains(text(), '登录')]"),
            ]

            for by, selector in login_selectors:
                try:
                    wait = self._get_wait(timeout=3)
                    element = wait.until(EC.element_to_be_clickable((by, selector)))
                    self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
                    time.sleep(0.5)
                    element.click()
                    logger.info(f"首页登录链接点击成功，定位器: {selector}")
                    logger.info("已点击首页登录链接，等待跳转到登录页面")
                    return
                except TimeoutException:
                    logger.info(f"定位器 {selector} 未找到元素，尝试下一个")
                    continue

            logger.error("所有定位器均未找到首页登录链接")
            raise NoSuchElementException("未找到首页登录链接")

        except NoSuchElementException:
            raise
        except Exception as e:
            logger.error(f"点击首页登录链接失败: {str(e)}", exc_info=True)
            raise

    def refresh_captcha(self):
        """
        刷新验证码图片
        """
        logger.info("刷新验证码图片")
        try:
            wait = self._get_wait()
            element = wait.until(EC.element_to_be_clickable(self.CAPTCHA_IMAGE))
            element.click()
            logger.info("验证码图片刷新成功")
        except TimeoutException:
            logger.error("验证码图片等待超时")
            raise
        except Exception as e:
            logger.error(f"刷新验证码失败: {str(e)}", exc_info=True)
            raise

    def recognize_captcha(self, max_retries=3):
        """
        识别验证码（4位纯数字）
        使用ddddocr库，针对纯色数字验证码识别效果更佳

        Args:
            max_retries (int): 最大重试次数，默认3次

        Returns:
            str: 识别到的验证码，识别失败返回空字符串
        """
        logger.info("开始识别验证码")

        try:
            ocr = ddddocr.DdddOcr()
        except Exception as e:
            logger.error(f"ddddocr初始化失败: {str(e)}")
            return ""

        for attempt in range(max_retries):
            try:
                wait = self._get_wait()
                captcha_element = wait.until(EC.visibility_of_element_located(self.CAPTCHA_IMAGE))

                image_data = captcha_element.screenshot_as_png

                captcha_text = ocr.classification(image_data)

                if len(captcha_text) == 4 and captcha_text.isdigit():
                    logger.info(f"验证码识别成功: {captcha_text}")
                    return captcha_text
                else:
                    logger.warning(f"验证码识别结果无效: {captcha_text}，尝试刷新")
                    self.refresh_captcha()

            except TimeoutException:
                logger.error("验证码图片加载超时")
                self.refresh_captcha()
            except Exception as e:
                logger.error(f"验证码识别失败: {str(e)}", exc_info=True)
                if attempt < max_retries - 1:
                    self.refresh_captcha()

        logger.error("验证码识别失败，已达到最大重试次数")
        return ""

    def get_error_message(self, timeout=5):
        """
        获取错误提示文本

        Args:
            timeout (int): 超时时间，默认5秒

        Returns:
            str: 错误提示文本，未找到返回空字符串
        """
        logger.info("获取错误提示信息")
        try:
            wait = WebDriverWait(self.driver, timeout=timeout)
            element = wait.until(EC.visibility_of_element_located(self.ERROR_MSG))
            error_text = element.text.strip()
            logger.info(f"获取到错误提示: {error_text}")
            return error_text
        except TimeoutException:
            logger.warning("未找到错误提示信息")
            return ""
        except Exception as e:
            logger.error(f"获取错误提示失败: {str(e)}", exc_info=True)
            return ""

    def get_success_message(self, timeout=5):
        """
        获取成功提示文本

        Args:
            timeout (int): 超时时间，默认5秒

        Returns:
            str: 成功提示文本，未找到返回空字符串
        """
        logger.info("获取成功提示信息")
        try:
            wait = WebDriverWait(self.driver, timeout=timeout)
            element = wait.until(EC.visibility_of_element_located(self.SUCCESS_MSG))
            success_text = element.text.strip()
            logger.info(f"获取到成功提示: {success_text}")
            return success_text
        except TimeoutException:
            logger.warning("未找到成功提示信息")
            return ""
        except Exception as e:
            logger.error(f"获取成功提示失败: {str(e)}", exc_info=True)
            return ""

    def is_avatar_displayed(self, timeout=2):
        """
        判断用户头像是否显示
        支持多重定位器容错：优先使用主定位器，失败后尝试备用定位器
        使用较短的超时时间，避免长时间等待

        Args:
            timeout (int): 每个定位器的超时时间，默认2秒

        Returns:
            bool: 用户头像显示返回True，否则返回False
        """
        logger.info("判断用户头像是否显示")
        try:
            avatar_selectors = [
                self.USER_AVATAR,
                (By.XPATH, "//img[@class='user-avatar']"),
                (By.XPATH, "//div[@class='m-baseinfo']//img"),
                (By.XPATH, "//a[@href='javascript:;']//img[@class='user-avatar']"),
                (By.XPATH, "//img[contains(@src, 'default-user-avatar')]"),
            ]

            for by, selector in avatar_selectors:
                try:
                    wait = self._get_wait(timeout=timeout)
                    element = wait.until(EC.visibility_of_element_located((by, selector)))
                    logger.info(f"用户头像已显示，定位器: {selector}")
                    return True
                except TimeoutException:
                    continue

            logger.warning("所有定位器均未找到用户头像")
            return False

        except Exception as e:
            logger.error(f"判断用户头像状态失败: {str(e)}", exc_info=True)
            return False

    def is_login_success(self):
        """
        判断登录是否成功
        优先通过URL判断，避免长时间等待

        Returns:
            bool: 登录成功返回True，失败返回False
        """
        logger.info("判断登录是否成功")
        try:
            current_url = self.driver.current_url
            logger.info(f"当前URL: {current_url}")

            if "/login.html" not in current_url:
                logger.info("登录成功：页面已跳转")
                return True

            try:
                success_msg = self.get_success_message(timeout=2)
                if success_msg and "登录成功" in success_msg:
                    logger.info("登录成功：页面显示登录成功提示")
                    return True
            except Exception:
                pass

            try:
                if self.is_avatar_displayed(timeout=1):
                    logger.info("登录成功：用户头像已显示")
                    return True
            except Exception:
                pass

            logger.info("登录失败：仍在登录页面")
            return False
        except Exception as e:
            logger.error(f"判断登录状态失败: {str(e)}", exc_info=True)
            return False

    def is_redirect_to_login(self):
        """
        判断是否已跳转到登录页面

        Returns:
            bool: 已跳转到登录页面返回True，否则返回False
        """
        logger.info("判断是否跳转到登录页面")
        try:
            current_url = self.driver.current_url
            logger.info(f"当前URL: {current_url}")

            if "/login.html" in current_url or "logininfo" in current_url:
                logger.info("已跳转到登录页面")
                return True

            logger.info("未跳转到登录页面")
            return False
        except Exception as e:
            logger.error(f"判断跳转状态失败: {str(e)}", exc_info=True)
            return False

    def get_all_error_messages(self, timeout=5, max_retries=2):
        """
        获取所有错误提示文本（支持多条错误提示）

        Args:
            timeout (int): 超时时间，默认5秒
            max_retries (int): 最大重试次数，默认2次

        Returns:
            list: 所有错误提示文本列表，未找到返回空列表
        """
        logger.info("获取所有错误提示信息")
        for attempt in range(max_retries):
            try:
                wait = WebDriverWait(self.driver, timeout=timeout)
                elements = wait.until(EC.visibility_of_all_elements_located(self.ERROR_MSG))
                error_texts = []
                for element in elements:
                    try:
                        text = element.text.strip()
                        if text:
                            error_texts.append(text)
                    except StaleElementReferenceException:
                        logger.warning("获取元素文本时遇到StaleElementReferenceException，跳过该元素")
                        continue
                logger.info(f"获取到错误提示列表: {error_texts}")
                return error_texts
            except TimeoutException:
                if attempt < max_retries - 1:
                    logger.warning(f"第{attempt+1}次获取错误提示超时，重试中...")
                    continue
                logger.warning("未找到错误提示信息")
                return []
            except StaleElementReferenceException:
                if attempt < max_retries - 1:
                    logger.warning(f"第{attempt+1}次获取错误提示遇到StaleElementReferenceException，重试中...")
                    continue
                logger.error("获取错误提示失败: StaleElementReferenceException")
                return []
            except Exception as e:
                logger.error(f"获取错误提示失败: {str(e)}", exc_info=True)
                return []

    def is_password_input_visible(self, timeout=1):
        """
        判断密码输入框是否可见（用于判断是否进入第二步）

        Args:
            timeout (int): 超时时间，默认1秒

        Returns:
            bool: 密码输入框可见返回True，否则返回False
        """
        logger.info("判断密码输入框是否可见")
        try:
            wait = self._get_wait(timeout=timeout)
            element = wait.until(EC.visibility_of_element_located(self.PASSWORD_INPUT))
            logger.info("密码输入框已可见")
            return True
        except TimeoutException:
            logger.info("密码输入框不可见")
            return False
        except Exception as e:
            logger.error(f"判断密码输入框状态失败: {str(e)}", exc_info=True)
            return False

    def is_captcha_input_visible(self, timeout=1):
        """
        判断验证码输入框是否可见

        Args:
            timeout (int): 超时时间，默认1秒

        Returns:
            bool: 验证码输入框可见返回True，否则返回False
        """
        logger.info("判断验证码输入框是否可见")
        try:
            wait = self._get_wait(timeout=timeout)
            element = wait.until(EC.visibility_of_element_located(self.CAPTCHA_INPUT))
            logger.info("验证码输入框已可见")
            return True
        except TimeoutException:
            logger.info("验证码输入框不可见")
            return False
        except Exception as e:
            logger.error(f"判断验证码输入框状态失败: {str(e)}", exc_info=True)
            return False

    def clear_all_inputs(self):
        """
        清空所有输入框内容
        """
        logger.info("清空所有输入框内容")
        try:
            self._clear_input(self.USERNAME_INPUT)
            self._clear_input(self.PASSWORD_INPUT)
            self._clear_input(self.CAPTCHA_INPUT)
            logger.info("所有输入框清空完成")
        except Exception as e:
            logger.error(f"清空输入框失败: {str(e)}", exc_info=True)
            raise

    def _clear_input(self, locator):
        """
        清空指定输入框

        Args:
            locator: 元素定位器
        """
        try:
            element = self.driver.find_element(*locator)
            element.clear()
        except NoSuchElementException:
            logger.warning(f"元素不存在，跳过清空: {locator}")
        except Exception as e:
            logger.error(f"清空元素失败: {locator}, 错误: {str(e)}")

    def reset_login_page(self):
        """
        重置登录页面至初始空白状态
        通过刷新页面实现，消除上一条操作残留输入内容与错误提示
        同时清除登录状态（通过清除cookies）
        """
        logger.info("重置登录页面")
        try:
            self.driver.delete_all_cookies()
            current_url = self.driver.current_url
            self.driver.get(current_url)
            logger.info("登录页面重置完成")
        except Exception as e:
            logger.error(f"重置登录页面失败: {str(e)}", exc_info=True)
            raise

    def dismiss_error_messages(self):
        """
        关闭所有错误提示框
        用于在分步验证的步骤之间清除过时的错误提示
        """
        logger.info("关闭所有错误提示框")
        try:
            close_buttons = self.driver.find_elements(*self.ERROR_CLOSE_BTN)
            for btn in close_buttons:
                try:
                    btn.click()
                except Exception:
                    pass
            logger.info(f"关闭了 {len(close_buttons)} 个错误提示框")
        except Exception as e:
            logger.error(f"关闭错误提示框失败: {str(e)}", exc_info=True)

    def login(self, username, password):
        """
        完整登录流程（带验证码识别）- 通过首页点击登录按钮的方式登录

        流程：首页 -> 点击登录按钮 -> 登录页 -> 输入账号密码验证码 -> 点击登录 -> 跳转首页

        Args:
            username (str): 用户名
            password (str): 密码

        Returns:
            bool: 登录成功返回True，失败返回False
        """
        logger.info(f"执行登录操作：用户名={username}")

        logger.info("=== 打开首页 ===")
        self.open_home_page()

        logger.info("=== 点击首页登录按钮跳转登录页 ===")
        self.click_home_login_link()

        logger.info("=== 清空输入框 ===")
        self.clear_all_inputs()

        logger.info("=== 输入用户名 ===")
        self.input_username(username)

        logger.info("=== 输入密码 ===")
        self.input_password(password)

        logger.info("=== 识别并输入验证码 ===")
        captcha = self.recognize_captcha()
        if not captcha:
            logger.error("验证码识别失败，登录流程终止")
            return False
        self.input_captcha(captcha)

        logger.info("=== 点击登录按钮 ===")
        self.click_login()

        error_msg = self.get_error_message(timeout=3)
        if error_msg:
            if "验证码" in error_msg:
                logger.info(f"验证码错误({error_msg})，重新识别")
                captcha = self.recognize_captcha()
                if captcha:
                    self.input_captcha(captcha)
                    self.click_login()

        if self.is_login_success():
            logger.info("登录成功，等待自动跳转首页")
            return True

        return False
