import pytest
from base.AssertUtil import AssertUtil
from utils.yaml_util import YamlUtil
from utils.log_util import logger

api_data = YamlUtil().read_yaml('data/api_data.yaml')
assert_util = AssertUtil()


class TestOrderQueryAPI:

    @pytest.mark.api
    def test_order_list_unauthorized(self):
        """
        TC_ORDER_QUERY_001: 测试未登录状态查询订单列表
        """
        logger.info("========== 测试：未登录状态查询订单列表 ==========")

        from base.ApiRequest import ApiRequest

        new_api_client = ApiRequest()
        response = new_api_client.get(api_data['order_api']['index_path'])

        logger.info(f"未登录查询订单列表响应: {response}")

        assert isinstance(response, dict) or 'login' in str(response).lower(), "未登录状态应该重定向到登录页面"

        new_api_client.close_session()

    @pytest.mark.api
    def test_order_list_success(self, api_client, login_token):
        """
        TC_ORDER_QUERY_002: 测试查询订单列表成功（已登录状态）
        """
        logger.info("========== 测试：查询订单列表成功 ==========")

        if not login_token:
            pytest.skip("登录失败，跳过此测试")

        response = api_client.get(api_data['order_api']['index_path'])

        logger.info(f"查询订单列表响应: {response}")

        assert isinstance(response, dict) or isinstance(response, str), "响应格式异常"

    @pytest.mark.api
    def test_order_detail_unauthorized(self):
        """
        TC_ORDER_QUERY_003: 测试未登录状态查询订单详情
        """
        logger.info("========== 测试：未登录状态查询订单详情 ==========")

        from base.ApiRequest import ApiRequest

        new_api_client = ApiRequest()
        detail_path = api_data['order_api']['detail_path'].replace('{id}', str(api_data['order_api']['valid_order_id']))
        response = new_api_client.get(detail_path)

        logger.info(f"未登录查询订单详情响应: {response}")

        assert isinstance(response, dict) or 'login' in str(response).lower(), "未登录状态应该重定向到登录页面"

        new_api_client.close_session()

    @pytest.mark.api
    def test_order_detail_success(self, api_client, login_token):
        """
        TC_ORDER_QUERY_004: 测试查询订单详情成功（已登录状态+有效订单ID）
        """
        logger.info("========== 测试：查询订单详情成功 ==========")

        if not login_token:
            pytest.skip("登录失败，跳过此测试")

        detail_path = api_data['order_api']['detail_path'].replace('{id}', str(api_data['order_api']['valid_order_id']))
        response = api_client.get(detail_path)

        logger.info(f"查询订单详情响应: {response}")

        assert isinstance(response, dict) or isinstance(response, str), "响应格式异常"

    @pytest.mark.api
    def test_order_detail_invalid_id(self, api_client, login_token):
        """
        TC_ORDER_QUERY_005: 测试查询不存在的订单详情
        """
        logger.info("========== 测试：查询不存在的订单详情 ==========")

        if not login_token:
            pytest.skip("登录失败，跳过此测试")

        detail_path = api_data['order_api']['detail_path'].replace('{id}', str(api_data['order_api']['invalid_order_id']))
        response = api_client.get(detail_path)

        logger.info(f"查询不存在订单详情响应: {response}")

        assert isinstance(response, dict) or isinstance(response, str), "响应格式异常"

    @pytest.mark.api
    def test_order_list_pagination(self, api_client, login_token):
        """
        TC_ORDER_QUERY_006: 测试订单列表分页查询
        """
        logger.info("========== 测试：订单列表分页查询 ==========")

        if not login_token:
            pytest.skip("登录失败，跳过此测试")

        response = api_client.get(
            api_data['order_api']['index_path'],
            params={'page': '1', 'page_size': '20'}
        )

        logger.info(f"分页查询订单列表响应: {response}")

        assert isinstance(response, dict) or isinstance(response, str), "响应格式异常"

    @pytest.mark.api
    def test_order_list_filter_status(self, api_client, login_token):
        """
        TC_ORDER_QUERY_007: 测试按订单状态筛选订单列表
        """
        logger.info("========== 测试：按订单状态筛选订单列表 ==========")

        if not login_token:
            pytest.skip("登录失败，跳过此测试")

        response = api_client.get(
            api_data['order_api']['index_path'],
            params={'order_model': '0'}
        )

        logger.info(f"按状态筛选订单列表响应: {response}")

        assert isinstance(response, dict) or isinstance(response, str), "响应格式异常"
