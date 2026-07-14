import requests
import json
from utils.yaml_util import YamlUtil
from utils.log_util import logger


class ApiRequest:
    """
    API请求封装类
    提供统一POST/GET请求封装、自动请求头、异常捕获、通用响应打印等功能
    无业务逻辑，仅提供通用能力
    """

    def __init__(self):
        """
        初始化API请求类
        加载环境配置，创建session对象
        """
        self.env_config = YamlUtil.read_conf("env.yaml")
        self.base_url = self.env_config.get("base_url", "")
        self.api_path = self.env_config.get("api_path", "")
        self.timeout = self.env_config.get("request_timeout", 30)

        # 创建session对象，保持会话
        self.session = requests.Session()

        # 设置默认请求头
        self.default_headers = {
            "Content-Type": "application/json;charset=UTF-8",
            "Accept": "application/json, text/plain, */*",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.7871.115 Safari/537.36"
        }

        # 更新session默认请求头
        self.session.headers.update(self.default_headers)

        logger.info("API请求类初始化成功")

    def _build_url(self, endpoint):
        """
        构建完整请求URL

        Args:
            endpoint (str): API接口路径

        Returns:
            str: 完整URL
        """
        # 如果endpoint是完整URL，直接返回
        if endpoint.startswith("http://") or endpoint.startswith("https://"):
            return endpoint

        # 拼接基础URL和API路径
        base = self.base_url.rstrip("/")
        api = self.api_path.strip("/")
        end = endpoint.lstrip("/")

        if api:
            full_url = f"{base}/{api}/{end}"
        else:
            full_url = f"{base}/{end}"

        return full_url

    def _handle_response(self, response):
        """
        处理响应结果

        Args:
            response (requests.Response): 响应对象

        Returns:
            dict: 响应数据（JSON格式）
            str: 响应文本（非JSON格式）
        """
        try:
            # 尝试解析JSON响应
            response_json = response.json()
            logger.log_response(
                status_code=response.status_code,
                response_text=response.text[:500],
                response_json=response_json,
                elapsed_time=response.elapsed.total_seconds()
            )
            return response_json

        except json.JSONDecodeError:
            # 非JSON响应，返回文本
            logger.log_response(
                status_code=response.status_code,
                response_text=response.text[:500],
                elapsed_time=response.elapsed.total_seconds()
            )
            return response.text

        except Exception as e:
            logger.error(f"处理响应失败: {str(e)}", exc_info=True)
            raise

    def get(self, endpoint, params=None, headers=None, **kwargs):
        """
        发送GET请求

        Args:
            endpoint (str): API接口路径或完整URL
            params (dict): URL参数（可选）
            headers (dict): 请求头（可选），会覆盖默认请求头
            **kwargs: 其他requests参数

        Returns:
            dict/str: 响应数据
        """
        try:
            url = self._build_url(endpoint)

            # 合并请求头
            request_headers = self.default_headers.copy()
            if headers:
                request_headers.update(headers)

            # 记录请求日志
            logger.log_request(method="GET", url=url, params=params, headers=request_headers)

            # 发送请求
            response = self.session.get(
                url=url,
                params=params,
                headers=request_headers,
                timeout=self.timeout,
                **kwargs
            )

            # 返回处理后的响应
            return self._handle_response(response)

        except requests.RequestException as e:
            logger.error(f"GET请求失败: {str(e)}", exc_info=True)
            raise
        except Exception as e:
            logger.error(f"GET请求异常: {str(e)}", exc_info=True)
            raise

    def post(self, endpoint, data=None, json=None, headers=None, **kwargs):
        """
        发送POST请求

        Args:
            endpoint (str): API接口路径或完整URL
            data (dict): 表单数据（可选）
            json (dict): JSON数据（可选）
            headers (dict): 请求头（可选），会覆盖默认请求头
            **kwargs: 其他requests参数

        Returns:
            dict/str: 响应数据
        """
        try:
            url = self._build_url(endpoint)

            # 合并请求头
            request_headers = self.default_headers.copy()
            if headers:
                request_headers.update(headers)

            # 记录请求日志
            logger.log_request(method="POST", url=url, data=data or json, headers=request_headers)

            # 发送请求
            response = self.session.post(
                url=url,
                data=data,
                json=json,
                headers=request_headers,
                timeout=self.timeout,
                **kwargs
            )

            # 返回处理后的响应
            return self._handle_response(response)

        except requests.RequestException as e:
            logger.error(f"POST请求失败: {str(e)}", exc_info=True)
            raise
        except Exception as e:
            logger.error(f"POST请求异常: {str(e)}", exc_info=True)
            raise

    def put(self, endpoint, data=None, json=None, headers=None, **kwargs):
        """
        发送PUT请求

        Args:
            endpoint (str): API接口路径或完整URL
            data (dict): 表单数据（可选）
            json (dict): JSON数据（可选）
            headers (dict): 请求头（可选），会覆盖默认请求头
            **kwargs: 其他requests参数

        Returns:
            dict/str: 响应数据
        """
        try:
            url = self._build_url(endpoint)

            request_headers = self.default_headers.copy()
            if headers:
                request_headers.update(headers)

            logger.log_request(method="PUT", url=url, data=data or json, headers=request_headers)

            response = self.session.put(
                url=url,
                data=data,
                json=json,
                headers=request_headers,
                timeout=self.timeout,
                **kwargs
            )

            return self._handle_response(response)

        except requests.RequestException as e:
            logger.error(f"PUT请求失败: {str(e)}", exc_info=True)
            raise
        except Exception as e:
            logger.error(f"PUT请求异常: {str(e)}", exc_info=True)
            raise

    def delete(self, endpoint, data=None, json=None, headers=None, **kwargs):
        """
        发送DELETE请求

        Args:
            endpoint (str): API接口路径或完整URL
            data (dict): 请求体数据（可选）
            json (dict): JSON数据（可选）
            headers (dict): 请求头（可选），会覆盖默认请求头
            **kwargs: 其他requests参数

        Returns:
            dict/str: 响应数据
        """
        try:
            url = self._build_url(endpoint)

            request_headers = self.default_headers.copy()
            if headers:
                request_headers.update(headers)

            logger.log_request(method="DELETE", url=url, data=data or json, headers=request_headers)

            response = self.session.delete(
                url=url,
                data=data,
                json=json,
                headers=request_headers,
                timeout=self.timeout,
                **kwargs
            )

            return self._handle_response(response)

        except requests.RequestException as e:
            logger.error(f"DELETE请求失败: {str(e)}", exc_info=True)
            raise
        except Exception as e:
            logger.error(f"DELETE请求异常: {str(e)}", exc_info=True)
            raise

    def patch(self, endpoint, data=None, json=None, headers=None, **kwargs):
        """
        发送PATCH请求

        Args:
            endpoint (str): API接口路径或完整URL
            data (dict): 请求体数据（可选）
            json (dict): JSON数据（可选）
            headers (dict): 请求头（可选），会覆盖默认请求头
            **kwargs: 其他requests参数

        Returns:
            dict/str: 响应数据
        """
        try:
            url = self._build_url(endpoint)

            request_headers = self.default_headers.copy()
            if headers:
                request_headers.update(headers)

            logger.log_request(method="PATCH", url=url, data=data or json, headers=request_headers)

            response = self.session.patch(
                url=url,
                data=data,
                json=json,
                headers=request_headers,
                timeout=self.timeout,
                **kwargs
            )

            return self._handle_response(response)

        except requests.RequestException as e:
            logger.error(f"PATCH请求失败: {str(e)}", exc_info=True)
            raise
        except Exception as e:
            logger.error(f"PATCH请求异常: {str(e)}", exc_info=True)
            raise

    def set_token(self, token, token_type="Bearer"):
        """
        设置认证Token到请求头

        Args:
            token (str): Token值
            token_type (str): Token类型，默认为"Bearer"
        """
        try:
            auth_header = f"{token_type} {token}"
            self.session.headers.update({"Authorization": auth_header})
            logger.info(f"已设置认证Token: {token_type} {token[:20]}...")

        except Exception as e:
            logger.error(f"设置Token失败: {str(e)}", exc_info=True)
            raise

    def remove_token(self):
        """
        移除请求头中的认证Token
        """
        try:
            if "Authorization" in self.session.headers:
                del self.session.headers["Authorization"]
                logger.info("已移除认证Token")

        except Exception as e:
            logger.error(f"移除Token失败: {str(e)}", exc_info=True)
            raise

    def set_header(self, key, value):
        """
        设置单个请求头

        Args:
            key (str): 请求头键名
            value (str): 请求头值
        """
        try:
            self.session.headers.update({key: value})
            logger.info(f"已设置请求头: {key} = {value}")

        except Exception as e:
            logger.error(f"设置请求头失败: {str(e)}", exc_info=True)
            raise

    def set_headers(self, headers):
        """
        设置多个请求头

        Args:
            headers (dict): 请求头字典
        """
        try:
            self.session.headers.update(headers)
            logger.info(f"已设置请求头: {headers}")

        except Exception as e:
            logger.error(f"设置请求头失败: {str(e)}", exc_info=True)
            raise

    def get_session(self):
        """
        获取当前session对象

        Returns:
            requests.Session: session对象
        """
        return self.session

    def close_session(self):
        """
        关闭session连接
        """
        try:
            self.session.close()
            logger.info("已关闭session连接")

        except Exception as e:
            logger.error(f"关闭session失败: {str(e)}", exc_info=True)
            raise

    def reset_session(self):
        """
        重置session，创建新的session对象
        """
        try:
            self.close_session()
            self.session = requests.Session()
            self.session.headers.update(self.default_headers)
            logger.info("已重置session")

        except Exception as e:
            logger.error(f"重置session失败: {str(e)}", exc_info=True)
            raise
