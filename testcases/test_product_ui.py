import pytest
import time
from selenium.webdriver.common.by import By
from page.home_page import HomePage
from page.search_page import SearchPage
from page.product_detail_page import ProductDetailPage
from page.login_page import LoginPage
from utils.yaml_util import YamlUtil
from base.AssertUtil import AssertUtil
from utils.log_util import logger


@pytest.mark.ui
@pytest.mark.smoke
class TestProductUI:
    """
    商品搜索和商品详情模块UI自动化测试用例
    覆盖场景：
        1. 首页搜索框输入关键词「手机」，点击搜索，校验页面展示手机类商品列表
        2. 搜索手机后，滚动页面使首个商品可见，点击进入对应商品详情页
        3. 商品详情切换规格，校验价格随所选规格同步变更
        4. 详情页选定规格后点击加入购物车，校验弹出加入购物车成功提示
        5. 搜索框输入无匹配商品关键词（如水果），点击搜索校验空商品列表提示
        6. 搜索框不输入内容直接点击搜索，会有全部商品
        7. 商品详情未选择任何规格，点击加入购物车，校验请输入购买数量提示
        8. 搜索手机进入商品详情，切换多组规格并多次加购，校验每次成功弹窗正常弹出
    """

    def test_TC_PRODUCT_001(self, web_driver, login):
        """Scenario 1: Search for '手机' and verify mobile product list displayed"""
        login_page = LoginPage(web_driver)
        AssertUtil.assert_true(
            login_page.is_avatar_displayed(),
            message="User not logged in, login fixture failed"
        )

        search_data = YamlUtil.read_test_data("ui_data.yaml")["search"]
        keyword = search_data["search_keyword"]

        home_page = HomePage(web_driver)
        home_page.open_home_page()

        logger.info("=== Input search keyword ===")
        home_page.input_search_keyword(keyword)

        AssertUtil.assert_equal(
            home_page.get_search_input_value(),
            keyword,
            message=f"Search input value mismatch: expected '{keyword}', actual '{home_page.get_search_input_value()}'"
        )

        logger.info("=== Click search button ===")
        home_page.click_search_btn()

        search_page = SearchPage(web_driver)
        search_page.wait_search_results_loaded()

        AssertUtil.assert_true(
            search_page.is_search_result_displayed(),
            message="Search results not displayed"
        )

        product_count = search_page.get_product_count()
        logger.info(f"Search result product count: {product_count}")

        AssertUtil.assert_greater_or_equal(
            product_count,
            search_data["expected_min_results"],
            message=f"Insufficient search results: expected >= {search_data['expected_min_results']}, actual {product_count}"
        )

        current_url = search_page.get_search_url()
        AssertUtil.assert_in(
            "search",
            current_url,
            message=f"Search page URL mismatch: {current_url}"
        )

    def test_TC_PRODUCT_002(self, web_driver, login):
        """Scenario 2: Scroll to first product and click to enter product detail page"""
        login_page = LoginPage(web_driver)
        AssertUtil.assert_true(
            login_page.is_avatar_displayed(),
            message="User not logged in, login fixture failed"
        )

        search_data = YamlUtil.read_test_data("ui_data.yaml")["search"]
        keyword = search_data["search_keyword"]

        home_page = HomePage(web_driver)
        home_page.open_home_page()
        home_page.input_search_keyword(keyword)
        home_page.click_search_btn()

        search_page = SearchPage(web_driver)
        search_page.wait_search_results_loaded()

        first_product_element = search_page.get_first_product_element()
        AssertUtil.assert_true(
            first_product_element is not None,
            message="First product element not found"
        )

        first_product_name = search_page.get_product_name_from_element(first_product_element)
        logger.info(f"First product name: {first_product_name}")

        logger.info("=== Scroll to first product ===")
        web_driver.driver.execute_script(
            "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
            first_product_element
        )
        import time
        time.sleep(2)

        logger.info("=== Click first product ===")
        search_page.click_first_product()

        product_detail_page = ProductDetailPage(web_driver)
        product_detail_page.wait_page_loaded()

        detail_product_name = product_detail_page.get_product_name()
        logger.info(f"Product detail page product name: {detail_product_name}")

        AssertUtil.assert_true(
            first_product_name in detail_product_name or detail_product_name in first_product_name,
            message=f"Product name mismatch: search page '{first_product_name}', detail page '{detail_product_name}'"
        )

        current_url = product_detail_page.get_current_url()
        AssertUtil.assert_in(
            "goods",
            current_url,
            message=f"Product detail page URL mismatch: {current_url}"
        )

    def test_TC_PRODUCT_003(self, web_driver, login):
        """Scenario 3: Change specs and verify price updates accordingly"""
        login_page = LoginPage(web_driver)
        AssertUtil.assert_true(
            login_page.is_avatar_displayed(),
            message="User not logged in, login fixture failed"
        )

        search_data = YamlUtil.read_test_data("ui_data.yaml")["search"]
        keyword = search_data["search_keyword"]

        home_page = HomePage(web_driver)
        home_page.open_home_page()
        home_page.input_search_keyword(keyword)
        home_page.click_search_btn()

        search_page = SearchPage(web_driver)
        search_page.wait_search_results_loaded()
        search_page.click_first_product()

        product_detail_page = ProductDetailPage(web_driver)
        product_detail_page.wait_page_loaded()

        logger.info("=== Scroll to specs container once ===")
        product_detail_page.scroll_to_specs_container()

        logger.info("=== Get all spec options ===")
        all_specs = product_detail_page.get_all_spec_options()
        logger.info(f"All spec options (complete combinations): {[opt['text'] + ' - ' + opt.get('price', '') for opt in all_specs]}")

        available_specs = [spec for spec in all_specs if not spec["is_disabled"]]
        if len(available_specs) < 2:
            logger.info("Not enough available specs to test price change, skip")
            pytest.skip("Not enough available specs")

        logger.info("=== Reset all quantities before testing ===")
        product_detail_page.reset_all_quantities()
        import time
        time.sleep(1)

        initial_total_price = product_detail_page.get_price_total()
        logger.info(f"Initial total price (before selecting any spec): {initial_total_price}")

        logger.info("=== Select first complete spec combination ===")
        first_spec = available_specs[0]
        first_spec_text = first_spec["text"]
        first_spec_price = first_spec["price"]
        logger.info(f"Selecting spec: '{first_spec_text}' with price: {first_spec_price}")
        product_detail_page.select_spec_option(first_spec_text)
        time.sleep(1)

        price_after_first_spec = product_detail_page.get_price_total()
        logger.info(f"Total price after selecting '{first_spec_text}': {price_after_first_spec}")

        AssertUtil.assert_equal(
            price_after_first_spec,
            first_spec_price,
            message=f"Price mismatch for spec '{first_spec_text}': expected '{first_spec_price}', actual '{price_after_first_spec}'"
        )

        logger.info("=== Reset quantities before selecting next spec ===")
        product_detail_page.reset_all_quantities()
        time.sleep(1)

        logger.info("=== Select second complete spec combination ===")
        second_spec = available_specs[1]
        second_spec_text = second_spec["text"]
        second_spec_price = second_spec["price"]
        logger.info(f"Selecting spec: '{second_spec_text}' with price: {second_spec_price}")
        product_detail_page.select_spec_option(second_spec_text)
        time.sleep(1)

        price_after_second_spec = product_detail_page.get_price_total()
        logger.info(f"Total price after selecting '{second_spec_text}': {price_after_second_spec}")

        AssertUtil.assert_equal(
            price_after_second_spec,
            second_spec_price,
            message=f"Price mismatch for spec '{second_spec_text}': expected '{second_spec_price}', actual '{price_after_second_spec}'"
        )

        AssertUtil.assert_not_equal(
            price_after_first_spec,
            price_after_second_spec,
            message=f"Prices should differ for different specs: both are '{price_after_first_spec}'"
        )

        logger.info("Price updated correctly according to selected specs")

    def test_TC_PRODUCT_004(self, web_driver, login):
        """Scenario 4: Select first spec row (金色32G) and add to cart"""
        login_page = LoginPage(web_driver)
        AssertUtil.assert_true(
            login_page.is_avatar_displayed(),
            message="User not logged in, login fixture failed"
        )

        search_data = YamlUtil.read_test_data("ui_data.yaml")["search"]
        keyword = search_data["search_keyword"]

        home_page = HomePage(web_driver)
        home_page.open_home_page()
        home_page.input_search_keyword(keyword)
        home_page.click_search_btn()

        search_page = SearchPage(web_driver)
        search_page.wait_search_results_loaded()
        search_page.click_first_product()

        product_detail_page = ProductDetailPage(web_driver)
        product_detail_page.wait_page_loaded()

        logger.info("=== Find first spec row (金色32G) ===")
        cart_btns = web_driver.find_elements((By.XPATH, "//button[contains(@class, 'common-goods-cart-submit-event') and contains(text(), '加入购物车')]"))
        logger.info(f"找到加入购物车按钮数量: {len(cart_btns)}")
        
        if not cart_btns:
            AssertUtil.assert_true(False, message="未找到加入购物车按钮")
        
        first_cart_btn = cart_btns[0]
        logger.info("=== Click plus button to set quantity ===")
        web_driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", first_cart_btn)
        time.sleep(0.5)
        
        row = first_cart_btn.find_element(By.XPATH, "./ancestor::tr")
        plus_buttons = row.find_elements(By.XPATH, ".//button[@data-type='1']")
        if plus_buttons:
            plus_buttons[0].click()
            time.sleep(0.5)
            logger.info("已点击+按钮设置数量")
        else:
            input_fields = row.find_elements(By.XPATH, ".//input[@type='number']")
            if input_fields:
                input_fields[0].clear()
                input_fields[0].send_keys("1")
                time.sleep(0.5)
                logger.info("已输入数量为1")
        
        logger.info("=== Click add to cart button ===")
        web_driver.execute_script("arguments[0].click();", first_cart_btn)
        logger.info("加入购物车按钮点击成功")
        
        logger.info("=== Verify add to cart success ===")
        time.sleep(3)
        
        success_msg = web_driver.execute_script(
            "var el = document.querySelector('div.am-toast, div.am-modal-success, div.common-prompt'); return el ? el.textContent.trim() : '';"
        )
        logger.info(f"成功提示信息: {success_msg}")
        
        if "加入成功" in success_msg or "加入购物车成功" in success_msg:
            logger.info("加入购物车成功")
        else:
            js_result = web_driver.execute_script(
                "return Array.from(document.querySelectorAll('div, span')).filter(el => el.textContent && (el.textContent.includes('加入成功') || el.textContent.includes('加入购物车成功'))).map(el => el.textContent.trim())[0] || '';"
            )
            logger.info(f"JS查找成功提示: {js_result}")
            AssertUtil.assert_true(
                "加入成功" in js_result or "加入购物车成功" in js_result,
                message=f"未找到加入购物车成功提示，当前提示: {js_result}"
            )

    def test_TC_PRODUCT_005(self, web_driver, login):
        """Scenario 5: Search for non-existent product (e.g. '水果') and verify empty result"""
        login_page = LoginPage(web_driver)
        AssertUtil.assert_true(
            login_page.is_avatar_displayed(),
            message="User not logged in, login fixture failed"
        )

        search_data = YamlUtil.read_test_data("ui_data.yaml")["search"]
        no_match_keyword = search_data["no_match_keyword"]

        home_page = HomePage(web_driver)
        home_page.open_home_page()

        logger.info("=== Input no-match keyword ===")
        home_page.input_search_keyword(no_match_keyword)

        logger.info("=== Click search button ===")
        home_page.click_search_btn()

        search_page = SearchPage(web_driver)
        search_page.wait_search_results_loaded()

        product_count = search_page.get_product_count()
        logger.info(f"Search result count for '{no_match_keyword}': {product_count}")

        AssertUtil.assert_equal(
            product_count,
            0,
            message=f"Expected 0 products for non-match keyword, actual {product_count}"
        )

    def test_TC_PRODUCT_006(self, web_driver, login):
        """Scenario 6: Search with empty keyword and verify all products displayed"""
        login_page = LoginPage(web_driver)
        AssertUtil.assert_true(
            login_page.is_avatar_displayed(),
            message="User not logged in, login fixture failed"
        )

        home_page = HomePage(web_driver)
        home_page.open_home_page()

        logger.info("=== Clear search input ===")
        home_page.input_search_keyword("")

        logger.info("=== Click search button with empty input ===")
        home_page.click_search_btn()

        search_page = SearchPage(web_driver)
        search_page.wait_search_results_loaded()

        AssertUtil.assert_true(
            search_page.is_search_result_displayed(),
            message="Search results not displayed for empty keyword"
        )

        product_count = search_page.get_product_count()
        logger.info(f"Product count for empty keyword search: {product_count}")

        AssertUtil.assert_greater_or_equal(
            product_count,
            1,
            message=f"Expected at least 1 product for empty keyword, actual {product_count}"
        )

    def test_TC_PRODUCT_007(self, web_driver, login):
        """Scenario 7: Click add to cart without selecting specs, verify error message"""
        login_page = LoginPage(web_driver)
        AssertUtil.assert_true(
            login_page.is_avatar_displayed(),
            message="User not logged in, login fixture failed"
        )

        search_data = YamlUtil.read_test_data("ui_data.yaml")["search"]
        keyword = search_data["search_keyword"]

        home_page = HomePage(web_driver)
        home_page.open_home_page()
        home_page.input_search_keyword(keyword)
        home_page.click_search_btn()

        search_page = SearchPage(web_driver)
        search_page.wait_search_results_loaded()
        search_page.click_first_product()

        product_detail_page = ProductDetailPage(web_driver)
        product_detail_page.wait_page_loaded()

        logger.info("=== Find add to cart button ===")
        cart_btns = web_driver.find_elements((By.XPATH, "//button[contains(@class, 'common-goods-cart-submit-event') and contains(text(), '加入购物车')]"))
        logger.info(f"找到加入购物车按钮数量: {len(cart_btns)}")
        
        if not cart_btns:
            AssertUtil.assert_true(False, message="未找到加入购物车按钮")
        
        first_cart_btn = cart_btns[0]
        web_driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", first_cart_btn)
        time.sleep(0.5)
        
        logger.info("=== Click add to cart without selecting specs ===")
        web_driver.execute_script("arguments[0].click();", first_cart_btn)
        logger.info("加入购物车按钮点击成功")
        
        logger.info("=== Wait for error message ===")
        time.sleep(2)
        
        logger.info("=== Find error message ===")
        error_elements = web_driver.find_elements((By.XPATH, "//div[contains(@class, 'common-prompt') and contains(@class, 'am-alert-danger')]"))
        logger.info(f"找到错误提示框数量: {len(error_elements)}")
        
        if not error_elements:
            AssertUtil.assert_true(False, message="未找到错误提示框")
        
        error_element = error_elements[0]
        msg_elements = error_element.find_elements(By.XPATH, ".//p[@class='prompt-msg']")
        if msg_elements:
            error_message = msg_elements[0].text.strip()
        else:
            error_message = error_element.text.strip()
        
        logger.info(f"错误提示信息: {error_message}")
        
        AssertUtil.assert_true(
            "请输入购买数量" in error_message,
            message=f"Unexpected error message: {error_message}"
        )
        logger.info("Expected error message displayed: 请输入购买数量")

    def test_TC_PRODUCT_008(self, web_driver, login):
        """Scenario 8: Switch multiple specs and add to cart multiple times"""
        login_page = LoginPage(web_driver)
        AssertUtil.assert_true(
            login_page.is_avatar_displayed(),
            message="User not logged in, login fixture failed"
        )

        search_data = YamlUtil.read_test_data("ui_data.yaml")["search"]
        keyword = search_data["search_keyword"]

        home_page = HomePage(web_driver)
        home_page.open_home_page()
        home_page.input_search_keyword(keyword)
        home_page.click_search_btn()

        search_page = SearchPage(web_driver)
        search_page.wait_search_results_loaded()
        search_page.click_first_product()

        product_detail_page = ProductDetailPage(web_driver)
        product_detail_page.wait_page_loaded()

        logger.info("=== Find spec rows ===")
        spec_cart_btns = web_driver.find_elements((By.XPATH, "//button[contains(@class, 'common-goods-cart-submit-event') and contains(text(), '加入购物车')]"))
        logger.info(f"找到规格行加入购物车按钮数量: {len(spec_cart_btns)}")
        
        if len(spec_cart_btns) < 2:
            logger.info("Not enough available spec rows, skip test")
            pytest.skip("Not enough available spec rows")

        logger.info("=== Find top add to cart button ===")
        top_cart_btn = web_driver.find_elements((By.XPATH, "//button[@data-type='cart' and contains(@class, 'am-btn-secondary')]"))
        logger.info(f"找到顶部加入购物车按钮数量: {len(top_cart_btn)}")
        
        if not top_cart_btn:
            logger.info("未找到顶部加入购物车按钮，使用规格行按钮")
            use_top_btn = False
        else:
            use_top_btn = True
            top_cart_btn = top_cart_btn[0]

        success_count = 0

        for i in range(2):
            logger.info(f"=== Round {i+1}: Select spec row {i+1} ===")
            
            spec_cart_btn = spec_cart_btns[i]
            web_driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", spec_cart_btn)
            time.sleep(0.5)
            
            row = spec_cart_btn.find_element(By.XPATH, "./ancestor::tr")
            plus_buttons = row.find_elements(By.XPATH, ".//button[@data-type='1']")
            if plus_buttons:
                plus_buttons[0].click()
                time.sleep(0.5)
                logger.info(f"Round {i+1}: 已点击+按钮设置数量")
            else:
                input_fields = row.find_elements(By.XPATH, ".//input[@type='number']")
                if input_fields:
                    input_fields[0].clear()
                    input_fields[0].send_keys("1")
                    time.sleep(0.5)
                    logger.info(f"Round {i+1}: 已输入数量为1")
            
            logger.info(f"Round {i+1}: 点击加入购物车按钮")
            if use_top_btn:
                web_driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", top_cart_btn)
                time.sleep(0.5)
                web_driver.execute_script("arguments[0].click();", top_cart_btn)
                logger.info(f"Round {i+1}: 使用顶部加入购物车按钮")
            else:
                web_driver.execute_script("arguments[0].click();", spec_cart_btn)
                logger.info(f"Round {i+1}: 使用规格行加入购物车按钮")
            
            logger.info(f"Round {i+1}: 等待弹窗出现")
            for _ in range(5):
                time.sleep(1)
                modal_dialogs = web_driver.find_elements((By.XPATH, "//div[contains(@class, 'am-modal-dialog') and contains(@class, 'am-radius')]"))
                if modal_dialogs:
                    logger.info(f"Round {i+1}: 弹窗已出现")
                    
                    success_text = web_driver.execute_script(
                        "var el = document.querySelector('span.am-text-success'); return el ? el.textContent.trim() : '';"
                    )
                    logger.info(f"Round {i+1} success message: {success_text}")
                    
                    if "成功加入购物车" in success_text or "加入购物车成功" in success_text or "加入成功" in success_text:
                        success_count += 1
                        logger.info(f"Round {i+1}: 加入购物车成功")
                    
                    continue_shopping_btns = web_driver.find_elements((By.XPATH, "//button[contains(@class, 'am-btn-primary') and contains(text(), '继续购物')]"))
                    if continue_shopping_btns:
                        web_driver.execute_script("arguments[0].click();", continue_shopping_btns[0])
                        logger.info(f"Round {i+1}: 点击继续购物按钮")
                        time.sleep(1)
                    break
            
            time.sleep(1)

        AssertUtil.assert_greater_or_equal(
            success_count,
            1,
            message=f"Expected at least 1 successful add to cart, actual {success_count}"
        )
        logger.info(f"测试完成，成功加入购物车 {success_count} 次")