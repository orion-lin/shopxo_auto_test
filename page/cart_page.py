import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from base.WebDriverBase import WebDriverBase
from utils.log_util import logger


class CartPage:
    """
    购物车页面对象类
    封装购物车页面的元素定位和操作方法
    页面结构：根容器cart-content -> 商品行tr[data-id] -> 各功能模块
    """

    # 页面元素定位器
    # ================================================
    # 首页购物车入口按钮 - 通过top-nav-items-cart容器定位
    HOME_CART_ENTRY = (By.XPATH, "//div[@class='top-nav-items top-nav-items-cart']//div[@class='menu-hd']//a")
    # 购物车页面标题
    CART_TITLE = (By.XPATH, "//h1[contains(text(), '购物车')]")
    # 购物车空状态提示
    EMPTY_CART_MSG = (By.XPATH, "//div[contains(@class, 'cart-empty')]")

    # 页面根滚动容器
    CART_CONTENT = (By.XPATH, "//div[@class='cart-content']")

    # 购物车商品行列表 - tr标签，带data-id属性
    PRODUCT_ROWS = (By.XPATH, "//div[@class='cart-content']//tr[@data-id]")

    # 行内元素定位器（相对于商品行）
    # 勾选框：input复选框，class=am-ucheck-checkbox
    ROW_CHECKBOX = (By.XPATH, ".//input[@class='am-ucheck-checkbox']")
    # 商品标题：a标签class=goods-title
    ROW_GOODS_TITLE = (By.XPATH, ".//a[@class='goods-title']")
    # 规格容器：ul class=goods-attr
    ROW_GOODS_ATTR = (By.XPATH, ".//ul[@class='goods-attr']")
    # 商品缩略图：goods-detail容器内的img标签
    ROW_GOODS_IMAGE = (By.XPATH, ".//div[@class='goods-detail']//img")

    # 数量操作模块：div.stock-tag
    ROW_STOCK_TAG = (By.XPATH, ".//div[@class='stock-tag']")
    # 减号按钮：span标签 class=stock-submit data-type="min"
    ROW_QUANTITY_MINUS = (By.XPATH, ".//span[@class='stock-submit' and @data-type='min']")
    # 加号按钮：span标签 class=stock-submit data-type="add"
    ROW_QUANTITY_PLUS = (By.XPATH, ".//span[@class='stock-submit' and @data-type='add']")
    # 数字输入框：input type=number
    ROW_QUANTITY_INPUT = (By.XPATH, ".//input[@type='number']")

    # 价格元素
    # 原价：p标签class=original-price
    ROW_ORIGINAL_PRICE = (By.XPATH, ".//p[@class='original-price']")
    # 售价：p标签class=line-price
    ROW_LINE_PRICE = (By.XPATH, ".//p[@class='line-price']")
    # 单行小计：strong class=total-price-content
    ROW_TOTAL_PRICE = (By.XPATH, ".//strong[@class='total-price-content']")

    # 操作列按钮
    # 删除按钮：a class=submit-delete
    ROW_DELETE_BTN = (By.XPATH, ".//a[contains(@class, 'submit-delete')]")
    # 收藏按钮：a class=submit-ajax
    ROW_COLLECT_BTN = (By.XPATH, ".//a[contains(@class, 'submit-ajax')]")

    # 底部全局结算栏
    CART_NAV = (By.XPATH, "//div[@class='cart-nav']")
    # 全选复选框：底部结算栏中的全选复选框，在label.select-all-event下
    SELECT_ALL_CHECKBOX = (By.XPATH, "//label[contains(@class, 'select-all-event')]//input")
    # 批量删除按钮：删除链接
    BATCH_DELETE_BTN = (By.XPATH, "//a[contains(text(), '删除') and not(contains(@class, 'submit-delete'))]")
    # 批量收藏按钮：收藏链接
    BATCH_COLLECT_BTN = (By.XPATH, "//a[contains(text(), '收藏') and not(contains(@class, 'submit-ajax'))]")
    # 已选件数：span.selected-tips内的strong标签
    SELECTED_COUNT = (By.XPATH, "//span[@class='selected-tips']//strong[@class='am-color-main']")
    # 总合计金额：strong class=nav-total-price
    TOTAL_AMOUNT = (By.XPATH, "//strong[@class='nav-total-price']")
    # 结算按钮：结算按钮
    CHECKOUT_BTN = (By.XPATH, "//button[contains(text(), '结算')]")

    # 购物车商品数量标签（首页顶部）
    CART_COUNT_BADGE = (By.XPATH, "//strong[@class='common-cart-total']")

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

    def open_cart_page(self):
        """
        打开购物车页面
        """
        base_url = self.env_config.get("base_url", "")
        cart_url = f"{base_url}/?s=cart/index.html"
        logger.info(f"打开购物车页面: {cart_url}")
        self.driver.get(cart_url)

    def click_home_cart_entry(self):
        """
        点击首页顶部购物车入口按钮
        """
        logger.info("点击首页顶部购物车入口按钮")
        try:
            cart_entry_selectors = [
                self.HOME_CART_ENTRY,
                (By.XPATH, "//a[@href='?s=cart/index.html']"),
                (By.XPATH, "//div[contains(@class, 'top-nav-items-cart')]//a"),
            ]

            for by, selector in cart_entry_selectors:
                try:
                    wait = self._get_wait(timeout=5)
                    element = wait.until(EC.element_to_be_clickable((by, selector)))
                    self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
                    time.sleep(0.5)
                    element.click()
                    logger.info(f"购物车入口点击成功，定位器: {selector}")
                    return
                except TimeoutException:
                    continue

            logger.error("未找到购物车入口按钮")
            raise NoSuchElementException("未找到购物车入口按钮")
        except NoSuchElementException:
            raise
        except Exception as e:
            logger.error(f"点击购物车入口失败: {str(e)}", exc_info=True)
            raise

    def is_cart_page_displayed(self, timeout=5):
        """
        判断购物车页面是否已显示

        Args:
            timeout (int): 超时时间，默认5秒

        Returns:
            bool: 购物车页面已显示返回True，否则返回False
        """
        logger.info("判断购物车页面是否已显示")
        try:
            page_locators = [
                self.CART_TITLE,
                self.CART_CONTENT,
                (By.XPATH, "//div[contains(@class, 'cart-content')]"),
                (By.XPATH, "//*[contains(text(), '购物车')]"),
            ]

            for by, selector in page_locators:
                try:
                    wait = self._get_wait(timeout=timeout)
                    element = wait.until(EC.visibility_of_element_located((by, selector)))
                    logger.info(f"购物车页面已显示，定位器: {selector}")
                    return True
                except TimeoutException:
                    continue

            logger.info("购物车页面未显示")
            return False
        except Exception as e:
            logger.error(f"判断购物车页面状态失败: {str(e)}", exc_info=True)
            return False

    def is_cart_empty(self, timeout=3):
        """
        判断购物车是否为空

        Args:
            timeout (int): 超时时间，默认3秒

        Returns:
            bool: 购物车为空返回True，否则返回False
        """
        logger.info("判断购物车是否为空")
        try:
            wait = self._get_wait(timeout=timeout)
            element = wait.until(EC.visibility_of_element_located(self.EMPTY_CART_MSG))
            logger.info("购物车为空")
            return True
        except TimeoutException:
            logger.info("购物车不为空")
            return False
        except Exception as e:
            logger.error(f"判断购物车状态失败: {str(e)}", exc_info=True)
            return False

    def get_cart_products(self):
        """
        获取购物车中所有商品信息

        Returns:
            list: 商品信息列表，每个元素为字典，包含name、spec、price、quantity、subtotal、is_selected
        """
        logger.info("获取购物车中所有商品信息")
        products = []

        try:
            wait = self._get_wait(timeout=3)
            product_rows = wait.until(EC.visibility_of_all_elements_located(self.PRODUCT_ROWS))
            logger.info(f"找到 {len(product_rows)} 个商品")

            self.driver.implicitly_wait(0)

            for index, row_element in enumerate(product_rows):
                try:
                    product_info = {}

                    try:
                        name_element = row_element.find_element(*self.ROW_GOODS_TITLE)
                        product_info["name"] = name_element.text.strip()
                    except NoSuchElementException:
                        product_info["name"] = ""

                    try:
                        spec_element = row_element.find_element(*self.ROW_GOODS_ATTR)
                        spec_text = ""
                        li_elements = spec_element.find_elements(By.TAG_NAME, "li")
                        for li in li_elements:
                            if spec_text:
                                spec_text += ", "
                            spec_text += li.text.strip()
                        product_info["spec"] = spec_text
                    except NoSuchElementException:
                        product_info["spec"] = ""

                    try:
                        price_element = row_element.find_element(*self.ROW_LINE_PRICE)
                        product_info["price"] = price_element.text.strip()
                    except NoSuchElementException:
                        product_info["price"] = ""

                    try:
                        quantity_element = row_element.find_element(*self.ROW_QUANTITY_INPUT)
                        product_info["quantity"] = int(quantity_element.get_attribute("value"))
                    except (NoSuchElementException, ValueError):
                        product_info["quantity"] = 1

                    try:
                        subtotal_element = row_element.find_element(*self.ROW_TOTAL_PRICE)
                        product_info["subtotal"] = subtotal_element.text.strip()
                    except NoSuchElementException:
                        product_info["subtotal"] = ""

                    try:
                        checkbox_element = row_element.find_element(*self.ROW_CHECKBOX)
                        product_info["is_selected"] = checkbox_element.is_selected()
                    except NoSuchElementException:
                        product_info["is_selected"] = False

                    product_info["cart_id"] = row_element.get_attribute("data-id")
                    product_info["goods_id"] = row_element.get_attribute("data-goods-id")
                    product_info["element"] = row_element
                    products.append(product_info)
                    logger.info(f"商品{index+1}: {product_info['name']}, 规格: {product_info['spec']}, 单价: {product_info['price']}, 数量: {product_info['quantity']}, 小计: {product_info['subtotal']}")
                except Exception as e:
                    logger.error(f"获取商品{index+1}信息失败: {str(e)}", exc_info=True)
                    continue

            self.driver.implicitly_wait(self.browser_config.get("implicit_wait", 10))

        except TimeoutException:
            logger.warning("未找到商品列表")
        except Exception as e:
            logger.error(f"获取购物车商品信息失败: {str(e)}", exc_info=True)

        return products

    def select_product(self, index=0):
        """
        勾选指定位置的商品

        Args:
            index (int): 商品索引，默认0（第一个商品）

        Returns:
            bool: 勾选成功返回True，否则返回False
        """
        logger.info(f"勾选第{index+1}个商品")
        try:
            wait = self._get_wait(timeout=3)
            product_rows = wait.until(EC.visibility_of_all_elements_located(self.PRODUCT_ROWS))

            if index >= len(product_rows):
                logger.error(f"商品索引{index}超出范围，共{len(product_rows)}个商品")
                return False

            row_element = product_rows[index]

            checkbox_locators = [
                self.ROW_CHECKBOX,
                (By.XPATH, ".//input[@type='checkbox' and contains(@class, 'am-ucheck')]"),
                (By.XPATH, ".//input[@type='checkbox' and @name='cart_id[]']"),
                (By.XPATH, ".//input[@type='checkbox']"),
            ]

            checkbox = None
            for by, selector in checkbox_locators:
                try:
                    checkbox = row_element.find_element(by, selector)
                    logger.info(f"找到勾选框，定位器: {selector}")
                    break
                except NoSuchElementException:
                    continue

            if checkbox is None:
                logger.error("未找到勾选框")
                return False

            logger.info(f"勾选框状态 - is_selected: {checkbox.is_selected()}, id: {checkbox.get_attribute('id')}, name: {checkbox.get_attribute('name')}")

            if not checkbox.is_selected():
                self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", checkbox)
                time.sleep(0.3)

                click_success = False
                clickable_locators = [
                    (By.XPATH, ".//i[contains(@class, 'am-icon-checked')]"),
                    (By.XPATH, ".//i[contains(@class, 'am-icon-unchecked')]"),
                    (By.XPATH, ".//span[contains(@class, 'am-ucheck')]"),
                    (By.XPATH, ".//label[contains(@class, 'am-ucheck')]"),
                ]

                for by, selector in clickable_locators:
                    try:
                        click_element = row_element.find_element(by, selector)
                        click_element.click()
                        time.sleep(0.5)
                        click_success = True
                        logger.info(f"通过{selector}点击成功")
                        break
                    except Exception:
                        continue

                if not click_success:
                    logger.info("尝试使用JavaScript直接点击checkbox")
                    self.driver.execute_script("arguments[0].click();", checkbox)
                    time.sleep(0.5)
                    click_success = True

                is_selected_after = checkbox.is_selected()
                logger.info(f"点击后勾选框状态 - is_selected: {is_selected_after}")
                logger.info(f"第{index+1}个商品已勾选")
            else:
                logger.info(f"第{index+1}个商品已处于勾选状态")

            return True
        except Exception as e:
            logger.error(f"勾选商品失败: {str(e)}", exc_info=True)
            return False

    def deselect_product(self, index=0):
        """
        取消勾选指定位置的商品

        Args:
            index (int): 商品索引，默认0（第一个商品）

        Returns:
            bool: 取消勾选成功返回True，否则返回False
        """
        logger.info(f"取消勾选第{index+1}个商品")
        try:
            wait = self._get_wait(timeout=3)
            product_rows = wait.until(EC.visibility_of_all_elements_located(self.PRODUCT_ROWS))

            if index >= len(product_rows):
                logger.error(f"商品索引{index}超出范围，共{len(product_rows)}个商品")
                return False

            row_element = product_rows[index]

            checkbox_locators = [
                self.ROW_CHECKBOX,
                (By.XPATH, ".//input[@type='checkbox' and contains(@class, 'am-ucheck')]"),
                (By.XPATH, ".//input[@type='checkbox']"),
            ]

            checkbox = None
            for by, selector in checkbox_locators:
                try:
                    checkbox = row_element.find_element(by, selector)
                    break
                except NoSuchElementException:
                    continue

            if checkbox is None:
                logger.error("未找到勾选框")
                return False

            if checkbox.is_selected():
                self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", checkbox)
                time.sleep(0.3)

                click_success = False
                clickable_locators = [
                    (By.XPATH, ".//i[contains(@class, 'am-icon-checked')]"),
                    (By.XPATH, ".//i[contains(@class, 'am-icon-unchecked')]"),
                    (By.XPATH, ".//span[contains(@class, 'am-ucheck')]"),
                    (By.XPATH, ".//label[contains(@class, 'am-ucheck')]"),
                ]

                for by, selector in clickable_locators:
                    try:
                        click_element = row_element.find_element(by, selector)
                        click_element.click()
                        time.sleep(0.5)
                        click_success = True
                        break
                    except Exception:
                        continue

                if not click_success:
                    self.driver.execute_script("arguments[0].click();", checkbox)
                    time.sleep(0.5)

                logger.info(f"第{index+1}个商品已取消勾选")
            else:
                logger.info(f"第{index+1}个商品已处于未勾选状态")

            return True
        except Exception as e:
            logger.error(f"取消勾选商品失败: {str(e)}", exc_info=True)
            return False

    def select_all_products(self):
        """
        全选所有商品

        Returns:
            bool: 全选成功返回True，否则返回False
        """
        logger.info("全选所有商品")
        try:
            wait = self._get_wait(timeout=3)

            select_all_label_locators = [
                (By.XPATH, "//label[@class='select-all-event']"),
                (By.XPATH, "//label[contains(@class, 'select-all-event')]"),
                (By.XPATH, "//label[contains(text(), '全选')]"),
            ]

            select_all_label = None
            for by, selector in select_all_label_locators:
                try:
                    select_all_label = wait.until(EC.element_to_be_clickable((by, selector)))
                    logger.info(f"找到全选label，定位器: {selector}")
                    break
                except Exception:
                    continue

            if select_all_label is None:
                logger.error("未找到全选label")
                return False

            select_all_label.click()
            time.sleep(0.5)
            logger.info("全选按钮已点击")

            return True
        except Exception as e:
            logger.error(f"全选商品失败: {str(e)}", exc_info=True)
            return False

    def deselect_all_products(self):
        """
        取消全选所有商品

        Returns:
            bool: 取消全选成功返回True，否则返回False
        """
        logger.info("取消全选所有商品")
        try:
            wait = self._get_wait(timeout=3)
            product_rows = wait.until(EC.visibility_of_all_elements_located(self.PRODUCT_ROWS))

            for index, row_element in enumerate(product_rows):
                try:
                    checkbox = row_element.find_element(*self.ROW_CHECKBOX)
                    if checkbox.is_selected():
                        click_element = row_element.find_element(By.XPATH, ".//i[contains(@class, 'am-icon-checked')]")
                        click_element.click()
                        time.sleep(0.3)
                        logger.info(f"取消勾选第{index+1}个商品")
                except Exception as e:
                    logger.warning(f"取消勾选第{index+1}个商品失败: {str(e)}")
                    continue

            logger.info("所有商品已取消勾选")
            return True
        except Exception as e:
            logger.error(f"取消全选商品失败: {str(e)}", exc_info=True)
            return False

    def increase_quantity(self, index=0):
        """
        增加指定商品的购买数量

        Args:
            index (int): 商品索引，默认0（第一个商品）

        Returns:
            int: 增加后的数量，失败返回-1
        """
        logger.info(f"增加第{index+1}个商品的数量")
        try:
            wait = self._get_wait(timeout=3)
            product_rows = wait.until(EC.visibility_of_all_elements_located(self.PRODUCT_ROWS))

            if index >= len(product_rows):
                logger.error(f"商品索引{index}超出范围，共{len(product_rows)}个商品")
                return -1

            row_element = product_rows[index]

            plus_locators = [
                self.ROW_QUANTITY_PLUS,
                (By.XPATH, ".//span[@class='stock-submit' and contains(@data-type, 'add')]"),
                (By.XPATH, ".//span[contains(@class, 'stock-submit') and @data-type='add']"),
                (By.XPATH, ".//span[contains(text(), '+')]"),
                (By.XPATH, ".//button[contains(@class, 'cart-plus')]"),
            ]

            plus_btn = None
            for by, selector in plus_locators:
                try:
                    plus_btn = row_element.find_element(by, selector)
                    logger.info(f"找到加号按钮，定位器: {selector}")
                    break
                except NoSuchElementException:
                    continue

            if plus_btn is None:
                logger.error("未找到加号按钮")
                return -1

            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", plus_btn)
            time.sleep(0.3)
            plus_btn.click()
            time.sleep(1)

            quantity_element = row_element.find_element(*self.ROW_QUANTITY_INPUT)
            new_quantity = int(quantity_element.get_attribute("value"))
            logger.info(f"第{index+1}个商品数量已增加，当前数量: {new_quantity}")

            return new_quantity
        except Exception as e:
            logger.error(f"增加商品数量失败: {str(e)}", exc_info=True)
            return -1

    def decrease_quantity(self, index=0):
        """
        减少指定商品的购买数量（数量最小值为1）

        Args:
            index (int): 商品索引，默认0（第一个商品）

        Returns:
            int: 减少后的数量，失败返回-1，数量已为1时返回1
        """
        logger.info(f"减少第{index+1}个商品的数量")
        try:
            wait = self._get_wait(timeout=3)
            product_rows = wait.until(EC.visibility_of_all_elements_located(self.PRODUCT_ROWS))

            if index >= len(product_rows):
                logger.error(f"商品索引{index}超出范围，共{len(product_rows)}个商品")
                return -1

            row_element = product_rows[index]
            quantity_element = row_element.find_element(*self.ROW_QUANTITY_INPUT)
            current_quantity = int(quantity_element.get_attribute("value"))

            if current_quantity <= 1:
                logger.info(f"第{index+1}个商品数量已为最小值1，无法继续减少")
                return 1

            minus_locators = [
                self.ROW_QUANTITY_MINUS,
                (By.XPATH, ".//span[@class='stock-submit' and contains(@data-type, 'min')]"),
                (By.XPATH, ".//span[contains(@class, 'stock-submit') and @data-type='min']"),
                (By.XPATH, ".//span[contains(text(), '-')]"),
                (By.XPATH, ".//button[contains(@class, 'cart-minus')]"),
            ]

            minus_btn = None
            for by, selector in minus_locators:
                try:
                    minus_btn = row_element.find_element(by, selector)
                    logger.info(f"找到减号按钮，定位器: {selector}")
                    break
                except NoSuchElementException:
                    continue

            if minus_btn is None:
                logger.error("未找到减号按钮")
                return -1

            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", minus_btn)
            time.sleep(0.3)
            minus_btn.click()
            time.sleep(0.5)

            new_quantity = int(quantity_element.get_attribute("value"))
            logger.info(f"第{index+1}个商品数量已减少，当前数量: {new_quantity}")

            return new_quantity
        except Exception as e:
            logger.error(f"减少商品数量失败: {str(e)}", exc_info=True)
            return -1

    def set_quantity(self, index=0, quantity=1):
        """
        设置指定商品的购买数量

        Args:
            index (int): 商品索引，默认0（第一个商品）
            quantity (int): 目标数量，最小值为1

        Returns:
            int: 设置后的数量，失败返回-1
        """
        logger.info(f"设置第{index+1}个商品的数量为: {quantity}")
        try:
            if quantity < 1:
                logger.warning("数量不能小于1，自动设置为1")
                quantity = 1

            wait = self._get_wait()
            product_rows = wait.until(EC.visibility_of_all_elements_located(self.PRODUCT_ROWS))

            if index >= len(product_rows):
                logger.error(f"商品索引{index}超出范围，共{len(product_rows)}个商品")
                return -1

            row_element = product_rows[index]
            quantity_element = row_element.find_element(*self.ROW_QUANTITY_INPUT)

            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", quantity_element)
            time.sleep(0.3)
            quantity_element.clear()
            quantity_element.send_keys(str(quantity))

            self.driver.execute_script("arguments[0].dispatchEvent(new Event('change'));", quantity_element)
            time.sleep(0.5)

            new_quantity = int(quantity_element.get_attribute("value"))
            logger.info(f"第{index+1}个商品数量已设置为: {new_quantity}")

            return new_quantity
        except Exception as e:
            logger.error(f"设置商品数量失败: {str(e)}", exc_info=True)
            return -1

    def delete_product(self, index=0):
        """
        删除指定位置的商品

        Args:
            index (int): 商品索引，默认0（第一个商品）

        Returns:
            bool: 删除成功返回True，否则返回False
        """
        logger.info(f"删除第{index+1}个商品")
        try:
            wait = self._get_wait(timeout=3)
            product_rows = wait.until(EC.visibility_of_all_elements_located(self.PRODUCT_ROWS))

            if index >= len(product_rows):
                logger.error(f"商品索引{index}超出范围，共{len(product_rows)}个商品")
                return False

            row_element = product_rows[index]
            delete_btn = row_element.find_element(*self.ROW_DELETE_BTN)

            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", delete_btn)
            time.sleep(0.3)
            self.driver.execute_script("arguments[0].click();", delete_btn)
            time.sleep(2)

            try:
                alert = self.driver.switch_to.alert
                alert.accept()
                time.sleep(1)
                logger.info("确认弹窗已处理")
            except Exception:
                logger.info("未出现确认弹窗")

            confirm_btn_locators = [
                (By.XPATH, "//div[@class='am-modal-dialog']//span[@class='am-modal-btn' and @data-am-modal-confirm]"),
                (By.XPATH, "//div[contains(@class, 'am-modal-footer')]//span[contains(text(), '确认')]"),
                (By.XPATH, "//span[@class='am-modal-btn' and not(contains(@class, 'am-text-danger'))]"),
            ]

            for by, selector in confirm_btn_locators:
                try:
                    wait = self._get_wait(timeout=3)
                    confirm_btn = wait.until(EC.element_to_be_clickable((by, selector)))
                    confirm_btn.click()
                    time.sleep(1)
                    logger.info(f"通过{selector}确认删除")
                    break
                except Exception:
                    continue

            logger.info(f"第{index+1}个商品已删除")
            return True
        except Exception as e:
            logger.error(f"删除商品失败: {str(e)}", exc_info=True)
            return False

    def batch_delete_products(self):
        """
        批量删除已勾选的商品

        Returns:
            bool: 批量删除成功返回True，否则返回False
        """
        logger.info("批量删除已勾选的商品")
        try:
            wait = self._get_wait(timeout=3)
            batch_delete_btn = wait.until(EC.element_to_be_clickable(self.BATCH_DELETE_BTN))
            batch_delete_btn.click()
            time.sleep(2)

            try:
                alert = self.driver.switch_to.alert
                alert.accept()
                time.sleep(1)
                logger.info("确认弹窗已处理")
            except Exception:
                logger.info("未出现确认弹窗")

            confirm_btn_locators = [
                (By.XPATH, "//div[@class='am-modal-dialog']//span[@class='am-modal-btn' and @data-am-modal-confirm]"),
                (By.XPATH, "//div[contains(@class, 'am-modal-footer')]//span[contains(text(), '确认')]"),
                (By.XPATH, "//span[@class='am-modal-btn' and not(contains(@class, 'am-text-danger'))]"),
            ]

            for by, selector in confirm_btn_locators:
                try:
                    wait = self._get_wait(timeout=3)
                    confirm_btn = wait.until(EC.element_to_be_clickable((by, selector)))
                    confirm_btn.click()
                    time.sleep(1)
                    logger.info(f"通过{selector}确认批量删除")
                    break
                except Exception:
                    continue

            logger.info("批量删除已完成")
            return True
        except Exception as e:
            logger.error(f"批量删除商品失败: {str(e)}", exc_info=True)
            return False

    def get_selected_count(self):
        """
        获取已选商品数量

        Returns:
            int: 已选商品数量，失败返回0
        """
        logger.info("获取已选商品数量")
        try:
            selected_count_locators = [
                (By.XPATH, "//span[@class='selected-tips']//strong"),
                (By.XPATH, "//span[contains(@class, 'selected-tips')]//strong"),
                (By.XPATH, "//strong[@class='am-color-main']"),
                (By.XPATH, "//div[contains(@class, 'cart-nav')]//span[contains(@class, 'selected-tips')]//strong"),
            ]

            for by, selector in selected_count_locators:
                try:
                    wait = self._get_wait(timeout=1)
                    selected_count_element = wait.until(EC.presence_of_element_located((by, selector)))
                    count_text = selected_count_element.text.strip()
                    import re
                    match = re.search(r'(\d+)', count_text)
                    if match:
                        count = int(match.group(1))
                        logger.info(f"已选商品数量: {count}")
                        return count
                    elif count_text.isdigit():
                        count = int(count_text)
                        logger.info(f"已选商品数量: {count}")
                        return count
                except TimeoutException:
                    continue
                except Exception as e:
                    logger.warning(f"尝试定位器 {selector} 失败: {str(e)}")
                    continue

            logger.error("未找到已选商品数量元素")
            return 0
        except Exception as e:
            logger.error(f"获取已选商品数量失败: {str(e)}", exc_info=True)
            return 0

    def get_total_amount(self):
        """
        获取已选商品总金额

        Returns:
            str: 总金额字符串，失败返回空字符串
        """
        logger.info("获取已选商品总金额")
        try:
            total_amount_locators = [
                (By.XPATH, "//strong[@class='nav-total-price']"),
                (By.XPATH, "//*[contains(@class, 'nav-total-price')]"),
                (By.XPATH, "//div[contains(@class, 'cart-nav')]//strong[contains(@class, 'total-price')]"),
            ]

            for by, selector in total_amount_locators:
                try:
                    wait = self._get_wait(timeout=1)
                    total_amount_element = wait.until(EC.presence_of_element_located((by, selector)))
                    total_amount = total_amount_element.text.strip()
                    if total_amount and "合计" not in total_amount:
                        logger.info(f"已选商品总金额: {total_amount}")
                        return total_amount
                except TimeoutException:
                    continue
                except Exception as e:
                    logger.warning(f"尝试定位器 {selector} 失败: {str(e)}")
                    continue

            logger.error("未找到总金额元素")
            return ""
        except Exception as e:
            logger.error(f"获取已选商品总金额失败: {str(e)}", exc_info=True)
            return ""

    def click_checkout(self):
        """
        点击结算按钮，跳转到订单确认页面

        Returns:
            bool: 点击成功返回True，否则返回False
        """
        logger.info("点击结算按钮")
        try:
            wait = self._get_wait()
            checkout_btn = wait.until(EC.element_to_be_clickable(self.CHECKOUT_BTN))
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", checkout_btn)
            time.sleep(0.3)
            checkout_btn.click()
            logger.info("结算按钮已点击，等待跳转到订单确认页面")
            return True
        except Exception as e:
            logger.error(f"点击结算按钮失败: {str(e)}", exc_info=True)
            return False

    def is_checkout_page_displayed(self, timeout=5):
        """
        判断是否已跳转到订单确认页面

        Args:
            timeout (int): 超时时间，默认5秒

        Returns:
            bool: 订单确认页面已显示返回True，否则返回False
        """
        logger.info("判断是否跳转到订单确认页面")
        try:
            wait = self._get_wait(timeout=timeout)

            checkout_locators = [
                (By.XPATH, "//h1[contains(text(), '确认订单') or contains(text(), '订单确认')]"),
                (By.XPATH, "//div[contains(text(), '确认收货地址')]"),
                (By.XPATH, "//button[contains(text(), '添加新地址')]"),
                (By.XPATH, "//div[contains(text(), '没有地址信息')]"),
                (By.XPATH, "//*[contains(text(), '订单信息')]"),
            ]

            for by, selector in checkout_locators:
                try:
                    element = wait.until(EC.visibility_of_element_located((by, selector)))
                    logger.info(f"通过定位器 {selector} 确认已跳转到订单确认页面")
                    return True
                except TimeoutException:
                    continue
                except Exception as e:
                    logger.warning(f"尝试定位器 {selector} 失败: {str(e)}")
                    continue

            current_url = self.driver.current_url
            if "order" in current_url.lower() or "checkout" in current_url.lower():
                logger.info(f"URL包含订单相关路径: {current_url}")
                return True

            logger.info(f"未跳转到订单确认页面，当前URL: {current_url}")
            return False
        except Exception as e:
            logger.error(f"判断订单确认页面状态失败: {str(e)}", exc_info=True)
            return False

    def get_cart_count_badge(self):
        """
        获取首页购物车数量标签的值

        Returns:
            int: 购物车数量，失败返回0
        """
        logger.info("获取首页购物车数量标签")
        try:
            wait = self._get_wait(timeout=3)
            badge_element = wait.until(EC.visibility_of_element_located(self.CART_COUNT_BADGE))
            count_text = badge_element.text.strip()
            count = int(count_text)
            logger.info(f"购物车数量: {count}")
            return count
        except Exception as e:
            logger.error(f"获取购物车数量失败: {str(e)}", exc_info=True)
            return 0

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
                (By.XPATH, "//div[@class='prompt-content']//p"),
                (By.XPATH, "//div[contains(@class, 'am-alert')]//p"),
                (By.XPATH, "//div[contains(@class, 'am-alert-success')]//p"),
                (By.XPATH, "//div[contains(@class, 'am-alert-danger')]//p"),
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

            try:
                script_result = self.driver.execute_script("""
                    var prompts = document.querySelectorAll('.common-prompt');
                    for (var i = 0; i < prompts.length; i++) {
                        var msg = prompts[i].querySelector('.prompt-msg');
                        if (msg && msg.textContent.trim()) {
                            return msg.textContent.trim();
                        }
                    }
                    return '';
                """)
                if script_result:
                    logger.info(f"通过JavaScript获取提示信息: {script_result}")
                    return script_result
            except Exception as e:
                logger.warning(f"通过JavaScript获取提示信息失败: {str(e)}")

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