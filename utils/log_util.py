import logging
import os
import time
from utils.path_util import PathUtil


class LogUtil:
    """
    日志工具类
    提供日志记录功能，按日期分文件保存日志到logs文件夹
    """

    LOG_LEVEL_MAP = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }

    def __init__(self, logger_name: str = "shopxo_auto_test", log_level: str = "INFO"):
        """
        初始化日志工具

        Args:
            logger_name: 日志器名称，默认为"shopxo_auto_test"
            log_level: 日志级别，可选值: DEBUG, INFO, WARNING, ERROR, CRITICAL
        """
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(self.LOG_LEVEL_MAP.get(log_level.upper(), logging.INFO))

        if self.logger.handlers:
            return

        log_dir = PathUtil.get_logs_dir()
        PathUtil.ensure_dir_exists(log_dir)

        log_filename = time.strftime("%Y-%m-%d") + ".log"
        log_filepath = os.path.join(log_dir, log_filename)

        file_handler = logging.FileHandler(log_filepath, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def debug(self, message: str) -> None:
        """
        记录DEBUG级别日志

        Args:
            message: 日志消息
        """
        self.logger.debug(message)

    def info(self, message: str) -> None:
        """
        记录INFO级别日志

        Args:
            message: 日志消息
        """
        self.logger.info(message)

    def warning(self, message: str) -> None:
        """
        记录WARNING级别日志

        Args:
            message: 日志消息
        """
        self.logger.warning(message)

    def error(self, message: str, exc_info: bool = False) -> None:
        """
        记录ERROR级别日志

        Args:
            message: 日志消息
            exc_info: 是否记录异常信息，默认为False
        """
        self.logger.error(message, exc_info=exc_info)

    def critical(self, message: str, exc_info: bool = False) -> None:
        """
        记录CRITICAL级别日志

        Args:
            message: 日志消息
            exc_info: 是否记录异常信息，默认为False
        """
        self.logger.critical(message, exc_info=exc_info)

    def log_request(self, method: str, url: str, params: dict = None, data: dict = None, headers: dict = None) -> None:
        """
        记录HTTP请求日志

        Args:
            method: 请求方法（GET/POST/PUT/DELETE等）
            url: 请求URL
            params: URL参数（可选）
            data: 请求体数据（可选）
            headers: 请求头（可选）
        """
        self.info(f"========== HTTP Request Start ==========")
        self.info(f"Method: {method}")
        self.info(f"URL: {url}")
        if params:
            self.info(f"Params: {params}")
        if data:
            self.info(f"Data: {data}")
        if headers:
            self.info(f"Headers: {headers}")
        self.info(f"========== HTTP Request End ==========")

    def log_response(self, status_code: int, response_text: str, response_json: dict = None, elapsed_time: float = None) -> None:
        """
        记录HTTP响应日志

        Args:
            status_code: 响应状态码
            response_text: 响应文本
            response_json: 响应JSON数据（可选）
            elapsed_time: 请求耗时（秒，可选）
        """
        self.info(f"========== HTTP Response Start ==========")
        self.info(f"Status Code: {status_code}")
        if elapsed_time:
            self.info(f"Elapsed Time: {elapsed_time:.2f}s")
        if response_json:
            self.info(f"Response JSON: {response_json}")
        else:
            self.info(f"Response Text: {response_text}")
        self.info(f"========== HTTP Response End ==========")

    def log_exception(self, message: str, exception: Exception) -> None:
        """
        记录异常信息

        Args:
            message: 异常描述消息
            exception: 异常对象
        """
        self.error(f"{message}: {str(exception)}", exc_info=True)


logger = LogUtil()
