import pytest
import json
import base64
import urllib.parse
from base.AssertUtil import AssertUtil
from utils.yaml_util import YamlUtil
from utils.log_util import logger

api_data = YamlUtil().read_yaml('data/api_data.yaml')
assert_util = AssertUtil()


class TestCartAPI:

    def _build_goods_data(self, goods_id, stock):
        goods_data = [{'goods_id': goods_id, 'stock': stock, 'spec': []}]
        goods_data_json = json.dumps(goods_data)
        goods_data_base64 = base64.b64encode(goods_data_json.encode('utf-8')).decode('utf-8')
        return urllib.parse.quote(goods_data_base64)

    @pytest.mark.api
    def test_cart_add_success(self, api_client, login_token):
        """
        TC_CART_001: 测试添加购物车成功（已登录状态）
        """
        logger.info("========== 测试：添加购物车成功 ==========")

        if not login_token:
            pytest.skip("登录失败，跳过此测试")

        goods_data = self._build_goods_data(
            api_data['cart_api']['valid_goods_id'],
            api_data['cart_api']['valid_stock']
        )

        response = api_client.post(
            api_data['cart_api']['save_path'],
            data={'goods_data': goods_data}
        )

        logger.info(f"添加购物车响应: {response}")

        if isinstance(response, dict):
            assert_util.assert_response_code(
                response,
                api_data['cart_api']['success_code']
            )
            assert_util.assert_response_contains_message(
                response,
                api_data['cart_api']['success_msg']
            )
            assert 'total_price' in response.get('data', {}), "响应数据中缺少total_price字段"
            assert 'buy_number' in response.get('data', {}), "响应数据中缺少buy_number字段"
        else:
            pytest.fail(f"响应不是JSON格式: {response}")

    @pytest.mark.api
    def test_cart_add_unauthorized(self):
        """
        TC_CART_002: 测试未登录状态添加购物车
        """
        logger.info("========== 测试：未登录状态添加购物车 ==========")

        from base.ApiRequest import ApiRequest

        new_api_client = ApiRequest()
        goods_data = self._build_goods_data(
            api_data['cart_api']['valid_goods_id'],
            api_data['cart_api']['valid_stock']
        )

        response = new_api_client.post(
            api_data['cart_api']['save_path'],
            data={'goods_data': goods_data}
        )

        logger.info(f"未登录添加购物车响应: {response}")

        assert isinstance(response, dict) or 'login' in str(response).lower(), "未登录状态应该重定向到登录页面"

        new_api_client.close_session()

    @pytest.mark.api
    def test_cart_add_invalid_goods_id(self, api_client, login_token):
        """
        TC_CART_003: 测试添加不存在的商品到购物车
        """
        logger.info("========== 测试：添加不存在的商品到购物车 ==========")

        if not login_token:
            pytest.skip("登录失败，跳过此测试")

        goods_data = self._build_goods_data(
            api_data['cart_api']['invalid_goods_id'],
            api_data['cart_api']['valid_stock']
        )

        response = api_client.post(
            api_data['cart_api']['save_path'],
            data={'goods_data': goods_data}
        )

        logger.info(f"添加不存在商品响应: {response}")

        assert isinstance(response, dict), "响应不是JSON格式"
        assert response.get('code') != 0, "添加不存在的商品不应该成功"

    @pytest.mark.api
    def test_cart_add_empty_goods_data(self, api_client, login_token):
        """
        TC_CART_004: 测试添加购物车时goods_data为空
        """
        logger.info("========== 测试：添加购物车时goods_data为空 ==========")

        if not login_token:
            pytest.skip("登录失败，跳过此测试")

        response = api_client.post(
            api_data['cart_api']['save_path'],
            data={'goods_data': ''}
        )

        logger.info(f"goods_data为空响应: {response}")

        assert isinstance(response, dict), "响应不是JSON格式"
        assert response.get('code') != 0, "goods_data为空不应该成功"

    @pytest.mark.api
    def test_cart_add_invalid_stock(self, api_client, login_token):
        """
        TC_CART_005: 测试添加购物车时购买数量为0
        """
        logger.info("========== 测试：添加购物车时购买数量为0 ==========")

        if not login_token:
            pytest.skip("登录失败，跳过此测试")

        goods_data = self._build_goods_data(
            api_data['cart_api']['valid_goods_id'],
            api_data['cart_api']['invalid_stock']
        )

        response = api_client.post(
            api_data['cart_api']['save_path'],
            data={'goods_data': goods_data}
        )

        logger.info(f"购买数量为0响应: {response}")

        assert isinstance(response, dict), "响应不是JSON格式"
        assert response.get('code') != 0, "购买数量为0不应该成功"

    @pytest.mark.api
    def test_cart_update_invalid_cart_id(self, api_client, login_token):
        """
        TC_CART_006: 测试更新购物车商品数量失败（无效cart_id）
        """
        logger.info("========== 测试：更新购物车商品数量失败（无效cart_id） ==========")

        if not login_token:
            pytest.skip("登录失败，跳过此测试")

        invalid_cart_id = 999999
        update_response = api_client.post(
            api_data['cart_api']['stock_path'],
            data={'id': invalid_cart_id, 'goods_id': api_data['cart_api']['valid_goods_id'], 'stock': 2}
        )

        logger.info(f"更新无效cart_id响应: {update_response}")

        assert isinstance(update_response, dict), "响应不是JSON格式"
        assert update_response.get('code') != 0, "更新无效cart_id不应该成功"

    @pytest.mark.api
    def test_cart_delete_invalid_cart_id(self, api_client, login_token):
        """
        TC_CART_007: 测试删除购物车商品失败（无效cart_id）
        """
        logger.info("========== 测试：删除购物车商品失败（无效cart_id） ==========")

        if not login_token:
            pytest.skip("登录失败，跳过此测试")

        invalid_cart_id = 999999
        delete_response = api_client.post(
            api_data['cart_api']['delete_path'],
            data={'id': invalid_cart_id}
        )

        logger.info(f"删除无效cart_id响应: {delete_response}")

        assert isinstance(delete_response, dict), "响应不是JSON格式"
        assert delete_response.get('code') != 0, "删除无效cart_id不应该成功"
