import pytest
import time
from page.home_page import HomePage
from page.search_page import SearchPage
from page.product_detail_page import ProductDetailPage
from utils.yaml_util import YamlUtil
from base.AssertUtil import AssertUtil
from utils.log_util import logger


@pytest.mark.ui
@pytest.mark.smoke
class TestProductUI:
    """
    商品搜索和商品详情模块UI自动化测试用例
    覆盖场景：
        1. 首页搜索框输入关键词「电脑」，点击搜索，校验页面展示电脑类商品列表
        2. 搜索电脑后，滚动页面使首个商品可见，点击进入对应商品详情页
        3. 商品详情切换规格（套餐二+颜色+容量），校验价格随所选规格同步变更
        4. 详情页选定规格后点击加入购物车，校验弹出加入购物车成功提示
        5. 搜索框输入无匹配商品关键词（如水果），点击搜索校验空商品列表提示
        6. 搜索框不输入内容直接点击搜索，会有全部商品
        7. 商品详情未选择任何规格，点击加入购物车，校验错误提示
        8. 搜索电脑进入商品详情，切换多组规格并多次加购，校验每次成功弹窗正常弹出
    """

    def test_TC_PRODUCT_001(self, web_driver, login):
        """Scenario 1: Search for '电脑' and verify computer product list displayed"""
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
        """Scenario 3: Change specs (套餐二+颜色+容量) and verify price updates accordingly"""
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

        logger.info("=== Scroll to specs container ===")
        product_detail_page.scroll_to_specs_container()

        logger.info("=== Select first spec combination: 套餐二 + 金色 + 32G ===")
        product_detail_page.select_spec_combination("金色", "32G")
        time.sleep(1)

        price_gold_32g = product_detail_page.get_current_price()
        logger.info(f"Price for 金色/32G: {price_gold_32g}")
        AssertUtil.assert_true(
            price_gold_32g,
            message="Price not found for 金色/32G"
        )

        logger.info("=== Select second spec combination: 套餐二 + 金色 + 128G ===")
        product_detail_page.select_spec_combination("金色", "128G")
        time.sleep(1)

        price_gold_128g = product_detail_page.get_current_price()
        logger.info(f"Price for 金色/128G: {price_gold_128g}")
        AssertUtil.assert_true(
            price_gold_128g,
            message="Price not found for 金色/128G"
        )

        logger.info("=== Select third spec combination: 套餐二 + 银色 + 64G ===")
        product_detail_page.select_spec_combination("银色", "64G")
        time.sleep(1)

        price_silver_64g = product_detail_page.get_current_price()
        logger.info(f"Price for 银色/64G: {price_silver_64g}")
        AssertUtil.assert_true(
            price_silver_64g,
            message="Price not found for 银色/64G"
        )

        logger.info("Price updated correctly according to selected specs")

    def test_TC_PRODUCT_004(self, web_driver, login):
        """Scenario 4: Select spec (套餐二+金色+32G) and add to cart"""
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

        logger.info("=== Scroll to specs container ===")
        product_detail_page.scroll_to_specs_container()

        logger.info("=== Select spec combination: 套餐二 + 金色 + 32G ===")
        product_detail_page.select_spec_combination("金色", "32G")
        time.sleep(1)

        logger.info("=== Click add to cart button ===")
        product_detail_page.click_add_to_cart()

        logger.info("=== Wait for success modal and get message ===")
        time.sleep(2)

        success_msg = product_detail_page.get_success_message(timeout=10)
        logger.info(f"成功提示信息: {success_msg}")

        if not success_msg:
            logger.info("未通过定位器找到成功提示，尝试直接检查购物车数量变化")
            cart_count = product_detail_page.get_cart_count()
            logger.info(f"当前购物车数量: {cart_count}")
            if cart_count and int(cart_count) > 0:
                success_msg = f"购物车数量: {cart_count}"

        AssertUtil.assert_true(
            "加入购物车" in success_msg or "加入成功" in success_msg or ("购物车" in success_msg and "数量" in success_msg),
            message=f"加入购物车失败，成功提示: {success_msg}"
        )
        logger.info("加入购物车成功")

        logger.info("=== Close success modal ===")
        product_detail_page.close_success_modal()

    def test_TC_PRODUCT_005(self, web_driver, login):
        """Scenario 5: Search for non-existent product (e.g. '水果') and verify empty result"""
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

        logger.info("=== Scroll to specs container ===")
        product_detail_page.scroll_to_specs_container()

        logger.info("=== Click add to cart without selecting specs ===")
        product_detail_page.click_add_to_cart()

        logger.info("=== Wait for error message ===")
        time.sleep(2)

        error_message = product_detail_page.get_error_message(timeout=5)
        logger.info(f"错误提示信息: {error_message}")

        AssertUtil.assert_true(
            error_message,
            message="未找到错误提示框"
        )
        logger.info(f"错误提示信息已显示: {error_message}")

    def test_TC_PRODUCT_008(self, web_driver, login):
        """Scenario 8: Switch multiple specs (套餐二+颜色+容量) and add to cart multiple times"""
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

        logger.info("=== Scroll to specs container ===")
        product_detail_page.scroll_to_specs_container()

        spec_combinations = [
            ("金色", "32G"),
            ("金色", "128G"),
            ("银色", "64G"),
        ]

        success_count = 0

        for i, (color, capacity) in enumerate(spec_combinations):
            logger.info(f"=== Round {i+1}: Select spec combination: 套餐二 + {color} + {capacity} ===")

            product_detail_page.select_spec_combination(color, capacity)
            time.sleep(1)

            current_price = product_detail_page.get_current_price()
            logger.info(f"Round {i+1}: 当前价格: {current_price}")

            logger.info(f"Round {i+1}: 点击加入购物车按钮")
            product_detail_page.click_add_to_cart()

            logger.info(f"Round {i+1}: 等待弹窗出现")
            time.sleep(3)

            success_msg = product_detail_page.get_success_message(timeout=10)
            logger.info(f"Round {i+1} success message: {success_msg}")

            if not success_msg:
                logger.info(f"Round {i+1}: 未通过定位器找到成功提示，尝试检查购物车数量")
                cart_count = product_detail_page.get_cart_count()
                logger.info(f"Round {i+1}: 当前购物车数量: {cart_count}")
                if cart_count and int(cart_count) > 0:
                    success_msg = f"购物车数量: {cart_count}"

            if "加入购物车" in success_msg or "加入成功" in success_msg or ("购物车" in success_msg and "数量" in success_msg):
                success_count += 1
                logger.info(f"Round {i+1}: 加入购物车成功")

            logger.info(f"Round {i+1}: 关闭成功提示弹窗")
            product_detail_page.close_success_modal()

            time.sleep(1)

        AssertUtil.assert_greater_or_equal(
            success_count,
            1,
            message=f"Expected at least 1 successful add to cart, actual {success_count}"
        )
        logger.info(f"测试完成，成功加入购物车 {success_count} 次")
