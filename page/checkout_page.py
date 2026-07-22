import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from base.WebDriverBase import WebDriverBase
from utils.log_util import logger


class CheckoutPage:
    """
    结算页面对象类
    封装结算页面的元素定位和操作方法
    页面结构：收货地址区域 -> 商品信息区域(goods-detail) -> 支付方式区域 -> 提交订单按钮
    """

    # 页面元素定位器
    # ================================================
    # 结算页面标题
    CHECKOUT_TITLE = (By.XPATH, "//h1[contains(text(), '确认订单') or contains(text(), '订单确认')]")

    # 收货地址区域
    # 默认地址容器（实际为ul标签）
    ADDRESS_CONTAINER = (By.XPATH, "//ul[@class='address-list']")
    ADDRESS_CONTAINER_ALT = (By.XPATH, "//ul[contains(@class, 'address-list')]")
    # 默认选中的地址（li标签，class包含address-default）
    DEFAULT_ADDRESS = (By.XPATH, "//ul[@class='address-list']//li[contains(@class, 'address-default')]")
    DEFAULT_ADDRESS_ALT = (By.XPATH, "//ul[contains(@class, 'address-list')]//li[@class='address-cart address-default']")
    # 默认地址radio按钮（实际结构中没有radio，通过li的address-default class判断）
    DEFAULT_ADDRESS_RADIO = (By.XPATH, "//ul[@class='address-list']//li[contains(@class, 'address-default')]")
    # 地址信息（姓名、电话、地址）
    ADDRESS_INFO = (By.XPATH, "//ul[@class='address-list']//li[contains(@class, 'address-default')]//div[@class='address-content']")
    # 收货人姓名（实际class为user）- 相对路径
    ADDRESS_NAME = (By.XPATH, ".//span[@class='user']")
    ADDRESS_NAME_ALT = (By.XPATH, ".//span[@class='address-detail']//span[not(@class='phone')]")
    # 收货人电话（实际class为phone）- 相对路径
    ADDRESS_PHONE = (By.XPATH, ".//span[@class='phone']")
    ADDRESS_PHONE_ALT = (By.XPATH, ".//span[@class='address-detail']//span[@class='phone']")
    # 收货地址详情（实际结构中在region div内）- 相对路径
    ADDRESS_DETAIL = (By.XPATH, ".//div[contains(@class, 'region')]")
    ADDRESS_DETAIL_ALT = (By.XPATH, ".//div[@class='address-content']//div[contains(@class, 'region')]")

    # 商品信息区域
    # 商品详情容器列表（结算页面商品行）
    GOODS_DETAIL_LIST = (By.XPATH, "//div[@class='goods-detail']")
    # 商品标题（相对于goods-detail，在goods-base容器内）
    GOODS_TITLE = (By.XPATH, ".//div[@class='goods-base']//a[@class='goods-title']")
    GOODS_TITLE_ALT = (By.XPATH, ".//div[@class='goods-base']//a")
    # 商品图片
    GOODS_IMAGE = (By.XPATH, ".//img")
    # 商品规格信息
    GOODS_SPEC = (By.XPATH, ".//div[@class='goods-base']//p")
    GOODS_SPEC_ALT = (By.XPATH, ".//ul[@class='goods-attr']")
    
    # 结算页面商品行（包含价格、数量的完整行）- tr标签，带data-id属性
    ORDER_ITEM_ROWS = (By.XPATH, "//tr[@data-id]")
    ORDER_ITEM_ROWS_ALT = (By.XPATH, "//div[@class='order-goods']//tr")
    ORDER_ITEM_ROWS_ALT2 = (By.XPATH, "//table//tr[td[@class='base']]")
    # 商品单价（结算页面价格，td class包含am-color-666且非数量列，p标签class=original-price）
    ORDER_ITEM_PRICE = (By.XPATH, ".//td[@class='am-hide-sm-only am-color-666' and not(contains(@class, 'number'))]//p[@class='original-price']")
    ORDER_ITEM_PRICE_ALT = (By.XPATH, ".//td[@class='am-hide-sm-only am-color-666' and not(contains(@class, 'number'))]")
    # 商品数量（结算页面数量，td class=number）
    ORDER_ITEM_QUANTITY = (By.XPATH, ".//td[@class='number']//span")
    ORDER_ITEM_QUANTITY_ALT = (By.XPATH, ".//td[@class='number']")
    # 商品小计（结算页面小计，td class包含total-price）
    ORDER_ITEM_SUBTOTAL = (By.XPATH, ".//td[contains(@class, 'total-price')]")
    ORDER_ITEM_SUBTOTAL_ALT = (By.XPATH, ".//td[contains(@class, 'total-price')]//strong[@class='total-price-content']")

    # 订单信息区域
    # 订单号
    ORDER_NO = (By.XPATH, "//div[@class='order-info']//span[contains(text(), '订单号')]/following-sibling::span")
    # 订单时间
    ORDER_TIME = (By.XPATH, "//div[@class='order-info']//span[contains(text(), '下单时间')]/following-sibling::span")

    # 支付方式区域
    # 支付方式容器（实际为div标签，business-item结构）
    PAYMENT_CONTAINER = (By.XPATH, "//div[@class='business-item']")
    PAYMENT_CONTAINER_ALT = (By.XPATH, "//div[contains(@class, 'business-item')]")
    PAYMENT_CONTAINER_ALT2 = (By.XPATH, "//ul[@class='payment-list']")
    PAYMENT_CONTAINER_ALT3 = (By.XPATH, "//ul[contains(@class, 'payment-list')]")
    # 支付方式选项列表（实际为div标签，business-item结构）
    PAYMENT_OPTIONS = (By.XPATH, "//div[@class='business-item']")
    PAYMENT_OPTIONS_ALT = (By.XPATH, "//div[contains(@class, 'business-item')]")
    PAYMENT_OPTIONS_ALT2 = (By.XPATH, "//ul[@class='payment-list']//li")
    PAYMENT_OPTIONS_ALT3 = (By.XPATH, "//ul[contains(@class, 'payment-list')]//li")
    # 微信支付选项
    PAYMENT_WECHAT = (By.XPATH, "//div[@class='business-item'][contains(span, '微信')]")
    PAYMENT_WECHAT_ALT = (By.XPATH, "//div[contains(@class, 'business-item')][contains(span, '微信')]")
    PAYMENT_WECHAT_ALT2 = (By.XPATH, "//ul[@class='payment-list']//li[contains(text(), '微信')]")
    # 支付宝支付选项
    PAYMENT_ALIPAY = (By.XPATH, "//div[@class='business-item'][contains(span, '支付宝')]")
    PAYMENT_ALIPAY_ALT = (By.XPATH, "//div[contains(@class, 'business-item')][contains(span, '支付宝')]")
    PAYMENT_ALIPAY_ALT2 = (By.XPATH, "//ul[@class='payment-list']//li[contains(text(), '支付宝')]")
    # 现金支付选项
    PAYMENT_CASH = (By.XPATH, "//div[@class='business-item'][contains(span, '现金')]")
    PAYMENT_CASH_ALT = (By.XPATH, "//div[contains(@class, 'business-item')][contains(span, '现金')]")
    PAYMENT_CASH_ALT2 = (By.XPATH, "//ul[@class='payment-list']//li[contains(text(), '现金')]")
    # 银行卡支付选项
    PAYMENT_BANK = (By.XPATH, "//div[@class='business-item'][contains(span, '银行卡')]")
    PAYMENT_BANK_ALT = (By.XPATH, "//div[contains(@class, 'business-item')][contains(span, '银行卡')]")
    PAYMENT_BANK_ALT2 = (By.XPATH, "//ul[@class='payment-list']//li[contains(text(), '银行卡')]")
    # 默认选中的支付方式（实际通过icon-subscript图标判断）
    SELECTED_PAYMENT = (By.XPATH, "//div[@class='business-item' and .//i[@class='iconfont icon-subscript']]")
    SELECTED_PAYMENT_ALT = (By.XPATH, "//div[contains(@class, 'business-item') and .//i[@class='iconfont icon-subscript']]")
    SELECTED_PAYMENT_ALT2 = (By.XPATH, "//ul[@class='payment-list']//li[contains(@class, 'am-active')]")
    SELECTED_PAYMENT_ALT3 = (By.XPATH, "//ul[contains(@class, 'payment-list')]//li[contains(@class, 'am-active')]")

    # 金额信息
    # 商品总金额
    GOODS_TOTAL_AMOUNT = (By.XPATH, "//*[contains(text(), '商品金额')]/following-sibling::span")
    # 运费
    SHIPPING_FEE = (By.XPATH, "//*[contains(text(), '运费')]/following-sibling::span")
    # 优惠金额
    DISCOUNT_AMOUNT = (By.XPATH, "//*[contains(text(), '优惠')]/following-sibling::span")
    # 实付金额
    ACTUAL_PAYMENT = (By.XPATH, "//*[contains(text(), '实付')]/following-sibling::span")
    # 底部实付金额（大字体）
    BOTTOM_ACTUAL_PAYMENT = (By.XPATH, "//span[@class='order-actual']")
    BOTTOM_ACTUAL_PAYMENT_ALT = (By.XPATH, "//strong[@class='total-price-content']")
    BOTTOM_ACTUAL_PAYMENT_ALT2 = (By.XPATH, "//*[@class='nav-total-price']")

    # 提交订单按钮
    SUBMIT_ORDER_BTN = (By.XPATH, "//button[@class='am-btn am-btn-primary am-btn-lg am-radius btn-loading-example buy-submit' and contains(text(), '提交订单')]")
    SUBMIT_ORDER_BTN_ALT = (By.XPATH, "//button[contains(@class, 'buy-submit') and contains(text(), '提交订单')]")
    SUBMIT_ORDER_BTN_ALT2 = (By.XPATH, "//button[contains(text(), '提交订单')]")

    # 支付成功页元素
    # 支付成功标题
    PAY_SUCCESS_TITLE = (By.XPATH, "//h1[contains(text(), '支付成功')]")
    # 支付成功提示信息
    PAY_SUCCESS_MSG = (By.XPATH, "//div[contains(@class, 'pay-success')]//p")
    # 我的订单按钮
    MY_ORDER_BTN = (By.XPATH, "//a[contains(@class, 'am-btn-primary') and contains(text(), '我的订单')]")
    # 继续购物按钮
    CONTINUE_SHOPPING_BTN = (By.XPATH, "//a[contains(@class, 'am-btn-secondary') and contains(text(), '继续购物')]")

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
        if timeout is not None:
            wait_time = timeout
        else:
            wait_time = self.browser_config.get("explicit_wait", 15)
        poll_frequency = self.browser_config.get("poll_frequency", 500) / 1000

        self._wait = WebDriverWait(
            self.driver,
            timeout=wait_time,
            poll_frequency=poll_frequency,
            ignored_exceptions=[NoSuchElementException]
        )
        return self._wait

    def is_checkout_page_displayed(self, timeout=5):
        """
        判断结算页面是否已显示

        Args:
            timeout (int): 超时时间，默认5秒

        Returns:
            bool: 结算页面已显示返回True，否则返回False
        """
        logger.info("判断结算页面是否已显示")
        try:
            page_locators = [
                self.CHECKOUT_TITLE,
                self.ADDRESS_CONTAINER,
                self.GOODS_DETAIL_LIST,
                self.SUBMIT_ORDER_BTN,
                (By.XPATH, "//*[contains(text(), '确认订单')]"),
            ]

            for by, selector in page_locators:
                try:
                    wait = self._get_wait(timeout=timeout)
                    element = wait.until(EC.visibility_of_element_located((by, selector)))
                    logger.info(f"结算页面已显示，定位器: {selector}")
                    return True
                except TimeoutException:
                    continue

            current_url = self.driver.current_url
            if "order" in current_url.lower():
                logger.info(f"URL包含订单相关路径: {current_url}")
                return True

            logger.info(f"未跳转到结算页面，当前URL: {current_url}")
            return False
        except Exception as e:
            logger.error(f"判断结算页面状态失败: {str(e)}", exc_info=True)
            return False

    def get_checkout_products(self):
        """
        获取结算页面中所有商品信息

        Returns:
            list: 商品信息列表，每个元素为字典，包含name、price、quantity、subtotal
        """
        logger.info("获取结算页面商品信息")
        products = []

        try:
            wait = self._get_wait(timeout=3)
            
            order_row_locators = [
                self.ORDER_ITEM_ROWS,
                self.ORDER_ITEM_ROWS_ALT,
                self.ORDER_ITEM_ROWS_ALT2,
            ]
            
            order_rows = None
            for by, selector in order_row_locators:
                try:
                    order_rows = wait.until(EC.visibility_of_all_elements_located((by, selector)))
                    if order_rows:
                        logger.info(f"找到 {len(order_rows)} 个商品行，定位器: {selector}")
                        break
                except TimeoutException:
                    continue
            
            if not order_rows:
                logger.warning("未找到结算页商品行")
                return products

            self.driver.implicitly_wait(0)

            for index, order_row in enumerate(order_rows):
                try:
                    product_info = {}

                    try:
                        goods_element = order_row.find_element(*self.GOODS_DETAIL_LIST)
                        
                        try:
                            name_element = goods_element.find_element(*self.GOODS_TITLE)
                            product_info["name"] = name_element.text.strip()
                        except NoSuchElementException:
                            try:
                                name_element = goods_element.find_element(*self.GOODS_TITLE_ALT)
                                product_info["name"] = name_element.text.strip()
                            except NoSuchElementException:
                                product_info["name"] = ""

                        try:
                            spec_element = goods_element.find_element(*self.GOODS_SPEC)
                            product_info["spec"] = spec_element.text.strip()
                        except NoSuchElementException:
                            try:
                                spec_element = goods_element.find_element(*self.GOODS_SPEC_ALT)
                                spec_element_text = ""
                                li_elements = spec_element.find_elements(By.TAG_NAME, "li")
                                for li in li_elements:
                                    if spec_element_text:
                                        spec_element_text += ", "
                                    spec_element_text += li.text.strip()
                                product_info["spec"] = spec_element_text
                            except NoSuchElementException:
                                product_info["spec"] = ""
                    except NoSuchElementException:
                        product_info["name"] = ""
                        product_info["spec"] = ""

                    price_locators = [
                        self.ORDER_ITEM_PRICE,
                        self.ORDER_ITEM_PRICE_ALT,
                    ]
                    for by, selector in price_locators:
                        try:
                            price_element = order_row.find_element(by, selector)
                            price_text = price_element.text.strip()
                            if price_text and (price_text.startswith('¥') or price_text.startswith('￥')):
                                product_info["price"] = price_text
                                break
                        except NoSuchElementException:
                            continue
                    if "price" not in product_info:
                        product_info["price"] = ""

                    quantity_locators = [
                        self.ORDER_ITEM_QUANTITY,
                        self.ORDER_ITEM_QUANTITY_ALT,
                    ]
                    for by, selector in quantity_locators:
                        try:
                            quantity_element = order_row.find_element(by, selector)
                            quantity_text = quantity_element.text.strip()
                            import re
                            match = re.search(r'(\d+)', quantity_text)
                            if match:
                                product_info["quantity"] = int(match.group(1))
                                break
                        except (NoSuchElementException, ValueError):
                            continue
                    if "quantity" not in product_info:
                        product_info["quantity"] = 1

                    subtotal_locators = [
                        self.ORDER_ITEM_SUBTOTAL,
                        self.ORDER_ITEM_SUBTOTAL_ALT,
                    ]
                    for by, selector in subtotal_locators:
                        try:
                            subtotal_element = order_row.find_element(by, selector)
                            subtotal_text = subtotal_element.text.strip()
                            if subtotal_text and (subtotal_text.startswith('¥') or subtotal_text.startswith('￥')):
                                product_info["subtotal"] = subtotal_text
                                break
                        except NoSuchElementException:
                            continue
                    if "subtotal" not in product_info:
                        product_info["subtotal"] = ""

                    products.append(product_info)
                    logger.info(f"结算页商品{index+1}: {product_info['name']}, 单价: {product_info['price']}, "
                                f"数量: {product_info['quantity']}, 小计: {product_info['subtotal']}")
                except Exception as e:
                    logger.error(f"获取结算页商品{index+1}信息失败: {str(e)}", exc_info=True)
                    continue

            self.driver.implicitly_wait(self.browser_config.get("implicit_wait", 10))

        except TimeoutException:
            logger.warning("未找到结算页商品列表")
        except Exception as e:
            logger.error(f"获取结算页商品信息失败: {str(e)}", exc_info=True)

        return products

    def is_default_address_selected(self, timeout=3):
        """
        判断是否已默认选中收货地址

        Args:
            timeout (int): 超时时间，默认3秒

        Returns:
            bool: 已默认选中地址返回True，否则返回False
        """
        logger.info("判断是否已默认选中收货地址")
        try:
            address_locators = [
                self.DEFAULT_ADDRESS,
                self.DEFAULT_ADDRESS_ALT,
                self.DEFAULT_ADDRESS_RADIO,
                (By.XPATH, "//ul[contains(@class, 'address-list')]//li[contains(@class, 'address-default')]"),
            ]

            for by, selector in address_locators:
                try:
                    wait = self._get_wait(timeout=timeout)
                    element = wait.until(EC.visibility_of_element_located((by, selector)))
                    logger.info(f"默认收货地址已选中，定位器: {selector}")
                    return True
                except TimeoutException:
                    continue

            logger.info("未找到默认选中的收货地址")
            return False
        except Exception as e:
            logger.error(f"判断默认地址状态失败: {str(e)}", exc_info=True)
            return False

    def get_default_address_info(self):
        """
        获取默认收货地址信息

        Returns:
            dict: 地址信息字典，包含name、phone、detail，失败返回空字典
        """
        logger.info("获取默认收货地址信息")
        address_info = {}

        try:
            wait = self._get_wait(timeout=3)
            
            address_container_locators = [
                self.ADDRESS_CONTAINER,
                self.ADDRESS_CONTAINER_ALT,
            ]
            
            address_container = None
            for by, selector in address_container_locators:
                try:
                    address_container = wait.until(EC.visibility_of_element_located((by, selector)))
                    break
                except TimeoutException:
                    continue
            
            if not address_container:
                logger.warning("未找到地址容器")
                return address_info

            name_locators = [
                self.ADDRESS_NAME,
                self.ADDRESS_NAME_ALT,
            ]
            for by, selector in name_locators:
                try:
                    name_element = address_container.find_element(by, selector)
                    address_info["name"] = name_element.text.strip()
                    break
                except NoSuchElementException:
                    continue
            if "name" not in address_info:
                address_info["name"] = ""

            phone_locators = [
                self.ADDRESS_PHONE,
                self.ADDRESS_PHONE_ALT,
            ]
            for by, selector in phone_locators:
                try:
                    phone_element = address_container.find_element(by, selector)
                    address_info["phone"] = phone_element.text.strip()
                    break
                except NoSuchElementException:
                    continue
            if "phone" not in address_info:
                address_info["phone"] = ""

            detail_locators = [
                self.ADDRESS_DETAIL,
                self.ADDRESS_DETAIL_ALT,
            ]
            for by, selector in detail_locators:
                try:
                    detail_element = address_container.find_element(by, selector)
                    address_info["detail"] = detail_element.text.strip()
                    break
                except NoSuchElementException:
                    continue
            if "detail" not in address_info:
                address_info["detail"] = ""

            logger.info(f"默认收货地址信息: 姓名={address_info['name']}, 电话={address_info['phone']}, "
                        f"地址={address_info['detail']}")

        except Exception as e:
            logger.error(f"获取默认收货地址信息失败: {str(e)}", exc_info=True)

        return address_info

    def get_selected_payment_method(self):
        """
        获取当前选中的支付方式

        Returns:
            str: 支付方式名称，失败返回空字符串
        """
        logger.info("获取当前选中的支付方式")
        try:
            js_script = """
                var businessItems = document.querySelectorAll('div.business-item');
                if (businessItems.length > 0) {
                    for (var i = 0; i < businessItems.length; i++) {
                        var item = businessItems[i];
                        var icon = item.querySelector('i.iconfont');
                        if (icon) {
                            var iconStyle = window.getComputedStyle(icon);
                            if (iconStyle.display === 'block') {
                                var span = item.querySelector('span');
                                return span ? span.textContent.trim() : '';
                            }
                        }
                    }
                    for (var j = 0; j < businessItems.length; j++) {
                        var item = businessItems[j];
                        var style = window.getComputedStyle(item);
                        if (style.borderColor.indexOf('226, 44, 8') !== -1 || style.borderColor.indexOf('226,44,8') !== -1) {
                            var span = item.querySelector('span');
                            return span ? span.textContent.trim() : '';
                        }
                    }
                    var firstSpan = businessItems[0].querySelector('span');
                    return firstSpan ? firstSpan.textContent.trim() : '';
                }
                return '';
            """
            selected_text = self.driver.execute_script(js_script)
            
            if selected_text:
                logger.info(f"当前选中的支付方式: {selected_text}")
                return selected_text
            
            wait = self._get_wait(timeout=3)
            
            selected_payment_locators = [
                self.SELECTED_PAYMENT,
                self.SELECTED_PAYMENT_ALT,
                self.SELECTED_PAYMENT_ALT2,
                self.SELECTED_PAYMENT_ALT3,
            ]
            
            selected_element = None
            for by, selector in selected_payment_locators:
                try:
                    selected_element = wait.until(EC.visibility_of_element_located((by, selector)))
                    break
                except TimeoutException:
                    continue
            
            if selected_element:
                payment_text = selected_element.text.strip()
                logger.info(f"当前选中的支付方式: {payment_text}")
                return payment_text

            payment_options_locators = [
                self.PAYMENT_OPTIONS,
                self.PAYMENT_OPTIONS_ALT,
                self.PAYMENT_OPTIONS_ALT2,
                self.PAYMENT_OPTIONS_ALT3,
            ]
            
            payment_options = None
            for by, selector in payment_options_locators:
                try:
                    payment_options = wait.until(EC.visibility_of_all_elements_located((by, selector)))
                    break
                except TimeoutException:
                    continue
            
            if payment_options:
                for option in payment_options:
                    try:
                        option_text = option.text.strip()
                        if option_text:
                            logger.info(f"找到支付方式选项: {option_text}")
                            return option_text
                    except Exception:
                        continue

            return ""
        except Exception as e:
            logger.error(f"获取选中支付方式失败: {str(e)}", exc_info=True)
            return ""

    def select_payment_method(self, payment_name):
        """
        选择支付方式

        Args:
            payment_name (str): 支付方式名称（微信支付、支付宝、银行卡等）

        Returns:
            bool: 选择成功返回True，否则返回False
        """
        logger.info(f"选择支付方式: {payment_name}")
        try:
            wait = self._get_wait(timeout=3)
            wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'business-item')]")))
            
            js_select_script = f"""
                var businessItems = document.querySelectorAll('div.business-item');
                for (var i = 0; i < businessItems.length; i++) {{
                    var item = businessItems[i];
                    var span = item.querySelector('span');
                    if (span && span.textContent.trim().indexOf('{payment_name}') !== -1) {{
                        item.scrollIntoView({{behavior: 'smooth', block: 'center'}});
                        item.click();
                        return true;
                    }}
                }}
                return false;
            """
            
            js_result = self.driver.execute_script(js_select_script)
            if js_result:
                time.sleep(0.5)
                
                verify_script = f"""
                    var businessItems = document.querySelectorAll('div.business-item');
                    for (var i = 0; i < businessItems.length; i++) {{
                        var item = businessItems[i];
                        var span = item.querySelector('span');
                        var icon = item.querySelector('i.iconfont');
                        if (span && span.textContent.trim().indexOf('{payment_name}') !== -1) {{
                            return icon && icon.classList.contains('icon-subscript');
                        }}
                    }}
                    return false;
                """
                
                for _ in range(3):
                    is_selected = self.driver.execute_script(verify_script)
                    if is_selected:
                        logger.info(f"支付方式 '{payment_name}' 选择成功")
                        return True
                    time.sleep(0.3)
                
                logger.info(f"支付方式 '{payment_name}' 选择成功（未验证图标状态）")
                return True
            
            payment_options_locators = [
                self.PAYMENT_OPTIONS,
                self.PAYMENT_OPTIONS_ALT,
                self.PAYMENT_OPTIONS_ALT2,
                self.PAYMENT_OPTIONS_ALT3,
            ]
            
            payment_options = None
            for by, selector in payment_options_locators:
                try:
                    payment_options = wait.until(EC.visibility_of_all_elements_located((by, selector)))
                    logger.info(f"找到支付方式选项，定位器: {selector}")
                    break
                except TimeoutException:
                    continue
            
            if not payment_options:
                logger.warning("未找到支付方式选项")
                return False

            for option in payment_options:
                try:
                    option_text = option.text.strip()
                    logger.info(f"检查支付方式选项: {option_text}")
                    if payment_name in option_text:
                        self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", option)
                        time.sleep(0.3)
                        self.driver.execute_script("arguments[0].click();", option)
                        time.sleep(0.5)
                        logger.info(f"支付方式 '{payment_name}' 选择成功")
                        return True
                except Exception:
                    continue

            logger.warning(f"未找到支付方式: {payment_name}")
            return False
        except Exception as e:
            logger.error(f"选择支付方式失败: {str(e)}", exc_info=True)
            return False

    def get_total_amount(self):
        """
        获取结算页面总金额

        Returns:
            str: 总金额字符串，失败返回空字符串
        """
        logger.info("获取结算页面总金额")
        try:
            total_amount_locators = [
                self.BOTTOM_ACTUAL_PAYMENT,
                self.BOTTOM_ACTUAL_PAYMENT_ALT,
                self.BOTTOM_ACTUAL_PAYMENT_ALT2,
                self.ACTUAL_PAYMENT,
                (By.XPATH, "//strong[@class='total-price-content']"),
                (By.XPATH, "//*[@class='nav-total-price']"),
                (By.XPATH, "//*[contains(text(), '￥') and contains(@class, 'price')]"),
            ]

            for by, selector in total_amount_locators:
                try:
                    wait = self._get_wait(timeout=2)
                    total_amount_element = wait.until(EC.visibility_of_element_located((by, selector)))
                    total_amount = total_amount_element.text.strip()
                    if total_amount and (total_amount.startswith('¥') or total_amount.startswith('￥')):
                        logger.info(f"结算页总金额: {total_amount}")
                        return total_amount
                except TimeoutException:
                    continue
                except Exception as e:
                    logger.warning(f"尝试定位器 {selector} 失败: {str(e)}")
                    continue

            logger.error("未找到总金额元素")
            return ""
        except Exception as e:
            logger.error(f"获取总金额失败: {str(e)}", exc_info=True)
            return ""

    def click_submit_order(self):
        """
        点击提交订单按钮

        Returns:
            bool: 点击成功返回True，否则返回False
        """
        logger.info("点击提交订单按钮")
        try:
            wait = self._get_wait()
            submit_btn_locators = [
                self.SUBMIT_ORDER_BTN,
                self.SUBMIT_ORDER_BTN_ALT,
                self.SUBMIT_ORDER_BTN_ALT2,
                (By.ID, "submit-btn"),
                (By.XPATH, "//button[contains(@class, 'buy-submit')]"),
            ]

            for by, selector in submit_btn_locators:
                try:
                    submit_btn = wait.until(EC.element_to_be_clickable((by, selector)))
                    self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", submit_btn)
                    time.sleep(0.3)
                    submit_btn.click()
                    logger.info(f"提交订单按钮已点击，定位器: {selector}")
                    return True
                except TimeoutException:
                    continue
                except Exception as e:
                    logger.warning(f"尝试定位器 {selector} 失败: {str(e)}")
                    continue

            logger.error("未找到提交订单按钮")
            return False
        except Exception as e:
            logger.error(f"点击提交订单按钮失败: {str(e)}", exc_info=True)
            return False

    def is_pay_success_page_displayed(self, timeout=10):
        """
        判断是否已跳转到支付成功页面

        Args:
            timeout (int): 超时时间，默认10秒

        Returns:
            bool: 支付成功页面已显示返回True，否则返回False
        """
        logger.info("判断是否跳转到支付成功页面")
        try:
            success_locators = [
                self.PAY_SUCCESS_TITLE,
                self.PAY_SUCCESS_MSG,
                self.MY_ORDER_BTN,
                (By.XPATH, "//*[contains(text(), '支付成功')]"),
                (By.XPATH, "//div[contains(@class, 'pay-success')]"),
            ]

            for by, selector in success_locators:
                try:
                    wait = self._get_wait(timeout=timeout)
                    element = wait.until(EC.visibility_of_element_located((by, selector)))
                    logger.info(f"支付成功页面已显示，定位器: {selector}")
                    return True
                except TimeoutException:
                    continue
                except Exception as e:
                    logger.warning(f"尝试定位器 {selector} 失败: {str(e)}")
                    continue

            current_url = self.driver.current_url
            if "success" in current_url.lower() or "pay" in current_url.lower():
                logger.info(f"URL包含支付成功相关路径: {current_url}")
                return True

            logger.info(f"未跳转到支付成功页面，当前URL: {current_url}")
            return False
        except Exception as e:
            logger.error(f"判断支付成功页面状态失败: {str(e)}", exc_info=True)
            return False

    def click_my_order_btn(self):
        """
        点击支付成功页的"我的订单"按钮

        Returns:
            bool: 点击成功返回True，否则返回False
        """
        logger.info("点击我的订单按钮")
        try:
            wait = self._get_wait(timeout=5)
            my_order_btn_locators = [
                self.MY_ORDER_BTN,
                (By.XPATH, "//a[contains(text(), '我的订单')]"),
                (By.XPATH, "//a[@href='?s=order/index.html']"),
            ]

            for by, selector in my_order_btn_locators:
                try:
                    my_order_btn = wait.until(EC.element_to_be_clickable((by, selector)))
                    self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", my_order_btn)
                    time.sleep(0.3)
                    my_order_btn.click()
                    logger.info(f"我的订单按钮已点击，定位器: {selector}")
                    return True
                except TimeoutException:
                    continue
                except Exception as e:
                    logger.warning(f"尝试定位器 {selector} 失败: {str(e)}")
                    continue

            logger.error("未找到我的订单按钮")
            return False
        except Exception as e:
            logger.error(f"点击我的订单按钮失败: {str(e)}", exc_info=True)
            return False

    def get_prompt_message(self):
        """
        获取提示信息内容

        Returns:
            str: 提示信息文本，失败返回空字符串
        """
        logger.info("获取提示信息")
        try:
            wait = self._get_wait(timeout=2)
            prompt_msg_locators = [
                (By.XPATH, "//div[@class='common-prompt']//p[@class='prompt-msg']"),
                (By.XPATH, "//div[contains(@class, 'common-prompt')]//p[contains(@class, 'prompt-msg')]"),
                (By.XPATH, "//div[contains(@class, 'am-alert')]//p"),
            ]

            for by, selector in prompt_msg_locators:
                try:
                    prompt_element = wait.until(EC.visibility_of_element_located((by, selector)))
                    message = prompt_element.text.strip()
                    if message:
                        logger.info(f"提示信息: {message}")
                        return message
                except TimeoutException:
                    continue
                except Exception as e:
                    logger.warning(f"尝试定位器 {selector} 失败: {str(e)}")
                    continue

            logger.info("未找到提示信息")
            return ""
        except Exception as e:
            logger.error(f"获取提示信息失败: {str(e)}", exc_info=True)
            return ""

    def close_prompt(self):
        """
        关闭提示弹窗

        Returns:
            bool: 关闭成功返回True，否则返回False
        """
        logger.info("关闭提示弹窗")
        try:
            close_btn_locators = [
                (By.XPATH, "//div[@class='common-prompt']//button[@class='am-close']"),
                (By.XPATH, "//div[contains(@class, 'common-prompt')]//button[@class='am-close']"),
            ]

            for by, selector in close_btn_locators:
                try:
                    close_btn = self.driver.find_element(by, selector)
                    close_btn.click()
                    time.sleep(0.3)
                    logger.info("提示弹窗已关闭")
                    return True
                except NoSuchElementException:
                    continue
                except Exception as e:
                    logger.warning(f"尝试定位器 {selector} 失败: {str(e)}")
                    continue

            logger.info("未找到提示弹窗关闭按钮")
            return False
        except Exception as e:
            logger.error(f"关闭提示弹窗失败: {str(e)}", exc_info=True)
            return False