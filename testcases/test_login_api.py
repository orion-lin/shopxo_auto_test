import pytest
from utils.yaml_util import YamlUtil
from base.AssertUtil import AssertUtil


@pytest.mark.api
@pytest.mark.smoke
class TestLoginAPI:
    """
    登录模块API接口测试用例
    """

    def test_normal_login_api(self, api_client):
        """
        场景1：使用正确的账号和密码登录系统

        预期结果：
            1. 登录接口返回code=200，msg="登录成功"，data携带有效token
        """
        api_data = YamlUtil.read_test_data("api_data.yaml")
        login_info = api_data["login_api"]

        response = api_client.post(
            endpoint=login_info["path"],
            json={
                "username": login_info["username"],
                "password": login_info["password"]
            }
        )

        AssertUtil.assert_response_code(
            response,
            expected_code=200,
            message=f"登录接口返回code错误：{response.get('code')}"
        )

        AssertUtil.assert_equal(
            response.get("msg"),
            login_info["success_msg"],
            message=f"登录接口返回msg错误：{response.get('msg')}"
        )

        token = response.get("data", {}).get("token")
        AssertUtil.assert_is_not_none(
            token,
            message="登录接口未返回token"
        )

    def test_empty_username_api(self, api_client):
        """
        场景2：账号输入为空时调用登录接口

        预期结果：
            1. 登录接口返回code=400，msg="请输入登录账号"
        """
        api_data = YamlUtil.read_test_data("api_data.yaml")
        login_info = api_data["login_api"]
        empty_user_data = api_data["login_errors"]["empty_user"]

        response = api_client.post(
            endpoint=login_info["path"],
            json={
                "username": empty_user_data["username"],
                "password": empty_user_data["password"]
            }
        )

        AssertUtil.assert_response_code(
            response,
            expected_code=empty_user_data["expected_code"],
            message=f"登录接口返回code错误：{response.get('code')}"
        )

        AssertUtil.assert_equal(
            response.get("msg"),
            empty_user_data["expected_msg"],
            message=f"登录接口返回msg错误：{response.get('msg')}"
        )

    def test_empty_password_api(self, api_client):
        """
        场景3：密码输入为空时调用登录接口

        预期结果：
            1. 登录接口返回code=400，msg="密码格式6~18个字符之间"
        """
        api_data = YamlUtil.read_test_data("api_data.yaml")
        login_info = api_data["login_api"]
        empty_pwd_data = api_data["login_errors"]["empty_pwd"]

        response = api_client.post(
            endpoint=login_info["path"],
            json={
                "username": empty_pwd_data["username"],
                "password": empty_pwd_data["password"]
            }
        )

        AssertUtil.assert_response_code(
            response,
            expected_code=empty_pwd_data["expected_code"],
            message=f"登录接口返回code错误：{response.get('code')}"
        )

        AssertUtil.assert_equal(
            response.get("msg"),
            empty_pwd_data["expected_msg"],
            message=f"登录接口返回msg错误：{response.get('msg')}"
        )

    def test_wrong_password_api(self, api_client):
        """
        场景4：账号正确但密码错误时调用登录接口

        预期结果：
            1. 登录接口返回code=400，msg="账号或密码不正确"
        """
        api_data = YamlUtil.read_test_data("api_data.yaml")
        login_info = api_data["login_api"]
        wrong_pwd_data = api_data["login_errors"]["wrong_pwd"]

        response = api_client.post(
            endpoint=login_info["path"],
            json={
                "username": wrong_pwd_data["username"],
                "password": wrong_pwd_data["password"]
            }
        )

        AssertUtil.assert_response_code(
            response,
            expected_code=wrong_pwd_data["expected_code"],
            message=f"登录接口返回code错误：{response.get('code')}"
        )

        AssertUtil.assert_equal(
            response.get("msg"),
            wrong_pwd_data["expected_msg"],
            message=f"登录接口返回msg错误：{response.get('msg')}"
        )

    def test_unauthorized_access_api(self, api_client):
        """
        场景5：未登录状态调用需要授权的接口（购物车列表）

        预期结果：
            1. 接口返回code=400，msg="未授权，请先登录"
        """
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