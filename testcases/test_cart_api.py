import pytest
from utils.yaml_util import YamlUtil
from base.AssertUtil import AssertUtil
from utils.log_util import logger


@pytest.mark.api
@pytest.mark.regression
class TestCartAPI:
    """
    购物车管理模块API接口测试用例
    """

    def test_cart_list_api_unauthorized(self, api_client):
        """
        TC_CART_API_001: 未登录状态调用购物车列表接口

        预期结果：
            1. 接口返回code=400，msg="未授权，请先登录"
        """
        logger.info("=== TC_CART_API_001: 验证未登录状态调用购物车列表接口 ===")

        api_data = YamlUtil.read_test_data("api_data.yaml")
        cart_list_path = api_data["cart_list"]["path"]
        unauthorized_data = api_data["unauthorized"]

        response = api_client.get(endpoint=cart_list_path)

        AssertUtil.assert_response_code(
            response,
            expected_code=unauthorized_data["expected_code"],
            message=f"未授权访问返回code错误：{response.get('code')}"
        )

        AssertUtil.assert_equal(
            response.get("msg"),
            unauthorized_data["expected_msg"],
            message=f"未授权访问返回msg错误：{response.get('msg')}"
        )

        logger.info("TC_CART_API_001 测试通过")

    def test_cart_list_api_authorized(self, api_client, login_token):
        """
        TC_CART_API_002: 已登录状态调用购物车列表接口

        预期结果：
            1. 接口返回code=200
            2. 返回购物车商品列表数据
        """
        logger.info("=== TC_CART_API_002: 验证已登录状态调用购物车列表接口 ===")

        if not login_token:
            pytest.skip("未获取到登录Token，跳过测试")

        api_data = YamlUtil.read_test_data("api_data.yaml")
        cart_list_path = api_data["cart_list"]["path"]

        response = api_client.get(endpoint=cart_list_path)

        AssertUtil.assert_response_code(
            response,
            expected_code=200,
            message=f"购物车列表接口返回code错误：{response.get('code')}"
        )

        data = response.get("data", {})
        logger.info(f"购物车列表数据: {data}")

        logger.info("TC_CART_API_002 测试通过")

    def test_cart_add_api_unauthorized(self, api_client):
        """
        TC_CART_API_003: 未登录状态调用添加购物车接口

        预期结果：
            1. 接口返回code=400，msg="未授权，请先登录"
        """
        logger.info("=== TC_CART_API_003: 验证未登录状态调用添加购物车接口 ===")

        api_data = YamlUtil.read_test_data("api_data.yaml")
        cart_add_path = api_data["cart_add"]["path"]
        unauthorized_data = api_data["unauthorized"]

        response = api_client.post(
            endpoint=cart_add_path,
            json={"goods_id": 1, "buy_number": 1}
        )

        AssertUtil.assert_response_code(
            response,
            expected_code=unauthorized_data["expected_code"],
            message=f"未授权访问返回code错误：{response.get('code')}"
        )

        AssertUtil.assert_equal(
            response.get("msg"),
            unauthorized_data["expected_msg"],
            message=f"未授权访问返回msg错误：{response.get('msg')}"
        )

        logger.info("TC_CART_API_003 测试通过")

    def test_cart_update_api_unauthorized(self, api_client):
        """
        TC_CART_API_004: 未登录状态调用更新购物车接口

        预期结果：
            1. 接口返回code=400，msg="未授权，请先登录"
        """
        logger.info("=== TC_CART_API_004: 验证未登录状态调用更新购物车接口 ===")

        api_data = YamlUtil.read_test_data("api_data.yaml")
        cart_update_path = api_data["cart_update"]["path"]
        unauthorized_data = api_data["unauthorized"]

        response = api_client.post(
            endpoint=cart_update_path,
            json={"id": 1, "number": 2}
        )

        AssertUtil.assert_response_code(
            response,
            expected_code=unauthorized_data["expected_code"],
            message=f"未授权访问返回code错误：{response.get('code')}"
        )

        AssertUtil.assert_equal(
            response.get("msg"),
            unauthorized_data["expected_msg"],
            message=f"未授权访问返回msg错误：{response.get('msg')}"
        )

        logger.info("TC_CART_API_004 测试通过")

    def test_cart_delete_api_unauthorized(self, api_client):
        """
        TC_CART_API_005: 未登录状态调用删除购物车接口

        预期结果：
            1. 接口返回code=400，msg="未授权，请先登录"
        """
        logger.info("=== TC_CART_API_005: 验证未登录状态调用删除购物车接口 ===")

        api_data = YamlUtil.read_test_data("api_data.yaml")
        cart_delete_path = api_data["cart_delete"]["path"]
        unauthorized_data = api_data["unauthorized"]

        response = api_client.post(
            endpoint=cart_delete_path,
            json={"id": 1}
        )

        AssertUtil.assert_response_code(
            response,
            expected_code=unauthorized_data["expected_code"],
            message=f"未授权访问返回code错误：{response.get('code')}"
        )

        AssertUtil.assert_equal(
            response.get("msg"),
            unauthorized_data["expected_msg"],
            message=f"未授权访问返回msg错误：{response.get('msg')}"
        )

        logger.info("TC_CART_API_005 测试通过")

    def test_cart_clear_api_unauthorized(self, api_client):
        """
        TC_CART_API_006: 未登录状态调用清空购物车接口

        预期结果：
            1. 接口返回code=400，msg="未授权，请先登录"
        """
        logger.info("=== TC_CART_API_006: 验证未登录状态调用清空购物车接口 ===")

        api_data = YamlUtil.read_test_data("api_data.yaml")
        cart_clear_path = api_data["cart_clear"]["path"]
        unauthorized_data = api_data["unauthorized"]

        response = api_client.post(endpoint=cart_clear_path)

        AssertUtil.assert_response_code(
            response,
            expected_code=unauthorized_data["expected_code"],
            message=f"未授权访问返回code错误：{response.get('code')}"
        )

        AssertUtil.assert_equal(
            response.get("msg"),
            unauthorized_data["expected_msg"],
            message=f"未授权访问返回msg错误：{response.get('msg')}"
        )

        logger.info("TC_CART_API_006 测试通过")

    def test_cart_add_api_invalid_params(self, api_client, login_token):
        """
        TC_CART_API_007: 已登录状态调用添加购物车接口（参数无效）

        预期结果：
            1. 接口返回code=400
            2. 返回错误提示信息
        """
        logger.info("=== TC_CART_API_007: 验证已登录状态调用添加购物车接口（参数无效） ===")

        if not login_token:
            pytest.skip("未获取到登录Token，跳过测试")

        api_data = YamlUtil.read_test_data("api_data.yaml")
        cart_add_path = api_data["cart_add"]["path"]

        response = api_client.post(
            endpoint=cart_add_path,
            json={"goods_id": 999999, "buy_number": 1}
        )

        logger.info(f"添加购物车响应: {response}")

        AssertUtil.assert_true(
            response.get("code") != 200,
            message="无效商品ID应返回非200状态码"
        )

        logger.info("TC_CART_API_007 测试通过")

    def test_cart_add_api_valid_params(self, api_client, login_token):
        """
        TC_CART_API_008: 已登录状态调用添加购物车接口（参数有效）

        预期结果：
            1. 接口返回code=200
            2. 返回成功提示信息
        """
        logger.info("=== TC_CART_API_008: 验证已登录状态调用添加购物车接口（参数有效） ===")

        if not login_token:
            pytest.skip("未获取到登录Token，跳过测试")

        api_data = YamlUtil.read_test_data("api_data.yaml")
        cart_add_path = api_data["cart_add"]["path"]

        response = api_client.post(
            endpoint=cart_add_path,
            json={"goods_id": 1, "buy_number": 1}
        )

        logger.info(f"添加购物车响应: {response}")

        AssertUtil.assert_response_code(
            response,
            expected_code=200,
            message=f"添加购物车接口返回code错误：{response.get('code')}"
        )

        logger.info("TC_CART_API_008 测试通过")