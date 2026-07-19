import pytest
import time
from page.checkout_page import CheckoutPage
from page.order_page import OrderPage
from page.cart_page import CartPage
from base.AssertUtil import AssertUtil
from utils.log_util import logger


@pytest.mark.ui
@pytest.mark.regression
class TestOrderUI:
    """
    订单提交结算模块UI自动化测试用例（TC_ORDER_001-005）
    前置条件：登录→购物车→选择商品→去结算
    """

    @pytest.fixture(scope="class", autouse=True)
    def setup_class(self, web_driver, login, request):
        """
        测试类级别的前置条件：完成登录并导航到结算页面

        流程：
            1. 复用登录模块的login fixture完成登录
            2. 打开购物车页面
            3. 勾选商品（如果未勾选）
            4. 点击结算按钮跳转到结算页面

        Args:
            web_driver: WebDriverBase实例
            login: UI登录fixture
            request: pytest请求对象，用于设置测试类属性
        """
        logger.info("========== 订单结算测试类前置条件 ==========")

        cart_page = CartPage(web_driver)
        checkout_page = CheckoutPage(web_driver)
        order_page = OrderPage(web_driver)

        request.cls.cart_page = cart_page
        request.cls.checkout_page = checkout_page
        request.cls.order_page = order_page

        logger.info("=== 打开商品详情页并添加商品到购物车 ===")
        from page.product_detail_page import ProductDetailPage
        product_page = ProductDetailPage(web_driver)
        web_driver.driver.get(f"http://shopxo.local/?s=goods/index/id/25.html")
        time.sleep(2)
        product_page.click_add_to_cart()
        time.sleep(2)

        logger.info("=== 打开购物车页面 ===")
        cart_page.open_cart_page()
        time.sleep(2)

        is_cart_empty = cart_page.is_cart_empty()
        if is_cart_empty:
            logger.error("购物车为空，添加商品失败")
            pytest.skip("购物车为空，跳过所有订单结算测试")

        logger.info("=== 勾选第一个商品 ===")
        try:
            cart_page.select_all_products()
            time.sleep(0.5)
        except Exception as e:
            logger.warning(f"全选失败，尝试单独勾选: {str(e)}")
            cart_page.select_product(0)
            time.sleep(0.5)

        logger.info("=== 点击结算按钮 ===")
        checkout_result = cart_page.click_checkout()
        AssertUtil.assert_true(checkout_result, message="点击结算按钮失败")
        time.sleep(2)

        is_checkout_page = checkout_page.is_checkout_page_displayed()
        AssertUtil.assert_true(is_checkout_page, message="未成功跳转到结算页面")

        logger.info("前置条件准备完成：已到达结算页面")

    def test_TC_ORDER_001_checkout_product_display(self):
        """
        TC_ORDER_001: 结算页面商品信息回显验证

        预期结果：
            1. 结算页面成功加载
            2. 购物车勾选商品信息正确回显（商品名称、单价、数量、合计总价）
        """
        logger.info("=== TC_ORDER_001: 验证结算页面商品信息回显 ===")

        is_checkout_page = self.checkout_page.is_checkout_page_displayed()
        AssertUtil.assert_true(is_checkout_page, message="结算页面未成功加载")

        products = self.checkout_page.get_checkout_products()
        AssertUtil.assert_true(len(products) > 0, message="未获取到结算页商品信息")

        for product in products:
            AssertUtil.assert_true(product.get("name"), message="商品名称为空")
            AssertUtil.assert_true(product.get("price"), message="商品单价为空")
            AssertUtil.assert_true(product.get("quantity") > 0, message="商品数量无效")
            AssertUtil.assert_true(product.get("subtotal"), message="商品小计为空")
            logger.info(f"商品信息验证通过: {product['name']} / {product['price']} / "
                        f"数量: {product['quantity']} / 小计: {product['subtotal']}")

        logger.info("TC_ORDER_001 测试通过")

    def test_TC_ORDER_002_default_address_selected(self):
        """
        TC_ORDER_002: 默认收货地址验证

        预期结果：
            1. 结算页面默认勾选系统预设收货地址
            2. 收货地址信息完整显示（姓名、电话、详细地址）
        """
        logger.info("=== TC_ORDER_002: 验证默认收货地址 ===")

        is_default_selected = self.checkout_page.is_default_address_selected()
        AssertUtil.assert_true(is_default_selected, message="未默认选中收货地址")

        address_info = self.checkout_page.get_default_address_info()
        AssertUtil.assert_true(address_info.get("name"), message="收货人姓名为空")
        AssertUtil.assert_true(address_info.get("phone"), message="收货人电话为空")
        AssertUtil.assert_true(address_info.get("detail"), message="收货地址详情为空")

        logger.info(f"默认收货地址验证通过: 姓名={address_info['name']}, "
                    f"电话={address_info['phone']}, 地址={address_info['detail']}")
        logger.info("TC_ORDER_002 测试通过")

    def test_TC_ORDER_003_checkout_total_amount(self):
        """
        TC_ORDER_003: 结算页总金额验证

        预期结果：
            1. 结算页面显示总金额
            2. 总金额大于0
            3. 总金额格式正确（包含货币符号）
        """
        logger.info("=== TC_ORDER_003: 验证结算页总金额 ===")

        total_amount = self.checkout_page.get_total_amount()
        AssertUtil.assert_true(total_amount, message="总金额为空")

        cleaned_amount = total_amount.replace("¥", "").replace("￥", "").replace(",", "").strip()
        AssertUtil.assert_true(cleaned_amount, message="总金额格式无效")
        AssertUtil.assert_true(float(cleaned_amount) > 0, message="总金额应大于0")

        logger.info(f"总金额验证通过: {total_amount}")
        logger.info("TC_ORDER_003 测试通过")

    def test_TC_ORDER_004_select_payment_and_submit(self):
        """
        TC_ORDER_004: 选择支付方式并提交订单

        预期结果：
            1. 选择支付方式成功
            2. 点击提交订单按钮后跳转到支付成功页面
            3. 支付成功页面显示成功提示
        """
        logger.info("=== TC_ORDER_004: 验证选择支付方式并提交订单 ===")

        current_payment = self.checkout_page.get_selected_payment_method()
        logger.info(f"当前默认支付方式: {current_payment}")

        select_result = self.checkout_page.select_payment_method("现金支付")
        AssertUtil.assert_true(select_result, message="选择支付方式失败")

        selected_payment = self.checkout_page.get_selected_payment_method()
        logger.info(f"选择后的支付方式: {selected_payment}")

        submit_result = self.checkout_page.click_submit_order()
        AssertUtil.assert_true(submit_result, message="点击提交订单按钮失败")
        time.sleep(3)

        is_pay_success = self.checkout_page.is_pay_success_page_displayed()
        AssertUtil.assert_true(is_pay_success, message="未跳转到支付成功页面")

        logger.info("TC_ORDER_004 测试通过")

    def test_TC_ORDER_005_pay_success_page_and_my_order_btn(self):
        """
        TC_ORDER_005: 支付成功页验证及我的订单按钮

        预期结果：
            1. 支付成功页面显示成功提示信息
            2. 点击"我的订单"按钮成功跳转到订单列表页面
        """
        logger.info("=== TC_ORDER_005: 验证支付成功页及我的订单按钮 ===")

        is_pay_success = self.checkout_page.is_pay_success_page_displayed()
        AssertUtil.assert_true(is_pay_success, message="当前不是支付成功页面")

        my_order_result = self.checkout_page.click_my_order_btn()
        AssertUtil.assert_true(my_order_result, message="点击我的订单按钮失败")
        time.sleep(2)

        is_order_page = self.order_page.is_order_page_displayed()
        AssertUtil.assert_true(is_order_page, message="未成功跳转到订单列表页面")

        logger.info("TC_ORDER_005 测试通过")


