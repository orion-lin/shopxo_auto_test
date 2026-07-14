
import time
import os
from selenium import webdriver
from utils.path_util import PathUtil
from utils.log_util import logger


class ScreenshotUtil:
    """
    截图工具类
    提供浏览器截图功能，自动命名并保存到report目录
    """

    @staticmethod
    def capture_screenshot(driver: webdriver.Chrome, filename: str = None) -> str:
        """
        截取当前页面截图

        Args:
            driver: WebDriver实例
            filename: 自定义文件名（可选），如果不提供则自动生成

        Returns:
            str: 截图文件的完整路径

        Raises:
            Exception: 截图失败时抛出
        """
        try:
            # 确保报告目录存在
            report_dir = PathUtil.get_report_path("screenshots")
            PathUtil.ensure_dir_exists(report_dir)

            # 生成文件名（自动命名规则：时间戳_自定义名称）
            if filename:
                # 移除文件名中的非法字符
                filename = filename.replace("/", "_").replace("\\", "_").replace(":", "_")
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                full_filename = f"{timestamp}_{filename}.png"
            else:
                full_filename = time.strftime("%Y%m%d_%H%M%S") + ".png"

            # 拼接完整路径
            screenshot_path = os.path.join(report_dir, full_filename)

            # 执行截图
            driver.save_screenshot(screenshot_path)

            logger.info(f"截图成功，保存路径: {screenshot_path}")
            return screenshot_path

        except Exception as e:
            logger.error(f"截图失败: {str(e)}", exc_info=True)
            raise Exception(f"截图失败: {str(e)}")

    @staticmethod
    def capture_element_screenshot(driver: webdriver.Chrome, element, filename: str = None) -> str:
        """
        截取指定元素的截图

        Args:
            driver: WebDriver实例
            element: WebElement对象
            filename: 自定义文件名（可选）

        Returns:
            str: 截图文件的完整路径

        Raises:
            Exception: 截图失败时抛出
        """
        try:
            # 确保报告目录存在
            report_dir = PathUtil.get_report_path("screenshots")
            PathUtil.ensure_dir_exists(report_dir)

            # 生成文件名
            if filename:
                filename = filename.replace("/", "_").replace("\\", "_").replace(":", "_")
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                full_filename = f"{timestamp}_{filename}_element.png"
            else:
                full_filename = time.strftime("%Y%m%d_%H%M%S") + "_element.png"

            # 拼接完整路径
            screenshot_path = os.path.join(report_dir, full_filename)

            # 执行元素截图
            element.screenshot(screenshot_path)

            logger.info(f"元素截图成功，保存路径: {screenshot_path}")
            return screenshot_path

        except Exception as e:
            logger.error(f"元素截图失败: {str(e)}", exc_info=True)
            raise Exception(f"元素截图失败: {str(e)}")

    @staticmethod
    def capture_full_page_screenshot(driver: webdriver.Chrome, filename: str = None) -> str:
        """
        截取完整页面截图（包括滚动区域）

        Args:
            driver: WebDriver实例
            filename: 自定义文件名（可选）

        Returns:
            str: 截图文件的完整路径

        Raises:
            Exception: 截图失败时抛出
        """
        try:
            # 确保报告目录存在
            report_dir = PathUtil.get_report_path("screenshots")
            PathUtil.ensure_dir_exists(report_dir)

            # 生成文件名
            if filename:
                filename = filename.replace("/", "_").replace("\\", "_").replace(":", "_")
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                full_filename = f"{timestamp}_{filename}_fullpage.png"
            else:
                full_filename = time.strftime("%Y%m%d_%H%M%S") + "_fullpage.png"

            # 拼接完整路径
            screenshot_path = os.path.join(report_dir, full_filename)

            # 使用DevTools协议截取完整页面
            full_screenshot = driver.execute_cdp_cmd(
                "Page.captureScreenshot",
                {"format": "png", "captureBeyondViewport": True}
            )

            # 保存截图
            import base64
            with open(screenshot_path, "wb") as f:
                f.write(base64.b64decode(full_screenshot["data"]))

            logger.info(f"完整页面截图成功，保存路径: {screenshot_path}")
            return screenshot_path

        except Exception as e:
            logger.error(f"完整页面截图失败: {str(e)}", exc_info=True)
            raise Exception(f"完整页面截图失败: {str(e)}")
