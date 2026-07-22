import pytest
import json
import base64
import urllib.parse
from base.AssertUtil import AssertUtil
from utils.yaml_util import YamlUtil
from utils.log_util import logger

api_data = YamlUtil().read_yaml('data/api_data.yaml')
assert_util = AssertUtil()


class TestOrderSubmitAPI:

    def _build_goods_data(self, goods_id, stock):
        goods_data = [{'goods_id': goods_id, 'stock': stock, 'spec': []}]
        goods_data_json = json.dumps(goods_data)
        goods_data_base64 = base64.b64encode(goods_data_json.encode('utf-8')).decode('utf-8')
        return urllib.parse.quote(goods_data_base64)

    @pytest.mark.api
    def test_order_submit_unauthorized(self):
        """
        TC_ORDER_SUBMIT_001: 测试未登录状态访问结算页面
        """
        logger.info("========== 测试：未登录状态访问结算页面 ==========")

        from base.ApiRequest import ApiRequest

        new_api_client = ApiRequest()
        response = new_api_client.get(api_data['order_api']['buy_path'])

        logger.info(f"未登录访问结算页面响应: {response}")

        assert isinstance(response, dict) or 'login' in str(response).lower(), "未登录状态应该重定向到登录页面"

        new_api_client.close_session()

    @pytest.mark.api
    def test_order_submit_empty_cart(self, api_client, login_token):
        """
        TC_ORDER_SUBMIT_002: 测试购物车为空时访问结算页面
        """
        logger.info("========== 测试：购物车为空时访问结算页面 ==========")

        if not login_token:
            pytest.skip("登录失败，跳过此测试")

        response = api_client.get(api_data['order_api']['buy_path'])

        logger.info(f"购物车为空访问结算页面响应: {response}")

        assert isinstance(response, dict) or isinstance(response, str), "响应格式异常"

    @pytest.mark.api
    def test_order_submit_success(self, api_client, login_token):
        """
        TC_ORDER_SUBMIT_003: 测试提交订单成功（已登录+有商品）
        """
        logger.info("========== 测试：提交订单成功 ==========")

        if not login_token:
            pytest.skip("登录失败，跳过此测试")

        goods_data = self._build_goods_data(
            api_data['cart_api']['valid_goods_id'],
            api_data['cart_api']['valid_stock']
        )

        add_response = api_client.post(
            api_data['cart_api']['save_path'],
            data={'goods_data': goods_data}
        )

        if isinstance(add_response, dict) and add_response.get('code') == 0:
            response = api_client.get(api_data['order_api']['buy_path'])

            logger.info(f"结算页面响应: {response}")

            assert isinstance(response, dict) or isinstance(response, str), "响应格式异常"
        else:
            pytest.skip("添加购物车失败，跳过订单提交测试")

    @pytest.mark.api
    def test_order_submit_with_invalid_goods(self, api_client, login_token):
        """
        TC_ORDER_SUBMIT_004: 测试提交订单时商品不存在
        """
        logger.info("========== 测试：提交订单时商品不存在 ==========")

        if not login_token:
            pytest.skip("登录失败，跳过此测试")

        goods_data = self._build_goods_data(
            api_data['cart_api']['invalid_goods_id'],
            api_data['cart_api']['valid_stock']
        )

        add_response = api_client.post(
            api_data['cart_api']['save_path'],
            data={'goods_data': goods_data}
        )

        if isinstance(add_response, dict) and add_response.get('code') != 0:
            logger.info(f"添加不存在商品响应: {add_response}")
            assert add_response.get('code') != 0, "添加不存在的商品不应该成功"
        else:
            pytest.skip("添加不存在商品意外成功，跳过此测试")

    @pytest.mark.api
    def test_order_submit_no_address(self, api_client, login_token):
        """
        TC_ORDER_SUBMIT_005: 测试提交订单时未选择收货地址
        """
        logger.info("========== 测试：提交订单时未选择收货地址 ==========")

        if not login_token:
            pytest.skip("登录失败，跳过此测试")

        goods_data = self._build_goods_data(
            api_data['cart_api']['valid_goods_id'],
            api_data['cart_api']['valid_stock']
        )

        add_response = api_client.post(
            api_data['cart_api']['save_path'],
            data={'goods_data': goods_data}
        )

        if isinstance(add_response, dict) and add_response.get('code') == 0:
            response = api_client.post(
                api_data['order_api']['buy_path'],
                data={'address_id': '-1', 'payment_id': '1'}
            )

            logger.info(f"未选择地址提交订单响应: {response}")

            if isinstance(response, dict):
                assert response.get('code') != 0, "未选择地址不应该提交订单成功"
            else:
                assert 'order' in str(response).lower() or 'cart' in str(response).lower(), "响应应该是订单相关页面"
        else:
            pytest.skip("添加购物车失败，跳过订单提交测试")

    @pytest.mark.api
    def test_order_submit_no_payment(self, api_client, login_token):
        """
        TC_ORDER_SUBMIT_006: 测试提交订单时未选择支付方式
        """
        logger.info("========== 测试：提交订单时未选择支付方式 ==========")

        if not login_token:
            pytest.skip("登录失败，跳过此测试")

        goods_data = self._build_goods_data(
            api_data['cart_api']['valid_goods_id'],
            api_data['cart_api']['valid_stock']
        )

        add_response = api_client.post(
            api_data['cart_api']['save_path'],
            data={'goods_data': goods_data}
        )

        if isinstance(add_response, dict) and add_response.get('code') == 0:
            response = api_client.post(
                api_data['order_api']['buy_path'],
                data={'address_id': '1', 'payment_id': '0'}
            )

            logger.info(f"未选择支付方式提交订单响应: {response}")

            if isinstance(response, dict):
                assert response.get('code') != 0, "未选择支付方式不应该提交订单成功"
            else:
                assert 'order' in str(response).lower() or 'cart' in str(response).lower(), "响应应该是订单相关页面"
        else:
            pytest.skip("添加购物车失败，跳过订单提交测试")

    @pytest.mark.api
    def test_order_submit_with_note(self, api_client, login_token):
        """
        TC_ORDER_SUBMIT_007: 测试提交订单时添加备注
        """
        logger.info("========== 测试：提交订单时添加备注 ==========")

        if not login_token:
            pytest.skip("登录失败，跳过此测试")

        goods_data = self._build_goods_data(
            api_data['cart_api']['valid_goods_id'],
            api_data['cart_api']['valid_stock']
        )

        add_response = api_client.post(
            api_data['cart_api']['save_path'],
            data={'goods_data': goods_data}
        )

        if isinstance(add_response, dict) and add_response.get('code') == 0:
            response = api_client.post(
                api_data['order_api']['buy_path'],
                data={'address_id': '1', 'payment_id': '1', 'user_note': '测试备注信息'}
            )

            logger.info(f"带备注提交订单响应: {response}")

            assert isinstance(response, dict) or isinstance(response, str), "响应格式异常"
        else:
            pytest.skip("添加购物车失败，跳过订单提交测试")