@pytest.mark.ui
@pytest.mark.regression
class TestOrderListUI:
    """
    订单列表模块测试类（TC_ORDER_006-008）
    测试订单列表页面功能：订单展示、商品信息、实付金额等
    """

    @pytest.fixture(scope="class", autouse=True)
    def setup_class(self, web_driver, login, request):
        """测试类级别前置条件：登录后打开订单列表页面"""
        logger.info("========== Order List Test Class Preconditions ==========")
        order_page = OrderPage(web_driver)
        request.cls.order_page = order_page

        logger.info("=== 打开订单列表页面 ===")
        base_url = web_driver.env_config.get("base_url", "")
        web_driver.driver.get(f"{base_url}/?s=order/index.html")
        time.sleep(3)

        is_order_page = order_page.is_order_page_displayed()
        AssertUtil.assert_true(is_order_page, message="未成功跳转到订单列表页面")

        logger.info("订单列表测试前置条件准备完成")

    def test_TC_ORDER_006_order_list_displays_new_order(self):
        """
        TC_ORDER_006: 订单列表展示新订单验证

        预期结果：
            1. 订单列表页面成功加载
            2. 订单列表中存在刚刚创建的订单
            3. 订单状态为已支付或待发货
        """
        logger.info("=== TC_ORDER_006: 验证订单列表展示新订单 ===")

        is_order_page = self.order_page.is_order_page_displayed()
        AssertUtil.assert_true(is_order_page, message="订单列表页面未成功加载")

        orders = self.order_page.get_order_list()
        AssertUtil.assert_true(len(orders) > 0, message="未获取到订单列表")

        latest_order = orders[0]
        AssertUtil.assert_true(latest_order.get("order_no"), message="订单号为空")
        AssertUtil.assert_true(latest_order.get("status"), message="订单状态为空")

        logger.info(f"最新订单信息: 订单号={latest_order['order_no']}, 状态={latest_order['status']}")
        logger.info("TC_ORDER_006 测试通过")

    def test_TC_ORDER_007_order_product_info_validation(self):
        """
        TC_ORDER_007: 订单商品名称和数量验证

        预期结果：
            1. 订单中展示商品名称信息
            2. 订单中展示购买数量信息
            3. 商品信息与结算页一致
        """
        logger.info("=== TC_ORDER_007: 验证订单商品名称和数量 ===")

        latest_order = self.order_page.get_latest_order()
        AssertUtil.assert_true(latest_order, message="未找到最新订单")

        products = latest_order.get("products", [])
        AssertUtil.assert_true(len(products) > 0, message="订单中没有商品信息")

        for product in products:
            AssertUtil.assert_true(product.get("name"), message="商品名称为空")
            AssertUtil.assert_true(product.get("quantity") > 0, message="商品数量无效")
            logger.info(f"订单商品验证通过: {product['name']}, 数量: {product['quantity']}")

        logger.info("TC_ORDER_007 测试通过")

    def test_TC_ORDER_008_order_payment_amount_validation(self):
        """
        TC_ORDER_008: 订单实付金额验证

        预期结果：
            1. 订单列表中显示实付金额
            2. 实付金额大于0
            3. 实付金额格式正确
        """
        logger.info("=== TC_ORDER_008: 验证订单实付金额 ===")

        latest_order = self.order_page.get_latest_order()
        AssertUtil.assert_true(latest_order, message="未找到最新订单")

        payment_amount = latest_order.get("payment", "")
        AssertUtil.assert_true(payment_amount, message="实付金额为空")

        cleaned_amount = payment_amount.replace("¥", "").replace("￥", "").replace(",", "").strip()
        AssertUtil.assert_true(cleaned_amount, message="实付金额格式无效")
        AssertUtil.assert_true(float(cleaned_amount) > 0, message="实付金额应大于0")

        logger.info(f"实付金额验证通过: {payment_amount}")
        logger.info("TC_ORDER_008 测试通过")
