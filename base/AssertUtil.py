import pytest
from utils.log_util import logger


class AssertUtil:
    """
    通用断言工具类
    提供状态码、code、文本包含、数据相等、响应时间等通用断言方法
    无业务逻辑，仅提供通用能力
    """

    @staticmethod
    def assert_equal(actual, expected, message=None):
        """
        断言两个值相等

        Args:
            actual: 实际值
            expected: 期望值
            message (str): 断言失败时的自定义消息（可选）

        Raises:
            AssertionError: 断言失败时抛出
        """
        try:
            assert actual == expected, message or f"期望值: {expected}, 实际值: {actual}"
            logger.info(f"断言相等成功: 期望值={expected}, 实际值={actual}")

        except AssertionError as e:
            logger.error(f"断言相等失败: {str(e)}")
            raise

    @staticmethod
    def assert_not_equal(actual, expected, message=None):
        """
        断言两个值不相等

        Args:
            actual: 实际值
            expected: 期望值
            message (str): 断言失败时的自定义消息（可选）

        Raises:
            AssertionError: 断言失败时抛出
        """
        try:
            assert actual != expected, message or f"期望值: {expected}, 实际值: {actual}"
            logger.info(f"断言不相等成功: 期望值={expected}, 实际值={actual}")

        except AssertionError as e:
            logger.error(f"断言不相等失败: {str(e)}")
            raise

    @staticmethod
    def assert_true(condition, message=None):
        """
        断言条件为True

        Args:
            condition: 布尔条件
            message (str): 断言失败时的自定义消息（可选）

        Raises:
            AssertionError: 断言失败时抛出
        """
        try:
            assert condition, message or f"条件为False"
            logger.info(f"断言为True成功: {condition}")

        except AssertionError as e:
            logger.error(f"断言为True失败: {str(e)}")
            raise

    @staticmethod
    def assert_false(condition, message=None):
        """
        断言条件为False

        Args:
            condition: 布尔条件
            message (str): 断言失败时的自定义消息（可选）

        Raises:
            AssertionError: 断言失败时抛出
        """
        try:
            assert not condition, message or f"条件为True"
            logger.info(f"断言为False成功: {condition}")

        except AssertionError as e:
            logger.error(f"断言为False失败: {str(e)}")
            raise

    @staticmethod
    def assert_is_none(value, message=None):
        """
        断言值为None

        Args:
            value: 要断言的值
            message (str): 断言失败时的自定义消息（可选）

        Raises:
            AssertionError: 断言失败时抛出
        """
        try:
            assert value is None, message or f"值不为None: {value}"
            logger.info(f"断言为None成功")

        except AssertionError as e:
            logger.error(f"断言为None失败: {str(e)}")
            raise

    @staticmethod
    def assert_is_not_none(value, message=None):
        """
        断言值不为None

        Args:
            value: 要断言的值
            message (str): 断言失败时的自定义消息（可选）

        Raises:
            AssertionError: 断言失败时抛出
        """
        try:
            assert value is not None, message or f"值为None"
            logger.info(f"断言不为None成功: {value}")

        except AssertionError as e:
            logger.error(f"断言不为None失败: {str(e)}")
            raise

    @staticmethod
    def assert_in(item, container, message=None):
        """
        断言item在container中

        Args:
            item: 要检查的元素
            container: 容器（列表、元组、字符串、字典等）
            message (str): 断言失败时的自定义消息（可选）

        Raises:
            AssertionError: 断言失败时抛出
        """
        try:
            assert item in container, message or f"{item} 不在 {container} 中"
            logger.info(f"断言包含成功: {item} 在 {container} 中")

        except AssertionError as e:
            logger.error(f"断言包含失败: {str(e)}")
            raise

    @staticmethod
    def assert_not_in(item, container, message=None):
        """
        断言item不在container中

        Args:
            item: 要检查的元素
            container: 容器（列表、元组、字符串、字典等）
            message (str): 断言失败时的自定义消息（可选）

        Raises:
            AssertionError: 断言失败时抛出
        """
        try:
            assert item not in container, message or f"{item} 在 {container} 中"
            logger.info(f"断言不包含成功: {item} 不在 {container} 中")

        except AssertionError as e:
            logger.error(f"断言不包含失败: {str(e)}")
            raise

    @staticmethod
    def assert_contains_text(actual_text, expected_text, message=None):
        """
        断言实际文本包含期望文本

        Args:
            actual_text (str): 实际文本
            expected_text (str): 期望包含的文本
            message (str): 断言失败时的自定义消息（可选）

        Raises:
            AssertionError: 断言失败时抛出
        """
        try:
            assert expected_text in actual_text, message or \
                f"实际文本: {actual_text}, 期望包含: {expected_text}"
            logger.info(f"断言文本包含成功: 实际文本='{actual_text}', 期望包含='{expected_text}'")

        except AssertionError as e:
            logger.error(f"断言文本包含失败: {str(e)}")
            raise

    @staticmethod
    def assert_status_code(response, expected_code=200, message=None):
        """
        断言HTTP响应状态码

        Args:
            response: 响应对象（requests.Response）或状态码（int）
            expected_code (int): 期望的状态码，默认为200
            message (str): 断言失败时的自定义消息（可选）

        Raises:
            AssertionError: 断言失败时抛出
        """
        try:
            # 如果是response对象，获取状态码
            if hasattr(response, "status_code"):
                actual_code = response.status_code
            else:
                actual_code = response

            assert actual_code == expected_code, message or \
                f"期望状态码: {expected_code}, 实际状态码: {actual_code}"
            logger.info(f"断言状态码成功: {actual_code}")

        except AssertionError as e:
            logger.error(f"断言状态码失败: {str(e)}")
            raise

    @staticmethod
    def assert_response_code(response_json, expected_code=0, code_key="code", message=None):
        """
        断言API响应中的code字段

        Args:
            response_json (dict): API响应JSON数据
            expected_code (int): 期望的code值，默认为0
            code_key (str): code字段的键名，默认为"code"
            message (str): 断言失败时的自定义消息（可选）

        Raises:
            AssertionError: 断言失败时抛出
        """
        try:
            actual_code = response_json.get(code_key)

            assert actual_code == expected_code, message or \
                f"期望code: {expected_code}, 实际code: {actual_code}"
            logger.info(f"断言响应code成功: {actual_code}")

        except AssertionError as e:
            logger.error(f"断言响应code失败: {str(e)}")
            raise
        except AttributeError as e:
            logger.error(f"响应数据不是字典类型: {str(e)}")
            raise

    @staticmethod
    def assert_response_message(response_json, expected_message, message_key="msg", message=None):
        """
        断言API响应中的message字段

        Args:
            response_json (dict): API响应JSON数据
            expected_message (str): 期望的message值
            message_key (str): message字段的键名，默认为"msg"
            message (str): 断言失败时的自定义消息（可选）

        Raises:
            AssertionError: 断言失败时抛出
        """
        try:
            actual_message = response_json.get(message_key)

            assert actual_message == expected_message, message or \
                f"期望message: {expected_message}, 实际message: {actual_message}"
            logger.info(f"断言响应message成功: {actual_message}")

        except AssertionError as e:
            logger.error(f"断言响应message失败: {str(e)}")
            raise
        except AttributeError as e:
            logger.error(f"响应数据不是字典类型: {str(e)}")
            raise

    @staticmethod
    def assert_response_contains_message(response_json, expected_substring, message_key="msg", message=None):
        """
        断言API响应中的message字段包含指定子串

        Args:
            response_json (dict): API响应JSON数据
            expected_substring (str): 期望包含的子串
            message_key (str): message字段的键名，默认为"msg"
            message (str): 断言失败时的自定义消息（可选）

        Raises:
            AssertionError: 断言失败时抛出
        """
        try:
            actual_message = response_json.get(message_key)

            assert expected_substring in str(actual_message), message or \
                f"期望message包含: {expected_substring}, 实际message: {actual_message}"
            logger.info(f"断言响应message包含成功: {actual_message}")

        except AssertionError as e:
            logger.error(f"断言响应message包含失败: {str(e)}")
            raise
        except AttributeError as e:
            logger.error(f"响应数据不是字典类型: {str(e)}")
            raise

    @staticmethod
    def assert_response_success(response_json, success_code=0, code_key="code", message=None):
        """
        断言API响应成功（code为success_code）

        Args:
            response_json (dict): API响应JSON数据
            success_code (int): 成功的code值，默认为0
            code_key (str): code字段的键名，默认为"code"
            message (str): 断言失败时的自定义消息（可选）

        Raises:
            AssertionError: 断言失败时抛出
        """
        try:
            actual_code = response_json.get(code_key)

            assert actual_code == success_code, message or \
                f"期望成功code: {success_code}, 实际code: {actual_code}"
            logger.info(f"断言响应成功: code={actual_code}")

        except AssertionError as e:
            logger.error(f"断言响应成功失败: {str(e)}")
            raise
        except AttributeError as e:
            logger.error(f"响应数据不是字典类型: {str(e)}")
            raise

    @staticmethod
    def assert_response_failure(response_json, fail_codes=None, code_key="code", message=None):
        """
        断言API响应失败（code不在success_codes中）

        Args:
            response_json (dict): API响应JSON数据
            fail_codes (list): 失败的code值列表，默认为非0值
            code_key (str): code字段的键名，默认为"code"
            message (str): 断言失败时的自定义消息（可选）

        Raises:
            AssertionError: 断言失败时抛出
        """
        try:
            actual_code = response_json.get(code_key)

            if fail_codes is not None:
                assert actual_code in fail_codes, message or \
                    f"期望code在失败列表中: {fail_codes}, 实际code: {actual_code}"
            else:
                assert actual_code != 0, message or \
                    f"期望响应失败，实际code: {actual_code}"

            logger.info(f"断言响应失败成功: code={actual_code}")

        except AssertionError as e:
            logger.error(f"断言响应失败失败: {str(e)}")
            raise
        except AttributeError as e:
            logger.error(f"响应数据不是字典类型: {str(e)}")
            raise

    @staticmethod
    def assert_list_length(items, expected_length, message=None):
        """
        断言列表长度

        Args:
            items (list): 要检查的列表
            expected_length (int): 期望的长度
            message (str): 断言失败时的自定义消息（可选）

        Raises:
            AssertionError: 断言失败时抛出
        """
        try:
            actual_length = len(items)
            assert actual_length == expected_length, message or \
                f"期望长度: {expected_length}, 实际长度: {actual_length}"
            logger.info(f"断言列表长度成功: {actual_length}")

        except AssertionError as e:
            logger.error(f"断言列表长度失败: {str(e)}")
            raise
        except TypeError as e:
            logger.error(f"输入不是可迭代对象: {str(e)}")
            raise

    @staticmethod
    def assert_greater_than(actual, expected, message=None):
        """
        断言实际值大于期望值

        Args:
            actual: 实际值
            expected: 期望值
            message (str): 断言失败时的自定义消息（可选）

        Raises:
            AssertionError: 断言失败时抛出
        """
        try:
            assert actual > expected, message or \
                f"实际值: {actual} 不大于期望值: {expected}"
            logger.info(f"断言大于成功: {actual} > {expected}")

        except AssertionError as e:
            logger.error(f"断言大于失败: {str(e)}")
            raise

    @staticmethod
    def assert_greater_or_equal(actual, expected, message=None):
        """
        断言实际值大于等于期望值

        Args:
            actual: 实际值
            expected: 期望值
            message (str): 断言失败时的自定义消息（可选）

        Raises:
            AssertionError: 断言失败时抛出
        """
        try:
            assert actual >= expected, message or \
                f"实际值: {actual} 小于期望值: {expected}"
            logger.info(f"断言大于等于成功: {actual} >= {expected}")

        except AssertionError as e:
            logger.error(f"断言大于等于失败: {str(e)}")
            raise

    @staticmethod
    def assert_less_than(actual, expected, message=None):
        """
        断言实际值小于期望值

        Args:
            actual: 实际值
            expected: 期望值
            message (str): 断言失败时的自定义消息（可选）

        Raises:
            AssertionError: 断言失败时抛出
        """
        try:
            assert actual < expected, message or \
                f"实际值: {actual} 不小于期望值: {expected}"
            logger.info(f"断言小于成功: {actual} < {expected}")

        except AssertionError as e:
            logger.error(f"断言小于失败: {str(e)}")
            raise

    @staticmethod
    def assert_less_or_equal(actual, expected, message=None):
        """
        断言实际值小于等于期望值

        Args:
            actual: 实际值
            expected: 期望值
            message (str): 断言失败时的自定义消息（可选）

        Raises:
            AssertionError: 断言失败时抛出
        """
        try:
            assert actual <= expected, message or \
                f"实际值: {actual} 大于期望值: {expected}"
            logger.info(f"断言小于等于成功: {actual} <= {expected}")

        except AssertionError as e:
            logger.error(f"断言小于等于失败: {str(e)}")
            raise

    @staticmethod
    def assert_response_time(elapsed_time, max_time=5.0, message=None):
        """
        断言响应时间在允许范围内

        Args:
            elapsed_time (float): 实际响应时间（秒）
            max_time (float): 最大允许响应时间（秒），默认为5秒
            message (str): 断言失败时的自定义消息（可选）

        Raises:
            AssertionError: 断言失败时抛出
        """
        try:
            assert elapsed_time <= max_time, message or \
                f"响应时间: {elapsed_time:.2f}s 超过最大允许时间: {max_time}s"
            logger.info(f"断言响应时间成功: {elapsed_time:.2f}s")

        except AssertionError as e:
            logger.error(f"断言响应时间失败: {str(e)}")
            raise

    @staticmethod
    def assert_dict_contains_keys(dictionary, keys, message=None):
        """
        断言字典包含指定键

        Args:
            dictionary (dict): 要检查的字典
            keys (list): 期望包含的键列表
            message (str): 断言失败时的自定义消息（可选）

        Raises:
            AssertionError: 断言失败时抛出
        """
        try:
            missing_keys = [key for key in keys if key not in dictionary]
            assert not missing_keys, message or \
                f"字典缺少键: {missing_keys}"
            logger.info(f"断言字典包含键成功: {keys}")

        except AssertionError as e:
            logger.error(f"断言字典包含键失败: {str(e)}")
            raise
        except TypeError as e:
            logger.error(f"输入不是字典类型: {str(e)}")
            raise

    @staticmethod
    def assert_dict_equal(actual_dict, expected_dict, message=None):
        """
        断言两个字典相等

        Args:
            actual_dict (dict): 实际字典
            expected_dict (dict): 期望字典
            message (str): 断言失败时的自定义消息（可选）

        Raises:
            AssertionError: 断言失败时抛出
        """
        try:
            assert actual_dict == expected_dict, message or \
                f"期望字典: {expected_dict}, 实际字典: {actual_dict}"
            logger.info(f"断言字典相等成功")

        except AssertionError as e:
            logger.error(f"断言字典相等失败: {str(e)}")
            raise

    @staticmethod
    def assert_dict_contains_subset(subset_dict, superset_dict, message=None):
        """
        断言字典包含子集

        Args:
            subset_dict (dict): 子集字典
            superset_dict (dict): 超集字典
            message (str): 断言失败时的自定义消息（可选）

        Raises:
            AssertionError: 断言失败时抛出
        """
        try:
            # pytest版本支持assert dict contains subset
            pytest.assert_dict_contains_subset(subset_dict, superset_dict, message)
            logger.info(f"断言字典包含子集成功")

        except AssertionError as e:
            logger.error(f"断言字典包含子集失败: {str(e)}")
            raise

    @staticmethod
    def assert_raises(exception_type, func, *args, **kwargs):
        """
        断言函数调用会抛出指定类型的异常

        Args:
            exception_type: 期望的异常类型
            func: 要调用的函数
            *args: 函数位置参数
            **kwargs: 函数关键字参数

        Returns:
            Exception: 捕获的异常对象

        Raises:
            AssertionError: 未抛出期望异常时抛出
        """
        try:
            with pytest.raises(exception_type) as exc_info:
                func(*args, **kwargs)

            logger.info(f"断言抛出异常成功: {exception_type.__name__}")
            return exc_info.value

        except AssertionError as e:
            logger.error(f"断言抛出异常失败: {str(e)}")
            raise
