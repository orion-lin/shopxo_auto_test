import ddddocr
import requests
from utils.log_util import logger


class CaptchaUtil:
    """
    验证码工具类
    提供验证码获取和识别功能
    """

    def __init__(self):
        """
        初始化验证码工具类
        """
        self.ocr = ddddocr.DdddOcr()
        self.session = requests.Session()
        logger.info("验证码工具类初始化成功")

    def get_and_recognize_captcha(self, base_url, session=None, max_retries=5):
        """
        获取验证码图片并识别

        Args:
            base_url (str): 基础URL
            session (requests.Session): 外部session对象，用于保持会话一致性
            max_retries (int): 最大重试次数，默认5次

        Returns:
            str: 识别到的验证码，识别失败返回空字符串
        """
        logger.info("开始获取并识别验证码")

        request_session = session if session else self.session

        for attempt in range(max_retries):
            try:
                login_page_url = f"{base_url.rstrip('/')}/?s=user/loginInfo.html"
                request_session.get(login_page_url, timeout=5)

                captcha_urls = [
                    f"{base_url.rstrip('/')}/?s=user/userverifyentry/type/user_login.html",
                    f"{base_url.rstrip('/')}/api/user/verify",
                    f"{base_url.rstrip('/')}/?s=api/user/verify",
                    f"{base_url.rstrip('/')}/user/verify"
                ]

                for captcha_url in captcha_urls:
                    try:
                        response = request_session.get(captcha_url, timeout=5)

                        if response.status_code == 200 and len(response.content) > 100:
                            captcha_text = self.ocr.classification(response.content)

                            if captcha_text and captcha_text.isalnum() and len(captcha_text) >= 3:
                                logger.info(f"验证码识别成功: {captcha_text}")
                                return captcha_text
                            else:
                                logger.warning(f"验证码识别结果无效: {captcha_text}，尝试下一个URL")
                    except requests.RequestException:
                        logger.info(f"验证码URL {captcha_url} 请求失败，尝试下一个URL")
                        continue

            except Exception as e:
                logger.error(f"验证码识别异常: {str(e)}")

            if attempt < max_retries - 1:
                logger.info(f"第{attempt + 1}次尝试失败，重试中...")

        logger.error("验证码获取和识别失败，已达到最大重试次数")
        return ""

    def recognize_captcha_from_bytes(self, image_bytes):
        """
        从图片字节数据中识别验证码

        Args:
            image_bytes (bytes): 验证码图片字节数据

        Returns:
            str: 识别到的验证码，识别失败返回空字符串
        """
        try:
            captcha_text = self.ocr.classification(image_bytes)

            if captcha_text and captcha_text.isalnum() and len(captcha_text) >= 3:
                logger.info(f"验证码识别成功: {captcha_text}")
                return captcha_text
            else:
                logger.warning(f"验证码识别结果无效: {captcha_text}")
                return ""

        except Exception as e:
            logger.error(f"验证码识别异常: {str(e)}")
            return ""


captcha_util = CaptchaUtil()