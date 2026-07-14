import os


class PathUtil:
    """
    统一项目绝对路径拼接工具类
    兼容Windows D盘路径，使用原始字符串规避转义问题
    """

    # 项目根目录（使用原始字符串定义，避免Windows路径转义）
    _ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    @classmethod
    def get_root_dir(cls):
        """
        获取项目根目录绝对路径

        Returns:
            str: 项目根目录绝对路径
        """
        return cls._ROOT_DIR

    @classmethod
    def get_conf_dir(cls):
        """
        获取配置文件目录绝对路径

        Returns:
            str: conf目录绝对路径
        """
        return os.path.join(cls._ROOT_DIR, "conf")

    @classmethod
    def get_conf_file(cls, filename):
        """
        获取指定配置文件的绝对路径

        Args:
            filename (str): 配置文件名，如"env.yaml"

        Returns:
            str: 配置文件绝对路径
        """
        return os.path.join(cls.get_conf_dir(), filename)

    @classmethod
    def get_base_dir(cls):
        """
        获取基础封装目录绝对路径

        Returns:
            str: base目录绝对路径
        """
        return os.path.join(cls._ROOT_DIR, "base")

    @classmethod
    def get_utils_dir(cls):
        """
        获取工具类目录绝对路径

        Returns:
            str: utils目录绝对路径
        """
        return os.path.join(cls._ROOT_DIR, "utils")

    @classmethod
    def get_data_dir(cls):
        """
        获取测试数据目录绝对路径

        Returns:
            str: data目录绝对路径
        """
        return os.path.join(cls._ROOT_DIR, "data")

    @classmethod
    def get_data_file(cls, filename):
        """
        获取指定测试数据文件的绝对路径

        Args:
            filename (str): 数据文件名，如"test_data.yaml"

        Returns:
            str: 数据文件绝对路径
        """
        return os.path.join(cls.get_data_dir(), filename)

    @classmethod
    def get_testcases_dir(cls):
        """
        获取测试用例目录绝对路径

        Returns:
            str: testcases目录绝对路径
        """
        return os.path.join(cls._ROOT_DIR, "testcases")

    @classmethod
    def get_report_dir(cls):
        """
        获取测试报告目录绝对路径

        Returns:
            str: report目录绝对路径
        """
        report_dir = os.path.join(cls._ROOT_DIR, "report")
        if not os.path.exists(report_dir):
            os.makedirs(report_dir, exist_ok=True)
        return report_dir

    @classmethod
    def get_allure_raw_dir(cls):
        """
        获取Allure原始报告目录绝对路径

        Returns:
            str: allure_raw目录绝对路径
        """
        allure_raw_dir = os.path.join(cls.get_report_dir(), "allure_raw")
        if not os.path.exists(allure_raw_dir):
            os.makedirs(allure_raw_dir, exist_ok=True)
        return allure_raw_dir

    @classmethod
    def get_allure_html_dir(cls):
        """
        获取Allure HTML报告目录绝对路径

        Returns:
            str: allure_html目录绝对路径
        """
        allure_html_dir = os.path.join(cls.get_report_dir(), "allure_html")
        if not os.path.exists(allure_html_dir):
            os.makedirs(allure_html_dir, exist_ok=True)
        return allure_html_dir

    @classmethod
    def get_logs_dir(cls):
        """
        获取日志文件目录绝对路径

        Returns:
            str: logs目录绝对路径
        """
        logs_dir = os.path.join(cls._ROOT_DIR, "logs")
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir, exist_ok=True)
        return logs_dir

    @classmethod
    def get_page_dir(cls):
        """
        获取页面类目录绝对路径

        Returns:
            str: page目录绝对路径
        """
        return os.path.join(cls._ROOT_DIR, "page")

    @classmethod
    def get_report_path(cls, sub_dir=None):
        """
        获取报告子目录绝对路径（兼容旧版本方法名）

        Args:
            sub_dir (str): 子目录名称，如"screenshots"

        Returns:
            str: 报告子目录绝对路径
        """
        report_dir = cls.get_report_dir()
        if sub_dir:
            full_path = os.path.join(report_dir, sub_dir)
            cls.ensure_dir_exists(full_path)
            return full_path
        return report_dir

    @classmethod
    def join_path(cls, *args):
        """
        拼接路径，自动处理路径分隔符

        Args:
            *args: 路径片段，可变参数

        Returns:
            str: 拼接后的绝对路径
        """
        return os.path.join(cls._ROOT_DIR, *args)

    @classmethod
    def ensure_dir_exists(cls, dir_path):
        """
        确保目录存在，不存在则创建

        Args:
            dir_path (str): 目录路径

        Returns:
            str: 目录路径
        """
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
        return dir_path


# 示例用法
if __name__ == "__main__":
    print(f"项目根目录: {PathUtil.get_root_dir()}")
    print(f"配置文件目录: {PathUtil.get_conf_dir()}")
    print(f"配置文件: {PathUtil.get_conf_file('env.yaml')}")
    print(f"日志目录: {PathUtil.get_logs_dir()}")
    print(f"报告目录: {PathUtil.get_report_dir()}")
