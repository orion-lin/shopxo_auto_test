import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from base.WebDriverBase import WebDriverBase
from utils.log_util import logger


class ProductDetailPage:
    """
    商品详情页面对象类
    封装商品详情页面的元素定位和操作方法
    """

    # 页面元素定位器（根据实际页面HTML结构更新）
    # ================================================
    # 商品名称 - h1标签
    PRODUCT_NAME = (By.XPATH, "//h1[contains(@class, 'goods-title') or contains(@class, 'title')]")
    
    # 规格选择区域容器（新结构：sku-container）
    SPECS_CONTAINER = (By.XPATH, "//div[@class='sku-container']")
    
    # 套餐选择按钮（套餐二）- 通过li标签定位
    PACKAGE_OPTION = (By.XPATH, "//div[@class='sku-container']//div[contains(@class, 'theme-options') and .//div[@class='cart-title' and text()='套餐']]//li[@data-value='套餐二']")
    
    # 颜色选项 - 通过li标签定位
    COLOR_OPTION_GOLD = (By.XPATH, "//div[@class='sku-container']//div[contains(@class, 'theme-options') and .//div[@class='cart-title' and text()='颜色']]//li[@data-value='金色']")
    COLOR_OPTION_SILVER = (By.XPATH, "//div[@class='sku-container']//div[contains(@class, 'theme-options') and .//div[@class='cart-title' and text()='颜色']]//li[@data-value='银色']")
    
    # 容量选项 - 通过li标签定位
    CAPACITY_OPTION_32G = (By.XPATH, "//div[@class='sku-container']//div[contains(@class, 'theme-options') and .//div[@class='cart-title' and text()='容量']]//li[@data-value='32G']")
    CAPACITY_OPTION_64G = (By.XPATH, "//div[@class='sku-container']//div[contains(@class, 'theme-options') and .//div[@class='cart-title' and text()='容量']]//li[@data-value='64G']")
    CAPACITY_OPTION_128G = (By.XPATH, "//div[@class='sku-container']//div[contains(@class, 'theme-options') and .//div[@class='cart-title' and text()='容量']]//li[@data-value='128G']")
    
    # 当前售价（选中规格后的价格）- 通过goods-sale-price-value类定位
    CURRENT_PRICE = (By.XPATH, "//b[@class='goods-sale-price-value']")
    CURRENT_PRICE_ALT = (By.XPATH, "//span[@class='goods-sale-price-value']")
    
    # 数量输入框
    QUANTITY_INPUT = (By.XPATH, "//div[contains(text(), '数量')]/following-sibling::div//input[@type='number']")
    
    # 数量+按钮
    QUANTITY_PLUS_BTN = (By.XPATH, "//div[contains(text(), '数量')]/following-sibling::div//button[@data-am-plus]")
    
    # 数量-按钮
    QUANTITY_MINUS_BTN = (By.XPATH, "//div[contains(text(), '数量')]/following-sibling::div//button[@data-am-minus]")
    
    # 加入购物车按钮（新结构：通过class cart-submit和data-type定位）
    ADD_TO_CART_BTN = (By.XPATH, "//button[@class='am-radius am-btn am-btn-secondary cart-submit buy-event login-event' and @data-type='cart']")
    
    # 立即购买按钮
    BUY_NOW_BTN = (By.XPATH, "//button[contains(text(), '立即购买')]")
    
    # 成功提示框（Toast）
    SUCCESS_MSG_TOAST = (By.XPATH, "//div[contains(@class,'am-toast') and contains(text(),'加入购物车成功')]")
    
    # 成功提示框（Modal弹窗 - 实际页面结构）
    SUCCESS_MSG_MODAL = (By.XPATH, "//div[@class='am-modal-dialog am-radius']//span[contains(text(),'商品已成功加入购物车')]")
    
    # 成功提示框（Modal弹窗备用）
    SUCCESS_MSG_MODAL_ALT = (By.XPATH, "//div[contains(@class,'am-modal-bd')]//span[contains(text(),'加入购物车')]")
    
    # 成功提示框（通用）
    SUCCESS_MSG = (By.XPATH, "//div[contains(@class, 'common-prompt') and contains(@class, 'am-alert-success')]//p[@class='prompt-msg']")
    
    # 错误提示框
    ERROR_MSG = (By.XPATH, "//div[contains(@class, 'common-prompt') and contains(@class, 'am-alert-danger')]//p[@class='prompt-msg']")

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

    def wait_page_loaded(self, timeout=10):
        """
        等待商品详情页面加载完成

        Args:
            timeout (int): 超时时间，默认10秒
        """
        logger.info("等待商品详情页面加载完成")
        try:
            wait = self._get_wait(timeout=timeout)
            wait.until(EC.visibility_of_element_located(self.PRODUCT_NAME))
            logger.info("商品详情页面已加载")
        except TimeoutException:
            logger.error("商品详情页面加载超时")
            raise
        except Exception as e:
            logger.error(f"等待商品详情页面加载失败: {str(e)}", exc_info=True)
            raise

    def get_product_name(self):
        """
        获取商品名称

        Returns:
            str: 商品名称，未找到返回空字符串
        """
        logger.info("获取商品名称")
        try:
            wait = self._get_wait()
            element = wait.until(EC.visibility_of_element_located(self.PRODUCT_NAME))
            name = element.text.strip()
            logger.info(f"商品名称: {name}")
            return name
        except TimeoutException:
            logger.warning("未找到商品名称元素")
            return ""
        except Exception as e:
            logger.error(f"获取商品名称失败: {str(e)}", exc_info=True)
            return ""

    def scroll_to_specs_container(self):
        """
        滚动到规格选择区域
        """
        logger.info("滚动到规格选择区域")
        try:
            wait = self._get_wait(timeout=10)
            element = wait.until(EC.presence_of_element_located(self.SPECS_CONTAINER))
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
            time.sleep(1)
            logger.info("已滚动到规格选择区域")
        except TimeoutException:
            logger.warning("未找到规格选择区域，尝试滚动到页面下方")
            self.driver.execute_script("window.scrollTo({top: 600, behavior: 'smooth'});")
            time.sleep(1)
        except Exception as e:
            logger.error(f"滚动到规格区域失败: {str(e)}", exc_info=True)

    def select_package(self):
        """
        选择套餐二
        支持多重定位器容错：优先使用主定位器，失败后尝试备用定位器

        Returns:
            bool: 选择成功返回True，失败返回False
        """
        logger.info("选择套餐二")
        try:
            package_selectors = [
                self.PACKAGE_OPTION,
                (By.XPATH, "//li[@data-type-value='套餐' and @data-value='套餐二']"),
                (By.XPATH, "//li[contains(@class, 'sku-line') and .//span[text()='套餐二']]"),
                (By.XPATH, "//div[@class='sku-container']//li[@data-value='套餐二']"),
            ]

            for by, selector in package_selectors:
                try:
                    wait = self._get_wait(timeout=3)
                    element = wait.until(EC.element_to_be_clickable((by, selector)))
                    self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
                    time.sleep(0.5)
                    element.click()
                    logger.info(f"套餐二选择成功，定位器: {selector}")
                    return True
                except TimeoutException:
                    logger.info(f"定位器 {selector} 未找到套餐二选项，尝试下一个")
                    continue

            logger.warning("所有定位器均未找到套餐二选项，可能已默认选中")
            return True
        except Exception as e:
            logger.error(f"选择套餐失败: {str(e)}", exc_info=True)
            return False

    def select_color(self, color_name):
        """
        选择颜色
        支持多重定位器容错：优先使用主定位器，失败后尝试备用定位器

        Args:
            color_name (str): 颜色名称（金色或银色）

        Returns:
            bool: 选择成功返回True，失败返回False
        """
        logger.info(f"选择颜色: {color_name}")
        try:
            if color_name == "金色":
                selectors = [
                    self.COLOR_OPTION_GOLD,
                    (By.XPATH, "//li[@data-type-value='颜色' and @data-value='金色']"),
                    (By.XPATH, "//li[contains(@class, 'sku-line') and .//span[text()='金色']]"),
                    (By.XPATH, "//div[@class='sku-container']//li[@data-value='金色']"),
                ]
            elif color_name == "银色":
                selectors = [
                    self.COLOR_OPTION_SILVER,
                    (By.XPATH, "//li[@data-type-value='颜色' and @data-value='银色']"),
                    (By.XPATH, "//li[contains(@class, 'sku-line') and .//span[text()='银色']]"),
                    (By.XPATH, "//div[@class='sku-container']//li[@data-value='银色']"),
                ]
            else:
                logger.error(f"未知颜色: {color_name}")
                return False

            for by, selector in selectors:
                try:
                    wait = self._get_wait(timeout=3)
                    element = wait.until(EC.element_to_be_clickable((by, selector)))
                    self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
                    time.sleep(0.5)
                    element.click()
                    logger.info(f"颜色 '{color_name}' 选择成功，定位器: {selector}")
                    return True
                except TimeoutException:
                    logger.info(f"定位器 {selector} 未找到颜色选项，尝试下一个")
                    continue

            logger.error(f"所有定位器均未找到颜色选项: {color_name}")
            return False
        except Exception as e:
            logger.error(f"选择颜色失败: {str(e)}", exc_info=True)
            return False

    def select_capacity(self, capacity_name):
        """
        选择容量
        支持多重定位器容错：优先使用主定位器，失败后尝试备用定位器

        Args:
            capacity_name (str): 容量名称（32G、64G、128G）

        Returns:
            bool: 选择成功返回True，失败返回False
        """
        logger.info(f"选择容量: {capacity_name}")
        try:
            if capacity_name == "32G":
                selectors = [
                    self.CAPACITY_OPTION_32G,
                    (By.XPATH, "//li[@data-type-value='容量' and @data-value='32G']"),
                    (By.XPATH, "//li[contains(@class, 'sku-line') and .//span[text()='32G']]"),
                    (By.XPATH, "//div[@class='sku-container']//li[@data-value='32G']"),
                ]
            elif capacity_name == "64G":
                selectors = [
                    self.CAPACITY_OPTION_64G,
                    (By.XPATH, "//li[@data-type-value='容量' and @data-value='64G']"),
                    (By.XPATH, "//li[contains(@class, 'sku-line') and .//span[text()='64G']]"),
                    (By.XPATH, "//div[@class='sku-container']//li[@data-value='64G']"),
                ]
            elif capacity_name == "128G":
                selectors = [
                    self.CAPACITY_OPTION_128G,
                    (By.XPATH, "//li[@data-type-value='容量' and @data-value='128G']"),
                    (By.XPATH, "//li[contains(@class, 'sku-line') and .//span[text()='128G']]"),
                    (By.XPATH, "//div[@class='sku-container']//li[@data-value='128G']"),
                ]
            else:
                logger.error(f"未知容量: {capacity_name}")
                return False

            for by, selector in selectors:
                try:
                    wait = self._get_wait(timeout=3)
                    element = wait.until(EC.element_to_be_clickable((by, selector)))
                    self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
                    time.sleep(0.5)
                    element.click()
                    logger.info(f"容量 '{capacity_name}' 选择成功，定位器: {selector}")
                    return True
                except TimeoutException:
                    logger.info(f"定位器 {selector} 未找到容量选项，尝试下一个")
                    continue

            logger.error(f"所有定位器均未找到容量选项: {capacity_name}")
            return False
        except Exception as e:
            logger.error(f"选择容量失败: {str(e)}", exc_info=True)
            return False

    def select_spec_combination(self, color_name, capacity_name):
        """
        选择完整的规格组合（套餐二+颜色+容量）

        Args:
            color_name (str): 颜色名称（金色或银色）
            capacity_name (str): 容量名称（32G、64G、128G）

        Returns:
            bool: 选择成功返回True，失败返回False
        """
        logger.info(f"选择规格组合: {color_name} / {capacity_name}")
        try:
            self.select_package()
            time.sleep(0.5)
            
            self.select_color(color_name)
            time.sleep(0.5)
            
            self.select_capacity(capacity_name)
            time.sleep(0.5)
            
            logger.info(f"规格组合 '{color_name} / {capacity_name}' 选择成功")
            return True
        except Exception as e:
            logger.error(f"选择规格组合失败: {str(e)}", exc_info=True)
            return False

    def get_current_price(self):
        """
        获取当前选中规格后的售价
        支持多重定位器容错：优先使用主定位器，失败后尝试备用定位器

        Returns:
            str: 当前售价，未找到返回空字符串
        """
        logger.info("获取当前售价")
        try:
            price_selectors = [
                self.CURRENT_PRICE,
                self.CURRENT_PRICE_ALT,
                (By.XPATH, "//span[contains(@class, 'goods-sale-price-value')]"),
                (By.XPATH, "//*[@class='goods-sale-price-value']"),
                (By.XPATH, "//*[contains(@class, 'goods-sale-price')]"),
            ]

            for by, selector in price_selectors:
                try:
                    wait = self._get_wait(timeout=3)
                    element = wait.until(EC.visibility_of_element_located((by, selector)))
                    price = element.text.strip()
                    if price and len(price) > 0:
                        logger.info(f"当前售价: {price}，定位器: {selector}")
                        return price
                except TimeoutException:
                    logger.info(f"定位器 {selector} 未找到价格元素，尝试下一个")
                    continue

            logger.warning("所有定位器均未找到价格元素")
            return ""
        except Exception as e:
            logger.error(f"获取当前售价失败: {str(e)}", exc_info=True)
            return ""

    def set_quantity(self, quantity):
        """
        设置商品数量

        Args:
            quantity (int): 要设置的数量

        Returns:
            bool: 设置成功返回True，失败返回False
        """
        logger.info(f"设置商品数量: {quantity}")
        try:
            wait = self._get_wait(timeout=5)
            element = wait.until(EC.visibility_of_element_located(self.QUANTITY_INPUT))
            element.clear()
            element.send_keys(str(quantity))
            logger.info(f"商品数量设置成功: {quantity}")
            return True
        except TimeoutException:
            logger.error("数量输入框等待超时")
            return False
        except Exception as e:
            logger.error(f"设置商品数量失败: {str(e)}", exc_info=True)
            return False

    def click_add_to_cart(self):
        """
        点击加入购物车按钮
        支持多重定位器容错：优先使用主定位器，失败后尝试备用定位器
        """
        logger.info("点击加入购物车按钮")
        try:
            self.scroll_to_specs_container()

            cart_selectors = [
                self.ADD_TO_CART_BTN,
                (By.XPATH, "//button[contains(@class, 'cart-submit') and @data-type='cart']"),
                (By.XPATH, "//button[contains(@class, 'cart-submit')]"),
                (By.XPATH, "//button[@data-type='cart']"),
                (By.XPATH, "//button[contains(text(), '加入购物车')]"),
                (By.XPATH, "//button[contains(@class, 'buy-event') and contains(@class, 'login-event')]"),
            ]

            for by, selector in cart_selectors:
                try:
                    wait = self._get_wait(timeout=3)
                    element = wait.until(EC.element_to_be_clickable((by, selector)))
                    self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
                    time.sleep(0.5)
                    element.click()
                    logger.info(f"加入购物车按钮点击成功，定位器: {selector}")
                    return
                except TimeoutException:
                    logger.info(f"定位器 {selector} 未找到加入购物车按钮，尝试下一个")
                    continue

            logger.error("所有定位器均未找到加入购物车按钮")
            raise NoSuchElementException("未找到加入购物车按钮")

        except NoSuchElementException:
            raise
        except Exception as e:
            logger.error(f"点击加入购物车按钮失败: {str(e)}", exc_info=True)
            raise

    def get_success_message(self, timeout=3):
        """
        获取成功提示文本（支持Toast、Modal弹窗等多种提示类型）
        支持多重定位器容错：优先使用主定位器，失败后尝试备用定位器
        使用WebDriverWait等待元素可见，确保能正确定位模态框内的元素

        Args:
            timeout (int): 超时时间，默认3秒

        Returns:
            str: 成功提示文本，未找到返回空字符串
        """
        logger.info("获取成功提示信息")
        try:
            success_selectors = [
                self.SUCCESS_MSG_TOAST,
                self.SUCCESS_MSG_MODAL,
                self.SUCCESS_MSG_MODAL_ALT,
                self.SUCCESS_MSG,
                (By.XPATH, "//span[contains(text(), '商品已成功加入购物车')]"),
                (By.XPATH, "//div[@class='am-modal-bd']//span[@class='am-text-success']"),
                (By.XPATH, "//span[@class='am-text-success' and contains(text(), '加入购物车')]"),
                (By.XPATH, "//div[@class='am-modal-dialog']//span[contains(text(), '加入购物车')]"),
                (By.XPATH, "//div[@class='am-modal-bd']//span[contains(text(), '加入购物车')]"),
            ]

            for _ in range(timeout):
                time.sleep(1)

                for by, selector in success_selectors:
                    try:
                        wait = self._get_wait(timeout=2)
                        element = wait.until(EC.visibility_of_element_located((by, selector)))
                        success_text = element.text.strip()
                        if success_text and "购物车" in success_text:
                            logger.info(f"获取到成功提示: {success_text}，定位器: {selector}")
                            return success_text
                    except TimeoutException:
                        continue
                    except Exception:
                        continue

                try:
                    js_result = self.driver.execute_script(
                        "var el = document.querySelector('div.am-toast, div.am-modal-dialog.am-radius, div.am-modal-bd span.am-text-success, div.am-modal-dialog span.am-text-success'); return el ? el.textContent.trim() : '';"
                    )
                    if js_result and len(js_result) < 200 and "购物车" in js_result:
                        logger.info(f"获取到成功提示(JS): {js_result}")
                        return js_result
                except Exception:
                    pass

                try:
                    js_find_all = self.driver.execute_script(
                        "var els = document.querySelectorAll('span.am-text-success, div.am-modal-dialog span'); \n"
                        "for(var i=0; i<els.length; i++) {\n"
                        "    if(els[i].textContent && els[i].textContent.indexOf('购物车') !== -1) {\n"
                        "        return els[i].textContent.trim();\n"
                        "    }\n"
                        "}\n"
                        "return '';"
                    )
                    if js_find_all and len(js_find_all) < 200:
                        logger.info(f"获取到成功提示(JS遍历): {js_find_all}")
                        return js_find_all
                except Exception:
                    pass

        except Exception as e:
            logger.error(f"获取成功提示失败: {str(e)}", exc_info=True)

        logger.warning("未找到成功提示信息")
        return ""

    def get_cart_count(self):
        """
        获取购物车商品数量
        用于验证加入购物车是否成功的替代方案

        Returns:
            str: 购物车数量，未找到返回空字符串
        """
        logger.info("获取购物车商品数量")
        try:
            cart_count_selectors = [
                (By.XPATH, "//strong[@class='common-cart-total']"),
                (By.XPATH, "//*[@class='common-cart-total']"),
                (By.XPATH, "//div[@class='am-modal-bd']//strong"),
            ]

            for by, selector in cart_count_selectors:
                try:
                    wait = self._get_wait(timeout=2)
                    element = wait.until(EC.visibility_of_element_located((by, selector)))
                    count_text = element.text.strip()
                    if count_text and count_text.isdigit():
                        logger.info(f"购物车数量: {count_text}")
                        return count_text
                except TimeoutException:
                    continue
                except Exception:
                    continue

            try:
                js_result = self.driver.execute_script(
                    "var el = document.querySelector('strong.common-cart-total, .common-cart-total'); return el ? el.textContent.trim() : '';"
                )
                if js_result and js_result.isdigit():
                    logger.info(f"购物车数量(JS): {js_result}")
                    return js_result
            except Exception:
                pass

            logger.warning("未找到购物车数量元素")
            return ""

        except Exception as e:
            logger.error(f"获取购物车数量失败: {str(e)}", exc_info=True)
            return ""

    def close_success_modal(self):
        """
        关闭加入购物车成功后的提示弹窗
        支持多种弹窗关闭方式：继续购物按钮、关闭按钮(×)、点击遮罩层、JS关闭

        Returns:
            bool: 关闭成功返回True，失败返回False
        """
        logger.info("关闭成功提示弹窗")
        try:
            close_selectors = [
                (By.XPATH, "//button[@data-am-modal-close and contains(text(), '继续购物')]"),
                (By.XPATH, "//button[contains(text(), '继续购物')]"),
                (By.XPATH, "//a[@data-am-modal-close and @class='am-close am-close-spin']"),
                (By.XPATH, "//a[@class='am-close am-close-spin']"),
                (By.XPATH, "//a[@data-am-modal-close]"),
                (By.XPATH, "//div[@class='am-modal-hd']//a[@class='am-close']"),
                (By.XPATH, "//a[contains(@class, 'am-close') and contains(@href, 'javascript')]"),
                (By.XPATH, "//a[contains(@class, 'am-close')]"),
                (By.XPATH, "//button[@data-am-modal-close]"),
                (By.XPATH, "//div[@class='am-modal-out']"),
            ]

            for by, selector in close_selectors:
                try:
                    wait = self._get_wait(timeout=2)
                    element = wait.until(EC.visibility_of_element_located((by, selector)))
                    self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
                    time.sleep(0.3)
                    element = wait.until(EC.element_to_be_clickable((by, selector)))
                    element.click()
                    logger.info(f"成功提示弹窗关闭成功，定位器: {selector}")
                    time.sleep(0.5)
                    return True
                except TimeoutException:
                    logger.info(f"定位器 {selector} 未找到关闭按钮，尝试下一个")
                    continue
                except Exception:
                    logger.info(f"定位器 {selector} 操作失败，尝试下一个")
                    continue

            logger.warning("所有定位器均未找到关闭按钮，尝试JS关闭")
            try:
                js_close_result = self.driver.execute_script(
                    "var closeBtn = document.querySelector('a.am-close.am-close-spin, button[data-am-modal-close], a[data-am-modal-close]'); \n"
                    "if(closeBtn) { closeBtn.click(); return true; } \n"
                    "var modal = document.querySelector('.am-modal-out'); \n"
                    "if(modal) { modal.click(); return true; } \n"
                    "return false;"
                )
                if js_close_result:
                    logger.info("通过JS关闭弹窗成功")
                    time.sleep(0.5)
                    return True
            except Exception as e:
                logger.info(f"JS关闭弹窗失败: {str(e)}")

            logger.warning("所有关闭方式均失败，可能弹窗已自动关闭")
            return False

        except Exception as e:
            logger.error(f"关闭成功提示弹窗失败: {str(e)}", exc_info=True)
            return False

    def get_error_message(self, timeout=3):
        """
        获取错误提示文本

        Args:
            timeout (int): 超时时间，默认3秒

        Returns:
            str: 错误提示文本，未找到返回空字符串
        """
        logger.info("获取错误提示信息")
        try:
            for _ in range(3):
                time.sleep(0.3)

                try:
                    elements = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'common-prompt') and contains(@class, 'am-alert-danger')]")
                    if elements:
                        msg_elements = elements[0].find_elements(By.XPATH, ".//p[@class='prompt-msg']")
                        if msg_elements:
                            error_text = msg_elements[0].text.strip()
                        else:
                            error_text = elements[0].text.strip()
                        logger.info(f"获取到错误提示(common-prompt): {error_text}")
                        return error_text
                except Exception:
                    pass

                try:
                    elements = self.driver.find_elements(*self.ERROR_MSG)
                    if elements:
                        error_text = elements[0].text.strip()
                        logger.info(f"获取到错误提示(ERROR_MSG): {error_text}")
                        return error_text
                except Exception:
                    pass

                try:
                    js_result = self.driver.execute_script(
                        "var el = document.querySelector('div.common-prompt.am-alert-danger .prompt-msg'); return el ? el.textContent.trim() : '';"
                    )
                    if js_result:
                        logger.info(f"获取到错误提示(JS): {js_result}")
                        return js_result
                except Exception:
                    pass

        except Exception as e:
            logger.error(f"获取错误提示失败: {str(e)}", exc_info=True)

        logger.warning("未找到错误提示信息")
        return ""

    def is_add_to_cart_success(self):
        """
        判断加入购物车是否成功

        Returns:
            bool: 成功返回True，失败返回False
        """
        logger.info("判断加入购物车是否成功")
        success_msg = self.get_success_message(timeout=3)
        return "加入购物车成功" in success_msg or "加入成功" in success_msg

    def is_specs_container_displayed(self):
        """
        判断规格选择区域是否可见

        Returns:
            bool: 可见返回True，否则返回False
        """
        logger.info("判断规格选择区域是否可见")
        try:
            wait = self._get_wait(timeout=3)
            element = wait.until(EC.visibility_of_element_located(self.SPECS_CONTAINER))
            logger.info("规格选择区域已可见")
            return True
        except TimeoutException:
            logger.info("规格选择区域不可见")
            return False
        except Exception as e:
            logger.error(f"判断规格选择区域状态失败: {str(e)}", exc_info=True)
            return False

    def get_current_url(self):
        """
        获取当前页面URL

        Returns:
            str: 当前页面URL
        """
        logger.info("获取商品详情页面URL")
        url = self.driver.current_url
        logger.info(f"当前商品详情页面URL: {url}")
        return url
