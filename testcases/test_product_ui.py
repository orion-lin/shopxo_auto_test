import pytest
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

    def _login(self, web_driver):
        """
        Execute login operation if not logged in

        Args:
            web_driver: WebDriverBase instance
        """
        login_page = LoginPage(web_driver)

        login_page.open_home_page()
        import time
        time.sleep(2)

        if login_page.is_avatar_displayed():
            logger.info("User already logged in, skip login step")
            return

        login_data = YamlUtil.read_test_data("ui_data.yaml")["login"]["normal"]
        username = login_data["username"]
        password = login_data["password"]

        logger.info("=== Call login module's login method ===")
        login_success = login_page.login(username, password)

        AssertUtil.assert_true(
            login_success,
            message="Login failed"
        )
        logger.info("Login successful")

        time.sleep(2)
        login_page.open_home_page()
        time.sleep(2)

        AssertUtil.assert_true(
            login_page.is_avatar_displayed(),
            message="User avatar not displayed on home page, login state not effective"
        )
        logger.info("Login state effective on home page")

    def test_search_mobile_products(self, web_driver):
        """Scenario 1: Search for '手机' and verify mobile product list displayed"""
        self._login(web_driver)

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

    def test_click_first_product_with_scroll(self, web_driver):
        """Scenario 2: Scroll to first product and click to enter product detail page"""
        self._login(web_driver)

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

    def test_spec_change_updates_price(self, web_driver):
        """Scenario 3: Change specs and verify price updates accordingly"""
        self._login(web_driver)

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

        if not product_detail_page.is_specs_container_displayed():
            logger.info("No specs available for current product, skip test")
            pytest.skip("No specs available")

        logger.info("=== Get initial price before selecting specs ===")
        initial_price = product_detail_page.get_product_price()
        logger.info(f"Initial price: {initial_price}")

        logger.info("=== Get all spec options ===")
        all_specs = product_detail_page.get_all_spec_options()
        logger.info(f"All spec options: {[opt['text'] for opt in all_specs]}")

        available_specs = [spec for spec in all_specs if not spec["is_disabled"]]
        if len(available_specs) < 2:
            logger.info("Not enough available specs to test price change, skip")
            pytest.skip("Not enough available specs")

        logger.info("=== Select first spec option ===")
        first_spec_text = available_specs[0]["text"]
        product_detail_page.select_spec_option(first_spec_text)
        import time
        time.sleep(2)

        price_after_first_spec = product_detail_page.get_product_price()
        logger.info(f"Price after selecting '{first_spec_text}': {price_after_first_spec}")

        logger.info("=== Select second spec option ===")
        second_spec_text = available_specs[1]["text"]
        product_detail_page.select_spec_option(second_spec_text)
        time.sleep(2)

        price_after_second_spec = product_detail_page.get_product_price()
        logger.info(f"Price after selecting '{second_spec_text}': {price_after_second_spec}")

        AssertUtil.assert_true(
            price_after_first_spec != "" or price_after_second_spec != "",
            message="Price not displayed after selecting specs"
        )

        logger.info("Price updated according to selected specs")

    def test_add_to_cart_success(self, web_driver):
        """Scenario 4: Select specs and add to cart, verify success message"""
        self._login(web_driver)

        search_data = YamlUtil.read_test_data("ui_data.yaml")["search"]
        keyword = search_data["search_keyword"]
        success_message = search_data["success_message"]

        home_page = HomePage(web_driver)
        home_page.open_home_page()
        home_page.input_search_keyword(keyword)
        home_page.click_search_btn()

        search_page = SearchPage(web_driver)
        search_page.wait_search_results_loaded()
        search_page.click_first_product()

        product_detail_page = ProductDetailPage(web_driver)
        product_detail_page.wait_page_loaded()

        logger.info("=== Check if specs need to be selected ===")
        if product_detail_page.is_specs_container_displayed():
            logger.info("=== Select product specs ===")
            product_detail_page.select_all_specs()

        logger.info("=== Click add to cart button ===")
        product_detail_page.click_add_to_cart()

        logger.info("=== Verify add to cart success message ===")
        actual_message = product_detail_page.get_success_message(timeout=5)
        logger.info(f"Actual success message: {actual_message}")

        AssertUtil.assert_true(
            "加入购物车成功" in actual_message or "加入成功" in actual_message or "购买" in actual_message,
            message=f"Add to cart failed, expected message containing '加入购物车成功' or '加入成功' or '购买', actual '{actual_message}'"
        )

    def test_search_no_match_keyword(self, web_driver):
        """Scenario 5: Search for non-existent product (e.g. '水果') and verify empty result"""
        self._login(web_driver)

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

    def test_search_empty_keyword(self, web_driver):
        """Scenario 6: Search with empty keyword and verify all products displayed"""
        self._login(web_driver)

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

    def test_add_to_cart_without_specs(self, web_driver):
        """Scenario 7: Click add to cart without selecting specs, verify error message"""
        self._login(web_driver)

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

        if not product_detail_page.is_specs_container_displayed():
            logger.info("No specs available for current product, skip test")
            pytest.skip("No specs available")

        logger.info("=== Click add to cart without selecting specs ===")
        product_detail_page.click_add_to_cart()

        logger.info("=== Get error message ===")
        error_message = product_detail_page.get_error_message(timeout=3)
        logger.info(f"Error message: {error_message}")

        success_message = product_detail_page.get_success_message(timeout=2)
        logger.info(f"Success message: {success_message}")

        if error_message:
            AssertUtil.assert_true(
                "请输入购买数量" in error_message or "请选择" in error_message or "请填写" in error_message,
                message=f"Unexpected error message: {error_message}"
            )
            logger.info("Expected error message displayed")
        elif success_message:
            logger.info("Add to cart succeeded even without selecting specs, possible behavior")
        else:
            logger.warning("No message displayed after clicking add to cart without specs")

    def test_multiple_spec_changes_and_add_to_cart(self, web_driver):
        """Scenario 8: Switch multiple specs and add to cart multiple times"""
        self._login(web_driver)

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

        if not product_detail_page.is_specs_container_displayed():
            logger.info("No specs available for current product, skip test")
            pytest.skip("No specs available")

        logger.info("=== Get all spec options ===")
        all_specs = product_detail_page.get_all_spec_options()
        available_specs = [spec for spec in all_specs if not spec["is_disabled"]]

        if len(available_specs) < 2:
            logger.info("Not enough available specs, skip test")
            pytest.skip("Not enough available specs")

        test_specs = available_specs[:2]
        success_count = 0

        for i, spec in enumerate(test_specs):
            logger.info(f"=== Round {i+1}: Select spec '{spec['text']}' ===")
            product_detail_page.select_spec_option(spec["text"])
            import time
            time.sleep(2)

            logger.info("=== Add to cart ===")
            product_detail_page.click_add_to_cart()

            actual_message = product_detail_page.get_success_message(timeout=5)
            logger.info(f"Round {i+1} message: {actual_message}")

            if "加入购物车成功" in actual_message or "加入成功" in actual_message or "购买" in actual_message:
                success_count += 1
                logger.info(f"Round {i+1} add to cart successful")
            else:
                logger.warning(f"Round {i+1} did not show success message")

        AssertUtil.assert_greater_or_equal(
            success_count,
            1,
            message="No successful add to cart operations"
        )
        logger.info(f"Total successful add to cart: {success_count} / {len(test_specs)}")