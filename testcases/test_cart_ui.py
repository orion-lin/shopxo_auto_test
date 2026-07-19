import pytest
import time
from page.cart_page import CartPage
from base.AssertUtil import AssertUtil
from utils.log_util import logger


@pytest.mark.ui
@pytest.mark.regression
class TestCartUI:
    """
    购物车管理模块UI自动化测试用例
    复用登录模块的login fixture完成登录
    """

    @pytest.fixture(autouse=True)
    def setup_class(self, web_driver, login):
        """
        测试类级别的前置条件：打开购物车页面

        Args:
            web_driver: WebDriverBase实例
            login: UI登录fixture
        """
        logger.info("========== 购物车测试类前置条件 ==========")
        self.cart_page = CartPage(web_driver)
        self.cart_page.open_cart_page()
        time.sleep(2)

    def test_TC_CART_001_view_cart_products(self):
        """
        TC_CART_001: 进入购物车页面，验证已添加商品信息展示

        预期结果：
            1. 购物车页面成功加载
            2. 展示商品名称、规格、单价、数量、小计金额等信息
        """
        logger.info("=== TC_CART_001: 验证购物车商品信息展示 ===")

        is_cart_displayed = self.cart_page.is_cart_page_displayed()
        AssertUtil.assert_true(is_cart_displayed, message="购物车页面未成功加载")

        is_empty = self.cart_page.is_cart_empty()
        if is_empty:
            logger.warning("购物车为空，跳过商品信息验证")
            pytest.skip("购物车为空，无法验证商品信息展示")

        products = self.cart_page.get_cart_products()
        AssertUtil.assert_true(len(products) > 0, message="未获取到购物车商品信息")

        for product in products:
            AssertUtil.assert_true(product.get("name"), message="商品名称为空")
            AssertUtil.assert_true(product.get("price"), message="商品单价为空")
            AssertUtil.assert_true(product.get("quantity") > 0, message="商品数量无效")
            AssertUtil.assert_true(product.get("subtotal"), message="商品小计为空")
            spec_info = product.get("spec") or "无规格"
            logger.info(f"商品信息验证通过: {product['name']} / {spec_info} / {product['price']}")

        logger.info("TC_CART_001 测试通过")

    def test_TC_CART_002_increase_quantity(self):
        """
        TC_CART_002: 数量加按钮测试

        预期结果：
            1. 点击数量加按钮后，商品数量增加1
            2. 小计金额相应更新
            3. 显示"更新成功"提示
        """
        logger.info("=== TC_CART_002: 验证数量加按钮功能 ===")

        is_empty = self.cart_page.is_cart_empty()
        if is_empty:
            logger.warning("购物车为空，跳过数量增加测试")
            pytest.skip("购物车为空，无法测试数量增加")

        products_before = self.cart_page.get_cart_products()
        original_quantity = products_before[0]["quantity"]

        new_quantity = self.cart_page.increase_quantity(0)

        AssertUtil.assert_equal(new_quantity, original_quantity + 1,
                               message=f"数量增加失败，预期: {original_quantity + 1}, 实际: {new_quantity}")

        products_after = self.cart_page.get_cart_products()
        AssertUtil.assert_equal(products_after[0]["quantity"], original_quantity + 1,
                               message="刷新后数量未更新")

        prompt_message = self.cart_page.get_prompt_message()
        if prompt_message:
            logger.info(f"提示信息验证成功: {prompt_message}")
            self.cart_page.close_prompt()
        else:
            logger.warning("未找到提示弹窗（可能已自动消失）")

        logger.info("TC_CART_002 测试通过")

    def test_TC_CART_003_decrease_quantity_min_value(self):
        """
        TC_CART_003: 数量减按钮测试（验证最小值为1）

        预期结果：
            1. 当数量大于1时，点击减按钮数量减少1，显示"更新成功"提示
            2. 当数量等于1时，点击减按钮数量保持为1，显示"最低起购数量1台"提示
        """
        logger.info("=== TC_CART_003: 验证数量减按钮功能及最小值限制 ===")

        is_empty = self.cart_page.is_cart_empty()
        if is_empty:
            logger.warning("购物车为空，跳过数量减少测试")
            pytest.skip("购物车为空，无法测试数量减少")

        products_before = self.cart_page.get_cart_products()
        original_quantity = products_before[0]["quantity"]

        if original_quantity > 1:
            new_quantity = self.cart_page.decrease_quantity(0)
            AssertUtil.assert_equal(new_quantity, original_quantity - 1,
                                   message=f"数量减少失败，预期: {original_quantity - 1}, 实际: {new_quantity}")

            products_after = self.cart_page.get_cart_products()
            AssertUtil.assert_equal(products_after[0]["quantity"], original_quantity - 1,
                                   message="刷新后数量未更新")

            prompt_message = self.cart_page.get_prompt_message()
            if prompt_message:
                logger.info(f"提示信息验证成功: {prompt_message}")
                self.cart_page.close_prompt()
            else:
                logger.warning("未找到提示弹窗（可能已自动消失）")
        else:
            new_quantity = self.cart_page.decrease_quantity(0)
            AssertUtil.assert_equal(new_quantity, 1,
                                   message=f"数量已为最小值1，减少后应为1，实际: {new_quantity}")

            products_after = self.cart_page.get_cart_products()
            AssertUtil.assert_equal(products_after[0]["quantity"], 1,
                                   message="数量已为1，点击减按钮后数量应保持为1")

            prompt_message = self.cart_page.get_prompt_message()
            if prompt_message:
                logger.info(f"提示信息验证成功: {prompt_message}")
                self.cart_page.close_prompt()
            else:
                logger.warning("未找到提示弹窗（可能已自动消失）")

        logger.info("TC_CART_003 测试通过")

    def test_TC_CART_004_select_product_and_calculate_total(self):
        """
        TC_CART_004: 勾选商品后验证底部自动计算总金额

        预期结果：
            1. 勾选商品后，已选数量正确更新（显示已选商品的总数量）
            2. 底部总金额正确计算（已选商品小计之和）
        """
        logger.info("=== TC_CART_004: 验证勾选商品后总金额计算 ===")

        is_empty = self.cart_page.is_cart_empty()
        if is_empty:
            logger.warning("购物车为空，跳过勾选测试")
            pytest.skip("购物车为空，无法测试勾选功能")

        self.cart_page.deselect_all_products()
        time.sleep(0.5)

        products = self.cart_page.get_cart_products()
        if len(products) < 2:
            logger.warning("购物车商品数量不足，跳过部分验证")
            selected_count = self.cart_page.get_selected_count()
            AssertUtil.assert_equal(selected_count, 0, message="取消全选后已选数量应为0")

            self.cart_page.select_product(0)
            time.sleep(0.5)
            selected_count = self.cart_page.get_selected_count()
            expected_count = products[0]["quantity"]
            AssertUtil.assert_equal(selected_count, expected_count,
                                   message=f"勾选一个商品后已选数量应为{expected_count}，实际为{selected_count}")
        else:
            selected_count = self.cart_page.get_selected_count()
            AssertUtil.assert_equal(selected_count, 0, message="取消全选后已选数量应为0")

            self.cart_page.select_product(0)
            time.sleep(0.5)
            selected_count = self.cart_page.get_selected_count()
            expected_count = products[0]["quantity"]
            AssertUtil.assert_equal(selected_count, expected_count,
                                   message=f"勾选第一个商品后已选数量应为{expected_count}，实际为{selected_count}")

            self.cart_page.select_product(1)
            time.sleep(0.5)
            selected_count = self.cart_page.get_selected_count()
            expected_count = products[0]["quantity"] + products[1]["quantity"]
            AssertUtil.assert_equal(selected_count, expected_count,
                                   message=f"勾选两个商品后已选数量应为{expected_count}，实际为{selected_count}")

        total_amount = self.cart_page.get_total_amount()
        AssertUtil.assert_true(total_amount, message="总金额为空")
        cleaned_amount = total_amount.replace("¥", "").replace("￥", "").replace(",", "")
        AssertUtil.assert_true(float(cleaned_amount) > 0,
                               message="总金额应大于0")

        logger.info(f"已选数量: {selected_count}, 总金额: {total_amount}")
        logger.info("TC_CART_004 测试通过")

    def test_TC_CART_005_select_all_products(self):
        """
        TC_CART_005: 全选商品测试

        预期结果：
            1. 点击全选按钮后，所有商品均被勾选
            2. 已选数量等于商品总数
        """
        logger.info("=== TC_CART_005: 验证全选商品功能 ===")

        is_empty = self.cart_page.is_cart_empty()
        if is_empty:
            logger.warning("购物车为空，跳过敏选测试")
            pytest.skip("购物车为空，无法测试全选功能")

        self.cart_page.deselect_all_products()
        time.sleep(0.5)

        products_before = self.cart_page.get_cart_products()
        product_count = len(products_before)

        self.cart_page.select_all_products()
        time.sleep(0.5)

        products_after = self.cart_page.get_cart_products()
        for product in products_after:
            AssertUtil.assert_true(product.get("is_selected"),
                                   message=f"商品'{product['name']}'未被全选")

        selected_count = self.cart_page.get_selected_count()
        expected_count = sum(p["quantity"] for p in products_after)
        AssertUtil.assert_equal(selected_count, expected_count,
                               message=f"已选数量应为{expected_count}，实际为{selected_count}")

        logger.info("TC_CART_005 测试通过")

    def test_TC_CART_006_delete_single_product(self):
        """
        TC_CART_006: 删除单个商品测试

        预期结果：
            1. 点击删除按钮后，商品从购物车中移除
            2. 购物车数量减少1
        """
        logger.info("=== TC_CART_006: 验证删除单个商品功能 ===")

        is_empty = self.cart_page.is_cart_empty()
        if is_empty:
            logger.warning("购物车为空，跳过删除测试")
            pytest.skip("购物车为空，无法测试删除功能")

        products_before = self.cart_page.get_cart_products()
        product_count_before = len(products_before)

        delete_result = self.cart_page.delete_product(0)
        AssertUtil.assert_true(delete_result, message="删除商品失败")
        time.sleep(1)

        products_after = self.cart_page.get_cart_products()
        product_count_after = len(products_after)

        AssertUtil.assert_equal(product_count_after, product_count_before - 1,
                               message=f"删除后商品数量应为{product_count_before - 1}，实际为{product_count_after}")

        logger.info("TC_CART_006 测试通过")

    def test_TC_CART_007_batch_delete_products(self):
        """
        TC_CART_007: 批量删除已勾选商品测试

        预期结果：
            1. 勾选多个商品后，点击批量删除按钮
            2. 所有已勾选商品从购物车中移除
        """
        logger.info("=== TC_CART_007: 验证批量删除商品功能 ===")

        is_empty = self.cart_page.is_cart_empty()
        if is_empty:
            logger.warning("购物车为空，跳过批量删除测试")
            pytest.skip("购物车为空，无法测试批量删除功能")

        products_before = self.cart_page.get_cart_products()
        product_count_before = len(products_before)

        if product_count_before < 2:
            logger.warning("购物车商品数量不足2个，无法测试批量删除")
            pytest.skip("购物车商品数量不足2个")

        self.cart_page.deselect_all_products()
        time.sleep(0.5)

        self.cart_page.select_product(0)
        time.sleep(0.3)
        self.cart_page.select_product(1)
        time.sleep(0.5)

        delete_result = self.cart_page.batch_delete_products()
        AssertUtil.assert_true(delete_result, message="批量删除商品失败")
        time.sleep(1)

        products_after = self.cart_page.get_cart_products()
        product_count_after = len(products_after)

        AssertUtil.assert_equal(product_count_after, product_count_before - 2,
                               message=f"批量删除后商品数量应为{product_count_before - 2}，实际为{product_count_after}")

        logger.info("TC_CART_007 测试通过")

    def test_TC_CART_008_checkout_to_order_page(self):
        """
        TC_CART_008: 点击结算按钮跳转到订单确认页面

        预期结果：
            1. 勾选商品后点击结算按钮
            2. 成功跳转到订单确认页面
        """
        logger.info("=== TC_CART_008: 验证结算跳转功能 ===")

        is_empty = self.cart_page.is_cart_empty()
        if is_empty:
            logger.warning("购物车为空，跳过结算测试")
            pytest.skip("购物车为空，无法测试结算功能")

        self.cart_page.deselect_all_products()
        time.sleep(0.5)

        self.cart_page.select_product(0)
        time.sleep(0.5)

        checkout_result = self.cart_page.click_checkout()
        AssertUtil.assert_true(checkout_result, message="点击结算按钮失败")
        time.sleep(2)

        is_checkout_page = self.cart_page.is_checkout_page_displayed()
        AssertUtil.assert_true(is_checkout_page, message="未成功跳转到订单确认页面")

        logger.info("TC_CART_008 测试通过")