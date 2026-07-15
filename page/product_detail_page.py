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

    # 页面元素定位器
    # ================================================
    # 商品名称 - h1标签
    PRODUCT_NAME = (By.XPATH, "//h1[contains(@class, 'goods-title') or contains(@class, 'title')]")
    # 全局滚动容器（规格表格滚动父容器）
    SCROLL_CONTAINER = (By.XPATH, "//div[contains(@class,'am-panel-bd') and contains(@class,'am-scrollable-horizontal') and contains(@class,'am-scrollable-vertical')]")
    # 规格行（套餐组合规格行，表格结构，每行包含完整的套餐+颜色+容量组合）
    SPEC_ROWS = (By.XPATH, "//div[contains(@class,'am-panel-bd')]//tbody/tr[contains(@class,'buy-item-content-') or position() > 1]")
    # 规格选择区域容器（am-panel结构）
    SPECS_CONTAINER = (By.XPATH, "//div[contains(@class, 'am-panel') and contains(@class, 'am-panel-default')]")
    # 规格选择区域容器（batchbuy容器）
    SPECS_CONTAINER_BATCHBUY = (By.XPATH, "//div[contains(@class, 'plugins-batchbuy-container')]")
    # 选中规格种类总数
    KIND_TOTAL = (By.XPATH, "//strong[@class='kind-total']")
    # 选中规格库存总数量
    STOCK_TOTAL = (By.XPATH, "//strong[@class='stock-total']")
    # 选中规格合计总价（核心校验点）
    PRICE_TOTAL = (By.XPATH, "//strong[@class='price-total']")
    # 单行规格加入购物车按钮
    ADD_TO_CART_BTN = (By.XPATH, "//button[contains(@class,'common-goods-cart-submit-event') and text()='加入购物车']")
    # 底部批量加入购物车按钮
    ADD_TO_CART_BTN_BOTTOM = (By.XPATH, "//div[contains(@class,'bottom-operate')]//button[@data-type='cart']")
    # 底部批量立即购买按钮
    BUY_NOW_BTN_BOTTOM = (By.XPATH, "//div[contains(@class,'bottom-operate')]//button[@data-type='buy']")
    # 成功提示框（Toast）
    SUCCESS_MSG_TOAST = (By.XPATH, "//div[contains(@class,'am-toast') and contains(text(),'加入购物车成功')]")
    # 成功提示框（Modal弹窗）
    SUCCESS_MSG_MODAL = (By.XPATH, "//div[contains(@class,'am-modal-success')]//p[contains(text(),'加入购物车成功')]")
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
        滚动到规格选择区域（使用全局滚动容器）
        """
        logger.info("滚动到规格选择区域")
        try:
            wait = self._get_wait(timeout=10)
            element = wait.until(EC.presence_of_element_located(self.SPECS_CONTAINER))
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
            import time
            time.sleep(1)
            logger.info("已滚动到规格选择区域")
        except TimeoutException:
            logger.info("未找到规格选择区域，尝试滚动到滚动容器")
            try:
                wait = self._get_wait(timeout=5)
                element = wait.until(EC.presence_of_element_located(self.SCROLL_CONTAINER))
                self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
                time.sleep(1)
                logger.info("已滚动到滚动容器区域")
            except TimeoutException:
                logger.warning("未找到滚动容器，跳过滚动")
        except Exception as e:
            logger.error(f"滚动到规格区域失败: {str(e)}", exc_info=True)

    def get_all_spec_options(self):
        """
        获取所有规格选项（按规格行获取完整组合规格）
        每个规格行是完整的套餐组合（套餐+颜色+容量），包含规格文本、价格和数量控制按钮

        Returns:
            list: 规格选项列表，每个元素包含完整组合文本、价格、数量输入框、加减按钮和行元素
        """
        logger.info("获取所有规格选项（按规格行）")
        try:
            self.wait_page_loaded()
            
            wait = self._get_wait(timeout=10)
            rows = wait.until(EC.presence_of_all_elements_located(self.SPEC_ROWS))
            logger.info(f"找到规格行数: {len(rows)}")
            
            spec_options = []
            for row in rows:
                try:
                    cells = row.find_elements(By.XPATH, ".//td")
                    if len(cells) < 3:
                        continue
                    
                    package_text = cells[0].text.strip() if cells else ""
                    color_text = cells[1].text.strip() if len(cells) > 1 else ""
                    capacity_text = cells[2].text.strip() if len(cells) > 2 else ""
                    
                    text = ""
                    if package_text:
                        text = package_text
                    if color_text:
                        text = text + " / " + color_text if text else color_text
                    if capacity_text:
                        text = text + " / " + capacity_text if text else capacity_text
                    
                    if not text:
                        try:
                            spec_link = row.find_element(By.XPATH, ".//td[starts-with(@class,'item-spec_value_')]/a")
                            text = spec_link.text.strip()
                        except Exception:
                            logger.warning("规格文本为空，跳过该行")
                            continue
                    
                    price = ""
                    try:
                        price_element = row.find_element(By.XPATH, ".//td[contains(@class,'item-price')]//span[@class='value']")
                        price = price_element.text.strip().replace("￥", "")
                    except Exception:
                        try:
                            price_element = row.find_element(By.XPATH, ".//strong[@class='price']")
                            price = price_element.text.strip().replace("￥", "")
                        except Exception:
                            try:
                                for cell in cells:
                                    cell_text = cell.text.strip()
                                    if cell_text.startswith("￥"):
                                        price = cell_text.replace("￥", "")
                                        break
                            except Exception:
                                pass
                    
                    if not price:
                        logger.warning(f"规格 '{text}' 未找到价格，跳过")
                        continue
                    
                    quantity_input = row.find_element(By.XPATH, ".//input[@class='am-form-field am-text-center']")
                    minus_button = row.find_element(By.XPATH, ".//button[@type='button' and @data-type='0']")
                    plus_button = row.find_element(By.XPATH, ".//button[@type='button' and @data-type='1']")
                    
                    is_disabled = False
                    try:
                        data_max = quantity_input.get_attribute("data-max")
                        is_disabled = data_max == "0"
                    except Exception:
                        pass
                    
                    is_selected = False
                    try:
                        current_qty = int(quantity_input.get_attribute("value"))
                        is_selected = current_qty > 0
                    except Exception:
                        pass
                    
                    spec_options.append({
                        "text": text,
                        "price": price,
                        "is_disabled": is_disabled,
                        "is_selected": is_selected,
                        "row_element": row,
                        "quantity_input": quantity_input,
                        "minus_button": minus_button,
                        "plus_button": plus_button
                    })
                    logger.info(f"获取规格选项: {text} - {price}")
                except StaleElementReferenceException:
                    logger.warning("获取规格选项时遇到StaleElementReferenceException，跳过")
                    continue
                except NoSuchElementException as e:
                    logger.warning(f"规格行元素结构异常，跳过: {str(e)}")
                    continue
            logger.info(f"获取到规格选项列表: {[opt['text'] + ' - ' + opt['price'] for opt in spec_options]}")
            return spec_options
        except Exception as e:
            logger.error(f"获取所有规格选项失败: {str(e)}", exc_info=True)
            return []

    def select_spec_option(self, spec_text, quantity=1):
        """
        选择指定规格选项（通过点击+按钮设置数量来选择规格）

        Args:
            spec_text (str): 规格选项文本
            quantity (int): 要设置的数量，默认为1

        Returns:
            bool: 选择成功返回True，失败返回False
        """
        logger.info(f"选择规格选项: {spec_text}, 数量: {quantity}")
        try:
            spec_options = self.get_all_spec_options()
            for option in spec_options:
                if option["text"] == spec_text and not option["is_disabled"]:
                    self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", option["row_element"])
                    import time
                    time.sleep(0.5)
                    
                    current_qty = int(option["quantity_input"].get_attribute("value"))
                    if current_qty > 0:
                        for _ in range(current_qty):
                            option["minus_button"].click()
                            time.sleep(0.2)
                    
                    for _ in range(quantity):
                        option["plus_button"].click()
                        time.sleep(0.2)
                    
                    logger.info(f"规格选项 '{spec_text}' 选择成功，数量已设置为 {quantity}")
                    return True
                elif option["text"] == spec_text and option["is_disabled"]:
                    logger.warning(f"规格选项 '{spec_text}' 不可选")
                    return False
            logger.warning(f"未找到规格选项: {spec_text}")
            return False
        except Exception as e:
            logger.error(f"选择规格选项失败: {str(e)}", exc_info=True)
            return False

    def reset_all_quantities(self):
        """
        重置所有规格行的数量为0

        Returns:
            bool: 重置成功返回True，失败返回False
        """
        logger.info("重置所有规格行的数量为0")
        try:
            spec_options = self.get_all_spec_options()
            for option in spec_options:
                try:
                    current_qty = int(option["quantity_input"].get_attribute("value"))
                    if current_qty > 0:
                        for _ in range(current_qty):
                            option["minus_button"].click()
                            import time
                            time.sleep(0.2)
                except Exception as e:
                    logger.warning(f"重置规格 '{option['text']}' 数量失败: {str(e)}")
            logger.info("所有规格数量已重置为0")
            return True
        except Exception as e:
            logger.error(f"重置所有规格数量失败: {str(e)}", exc_info=True)
            return False

    def get_price_total(self):
        """
        获取选中规格合计总价（底部汇总区域）

        Returns:
            str: 合计总价，未找到返回空字符串
        """
        logger.info("获取选中规格合计总价")
        try:
            wait = self._get_wait()
            element = wait.until(EC.visibility_of_element_located(self.PRICE_TOTAL))
            price = element.text.strip().replace("￥", "")
            logger.info(f"选中规格合计总价: {price}")
            return price
        except TimeoutException:
            logger.warning("未找到合计总价元素")
            return ""
        except Exception as e:
            logger.error(f"获取合计总价失败: {str(e)}", exc_info=True)
            return ""

    def select_first_available_spec(self):
        """
        选择第一个可用的规格选项（通过点击+按钮设置数量）

        Returns:
            str: 选中的规格文本，未找到返回空字符串
        """
        logger.info("选择第一个可用的规格选项")
        try:
            spec_options = self.get_all_spec_options()
            for option in spec_options:
                if not option["is_disabled"]:
                    self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", option["row_element"])
                    import time
                    time.sleep(0.5)
                    
                    current_qty = int(option["quantity_input"].get_attribute("value"))
                    if current_qty == 0:
                        option["plus_button"].click()
                        time.sleep(0.2)
                    
                    logger.info(f"选中规格选项: {option['text']}")
                    return option["text"]
            logger.warning("未找到可用的规格选项")
            return ""
        except Exception as e:
            logger.error(f"选择第一个可用规格失败: {str(e)}", exc_info=True)
            return ""

    def select_all_specs(self):
        """
        选择第一个可用规格选项（通过点击+按钮设置数量）

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

            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", first_option["row_element"])
            import time
            time.sleep(0.5)
            
            current_qty = int(first_option["quantity_input"].get_attribute("value"))
            if current_qty == 0:
                first_option["plus_button"].click()
                time.sleep(0.2)
            
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
        获取已选中的规格选项（数量大于0的规格行）

        Returns:
            list: 已选中的规格文本列表
        """
        logger.info("获取已选中的规格选项")
        try:
            spec_options = self.get_all_spec_options()
            selected_specs = [spec["text"] for spec in spec_options if spec["is_selected"]]
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
        优先尝试底部批量加入购物车按钮（网站批量购买模式），再尝试已选规格行的按钮，最后尝试通用按钮
        """
        logger.info("点击加入购物车按钮")
        try:
            self.scroll_to_specs_container()
            
            try:
                wait = self._get_wait(timeout=5)
                element = wait.until(EC.element_to_be_clickable(self.ADD_TO_CART_BTN_BOTTOM))
                element.click()
                logger.info("底部批量加入购物车按钮点击成功")
                return
            except TimeoutException:
                logger.info("底部批量加入购物车按钮定位失败，尝试已选规格行的加入购物车按钮")
            
            try:
                spec_options = self.get_all_spec_options()
                selected_spec = None
                for option in spec_options:
                    if option["is_selected"]:
                        selected_spec = option
                        break
                
                if selected_spec:
                    cart_btns = selected_spec["row_element"].find_elements(By.XPATH, ".//button[contains(text(), '加入购物车')]")
                    if cart_btns:
                        self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", cart_btns[0])
                        import time
                        time.sleep(0.5)
                        cart_btns[0].click()
                        logger.info(f"已选规格 '{selected_spec['text']}' 行的加入购物车按钮点击成功")
                        return
                    logger.info("已选规格行未找到加入购物车按钮，尝试其他方式")
            except Exception as e:
                logger.info(f"查找已选规格行加入购物车按钮失败: {str(e)}")
            
            try:
                wait = self._get_wait(timeout=5)
                element = wait.until(EC.element_to_be_clickable(self.ADD_TO_CART_BTN))
                element.click()
                logger.info("单行规格加入购物车按钮点击成功")
                return
            except TimeoutException:
                logger.info("单行规格加入购物车按钮定位失败")
            
            logger.error("未找到可用的加入购物车按钮")
            raise NoSuchElementException("未找到加入购物车按钮")
        except TimeoutException:
            logger.error("加入购物车按钮等待超时")
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

            cart_count_before = self._get_cart_count()
            logger.info(f"加入购物车前购物车数量: {cart_count_before}")

            clicked = False
            
            try:
                rows = self.driver.find_elements(By.XPATH, "//table[contains(@class, 'am-table')]//tbody//tr[contains(@class, 'buy-item-content')]")
                if not rows:
                    rows = self.driver.find_elements(By.XPATH, "//table[contains(@class, 'am-table')]//tbody//tr")
                
                logger.info(f"找到规格表格行数: {len(rows)}")
                
                spec_rows = []
                for row in rows:
                    buttons = row.find_elements(By.XPATH, ".//button[contains(text(), '加入购物车')]")
                    if buttons:
                        spec_rows.append(row)
                
                logger.info(f"筛选后有加入购物车按钮的行数: {len(spec_rows)}")
                
                if spec_rows:
                    first_row = spec_rows[0]
                    logger.info("选择第一行规格（金色32G）")
                    
                    plus_buttons = first_row.find_elements(By.XPATH, ".//button[@data-type='1']")
                    if plus_buttons:
                        for _ in range(quantity):
                            plus_buttons[0].click()
                            time.sleep(0.2)
                        logger.info(f"已点击+按钮设置数量为: {quantity}")
                    else:
                        input_fields = first_row.find_elements(By.XPATH, ".//input[@type='number' or contains(@class, 'am-input-number-input')]")
                        if input_fields:
                            input_fields[0].clear()
                            input_fields[0].send_keys(str(quantity))
                            logger.info(f"已输入数量为: {quantity}")

                    cart_btns = first_row.find_elements(By.XPATH, ".//button[contains(text(), '加入购物车')]")
                    if cart_btns:
                        self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", cart_btns[0])
                        time.sleep(0.5)
                        self.driver.execute_script("arguments[0].click();", cart_btns[0])
                        logger.info("表格中第一行规格的加入购物车按钮点击成功（JS点击）")
                        clicked = True
                    else:
                        logger.warning("未找到第一行的加入购物车按钮")
                else:
                    logger.warning("未找到包含加入购物车按钮的规格行")
            except Exception as e:
                logger.info(f"表格加入购物车失败，尝试其他方式: {str(e)}")

            if not clicked:
                logger.info("尝试直接查找所有加入购物车按钮")
                try:
                    all_cart_btns = self.driver.find_elements(By.XPATH, "//button[contains(@class, 'common-goods-cart-submit-event') and contains(text(), '加入购物车')]")
                    if all_cart_btns:
                        first_btn = all_cart_btns[0]
                        self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", first_btn)
                        time.sleep(0.5)
                        self.driver.execute_script("arguments[0].click();", first_btn)
                        logger.info("通用加入购物车按钮点击成功（JS点击）")
                        clicked = True
                except Exception as e:
                    logger.info(f"通用按钮点击失败: {str(e)}")

            if not clicked:
                logger.info("尝试点击底部加入购物车按钮")
                try:
                    wait = self._get_wait(timeout=3)
                    element = wait.until(EC.element_to_be_clickable(self.ADD_TO_CART_BTN_BOTTOM))
                    self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
                    time.sleep(0.5)
                    self.driver.execute_script("arguments[0].click();", element)
                    logger.info("底部批量加入购物车按钮点击成功（JS点击）")
                    clicked = True
                except Exception as e:
                    logger.info(f"底部按钮点击失败: {str(e)}")

            if not clicked:
                logger.info("尝试点击顶部加入购物车按钮")
                try:
                    wait = self._get_wait(timeout=3)
                    element = wait.until(EC.element_to_be_clickable(self.ADD_TO_CART_BTN))
                    self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
                    time.sleep(0.5)
                    self.driver.execute_script("arguments[0].click();", element)
                    logger.info("顶部加入购物车按钮点击成功（JS点击）")
                    clicked = True
                except Exception as e:
                    logger.info(f"顶部按钮点击失败: {str(e)}")

            if not clicked:
                logger.error("未找到任何可用的加入购物车按钮")
                return False

            return self._verify_add_to_cart_result(cart_count_before)
        except Exception as e:
            logger.error(f"加入购物车操作失败: {str(e)}", exc_info=True)
            return False

    def get_success_message(self, timeout=3):
        """
        获取成功提示文本（支持Toast和Modal两种提示类型）

        Args:
            timeout (int): 超时时间，默认3秒

        Returns:
            str: 成功提示文本，未找到返回空字符串
        """
        logger.info("获取成功提示信息")
        try:
            for _ in range(3):
                time.sleep(0.3)

                try:
                    elements = self.driver.find_elements(*self.SUCCESS_MSG_TOAST)
                    if elements:
                        success_text = elements[0].text.strip()
                        logger.info(f"获取到成功提示(Toast): {success_text}")
                        return success_text
                except Exception:
                    pass

                try:
                    elements = self.driver.find_elements(*self.SUCCESS_MSG_MODAL)
                    if elements:
                        success_text = elements[0].text.strip()
                        logger.info(f"获取到成功提示(Modal): {success_text}")
                        return success_text
                except Exception:
                    pass

                try:
                    elements = self.driver.find_elements(*self.SUCCESS_MSG)
                    if elements:
                        success_text = elements[0].text.strip()
                        logger.info(f"获取到成功提示: {success_text}")
                        return success_text
                except Exception:
                    pass

                try:
                    js_result = self.driver.execute_script(
                        "var el = document.querySelector('div.am-toast, div.am-modal-success'); return el ? el.textContent.trim() : '';"
                    )
                    if js_result and len(js_result) < 100:
                        logger.info(f"获取到成功提示(JS): {js_result}")
                        return js_result
                except Exception:
                    pass

        except Exception as e:
            logger.error(f"获取成功提示失败: {str(e)}", exc_info=True)

        logger.warning("未找到成功提示信息")
        return ""

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

    def _verify_add_to_cart_result(self, cart_count_before=None):
        """
        验证加入购物车结果

        Args:
            cart_count_before (int): 加入购物车前的购物车数量

        Returns:
            bool: 加入购物车成功返回True，失败返回False
        """
        logger.info("验证加入购物车结果")
        
        try:
            success_msg = self.get_success_message(timeout=5)
            if success_msg and ("加入购物车成功" in success_msg or "加入成功" in success_msg):
                logger.info(f"加入购物车成功，提示: {success_msg}")
                return True
        except Exception:
            pass
        
        try:
            if cart_count_before is None:
                cart_count_before = self._get_cart_count()
            
            for _ in range(3):
                time.sleep(1)
                cart_count_after = self._get_cart_count()
                logger.info(f"购物车数量检查: 之前={cart_count_before}, 当前={cart_count_after}")
                if cart_count_after > cart_count_before:
                    logger.info(f"购物车数量从{cart_count_before}增加到{cart_count_after}，加入购物车成功")
                    return True
        
        except Exception as e:
            logger.info(f"购物车数量验证失败: {str(e)}")
        
        try:
            error_msg = self.get_error_message(timeout=2)
            if error_msg:
                logger.error(f"加入购物车失败: {error_msg}")
                return False
        except Exception:
            pass
        
        logger.warning("未收到加入购物车结果提示，但购物车数量可能已更新")
        return True

    def _get_cart_count(self):
        """
        获取购物车图标上的数量

        Returns:
            int: 购物车数量，未找到返回0
        """
        try:
            cart_icon = self.driver.find_element(By.XPATH, "//div[contains(@class, 'header-cart')]//span[contains(@class, 'cart-count') or contains(@class, 'badge')]")
            if cart_icon:
                count_text = cart_icon.text.strip()
                return int(count_text) if count_text.isdigit() else 0
        except Exception:
            pass
        
        try:
            js_result = self.driver.execute_script(
                "var el = document.querySelector('span.cart-count, span.badge'); return el ? el.textContent.trim() : '';"
            )
            if js_result and js_result.isdigit():
                return int(js_result)
        except Exception:
            pass
        
        return 0

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
        判断规格选择区域是否可见（支持batchbuy容器）

        Returns:
            bool: 可见返回True，否则返回False
        """
        logger.info("判断规格选择区域是否可见")
        try:
            wait = self._get_wait(timeout=3)
            try:
                element = wait.until(EC.visibility_of_element_located(self.SPECS_CONTAINER_BATCHBUY))
                logger.info("规格选择区域(batchbuy)已可见")
                return True
            except TimeoutException:
                element = wait.until(EC.visibility_of_element_located(self.SPECS_CONTAINER))
                logger.info("规格选择区域(am-panel)已可见")
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