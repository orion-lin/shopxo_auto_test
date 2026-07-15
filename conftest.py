import pytest
import os
from selenium import webdriver
from utils.log_util import logger
from utils.path_util import PathUtil
from base.WebDriverBase import WebDriverBase
from base.ApiRequest import ApiRequest


@pytest.fixture(scope="session")
def web_driver():
    """
    全局浏览器fixture（session级别）
    前置：初始化浏览器驱动
    后置：关闭浏览器驱动

    Returns:
        WebDriverBase: WebDriver基础操作类实例
    """
    logger.info("========== 初始化全局浏览器会话 ==========")

    # 创建WebDriverBase实例
    wd_base = WebDriverBase()

    try:
        # 初始化驱动
        wd_base.init_driver()

        # 最大化窗口（根据配置）
        wd_base.maximize_window()

        logger.info("全局浏览器初始化成功")

        # 提供fixture给测试用例使用
        yield wd_base

    except Exception as e:
        logger.error(f"全局浏览器初始化失败: {str(e)}", exc_info=True)
        raise

    finally:
        # 后置：关闭浏览器
        logger.info("========== 关闭全局浏览器会话 ==========")
        wd_base.quit()


@pytest.fixture(scope="session")
def api_client():
    """
    全局API请求客户端fixture（session级别）
    前置：创建API请求实例
    后置：关闭session连接

    Returns:
        ApiRequest: API请求封装类实例
    """
    logger.info("========== 初始化全局API请求客户端 ==========")

    # 创建API请求实例
    api = ApiRequest()

    try:
        logger.info("全局API请求客户端初始化成功")

        # 提供fixture给测试用例使用
        yield api

    except Exception as e:
        logger.error(f"全局API请求客户端初始化失败: {str(e)}", exc_info=True)
        raise

    finally:
        # 后置：关闭session连接
        logger.info("========== 关闭全局API请求客户端 ==========")
        api.close_session()


@pytest.fixture(scope="session")
def login_token(api_client):
    """
    全局登录Token fixture（session级别）
    调用登录接口获取Token，用于需要已登录状态的测试用例

    Args:
        api_client: API请求客户端fixture

    Returns:
        str: 登录Token值（未登录时返回空字符串）
    """
    logger.info("========== 获取全局登录Token ==========")

    token = ""

    try:
        from utils.yaml_util import YamlUtil

        login_data = YamlUtil.read_test_data("api_data.yaml")
        login_info = login_data["login_api"]

        response = api_client.post(
            endpoint=login_info["path"],
            json={
                "username": login_info["username"],
                "password": login_info["password"]
            }
        )

        token = response.get("data", {}).get("token", "")

        if token:
            api_client.set_token(token)
            logger.info(f"登录成功，Token: {token[:20]}...")
        else:
            logger.warning("登录接口未返回Token")

    except Exception as e:
        logger.error(f"登录失败: {str(e)}", exc_info=True)

    if not token:
        logger.warning("未执行登录逻辑，Token为空，测试将在未登录状态下执行")

    yield token

    logger.info("========== 登录Token会话结束 ==========")


@pytest.fixture(scope="class")
def login(web_driver):
    """
    UI登录fixture（class级别）
    复用登录模块的login()方法完成登录操作
    商品详情模块所有用例共享同一登录态

    Args:
        web_driver: WebDriverBase实例

    Returns:
        bool: 登录成功返回True，失败返回False
    """
    logger.info("========== 执行UI登录操作 ==========")

    from page.login_page import LoginPage
    from utils.yaml_util import YamlUtil

    login_page = LoginPage(web_driver)

    try:
        login_data = YamlUtil.read_test_data("ui_data.yaml")["login"]["normal"]
        username = login_data["username"]
        password = login_data["password"]

        logger.info(f"调用登录模块login()方法，用户名: {username}")
        login_success = login_page.login(username, password)

        if login_success:
            logger.info("UI登录成功")
        else:
            logger.error("UI登录失败")
            pytest.skip("Login failed, skip all test cases in this class")

        yield login_success

    except Exception as e:
        logger.error(f"UI登录异常: {str(e)}", exc_info=True)
        pytest.skip(f"Login exception: {str(e)}")


@pytest.fixture(autouse=True)
def test_case_logging(request):
    """
    自动fixture：记录每个测试用例的开始和结束
    """
    test_name = request.node.name
    logger.info(f"\n{'='*60}")
    logger.info(f"开始执行测试用例: {test_name}")
    logger.info(f"{'='*60}")

    yield

    logger.info(f"\n{'='*60}")
    logger.info(f"测试用例执行完成: {test_name}")
    logger.info(f"{'='*60}\n")


def pytest_runtest_makereport(item, call):
    """
    pytest钩子函数：在测试用例执行完成后生成报告
    用于捕获测试失败时的截图并绑定到Allure报告

    Args:
        item: 测试用例对象
        call: 测试用例调用对象
    """
    # 获取测试结果
    if call.when == "call":
        # 获取测试状态
        test_status = call.excinfo is not None and "failed" or "passed"

        # 如果测试失败，进行截图
        if test_status == "failed":
            logger.error(f"测试用例失败: {item.name}")

            try:
                # 获取web_driver fixture（如果存在）
                web_driver_fixture = item.funcargs.get("web_driver")

                if web_driver_fixture and web_driver_fixture.driver:
                    # 截图并保存
                    screenshot_path = web_driver_fixture.screenshot(filename=item.name)
                    logger.info(f"测试失败截图已保存: {screenshot_path}")

                    # 绑定截图到Allure报告
                    try:
                        import allure
                        with open(screenshot_path, "rb") as f:
                            allure.attach(
                                f.read(),
                                name=f"{item.name}_screenshot",
                                attachment_type=allure.attachment_type.PNG
                            )
                        logger.info("截图已绑定到Allure报告")
                    except ImportError:
                        logger.warning("Allure模块未安装，无法绑定截图到报告")
                    except Exception as e:
                        logger.error(f"绑定截图到Allure报告失败: {str(e)}")

            except Exception as e:
                logger.error(f"测试失败截图失败: {str(e)}")


def pytest_collection_modifyitems(items):
    """
    pytest钩子函数：修改测试用例收集结果
    可用于对测试用例进行排序、过滤等操作

    Args:
        items: 测试用例列表
    """
    logger.info(f"共收集到 {len(items)} 个测试用例")


def pytest_configure(config):
    """
    pytest钩子函数：在pytest配置完成后执行
    可用于添加自定义配置项

    Args:
        config: pytest配置对象
    """
    # 添加自定义标记
    config.addinivalue_line("markers", "ui: 标记UI自动化测试用例")
    config.addinivalue_line("markers", "api: 标记API接口测试用例")
    config.addinivalue_line("markers", "smoke: 标记冒烟测试用例")
    config.addinivalue_line("markers", "regression: 标记回归测试用例")

    logger.info("pytest配置完成")


def pytest_unconfigure(config):
    """
    pytest钩子函数：在pytest退出前执行
    可用于清理资源

    Args:
        config: pytest配置对象
    """
    logger.info("pytest会话结束")
