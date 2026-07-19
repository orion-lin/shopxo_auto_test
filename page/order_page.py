import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from base.WebDriverBase import WebDriverBase
from utils.log_util import logger


class OrderPage:
    """
    订单列表页面对象类
    封装订单列表页面的元素定位和操作方法
    页面结构：订单列表容器 -> 订单卡片 -> 订单商品信息 -> 订单操作按钮
    """

    # 页面元素定位器
    # ================================================
    # 订单列表页面标题
    ORDER_TITLE = (By.XPATH, "//h1[contains(text(), '我的订单') or contains(text(), '订单列表')]")

    # 订单列表容器（表格结构）
    ORDER_LIST_CONTAINER = (By.XPATH, "//table[@class='am-table am-table-striped am-table-hover am-text-nowrap form-table-data-list']")
    ORDER_LIST_CONTAINER_ALT = (By.XPATH, "//table[contains(@class, 'form-table-data-list')]")

    # 订单行列表（表格行）
    ORDER_CARDS = (By.XPATH, "//table[@class='am-table am-table-striped am-table-hover am-text-nowrap form-table-data-list']//tbody//tr")
    ORDER_CARDS_ALT = (By.XPATH, "//table[contains(@class, 'form-table-data-list')]//tbody//tr")

    # 订单行内元素（相对于订单行）
    # 订单号（在strong.am-icon-bookmark-o标签中）
    ORDER_NO = (By.XPATH, ".//strong[@class='am-icon-bookmark-o text-copy-submit']")
    ORDER_NO_ALT = (By.XPATH, ".//strong[contains(@class, 'text-copy-submit')]")
    # 下单时间
    ORDER_TIME = (By.XPATH, ".//td//span[contains(text(), '下单时间')]/following-sibling::span")
    ORDER_TIME_ALT = (By.XPATH, ".//td//*[contains(text(), '下单时间')]/following-sibling::*")
    # 订单状态
    ORDER_STATUS = (By.XPATH, ".//td//span[contains(text(), '待支付') or contains(text(), '已支付') or contains(text(), '已完成')]")
    ORDER_STATUS_ALT = (By.XPATH, ".//td//*[contains(text(), '待支付') or contains(text(), '已支付')]")

    # 订单商品列表（相对于订单行）- 商品名称链接
    ORDER_GOODS_LIST = (By.XPATH, ".//td//div[@class='am-text-truncate']//a")

    # 订单商品元素（相对于商品列）
    GOODS_TITLE = (By.XPATH, ".//a")
    GOODS_IMAGE = (By.XPATH, ".//img")
    GOODS_SPEC = (By.XPATH, ".//p")
    GOODS_PRICE = (By.XPATH, ".//td//span[contains(text(), '￥')]")
    GOODS_QUANTITY = (By.XPATH, ".//td//span[contains(text(), 'x')]")
    GOODS_SUBTOTAL = (By.XPATH, ".//td//span[contains(text(), '￥')]")

    # 订单金额信息（相对于订单行）
    ORDER_TOTAL_AMOUNT = (By.XPATH, ".//td//span[contains(text(), '￥')]")
    ORDER_PAYMENT = (By.XPATH, ".//td//span[contains(text(), '￥')]")
    ORDER_PAYMENT_ALT = (By.XPATH, ".//*[contains(text(), '￥')]")

    # 订单操作按钮（相对于订单行）
    ORDER_OPERATIONS = (By.XPATH, ".//td[last()]")
    VIEW_DETAIL_BTN = (By.XPATH, ".//a[contains(text(), '详情')]")
    CANCEL_BTN = (By.XPATH, ".//button[contains(text(), '取消')]")
    PAY_BTN = (By.XPATH, ".//button[contains(text(), '支付')]")
    CONFIRM_BTN = (By.XPATH, ".//a[contains(text(), '确认收货')]")

    # 订单详情页元素
    ORDER_DETAIL_TITLE = (By.XPATH, "//h1[contains(text(), '订单详情')]")
    ORDER_DETAIL_NO = (By.XPATH, "//div[@class='order-detail']//span[contains(text(), '订单号')]/following-sibling::span")

    # 分页元素
    PAGINATION = (By.XPATH, "//div[@class='pagination']")
    NEXT_PAGE_BTN = (By.XPATH, "//a[@class='next']")
    CURRENT_PAGE = (By.XPATH, "//span[@class='current']")

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

    def open_order_page(self):
        """
        打开订单列表页面
        """
        base_url = self.env_config.get("base_url", "")
        order_url = f"{base_url}/?s=order/index.html"
        logger.info(f"打开订单列表页面: {order_url}")
        self.driver.get(order_url)

    def is_order_page_displayed(self, timeout=5):
        """
        判断订单列表页面是否已显示

        Args:
            timeout (int): 超时时间，默认5秒

        Returns:
            bool: 订单列表页面已显示返回True，否则返回False
        """
        logger.info("判断订单列表页面是否已显示")
        try:
            page_locators = [
                self.ORDER_TITLE,
                self.ORDER_LIST_CONTAINER,
                self.ORDER_CARDS,
                (By.XPATH, "//*[contains(text(), '我的订单')]"),
                (By.XPATH, "//div[@class='order-list']"),
            ]

            for by, selector in page_locators:
                try:
                    wait = self._get_wait(timeout=timeout)
                    element = wait.until(EC.visibility_of_element_located((by, selector)))
                    logger.info(f"订单列表页面已显示，定位器: {selector}")
                    return True
                except TimeoutException:
                    continue

            current_url = self.driver.current_url
            if "order" in current_url.lower() and "index" in current_url.lower():
                logger.info(f"URL包含订单列表相关路径: {current_url}")
                return True

            logger.info(f"未跳转到订单列表页面，当前URL: {current_url}")
            return False
        except Exception as e:
            logger.error(f"判断订单列表页面状态失败: {str(e)}", exc_info=True)
            return False

    def get_order_list(self):
        """
        获取订单列表中的所有订单信息

        Returns:
            list: 订单信息列表，每个元素为字典，包含order_no、order_time、status、products、payment
        """
        logger.info("获取订单列表信息")
        orders = []

        try:
            wait = self._get_wait(timeout=3)
            
            order_cards_locators = [
                self.ORDER_CARDS,
                self.ORDER_CARDS_ALT,
            ]
            
            order_cards = None
            for by, selector in order_cards_locators:
                try:
                    order_cards = wait.until(EC.visibility_of_all_elements_located((by, selector)))
                    logger.info(f"找到 {len(order_cards)} 个订单，定位器: {selector}")
                    break
                except TimeoutException:
                    continue
            
            if not order_cards:
                logger.warning("未找到订单列表")
                return orders

            self.driver.implicitly_wait(0)

            for index, order_card in enumerate(order_cards):
                try:
                    order_info = {}

                    order_no_locators = [
                        self.ORDER_NO,
                        self.ORDER_NO_ALT,
                    ]
                    for by, selector in order_no_locators:
                        try:
                            order_no_element = order_card.find_element(by, selector)
                            order_info["order_no"] = order_no_element.text.strip()
                            break
                        except NoSuchElementException:
                            continue
                    if "order_no" not in order_info:
                        order_info["order_no"] = ""

                    order_time_locators = [
                        self.ORDER_TIME,
                        self.ORDER_TIME_ALT,
                    ]
                    for by, selector in order_time_locators:
                        try:
                            order_time_element = order_card.find_element(by, selector)
                            order_info["order_time"] = order_time_element.text.strip()
                            break
                        except NoSuchElementException:
                            continue
                    if "order_time" not in order_info:
                        order_info["order_time"] = ""

                    order_status_locators = [
                        self.ORDER_STATUS,
                        self.ORDER_STATUS_ALT,
                    ]
                    for by, selector in order_status_locators:
                        try:
                            order_status_element = order_card.find_element(by, selector)
                            order_info["status"] = order_status_element.text.strip()
                            break
                        except NoSuchElementException:
                            continue
                    if "status" not in order_info:
                        order_info["status"] = ""

                    order_payment_locators = [
                        self.ORDER_PAYMENT,
                        self.ORDER_PAYMENT_ALT,
                    ]
                    for by, selector in order_payment_locators:
                        try:
                            order_payment_element = order_card.find_element(by, selector)
                            order_info["payment"] = order_payment_element.text.strip()
                            break
                        except NoSuchElementException:
                            continue
                    if "payment" not in order_info:
                        order_info["payment"] = ""

                    products = []
                    try:
                        goods_links = order_card.find_elements(*self.ORDER_GOODS_LIST)
                        for goods_index, goods_link in enumerate(goods_links):
                            product_info = {}
                            try:
                                product_info["name"] = goods_link.text.strip()
                            except Exception:
                                product_info["name"] = ""

                            try:
                                goods_parent = goods_link.find_element(By.XPATH, "..")
                                try:
                                    spec_element = goods_parent.find_element(*self.GOODS_SPEC)
                                    product_info["spec"] = spec_element.text.strip()
                                except NoSuchElementException:
                                    product_info["spec"] = ""
                            except Exception:
                                product_info["spec"] = ""

                            try:
                                price_element = order_card.find_element(*self.GOODS_PRICE)
                                product_info["price"] = price_element.text.strip()
                            except NoSuchElementException:
                                product_info["price"] = ""

                            try:
                                quantity_element = order_card.find_element(*self.GOODS_QUANTITY)
                                quantity_text = quantity_element.text.strip()
                                product_info["quantity"] = int(quantity_text) if quantity_text else 1
                            except (NoSuchElementException, ValueError):
                                product_info["quantity"] = 1

                            try:
                                subtotal_element = order_card.find_element(*self.GOODS_SUBTOTAL)
                                product_info["subtotal"] = subtotal_element.text.strip()
                            except NoSuchElementException:
                                product_info["subtotal"] = ""

                            if product_info["name"]:
                                products.append(product_info)
                    except NoSuchElementException:
                        pass

                    order_info["products"] = products
                    
                    if order_info["order_no"] or order_info["status"] or products:
                        orders.append(order_info)
                        logger.info(f"订单{index+1}: 订单号={order_info['order_no']}, 状态={order_info['status']}, "
                                    f"实付金额={order_info['payment']}, 商品数={len(products)}")

                except Exception as e:
                    logger.error(f"获取订单{index+1}信息失败: {str(e)}", exc_info=True)
                    continue

            self.driver.implicitly_wait(self.browser_config.get("implicit_wait", 10))

        except TimeoutException:
            logger.warning("未找到订单列表")
        except Exception as e:
            logger.error(f"获取订单列表信息失败: {str(e)}", exc_info=True)

        return orders

    def get_latest_order(self):
        """
        获取最新的订单信息（列表中第一个订单）

        Returns:
            dict: 最新订单信息字典，失败返回空字典
        """
        logger.info("获取最新订单信息")
        orders = self.get_order_list()
        if orders:
            latest_order = orders[0]
            logger.info(f"最新订单: 订单号={latest_order['order_no']}, 状态={latest_order['status']}")
            return latest_order
        else:
            logger.warning("未找到任何订单")
            return {}

    def get_order_by_no(self, order_no):
        """
        根据订单号查找订单

        Args:
            order_no (str): 订单号

        Returns:
            dict: 订单信息字典，未找到返回空字典
        """
        logger.info(f"根据订单号查找订单: {order_no}")
        orders = self.get_order_list()
        for order in orders:
            if order.get("order_no") == order_no or order_no in str(order.get("order_no")):
                logger.info(f"找到匹配订单: {order}")
                return order
        logger.warning(f"未找到订单号为 {order_no} 的订单")
        return {}

    def click_view_detail(self, index=0):
        """
        点击查看订单详情

        Args:
            index (int): 订单索引，默认0（第一个订单）

        Returns:
            bool: 点击成功返回True，否则返回False
        """
        logger.info(f"点击查看第{index+1}个订单详情")
        try:
            wait = self._get_wait(timeout=3)
            order_cards = wait.until(EC.visibility_of_all_elements_located(self.ORDER_CARDS))

            if index >= len(order_cards):
                logger.error(f"订单索引{index}超出范围，共{len(order_cards)}个订单")
                return False

            order_card = order_cards[index]

            try:
                view_detail_btn = order_card.find_element(*self.VIEW_DETAIL_BTN)
                self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", view_detail_btn)
                time.sleep(0.3)
                view_detail_btn.click()
                time.sleep(1)
                logger.info(f"订单详情按钮已点击")
                return True
            except NoSuchElementException:
                logger.warning("未找到查看详情按钮，尝试点击订单卡片")
                order_card.click()
                time.sleep(1)
                return True

        except Exception as e:
            logger.error(f"点击查看订单详情失败: {str(e)}", exc_info=True)
            return False

    def is_order_detail_page_displayed(self, timeout=5):
        """
        判断订单详情页面是否已显示

        Args:
            timeout (int): 超时时间，默认5秒

        Returns:
            bool: 订单详情页面已显示返回True，否则返回False
        """
        logger.info("判断订单详情页面是否已显示")
        try:
            page_locators = [
                self.ORDER_DETAIL_TITLE,
                self.ORDER_DETAIL_NO,
                (By.XPATH, "//*[contains(text(), '订单详情')]"),
            ]

            for by, selector in page_locators:
                try:
                    wait = self._get_wait(timeout=timeout)
                    element = wait.until(EC.visibility_of_element_located((by, selector)))
                    logger.info(f"订单详情页面已显示，定位器: {selector}")
                    return True
                except TimeoutException:
                    continue

            logger.info("未跳转到订单详情页面")
            return False
        except Exception as e:
            logger.error(f"判断订单详情页面状态失败: {str(e)}", exc_info=True)
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