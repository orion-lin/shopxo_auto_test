import pytest
import time
import re
from page.user_center_page import UserCenterPage
from page.order_page import OrderPage
from page.checkout_page import CheckoutPage
from page.cart_page import CartPage
from base.AssertUtil import AssertUtil
from utils.log_util import logger


@pytest.mark.ui
@pytest.mark.regression
class TestOrderQueryUI:
    """
    订单查询模块UI自动化测试用例（TC_ORDER_QUERY_001-005）
    业务功能：登录用户进入个人中心-订单管理，查看全部历史订单，校验刚提交订单数据一致性
    """

    @pytest.fixture(scope="class", autouse=True)
    def setup_class(self, web_driver, login, request):
        """
        测试类级别的前置条件：完成登录并创建测试订单

        流程：
            1. 复用登录模块的login fixture完成登录
            2. 添加商品到购物车
            3. 结算并创建订单（现金支付）
            4. 记录结算页面的订单数据用于后续校验
            5. 导航到个人中心-订单管理页面

        Args:
            web_driver: WebDriverBase实例
            login: UI登录fixture
            request: pytest请求对象，用于设置测试类属性
        """
        logger.info("========== 订单查询测试类前置条件 ==========")

        # 创建页面实例
        cart_page = CartPage(web_driver)
        checkout_page = CheckoutPage(web_driver)
        order_page = OrderPage(web_driver)
        user_center_page = UserCenterPage(web_driver)

        request.cls.cart_page = cart_page
        request.cls.checkout_page = checkout_page
        request.cls.order_page = order_page
        request.cls.user_center_page = user_center_page

        # 添加商品到购物车
        logger.info("=== 添加商品到购物车 ===")
        from page.product_detail_page import ProductDetailPage
        product_page = ProductDetailPage(web_driver)
        web_driver.driver.get("http://shopxo.local/?s=goods/index/id/25.html")
        time.sleep(2)
        product_page.click_add_to_cart()
        time.sleep(2)

        # 打开购物车页面
        cart_page.open_cart_page()
        time.sleep(2)
        
        # 查看购物车商品数量并将数量修改为1
        cart_products = cart_page.get_cart_products()
        logger.info(f"购物车商品数量: {len(cart_products)}")
        for i, p in enumerate(cart_products):
            logger.info(f"商品{i+1}: {p.get('name')}, 数量: {p.get('quantity')}, 价格: {p.get('price')}")
        
        # 将购物车中第一个商品数量修改为1
        if cart_products:
            current_qty = cart_products[0].get('quantity', 1)
            logger.info(f"当前商品数量: {current_qty}")
            while current_qty > 1:
                try:
                    new_qty = cart_page.decrease_quantity(0)
                    time.sleep(1)
                    logger.info(f"减少数量后: {new_qty}")
                    if new_qty <= 1:
                        break
                    current_qty = new_qty
                except Exception as e:
                    logger.warning(f"减少数量失败: {str(e)}")
                    break
            logger.info("商品数量已修改为1")
        
        # 重新获取购物车信息确认数量
        cart_products = cart_page.get_cart_products()
        logger.info(f"修改后购物车商品数量: {len(cart_products)}")
        for i, p in enumerate(cart_products):
            logger.info(f"商品{i+1}: {p.get('name')}, 数量: {p.get('quantity')}, 价格: {p.get('price')}")

        # 勾选商品并结算
        logger.info("=== 勾选商品并结算 ===")
        try:
            cart_page.select_all_products()
        except Exception:
            cart_page.select_product(0)
        time.sleep(0.5)

        cart_page.click_checkout()
        time.sleep(2)

        # 记录结算页面数据
        logger.info("=== 记录结算页面订单数据 ===")
        checkout_products = checkout_page.get_checkout_products()
        checkout_total_amount = checkout_page.get_total_amount()
        
        request.cls.checkout_products = checkout_products
        request.cls.checkout_total_amount = checkout_total_amount

        logger.info(f"结算页面商品数: {len(checkout_products)}")
        for p in checkout_products:
            logger.info(f"商品: {p.get('name')}, 数量: {p.get('quantity')}, 单价: {p.get('price')}, 小计: {p.get('subtotal')}")
        logger.info(f"结算页面总金额: {checkout_total_amount}")

        # 选择现金支付并提交订单
        logger.info("=== 选择现金支付并提交订单 ===")
        checkout_page.select_payment_method("现金支付")
        time.sleep(0.5)
        checkout_page.click_submit_order()
        time.sleep(3)

        # 导航到个人中心-订单管理页面
        logger.info("=== 导航到个人中心-订单管理页面 ===")
        user_center_page.open_user_center_page()
        time.sleep(2)
        
        user_center_page.click_order_management()
        time.sleep(2)

        logger.info("订单查询测试前置条件准备完成")

    def test_TC_ORDER_QUERY_001_navigate_from_user_center(self):
        """
        TC_ORDER_QUERY_001: 从个人中心进入订单管理页面验证

        预期结果：
            1. 个人中心页面成功加载
            2. 点击订单管理菜单成功跳转到订单列表页面
            3. 订单列表页面成功显示
        """
        logger.info("=== TC_ORDER_QUERY_001: 验证从个人中心进入订单管理页面 ===")

        is_order_page = self.order_page.is_order_page_displayed()
        AssertUtil.assert_true(is_order_page, message="订单列表页面未成功加载")

        logger.info("TC_ORDER_QUERY_001 测试通过")

    def test_TC_ORDER_QUERY_002_order_list_displays_latest_first(self):
        """
        TC_ORDER_QUERY_002: 订单列表第一条为最新下单记录验证

        预期结果：
            1. 订单列表页面成功加载
            2. 订单列表中存在订单记录
            3. 第一条订单为最新创建的订单（状态为已支付或待发货）
        """
        logger.info("=== TC_ORDER_QUERY_002: 验证订单列表第一条为最新下单记录 ===")

        orders = self.order_page.get_order_list()
        AssertUtil.assert_true(len(orders) > 0, message="订单列表为空")

        latest_order = orders[0]
        logger.info(f"最新订单: 订单号={latest_order.get('order_no')}, 状态={latest_order.get('status')}")

        AssertUtil.assert_true(latest_order.get("order_no"), message="最新订单号为空")
        AssertUtil.assert_true(latest_order.get("status"), message="最新订单状态为空")

        valid_status = ["已支付", "待发货", "待支付"]
        status_valid = any(status in latest_order.get("status", "") for status in valid_status)
        AssertUtil.assert_true(status_valid, message=f"最新订单状态{latest_order.get('status')}不在有效状态列表中")

        logger.info("TC_ORDER_QUERY_002 测试通过")

    def test_TC_ORDER_QUERY_003_order_product_name_consistency(self):
        """
        TC_ORDER_QUERY_003: 订单商品名称一致性校验

        预期结果：
            1. 订单列表第一条订单的商品名称与结算页面完全一致
        """
        logger.info("=== TC_ORDER_QUERY_003: 验证订单商品名称一致性 ===")

        latest_order = self.order_page.get_latest_order()
        AssertUtil.assert_true(latest_order, message="未获取到最新订单")

        order_products = latest_order.get("products", [])
        AssertUtil.assert_true(len(order_products) > 0, message="订单中无商品")

        checkout_products = getattr(self, "checkout_products", [])
        AssertUtil.assert_true(len(checkout_products) > 0, message="结算页面无商品记录")

        order_product_names = [p.get("name", "") for p in order_products]
        checkout_product_names = [p.get("name", "") for p in checkout_products]

        logger.info(f"订单页面商品名称: {order_product_names}")
        logger.info(f"结算页面商品名称: {checkout_product_names}")

        for order_name, checkout_name in zip(order_product_names, checkout_product_names):
            AssertUtil.assert_true(order_name == checkout_name, 
                message=f"商品名称不一致: 订单页={order_name}, 结算页={checkout_name}")

        logger.info("TC_ORDER_QUERY_003 测试通过")

    def test_TC_ORDER_QUERY_004_order_product_quantity_consistency(self):
        """
        TC_ORDER_QUERY_004: 订单商品数量一致性校验

        预期结果：
            1. 订单列表第一条订单的商品数量与结算页面完全一致
        """
        logger.info("=== TC_ORDER_QUERY_004: 验证订单商品数量一致性 ===")

        latest_order = self.order_page.get_latest_order()
        AssertUtil.assert_true(latest_order, message="未获取到最新订单")

        order_products = latest_order.get("products", [])
        AssertUtil.assert_true(len(order_products) > 0, message="订单中无商品")

        checkout_products = getattr(self, "checkout_products", [])
        AssertUtil.assert_true(len(checkout_products) > 0, message="结算页面无商品记录")

        order_quantities = [p.get("quantity", 0) for p in order_products]
        checkout_quantities = [p.get("quantity", 0) for p in checkout_products]

        logger.info(f"订单页面商品数量: {order_quantities}")
        logger.info(f"结算页面商品数量: {checkout_quantities}")

        for order_qty, checkout_qty in zip(order_quantities, checkout_quantities):
            AssertUtil.assert_true(order_qty == checkout_qty, 
                message=f"商品数量不一致: 订单页={order_qty}, 结算页={checkout_qty}")

        logger.info("TC_ORDER_QUERY_004 测试通过")

    def test_TC_ORDER_QUERY_005_order_total_amount_validation(self):
        """
        TC_ORDER_QUERY_005: 订单实付金额验证

        预期结果：
            1. 订单列表第一条订单的实付金额不为空
            2. 实付金额格式正确（包含货币符号）
        """
        logger.info("=== TC_ORDER_QUERY_005: 验证订单实付金额 ===")

        latest_order = self.order_page.get_latest_order()
        AssertUtil.assert_true(latest_order, message="未获取到最新订单")

        order_payment = latest_order.get("payment", "")
        AssertUtil.assert_true(order_payment, message="订单实付金额为空")

        logger.info(f"订单页面实付金额: {order_payment}")

        AssertUtil.assert_true(order_payment.startswith('￥') or order_payment.startswith('¥'), 
            message=f"订单金额格式不正确: {order_payment}")

        AssertUtil.assert_true('.' in order_payment or re.search(r'\d+', order_payment), 
            message=f"订单金额不含数字: {order_payment}")

        logger.info("TC_ORDER_QUERY_005 测试通过")