import pytest
from page.login_page import LoginPage
from utils.yaml_util import YamlUtil
from base.AssertUtil import AssertUtil
from utils.log_util import logger


@pytest.mark.ui
@pytest.mark.smoke
class TestLoginUI:
    """
    登录模块UI自动化测试用例
    符合被测网站真实交互逻辑：
    - 三个输入框在登录页都可见
    - 存在空白输入框时点击登录，文本光标会在对应输入框跳动
    - 不输入再次点击登录会提示错误
    - 三个输入框都填写后点击登录才会完整提交表单
    """

    def test_empty_username_all_errors(self, web_driver):
        """
        场景1：账号为空，校验三条空值错误提示完整流程

        操作步骤：
            1. 打开商城登录页面；
            2. 账号输入框无任何内容，直接点击登录按钮；
            3. 账号输入框出现闪烁输入光标，页面停留在账号填写步骤；
            4. 不填写任何账号内容，再次点击登录按钮；
            5. 页面弹出三条提示文案：账号不能为空、密码不能为空、验证码不能为空。
        """
        login_data = YamlUtil.read_test_data("ui_data.yaml")
        empty_all_data = login_data["login"]["empty_all"]

        login_page = LoginPage(web_driver)
        login_page.open_login_page()
        login_page.reset_login_page()

        logger.info("=== 第一次点击登录（账号为空） ===")
        login_page.click_login()

        logger.info("=== 第二次点击登录（所有字段为空） ===")
        login_page.click_login()

        error_messages = login_page.get_all_error_messages()
        AssertUtil.assert_list_length(
            error_messages,
            3,
            message=f"错误提示数量不匹配：期望3条，实际{len(error_messages)}条"
        )

        for expected_error in empty_all_data["expected_errors_step2"]:
            AssertUtil.assert_in(
                expected_error,
                error_messages,
                message=f"错误提示不匹配：期望包含'{expected_error}', 实际={error_messages}"
            )

    def test_valid_username_empty_password(self, web_driver):
        """
        场景2：仅填写有效账号，校验密码为空完整流程

        操作步骤：
            1. 打开商城登录页面；
            2. 在账号输入框录入合规账号内容；
            3. 点击登录按钮，密码输入框出现闪烁输入光标；
            4. 密码输入框不填写任何内容，直接再次点击登录按钮；
            5. 页面弹出密码格式错误提示。
        """
        login_data = YamlUtil.read_test_data("ui_data.yaml")
        empty_pwd_data = login_data["login"]["empty_pwd"]

        login_page = LoginPage(web_driver)
        login_page.open_login_page()
        login_page.reset_login_page()

        logger.info("=== 输入有效账号 ===")
        login_page.input_username(empty_pwd_data["username"])

        logger.info("=== 第一次点击登录（密码为空） ===")
        login_page.click_login()

        logger.info("=== 第二次点击登录（密码仍为空） ===")
        login_page.click_login()

        error_messages = login_page.get_all_error_messages()
        AssertUtil.assert_in(
            empty_pwd_data["expected_error"],
            error_messages,
            message=f"错误提示不匹配：期望包含'{empty_pwd_data['expected_error']}', 实际={error_messages}"
        )

    def test_valid_username_short_password(self, web_driver):
        """场景3：输入有效账号，校验密码格式错误（密码长度小于6位）

        操作步骤：
            1. 打开商城登录页面；
            2. 输入有效账号和小于6位的密码；
            3. 点击登录按钮；
            4. 验证页面状态：弹出密码格式错误提示。
        """
        login_data = YamlUtil.read_test_data("ui_data.yaml")
        short_pwd_data = login_data["login"]["password_too_short"]

        login_page = LoginPage(web_driver)
        login_page.open_login_page()
        login_page.reset_login_page()

        logger.info("=== 输入有效账号和过短密码 ===")
        login_page.input_username(short_pwd_data["username"])
        login_page.input_password(short_pwd_data["password"])

        logger.info("=== 点击登录按钮 ===")
        login_page.click_login()

        error_messages = login_page.get_all_error_messages()
        AssertUtil.assert_in(
            short_pwd_data["expected_error"],
            error_messages,
            message=f"错误提示不匹配：期望包含'{short_pwd_data['expected_error']}', 实际={error_messages}"
        )

    def test_valid_username_long_password(self, web_driver):
        """
        场景4：输入有效账号，校验密码格式错误（密码长度大于18位）

        操作步骤：
            1. 打开商城登录页面；
            2. 输入有效账号和大于18位的密码；
            3. 点击登录按钮；
            4. 验证页面状态：弹出密码格式错误提示。
        """
        login_data = YamlUtil.read_test_data("ui_data.yaml")
        long_pwd_data = login_data["login"]["password_too_long"]

        login_page = LoginPage(web_driver)
        login_page.open_login_page()
        login_page.reset_login_page()

        logger.info("=== 输入有效账号和过长密码 ===")
        login_page.input_username(long_pwd_data["username"])
        login_page.input_password(long_pwd_data["password"])

        logger.info("=== 点击登录按钮 ===")
        login_page.click_login()

        error_messages = login_page.get_all_error_messages()
        AssertUtil.assert_in(
            long_pwd_data["expected_error"],
            error_messages,
            message=f"错误提示不匹配：期望包含'{long_pwd_data['expected_error']}', 实际={error_messages}"
        )

    def test_normal_login_success(self, web_driver):
        """
        场景5：使用正确的账号和密码登录系统，验证登录成功

        操作步骤：
            1. 打开商城登录页面；
            2. 输入有效账号；
            3. 输入有效密码；
            4. 识别并输入验证码；
            5. 点击登录按钮；

        预期结果：
            1. 页面跳转至商城首页；
            2. 页面显示登录成功提示；
            3. 页面右上角显示用户头像；
        """
        login_data = YamlUtil.read_test_data("ui_data.yaml")
        normal_data = login_data["login"]["normal"]

        login_page = LoginPage(web_driver)
        login_page.open_login_page()
        login_page.reset_login_page()

        logger.info("=== 输入有效账号 ===")
        login_page.input_username(normal_data["username"])

        logger.info("=== 输入有效密码 ===")
        login_page.input_password(normal_data["password"])

        logger.info("=== 识别并输入验证码 ===")
        captcha = login_page.recognize_captcha()
        if not captcha:
            pytest.skip("验证码识别失败，跳过此用例")
        login_page.input_captcha(captcha)

        logger.info("=== 点击登录按钮 ===")
        login_page.click_login()

        error_msg = login_page.get_error_message(timeout=3)
        if error_msg and "验证码" in error_msg:
            logger.info(f"验证码错误({error_msg})，重新识别")
            captcha = login_page.recognize_captcha()
            if captcha:
                login_page.input_captcha(captcha)
                login_page.click_login()

        AssertUtil.assert_true(
            login_page.is_login_success(),
            message="登录失败：页面未跳转或未显示登录成功提示"
        )

    def test_wrong_password_login(self, web_driver):
        """
        场景6：账号正确但密码错误时点击登录，验证系统提示

        操作步骤：
            1. 打开商城登录页面；
            2. 输入有效账号；
            3. 输入错误密码；
            4. 识别并输入验证码；
            5. 点击登录按钮；

        预期结果：
            1. 页面弹出错误提示：密码错误；
        """
        login_data = YamlUtil.read_test_data("ui_data.yaml")
        wrong_pwd_data = login_data["login"]["wrong_pwd"]

        login_page = LoginPage(web_driver)
        login_page.open_login_page()
        login_page.reset_login_page()

        logger.info("=== 输入有效账号 ===")
        login_page.input_username(wrong_pwd_data["username"])

        logger.info("=== 输入错误密码 ===")
        login_page.input_password(wrong_pwd_data["password"])

        logger.info("=== 识别并输入验证码 ===")
        captcha = login_page.recognize_captcha()
        if not captcha:
            pytest.skip("验证码识别失败，跳过此用例")
        login_page.input_captcha(captcha)

        logger.info("=== 点击登录按钮 ===")
        login_page.click_login()

        error_messages = login_page.get_all_error_messages()
        AssertUtil.assert_in(
            wrong_pwd_data["expected_error"],
            error_messages,
            message=f"错误提示不匹配：期望包含'{wrong_pwd_data['expected_error']}', 实际={error_messages}"
        )

    def test_wrong_captcha_login(self, web_driver):
        """
        场景7：验证码输入错误时点击登录，验证系统提示

        操作步骤：
            1. 打开商城登录页面；
            2. 输入有效账号；
            3. 输入有效密码；
            4. 输入错误验证码；
            5. 点击登录按钮；

        预期结果：
            1. 页面弹出错误提示：验证码错误；
        """
        login_data = YamlUtil.read_test_data("ui_data.yaml")
        empty_captcha_data = login_data["login"]["empty_captcha"]

        login_page = LoginPage(web_driver)
        login_page.open_login_page()
        login_page.reset_login_page()

        logger.info("=== 输入有效账号 ===")
        login_page.input_username(empty_captcha_data["username"])

        logger.info("=== 输入有效密码 ===")
        login_page.input_password(empty_captcha_data["password"])

        logger.info("=== 输入错误验证码 ===")
        login_page.input_captcha("9999")

        logger.info("=== 点击登录按钮 ===")
        login_page.click_login()

        error_messages = login_page.get_all_error_messages()
        AssertUtil.assert_in(
            empty_captcha_data["expected_error"],
            error_messages,
            message=f"错误提示不匹配：期望包含'{empty_captcha_data['expected_error']}', 实际={error_messages}"
        )

    def test_unauthorized_access_cart(self, web_driver):
        """
        场景8：未登录状态访问需授权页面，验证跳转逻辑

        操作步骤：
            1. 打开商城首页，直接点击购物车按钮；

        预期结果：
            1. 页面自动跳转至登录页面；
        """
        login_page = LoginPage(web_driver)
        login_page.open_home_page()
        login_page.click_cart_btn()

        AssertUtil.assert_true(
            login_page.is_redirect_to_login(),
            message="未跳转到登录页面：未登录访问购物车失败"
        )
