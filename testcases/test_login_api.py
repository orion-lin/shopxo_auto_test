import pytest
from utils.yaml_util import YamlUtil
from base.AssertUtil import AssertUtil
from utils.log_util import logger
from utils.captcha_util import captcha_util


@pytest.mark.api
@pytest.mark.smoke
class TestLoginAPI:
    """
    登录模块API接口测试用例
    """

    def _get_captcha(self, api_client):
        """
        获取验证码

        Args:
            api_client: API请求客户端

        Returns:
            str: 识别到的验证码，识别失败返回空字符串
        """
        env_config = api_client.env_config
        base_url = env_config.get("base_url", "")
        return captcha_util.get_and_recognize_captcha(base_url)

    def test_normal_login_api(self, api_client):
        """
        TC_LOGIN_API_001: 使用正确的账号和密码登录系统

        预期结果：
            1. 登录接口返回code=200，msg="登录成功"，data携带有效token
        """
        logger.info("=== TC_LOGIN_API_001: 验证使用正确账号密码登录 ===")

        api_data = YamlUtil.read_test_data("api_data.yaml")
        login_info = api_data["login_api"]

        captcha = self._get_captcha(api_client)
        if not captcha:
            pytest.skip("验证码获取失败，跳过测试")

        response = api_client.post(
            endpoint=login_info["path"],
            data={
                "type": login_info["type"],
                "accounts": login_info["accounts"],
                "pwd": login_info["pwd"],
                "verify": captcha
            }
        )

        logger.info(f"登录响应: {response}")

        if response.get("code") == -10:
            logger.info("验证码错误，重新获取验证码重试")
            captcha = self._get_captcha(api_client)
            if captcha:
                response = api_client.post(
                    endpoint=login_info["path"],
                    data={
                        "type": login_info["type"],
                        "accounts": login_info["accounts"],
                        "pwd": login_info["pwd"],
                        "verify": captcha
                    }
                )
                logger.info(f"登录重试响应: {response}")

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

        logger.info("TC_LOGIN_API_001 测试通过")

    def test_empty_username_api(self, api_client):
        """
        TC_LOGIN_API_002: 账号输入为空时调用登录接口

        预期结果：
            1. 登录接口返回code=-1，msg="请输入登录账号"
        """
        logger.info("=== TC_LOGIN_API_002: 验证账号为空时登录 ===")

        api_data = YamlUtil.read_test_data("api_data.yaml")
        login_info = api_data["login_api"]
        empty_user_data = api_data["login_errors"]["empty_user"]

        response = api_client.post(
            endpoint=login_info["path"],
            data={
                "type": empty_user_data["type"],
                "accounts": empty_user_data["accounts"],
                "pwd": empty_user_data["pwd"],
                "verify": ""
            }
        )

        logger.info(f"账号为空登录响应: {response}")

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

        logger.info("TC_LOGIN_API_002 测试通过")

    def test_empty_password_api(self, api_client):
        """
        TC_LOGIN_API_003: 密码输入为空时调用登录接口

        预期结果：
            1. 登录接口返回code=-1，msg="密码格式6~18个字符之间"
        """
        logger.info("=== TC_LOGIN_API_003: 验证密码为空时登录 ===")

        api_data = YamlUtil.read_test_data("api_data.yaml")
        login_info = api_data["login_api"]
        empty_pwd_data = api_data["login_errors"]["empty_pwd"]

        response = api_client.post(
            endpoint=login_info["path"],
            data={
                "type": empty_pwd_data["type"],
                "accounts": empty_pwd_data["accounts"],
                "pwd": empty_pwd_data["pwd"],
                "verify": ""
            }
        )

        logger.info(f"密码为空登录响应: {response}")

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

        logger.info("TC_LOGIN_API_003 测试通过")

    def test_wrong_password_api(self, api_client):
        """
        TC_LOGIN_API_004: 账号正确但密码错误时调用登录接口

        预期结果：
            1. 登录接口返回code=-1，msg="账号或密码不正确"
        """
        logger.info("=== TC_LOGIN_API_004: 验证密码错误时登录 ===")

        api_data = YamlUtil.read_test_data("api_data.yaml")
        login_info = api_data["login_api"]
        wrong_pwd_data = api_data["login_errors"]["wrong_pwd"]

        captcha = self._get_captcha(api_client)
        if not captcha:
            pytest.skip("验证码获取失败，跳过测试")

        response = api_client.post(
            endpoint=login_info["path"],
            data={
                "type": wrong_pwd_data["type"],
                "accounts": wrong_pwd_data["accounts"],
                "pwd": wrong_pwd_data["pwd"],
                "verify": captcha
            }
        )

        logger.info(f"密码错误登录响应: {response}")

        if response.get("code") == -10:
            logger.info("验证码错误，重新获取验证码重试")
            captcha = self._get_captcha(api_client)
            if captcha:
                response = api_client.post(
                    endpoint=login_info["path"],
                    data={
                        "type": wrong_pwd_data["type"],
                        "accounts": wrong_pwd_data["accounts"],
                        "pwd": wrong_pwd_data["pwd"],
                        "verify": captcha
                    }
                )
                logger.info(f"密码错误登录重试响应: {response}")

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

        logger.info("TC_LOGIN_API_004 测试通过")

    def test_empty_captcha_api(self, api_client):
        """
        TC_LOGIN_API_005: 账号密码正确但验证码为空时调用登录接口

        预期结果：
            1. 登录接口返回code=-10，msg="图片验证码不能为空"
        """
        logger.info("=== TC_LOGIN_API_005: 验证验证码为空时登录 ===")

        api_data = YamlUtil.read_test_data("api_data.yaml")
        login_info = api_data["login_api"]
        empty_captcha_data = api_data["login_errors"]["empty_captcha"]

        response = api_client.post(
            endpoint=login_info["path"],
            data={
                "type": empty_captcha_data["type"],
                "accounts": empty_captcha_data["accounts"],
                "pwd": empty_captcha_data["pwd"],
                "verify": empty_captcha_data["verify"]
            }
        )

        logger.info(f"验证码为空登录响应: {response}")

        AssertUtil.assert_response_code(
            response,
            expected_code=empty_captcha_data["expected_code"],
            message=f"登录接口返回code错误：{response.get('code')}"
        )

        AssertUtil.assert_equal(
            response.get("msg"),
            empty_captcha_data["expected_msg"],
            message=f"登录接口返回msg错误：{response.get('msg')}"
        )

        logger.info("TC_LOGIN_API_005 测试通过")

    def test_wrong_captcha_api(self, api_client):
        """
        TC_LOGIN_API_006: 账号密码正确但验证码错误时调用登录接口

        预期结果：
            1. 登录接口返回code=-10，msg="验证码错误"
        """
        logger.info("=== TC_LOGIN_API_006: 验证验证码错误时登录 ===")

        api_data = YamlUtil.read_test_data("api_data.yaml")
        login_info = api_data["login_api"]
        wrong_captcha_data = api_data["login_errors"]["wrong_captcha"]

        response = api_client.post(
            endpoint=login_info["path"],
            data={
                "type": wrong_captcha_data["type"],
                "accounts": wrong_captcha_data["accounts"],
                "pwd": wrong_captcha_data["pwd"],
                "verify": wrong_captcha_data["verify"]
            }
        )

        logger.info(f"验证码错误登录响应: {response}")

        AssertUtil.assert_response_code(
            response,
            expected_code=wrong_captcha_data["expected_code"],
            message=f"登录接口返回code错误：{response.get('code')}"
        )

        AssertUtil.assert_equal(
            response.get("msg"),
            wrong_captcha_data["expected_msg"],
            message=f"登录接口返回msg错误：{response.get('msg')}"
        )

        logger.info("TC_LOGIN_API_006 测试通过")

    def test_unauthorized_access_api(self, api_client):
        """
        TC_LOGIN_API_007: 未登录状态调用需要授权的接口（购物车列表）

        预期结果：
            1. 接口返回code=400，msg="未授权，请先登录"，或重定向到登录页面
        """
        logger.info("=== TC_LOGIN_API_007: 验证未登录状态访问需要授权的接口 ===")

        api_data = YamlUtil.read_test_data("api_data.yaml")
        cart_list_path = api_data["cart_list"]["path"]
        unauthorized_data = api_data["unauthorized"]

        response = api_client.get(endpoint=cart_list_path)

        logger.info(f"未授权访问购物车响应: {response}")

        if isinstance(response, dict):
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
        else:
            AssertUtil.assert_true(
                "login" in response.lower() if isinstance(response, str) else False,
                message="未授权访问应重定向到登录页面"
            )

        logger.info("TC_LOGIN_API_007 测试通过")