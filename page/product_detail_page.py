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

    # 页面元素定位器
    # ================================================
    # 商品名称 - h1标签
    PRODUCT_NAME = (By.XPATH, "//h1[contains(@class, 'goods-title') or contains(@class, 'title')]")
    # 商品价格（table结构中的价格）
    PRODUCT_PRICE = (By.XPATH, "//td[contains(@class, 'item-price')]//span[contains(@class, 'value')]")
    # 原始价格（table结构中的原价）
    ORIGINAL_PRICE = (By.XPATH, "//td[contains(@class, 'item-original_price')]//span[contains(@class, 'value')]")
    # 规格选择区域容器（am-panel结构）
    SPECS_CONTAINER = (By.XPATH, "//div[contains(@class, 'am-panel') and contains(@class, 'am-panel-default')]")
    # 规格选项（table中的td链接）
    SPEC_OPTIONS = (By.XPATH, "//td[starts-with(@class, 'item-spec_value')]//a")
    # 选中的规格选项
    SELECTED_SPEC_OPTION = (By.XPATH, "//td[starts-with(@class, 'item-spec_value')]//a[contains(@class, 'selected') or contains(@class, 'active')]")
    # 加入购物车按钮 - 使用包含文本"加入购物车"的按钮
    ADD_TO_CART_BTN = (By.XPATH, "//button[contains(text(), '加入购物车')]")
    # 加入购物车按钮（备用：使用class定位）
    ADD_TO_CART_BTN_ALT = (By.XPATH, "//button[contains(@class, 'add-cart') or contains(@class, 'cart-btn')]")
    # 成功提示框
    SUCCESS_MSG = (By.XPATH, "//div[contains(@class, 'common-prompt') and contains(@class, 'am-alert-success')]//p[@class='prompt-msg']")
    # 成功提示框（备用）
    SUCCESS_MSG_ALT = (By.XPATH, "//div[contains(@class, 'am-alert-success')]")
    # 成功提示框（Toast消息）
    SUCCESS_MSG_TOAST = (By.XPATH, "//div[contains(@class, 'prompt') or contains(@class, 'toast') or contains(@class, 'msg')]")
    # 错误提示框
    ERROR_MSG = (By.XPATH, "//div[contains(@class, 'common-prompt') and contains(@class, 'am-alert-danger')]//p[@class='prompt-msg']")
    # 商品数量输入框
    QUANTITY_INPUT = (By.NAME, "num")
    # 减号按钮（数量）
    QUANTITY_MINUS = (By.XPATH, "//button[contains(@class, 'num-minus') or contains(text(), '-')]")
    # 加号按钮（数量）
    QUANTITY_PLUS = (By.XPATH, "//button[contains(@class, 'num-plus') or contains(text(), '+')]")
    # 规格表格中的加入购物车按钮
    ADD_TO_CART_BTN_TABLE = (By.XPATH, "//td[contains(@class, 'am-text-center')]//button[contains(text(), '加入购物车')]")
    # 规格表格中的加入购物车按钮（备用）
    ADD_TO_CART_BTN_TABLE_ALT = (By.XPATH, "//table[contains(@class, 'am-table')]//button[contains(text(), '加入购物车')]")

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

    def get_product_price(self):
        """
        获取商品当前价格（已选择规格后的价格）

        Returns:
            str: 商品价格，未找到返回空字符串
        """
        logger.info("获取商品当前价格")
        try:
            wait = self._get_wait()
            element = wait.until(EC.visibility_of_element_located(self.PRODUCT_PRICE))
            price = element.text.strip()
            logger.info(f"商品价格: {price}")
            return price
        except TimeoutException:
            logger.warning("未找到商品价格元素")
            return ""
        except Exception as e:
            logger.error(f"获取商品价格失败: {str(e)}", exc_info=True)
            return ""

    def get_original_price(self):
        """
        获取商品原始价格

        Returns:
            str: 原始价格，未找到返回空字符串
        """
        logger.info("获取商品原始价格")
        try:
            wait = self._get_wait(timeout=3)
            element = wait.until(EC.visibility_of_element_located(self.ORIGINAL_PRICE))
            price = element.text.strip()
            logger.info(f"商品原始价格: {price}")
            return price
        except TimeoutException:
            logger.warning("未找到商品原始价格元素")
            return ""
        except Exception as e:
            logger.error(f"获取商品原始价格失败: {str(e)}", exc_info=True)
            return ""

    def scroll_to_specs_container(self):
        """
        滚动到规格选择区域
        """
        logger.info("滚动到规格选择区域")
        try:
            wait = self._get_wait(timeout=5)
            element = wait.until(EC.presence_of_element_located(self.SPECS_CONTAINER))
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
            import time
            time.sleep(1)
            logger.info("已滚动到规格选择区域")
        except TimeoutException:
            logger.warning("未找到规格选择区域，跳过滚动")
        except Exception as e:
            logger.error(f"滚动到规格区域失败: {str(e)}", exc_info=True)

    def get_all_spec_options(self):
        """
        获取所有规格选项

        Returns:
            list: 规格选项列表，每个元素包含文本和是否可选
        """
        logger.info("获取所有规格选项")
        try:
            self.wait_page_loaded()
            self.scroll_to_specs_container()
            
            elements = self.driver.find_elements(*self.SPEC_OPTIONS)
            spec_options = []
            for element in elements:
                try:
                    text = element.text.strip()
                    if not text:
                        continue
                    is_disabled = "disabled" in element.get_attribute("class") or "not-available" in element.get_attribute("class")
                    is_selected = "selected" in element.get_attribute("class") or "active" in element.get_attribute("class")
                    href = element.get_attribute("href")
                    spec_options.append({
                        "text": text,
                        "is_disabled": is_disabled,
                        "is_selected": is_selected,
                        "element": element,
                        "href": href
                    })
                except StaleElementReferenceException:
                    logger.warning("获取规格选项时遇到StaleElementReferenceException，跳过")
                    continue
            logger.info(f"获取到规格选项列表: {[opt['text'] for opt in spec_options]}")
            return spec_options
        except Exception as e:
            logger.error(f"获取所有规格选项失败: {str(e)}", exc_info=True)
            return []

    def select_spec_option(self, spec_text):
        """
        选择指定规格选项

        Args:
            spec_text (str): 规格选项文本

        Returns:
            bool: 选择成功返回True，失败返回False
        """
        logger.info(f"选择规格选项: {spec_text}")
        try:
            spec_options = self.get_all_spec_options()
            for option in spec_options:
                if option["text"] == spec_text and not option["is_disabled"]:
                    self.driver.execute_script("arguments[0].removeAttribute('target');", option["element"])
                    self.driver.execute_script("arguments[0].removeAttribute('rel');", option["element"])
                    option["element"].click()
                    logger.info(f"规格选项 '{spec_text}' 选择成功")
                    return True
                elif option["text"] == spec_text and option["is_disabled"]:
                    logger.warning(f"规格选项 '{spec_text}' 不可选")
                    return False
            logger.warning(f"未找到规格选项: {spec_text}")
            return False
        except Exception as e:
            logger.error(f"选择规格选项失败: {str(e)}", exc_info=True)
            return False

    def select_first_available_spec(self):
        """
        选择第一个可用的规格选项

        Returns:
            str: 选中的规格文本，未找到返回空字符串
        """
        logger.info("选择第一个可用的规格选项")
        try:
            spec_options = self.get_all_spec_options()
            for option in spec_options:
                if not option["is_disabled"]:
                    self.driver.execute_script("arguments[0].removeAttribute('target');", option["element"])
                    self.driver.execute_script("arguments[0].removeAttribute('rel');", option["element"])
                    option["element"].click()
                    logger.info(f"选中规格选项: {option['text']}")
                    return option["text"]
            logger.warning("未找到可用的规格选项")
            return ""
        except Exception as e:
            logger.error(f"选择第一个可用规格失败: {str(e)}", exc_info=True)
            return ""

    def select_all_specs(self):
        """
        选择所有规格选项（点击第一个规格选项，因为每个规格链接已包含完整的规格组合）

        Returns:
            list: 选中的规格文本列表
        """
        logger.info("选择所有规格选项")
        try:
            spec_options = self.get_all_spec_options()
            
            if not spec_options:
                logger.warning("未找到规格选项")
                return []

            first_option = spec_options[0]
            if first_option["is_disabled"]:
                logger.warning("第一个规格选项不可选")
                return []

            self.driver.execute_script("arguments[0].removeAttribute('target');", first_option["element"])
            self.driver.execute_script("arguments[0].removeAttribute('rel');", first_option["element"])
            first_option["element"].click()
            
            import time
            time.sleep(2)
            
            self.wait_page_loaded()
            
            selected_specs = self.get_selected_specs()
            if not selected_specs:
                selected_specs = [first_option["text"]]
            
            logger.info(f"选中的规格列表: {selected_specs}")
            return selected_specs
        except Exception as e:
            logger.error(f"选择所有规格失败: {str(e)}", exc_info=True)
            return []

    def get_selected_specs(self):
        """
        获取已选中的规格选项

        Returns:
            list: 已选中的规格文本列表
        """
        logger.info("获取已选中的规格选项")
        try:
            elements = self.driver.find_elements(*self.SELECTED_SPEC_OPTION)
            selected_specs = [element.text.strip() for element in elements if element.text.strip()]
            logger.info(f"已选中的规格列表: {selected_specs}")
            return selected_specs
        except Exception as e:
            logger.error(f"获取已选中规格失败: {str(e)}", exc_info=True)
            return []

    def get_selected_specs_text(self):
        """
        获取已选中规格的文本（用于验证）

        Returns:
            str: 已选中规格的文本，多个规格用|分隔
        """
        logger.info("获取已选中规格的文本")
        try:
            selected_specs = self.get_selected_specs()
            if selected_specs:
                return "|".join(selected_specs)
            
            logger.info("未找到已选中的规格，尝试获取页面上的规格文本信息")
            try:
                spec_container = self.driver.find_element(*self.SPECS_CONTAINER)
                return spec_container.text
            except Exception:
                return ""
        except Exception as e:
            logger.error(f"获取已选中规格文本失败: {str(e)}", exc_info=True)
            return ""

    def get_quantity(self):
        """
        获取当前商品数量

        Returns:
            int: 当前数量，获取失败返回1
        """
        logger.info("获取当前商品数量")
        try:
            wait = self._get_wait(timeout=3)
            element = wait.until(EC.visibility_of_element_located(self.QUANTITY_INPUT))
            quantity = int(element.get_attribute("value"))
            logger.info(f"当前商品数量: {quantity}")
            return quantity
        except TimeoutException:
            logger.warning("未找到数量输入框，默认数量为1")
            return 1
        except Exception as e:
            logger.error(f"获取商品数量失败: {str(e)}", exc_info=True)
            return 1

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
            wait = self._get_wait()
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
        优先尝试表格中的按钮（规格选择后需要使用表格中的按钮）
        """
        logger.info("点击加入购物车按钮")
        try:
            self.scroll_to_specs_container()
            
            try:
                wait = self._get_wait(timeout=5)
                element = wait.until(EC.element_to_be_clickable(self.ADD_TO_CART_BTN_TABLE))
                element.click()
                logger.info("表格中的加入购物车按钮点击成功")
                return
            except TimeoutException:
                logger.info("表格中的加入购物车按钮定位失败，尝试主加入购物车按钮")
            
            wait = self._get_wait()
            element = wait.until(EC.element_to_be_clickable(self.ADD_TO_CART_BTN))
            element.click()
            logger.info("加入购物车按钮点击成功")
        except TimeoutException:
            logger.info("主加入购物车按钮定位失败，尝试备用定位器（class定位）")
            try:
                wait = self._get_wait()
                element = wait.until(EC.element_to_be_clickable(self.ADD_TO_CART_BTN_ALT))
                element.click()
                logger.info("备用加入购物车按钮点击成功")
            except TimeoutException:
                logger.error("加入购物车按钮等待超时")
                raise
            except Exception as e:
                logger.error(f"备用加入购物车按钮点击失败: {str(e)}", exc_info=True)
                raise
        except Exception as e:
            logger.error(f"点击加入购物车按钮失败: {str(e)}", exc_info=True)
            raise

    def add_to_cart(self, quantity=1, select_spec=True):
        """
        完整加入购物车流程

        Args:
            quantity (int): 商品数量，默认为1
            select_spec (bool): 是否自动选择规格，默认为True

        Returns:
            bool: 加入购物车成功返回True，失败返回False
        """
        logger.info(f"执行加入购物车操作，数量: {quantity}")
        try:
            self.wait_page_loaded()

            if select_spec:
                self.select_all_specs()

            self.scroll_to_specs_container()

            try:
                wait = self._get_wait(timeout=5)
                rows = wait.until(EC.presence_of_all_elements_located(
                    (By.XPATH, "//table[contains(@class, 'am-table')]//tbody//tr")
                ))
                
                if rows:
                    first_row = rows[0]
                    
                    plus_buttons = first_row.find_elements(By.XPATH, ".//button[@data-type='1']")
                    if plus_buttons:
                        for _ in range(quantity):
                            plus_buttons[0].click()
                            import time
                            time.sleep(0.2)
                        logger.info(f"已设置数量为: {quantity}")
                    else:
                        input_fields = first_row.find_elements(By.XPATH, ".//input[@type='number' or contains(@class, 'am-input-number-input')]")
                        if input_fields:
                            input_fields[0].clear()
                            input_fields[0].send_keys(str(quantity))
                            logger.info(f"已设置数量为: {quantity}")

                    cart_btns = first_row.find_elements(By.XPATH, ".//button[contains(text(), '加入购物车')]")
                    if cart_btns:
                        cart_btns[0].click()
                        logger.info("表格中第一行规格的加入购物车按钮点击成功")
                    else:
                        logger.info("未找到表格中第一行的加入购物车按钮，尝试使用表格中的任意加入购物车按钮")
                        try:
                            all_table_cart_btns = self.driver.find_elements(*self.ADD_TO_CART_BTN_TABLE_ALT)
                            if all_table_cart_btns:
                                all_table_cart_btns[0].click()
                                logger.info("表格中的加入购物车按钮点击成功")
                            else:
                                logger.warning("未找到表格中的加入购物车按钮")
                                self.click_add_to_cart()
                        except Exception:
                            logger.warning("表格按钮定位失败")
                            self.click_add_to_cart()
                else:
                    logger.warning("未找到规格表格行")
                    self.click_add_to_cart()
            except Exception as e:
                logger.info(f"表格加入购物车失败，尝试普通加入购物车: {str(e)}")
                self.click_add_to_cart()

            success_msg = self.get_success_message(timeout=5)
            if success_msg and ("加入购物车成功" in success_msg or "加入成功" in success_msg):
                logger.info(f"加入购物车成功，提示: {success_msg}")
                return True

            error_msg = self.get_error_message(timeout=2)
            if error_msg:
                logger.error(f"加入购物车失败: {error_msg}")
                return False

            logger.warning("未收到加入购物车结果提示")
            return False
        except Exception as e:
            logger.error(f"加入购物车操作失败: {str(e)}", exc_info=True)
            return False

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
            for _ in range(5):
                import time
                time.sleep(0.5)
                
                js_result = self.driver.execute_script(
                    "return Array.from(document.querySelectorAll('div, span')).filter(el => el.textContent && (el.textContent.includes('成功') || el.textContent.includes('加入') || el.textContent.includes('购买') || el.textContent.includes('台'))).map(el => el.textContent.trim()).slice(0, 3);"
                )
                if js_result and len(js_result) > 0:
                    for msg in js_result:
                        if msg and len(msg) < 50 and not msg.startswith('https'):
                            logger.info(f"获取到成功提示(JS): {msg}")
                            return msg

                elements = self.driver.find_elements(*self.SUCCESS_MSG_TOAST)
                for elem in elements:
                    text = elem.text.strip()
                    if text and ("成功" in text or "加入" in text or "购买" in text):
                        logger.info(f"获取到成功提示(Toast): {text}")
                        return text

            try:
                wait = WebDriverWait(self.driver, timeout=timeout)
                element = wait.until(EC.visibility_of_element_located(self.SUCCESS_MSG))
                success_text = element.text.strip()
                logger.info(f"获取到成功提示: {success_text}")
                return success_text
            except TimeoutException:
                pass

            try:
                wait = WebDriverWait(self.driver, timeout=timeout)
                element = wait.until(EC.visibility_of_element_located(self.SUCCESS_MSG_ALT))
                success_text = element.text.strip()
                logger.info(f"获取到成功提示(备用): {success_text}")
                return success_text
            except TimeoutException:
                pass

        except Exception as e:
            logger.error(f"获取成功提示失败: {str(e)}", exc_info=True)

        logger.warning("未找到成功提示信息")
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

    def is_add_to_cart_success(self):
        """
        判断加入购物车是否成功

        Returns:
            bool: 成功返回True，失败返回False
        """
        logger.info("判断加入购物车是否成功")
        success_msg = self.get_success_message(timeout=3)
        return "加入购物车成功" in success_msg

    def is_add_to_cart_enabled(self):
        """
        判断加入购物车按钮是否可用（未被禁用）

        Returns:
            bool: 可用返回True，否则返回False
        """
        logger.info("判断加入购物车按钮是否可用")
        try:
            wait = self._get_wait(timeout=3)
            
            try:
                element = wait.until(EC.element_to_be_clickable(self.ADD_TO_CART_BTN))
                is_enabled = element.is_enabled()
                logger.info(f"加入购物车按钮可用状态: {is_enabled}")
                return is_enabled
            except TimeoutException:
                logger.info("主加入购物车按钮定位失败，尝试备用定位器（表格中的按钮）")
                try:
                    self.scroll_to_specs_container()
                    element = wait.until(EC.element_to_be_clickable(self.ADD_TO_CART_BTN_TABLE))
                    is_enabled = element.is_enabled()
                    logger.info(f"表格中加入购物车按钮可用状态: {is_enabled}")
                    return is_enabled
                except TimeoutException:
                    logger.info("表格加入购物车按钮定位失败，尝试备用定位器（class定位）")
                    try:
                        element = wait.until(EC.element_to_be_clickable(self.ADD_TO_CART_BTN_ALT))
                        is_enabled = element.is_enabled()
                        logger.info(f"备用加入购物车按钮可用状态: {is_enabled}")
                        return is_enabled
                    except TimeoutException:
                        logger.warning("未找到加入购物车按钮")
                        return False
        except Exception as e:
            logger.error(f"判断加入购物车按钮可用性失败: {str(e)}", exc_info=True)
            return False

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