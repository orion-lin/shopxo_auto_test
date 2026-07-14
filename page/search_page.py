from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from base.WebDriverBase import WebDriverBase
from utils.log_util import logger


class SearchPage:
    """
    搜索结果页面对象类
    封装搜索结果页面的元素定位和操作方法
    """

    # 页面元素定位器
    # ================================================
    # 搜索结果数量文本（如"筛选出5条数据"）
    SEARCH_RESULT_COUNT = (By.XPATH, "//*[contains(text(), '筛选出') and contains(text(), '条数据')]")
    # 商品列表项 - 获取所有商品卡片（通过包含商品图片和链接的元素）
    PRODUCT_ITEMS = (By.XPATH, "//div[contains(@class, 'am-u-md') or contains(@class, 'am-u-sm') or contains(@class, 'goods-item') or contains(@class, 'list-item')]")
    # 第一个商品项
    FIRST_PRODUCT_ITEM = (By.XPATH, "(//div[contains(@class, 'am-u-md') or contains(@class, 'am-u-sm') or contains(@class, 'goods-item') or contains(@class, 'list-item')])[1]")
    # 商品名称（在商品项内）- 链接标签
    PRODUCT_NAME_LINK = (By.XPATH, ".//a[@title]")
    # 商品名称（备用：直接获取文本）
    PRODUCT_NAME_TEXT = (By.XPATH, ".//*[contains(@class, 'title')]")
    # 商品图片（在商品项内）
    PRODUCT_IMAGE = (By.XPATH, ".//img")
    # 商品价格（在商品项内）
    PRODUCT_PRICE = (By.XPATH, ".//span[contains(@class, 'price')]")
    # 搜索关键词展示
    SEARCH_KEYWORD_DISPLAY = (By.XPATH, "//span[contains(@class, 'search-keyword') or contains(text(), '搜索')]")

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

    def wait_search_results_loaded(self, timeout=10):
        """
        等待搜索结果加载完成

        Args:
            timeout (int): 超时时间，默认10秒
        """
        logger.info("等待搜索结果加载完成")
        try:
            wait = self._get_wait(timeout=timeout)
            wait.until(EC.visibility_of_element_located(self.SEARCH_RESULT_COUNT))
            logger.info("搜索结果数量已加载")
        except TimeoutException:
            logger.info("搜索结果数量定位失败，尝试等待商品列表项")
            try:
                wait = self._get_wait(timeout=5)
                wait.until(EC.visibility_of_element_located(self.PRODUCT_ITEMS))
                logger.info("商品列表项已加载")
            except TimeoutException:
                logger.error("搜索结果加载超时")
                raise
        except Exception as e:
            logger.error(f"等待搜索结果加载失败: {str(e)}", exc_info=True)
            raise

    def get_product_count(self):
        """
        获取搜索结果中的商品数量

        Returns:
            int: 商品数量，未找到返回0
        """
        logger.info("获取搜索结果商品数量")
        try:
            self.wait_search_results_loaded()
            elements = self.driver.find_elements(*self.PRODUCT_ITEMS)
            count = len(elements)
            logger.info(f"搜索结果商品数量: {count}")
            return count
        except Exception as e:
            logger.error(f"获取商品数量失败: {str(e)}", exc_info=True)
            return 0

    def get_first_product_element(self):
        """
        获取第一个商品元素

        Returns:
            WebElement: 第一个商品元素，未找到返回None
        """
        logger.info("获取第一个商品元素")
        try:
            self.wait_search_results_loaded()
            wait = self._get_wait()
            element = wait.until(EC.visibility_of_element_located(self.FIRST_PRODUCT_ITEM))
            logger.info("第一个商品元素已找到")
            return element
        except TimeoutException:
            logger.error("第一个商品元素等待超时")
            return None
        except Exception as e:
            logger.error(f"获取第一个商品元素失败: {str(e)}", exc_info=True)
            return None

    def click_first_product(self):
        """
        点击第一个商品，跳转商品详情页
        处理target="_blank"问题：先移除target属性再点击，避免打开新标签页
        处理元素不可见问题：先滚动页面确保元素进入可视区域
        """
        logger.info("点击第一个商品")
        try:
            self.driver.execute_script("window.scrollTo(0, 0);")
            import time
            time.sleep(1)

            try:
                wait = self._get_wait(timeout=10)
                goods_info_links = wait.until(EC.presence_of_all_elements_located(
                    (By.XPATH, "//a[contains(@class, 'goods-info')]")
                ))
                
                if goods_info_links:
                    first_link = goods_info_links[0]
                    self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", first_link)
                    time.sleep(2)
                    
                    href = first_link.get_attribute("href")
                    product_name = first_link.get_attribute("title") or ""
                    logger.info(f"找到商品链接: {href}")
                    logger.info(f"商品名称: {product_name}")
                    
                    self.driver.execute_script("arguments[0].removeAttribute('target');", first_link)
                    self.driver.execute_script("arguments[0].removeAttribute('rel');", first_link)
                    first_link.click()
                    logger.info("商品详情链接点击成功（已移除target属性）")
                    return
            except TimeoutException:
                logger.info("未找到goods-info链接，尝试其他定位方式")

            first_product = self.get_first_product_element()
            if not first_product:
                logger.error("未找到第一个商品元素，尝试直接点击第一个商品链接")
                try:
                    wait = self._get_wait()
                    first_link = wait.until(EC.element_to_be_clickable(
                        (By.XPATH, "(//a[@title])[1]")
                    ))
                    self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", first_link)
                    time.sleep(2)
                    
                    product_name = first_link.get_attribute("title") or first_link.text
                    logger.info(f"点击商品: {product_name}")
                    
                    self.driver.execute_script("arguments[0].removeAttribute('target');", first_link)
                    first_link.click()
                    return
                except Exception:
                    raise NoSuchElementException("未找到第一个商品元素")

            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", first_product)
            time.sleep(2)

            product_name = self.get_product_name_from_element(first_product)
            logger.info(f"点击商品: {product_name}")

            try:
                goods_info_link = first_product.find_element(By.XPATH, ".//a[contains(@class, 'goods-info')]")
                href = goods_info_link.get_attribute("href")
                logger.info(f"找到商品链接: {href}")
                
                self.driver.execute_script("arguments[0].removeAttribute('target');", goods_info_link)
                self.driver.execute_script("arguments[0].removeAttribute('rel');", goods_info_link)
                goods_info_link.click()
                
                logger.info("商品详情链接点击成功（已移除target属性）")
            except NoSuchElementException:
                logger.info("未找到goods-info链接，尝试查找包含goods的链接")
                link_elements = first_product.find_elements(By.TAG_NAME, "a")
                product_link = None
                for link in link_elements:
                    href = link.get_attribute("href")
                    if href and ("goods" in href or "/item/" in href or "/product/" in href):
                        product_link = link
                        break
                
                if product_link:
                    self.driver.execute_script("arguments[0].removeAttribute('target');", product_link)
                    self.driver.execute_script("arguments[0].removeAttribute('rel');", product_link)
                    product_link.click()
                    logger.info("商品详情链接点击成功（已移除target属性）")
                elif link_elements:
                    logger.info(f"找到{len(link_elements)}个链接，点击第一个")
                    self.driver.execute_script("arguments[0].removeAttribute('target');", link_elements[0])
                    link_elements[0].click()
                else:
                    logger.info("未找到链接，点击商品卡片本身")
                    self.driver.execute_script("arguments[0].click();", first_product)
            except Exception as e:
                logger.error(f"点击商品链接异常: {str(e)}")
                self.driver.execute_script("arguments[0].click();", first_product)

            logger.info("第一个商品点击成功")
        except Exception as e:
            logger.error(f"点击第一个商品失败: {str(e)}", exc_info=True)
            raise

    def get_product_name_from_element(self, product_element):
        """
        从商品元素中获取商品名称

        Args:
            product_element (WebElement): 商品元素

        Returns:
            str: 商品名称，未找到返回空字符串
        """
        try:
            name_element = product_element.find_element(*self.PRODUCT_NAME_LINK)
            return name_element.text.strip() or name_element.get_attribute("title") or ""
        except NoSuchElementException:
            try:
                name_element = product_element.find_element(*self.PRODUCT_NAME_TEXT)
                return name_element.text.strip()
            except NoSuchElementException:
                logger.warning("未找到商品名称元素")
                return ""
        except Exception as e:
            logger.error(f"获取商品名称失败: {str(e)}", exc_info=True)
            return ""

    def get_product_price_from_element(self, product_element):
        """
        从商品元素中获取商品价格

        Args:
            product_element (WebElement): 商品元素

        Returns:
            str: 商品价格，未找到返回空字符串
        """
        try:
            price_element = product_element.find_element(*self.PRODUCT_PRICE)
            return price_element.text.strip()
        except NoSuchElementException:
            logger.warning("未找到商品价格元素")
            return ""
        except Exception as e:
            logger.error(f"获取商品价格失败: {str(e)}", exc_info=True)
            return ""

    def get_all_product_names(self):
        """
        获取所有商品名称

        Returns:
            list: 商品名称列表，未找到返回空列表
        """
        logger.info("获取所有商品名称")
        try:
            self.wait_search_results_loaded()
            elements = self.driver.find_elements(*self.PRODUCT_ITEMS)
            product_names = []
            for element in elements:
                try:
                    name = self.get_product_name_from_element(element)
                    if name:
                        product_names.append(name)
                except StaleElementReferenceException:
                    logger.warning("获取商品名称时遇到StaleElementReferenceException，跳过")
                    continue
            logger.info(f"获取到商品名称列表: {product_names}")
            return product_names
        except Exception as e:
            logger.error(f"获取所有商品名称失败: {str(e)}", exc_info=True)
            return []

    def is_search_result_displayed(self):
        """
        判断搜索结果是否展示

        Returns:
            bool: 搜索结果展示返回True，否则返回False
        """
        logger.info("判断搜索结果是否展示")
        try:
            self.wait_search_results_loaded()
            elements = self.driver.find_elements(*self.PRODUCT_ITEMS)
            return len(elements) > 0
        except TimeoutException:
            logger.info("搜索结果未展示")
            return False
        except Exception as e:
            logger.error(f"判断搜索结果状态失败: {str(e)}", exc_info=True)
            return False

    def get_search_keyword(self):
        """
        获取当前搜索的关键词

        Returns:
            str: 搜索关键词，未找到返回空字符串
        """
        logger.info("获取当前搜索关键词")
        try:
            wait = self._get_wait()
            element = wait.until(EC.visibility_of_element_located(self.SEARCH_KEYWORD_DISPLAY))
            keyword = element.text.strip()
            logger.info(f"当前搜索关键词: {keyword}")
            return keyword
        except TimeoutException:
            logger.warning("未找到搜索关键词展示元素")
            return ""
        except Exception as e:
            logger.error(f"获取搜索关键词失败: {str(e)}", exc_info=True)
            return ""

    def get_search_url(self):
        """
        获取当前搜索页面的URL

        Returns:
            str: 当前页面URL
        """
        logger.info("获取搜索页面URL")
        url = self.driver.current_url
        logger.info(f"当前搜索页面URL: {url}")
        return url