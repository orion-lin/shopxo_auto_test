import yaml
import os
from utils.path_util import PathUtil


class YamlUtil:
    """
    YAML文件读写工具类
    提供读取配置文件、测试数据的通用方法
    """

    @classmethod
    def read_yaml(cls, file_path, encoding="utf-8"):
        """
        读取YAML文件内容

        Args:
            file_path (str): YAML文件路径
            encoding (str): 文件编码，默认为utf-8

        Returns:
            dict: YAML文件解析后的字典数据
            None: 文件不存在或解析失败时返回None
        """
        # 检查文件是否存在
        if not os.path.exists(file_path):
            print(f"[WARN] YAML文件不存在: {file_path}")
            return None

        try:
            with open(file_path, "r", encoding=encoding) as file:
                data = yaml.safe_load(file)
                print(f"[INFO] 成功读取YAML文件: {file_path}")
                return data
        except yaml.YAMLError as e:
            print(f"[ERROR] YAML文件解析错误: {file_path}, 错误信息: {str(e)}")
            return None
        except Exception as e:
            print(f"[ERROR] 读取YAML文件失败: {file_path}, 错误信息: {str(e)}")
            return None

    @classmethod
    def write_yaml(cls, file_path, data, encoding="utf-8"):
        """
        写入数据到YAML文件

        Args:
            file_path (str): YAML文件路径
            data (dict/list): 要写入的数据，支持字典或列表
            encoding (str): 文件编码，默认为utf-8

        Returns:
            bool: 写入成功返回True，失败返回False
        """
        # 确保目录存在
        dir_path = os.path.dirname(file_path)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)

        try:
            with open(file_path, "w", encoding=encoding) as file:
                yaml.dump(data, file, default_flow_style=False, allow_unicode=True)
                print(f"[INFO] 成功写入YAML文件: {file_path}")
                return True
        except Exception as e:
            print(f"[ERROR] 写入YAML文件失败: {file_path}, 错误信息: {str(e)}")
            return False

    @classmethod
    def read_conf(cls, filename, encoding="utf-8"):
        """
        读取配置文件（conf目录下的YAML文件）

        Args:
            filename (str): 配置文件名，如"env.yaml"
            encoding (str): 文件编码，默认为utf-8

        Returns:
            dict: 配置文件解析后的字典数据
            None: 文件不存在或解析失败时返回None
        """
        file_path = PathUtil.get_conf_file(filename)
        return cls.read_yaml(file_path, encoding)

    @classmethod
    def read_test_data(cls, filename, encoding="utf-8"):
        """
        读取测试数据文件（data目录下的YAML文件）

        Args:
            filename (str): 测试数据文件名，如"test_data.yaml"
            encoding (str): 文件编码，默认为utf-8

        Returns:
            dict: 测试数据解析后的字典数据
            None: 文件不存在或解析失败时返回None
        """
        file_path = PathUtil.get_data_file(filename)
        return cls.read_yaml(file_path, encoding)

    @classmethod
    def write_test_data(cls, filename, data, encoding="utf-8"):
        """
        写入测试数据到data目录

        Args:
            filename (str): 测试数据文件名
            data (dict/list): 要写入的数据
            encoding (str): 文件编码，默认为utf-8

        Returns:
            bool: 写入成功返回True，失败返回False
        """
        file_path = PathUtil.get_data_file(filename)
        return cls.write_yaml(file_path, data, encoding)

    @classmethod
    def get_value(cls, data, key, default=None):
        """
        从字典中安全获取值，支持多级键值获取

        Args:
            data (dict): 字典数据
            key (str): 键名，支持"key1.key2.key3"格式的多级键
            default: 默认值，当键不存在时返回

        Returns:
            任意类型: 获取到的值或默认值
        """
        if data is None or not isinstance(data, dict):
            return default

        keys = key.split(".")
        result = data

        for k in keys:
            if isinstance(result, dict) and k in result:
                result = result[k]
            else:
                return default

        return result


# 示例用法
if __name__ == "__main__":
    # 读取配置文件
    env_config = YamlUtil.read_conf("env.yaml")
    if env_config:
        print(f"环境配置: {env_config}")
        base_url = YamlUtil.get_value(env_config, "base_url")
        print(f"基础URL: {base_url}")

    # 读取浏览器配置
    browser_config = YamlUtil.read_conf("browser.yaml")
    if browser_config:
        print(f"浏览器配置: {browser_config}")
