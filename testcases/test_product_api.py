import pytest
from utils.yaml_util import YamlUtil
from base.AssertUtil import AssertUtil
from utils.log_util import logger


@pytest.mark.api
@pytest.mark.smoke
class TestProductAPI:
    """
    商品搜索与商品详情模块API接口测试用例
    """

    def test_search_valid_keyword_api(self, api_client):
        """
        TC_PRODUCT_SEARCH_001: 使用有效关键词搜索商品

        预期结果：
            1. 搜索接口返回code=0
            2. 返回结果中包含商品列表
            3. 商品数量大于0
        """
        logger.info("=== TC_PRODUCT_SEARCH_001: 使用有效关键词搜索商品 ===")

        api_data = YamlUtil.read_test_data("api_data.yaml")
        search_info = api_data["search_api"]

        response = api_client.post(
            endpoint=search_info["path"],
            data={"wd": search_info["valid_keyword"]}
        )

        logger.info(f"搜索响应: {response}")

        if isinstance(response, dict):
            AssertUtil.assert_response_code(
                response,
                expected_code=search_info["success_code"],
                message=f"搜索接口返回code错误：{response.get('code')}"
            )

            data = response.get("data", {})
            AssertUtil.assert_is_not_none(
                data,
                message="搜索接口未返回data"
            )

            if isinstance(data, dict):
                products = data.get("list", data.get("data", []))
            elif isinstance(data, list):
                products = data
            else:
                products = []

            AssertUtil.assert_true(
                len(products) > 0,
                message=f"搜索结果为空，关键词: {search_info['valid_keyword']}"
            )

            logger.info(f"搜索到商品数量: {len(products)}")

            if products:
                first_product = products[0]
                AssertUtil.assert_is_not_none(
                    first_product.get("id"),
                    message="商品ID为空"
                )
                AssertUtil.assert_is_not_none(
                    first_product.get("name"),
                    message="商品名称为空"
                )
        else:
            logger.info("搜索接口返回非JSON响应，验证页面包含搜索结果")
            AssertUtil.assert_true(
                isinstance(response, str) and response.find("商品") != -1,
                message="搜索页面未包含商品相关内容"
            )

        logger.info("TC_PRODUCT_SEARCH_001 测试通过")

    def test_search_no_match_keyword_api(self, api_client):
        """
        TC_PRODUCT_SEARCH_002: 使用不存在的关键词搜索商品（无结果）

        预期结果：
            1. 搜索接口返回code=0或正确的错误码
            2. 返回结果中商品列表为空或返回提示信息
        """
        logger.info("=== TC_PRODUCT_SEARCH_002: 使用不存在的关键词搜索商品 ===")

        api_data = YamlUtil.read_test_data("api_data.yaml")
        search_info = api_data["search_api"]

        response = api_client.post(
            endpoint=search_info["path"],
            data={"wd": search_info["no_match_keyword"]}
        )

        logger.info(f"无结果搜索响应: {response}")

        if isinstance(response, dict):
            code = response.get("code", -1)
            AssertUtil.assert_true(
                code == search_info["success_code"] or code >= 0,
                message=f"搜索接口返回异常code：{code}"
            )

            data = response.get("data", {})
            if isinstance(data, dict):
                products = data.get("list", data.get("data", []))
            elif isinstance(data, list):
                products = data
            else:
                products = []

            AssertUtil.assert_true(
                len(products) == 0,
                message=f"不存在的关键词搜索到了商品，数量: {len(products)}"
            )
        else:
            logger.info("搜索接口返回非JSON响应")

        logger.info("TC_PRODUCT_SEARCH_002 测试通过")

    def test_search_empty_keyword_api(self, api_client):
        """
        TC_PRODUCT_SEARCH_003: 使用空关键词搜索商品

        预期结果：
            1. 搜索接口返回code=0或正确的错误码
            2. 返回结果中包含商品列表（可能返回全部商品或提示信息）
        """
        logger.info("=== TC_PRODUCT_SEARCH_003: 使用空关键词搜索商品 ===")

        api_data = YamlUtil.read_test_data("api_data.yaml")
        search_info = api_data["search_api"]

        response = api_client.post(
            endpoint=search_info["path"],
            data={"wd": search_info["empty_keyword"]}
        )

        logger.info(f"空关键词搜索响应: {response}")

        if isinstance(response, dict):
            code = response.get("code", -1)
            AssertUtil.assert_true(
                code == search_info["success_code"] or code >= 0,
                message=f"空关键词搜索接口返回异常code：{code}"
            )
        else:
            logger.info("空关键词搜索接口返回非JSON响应")

        logger.info("TC_PRODUCT_SEARCH_003 测试通过")

    def test_product_detail_valid_id_api(self, api_client):
        """
        TC_PRODUCT_DETAIL_004: 查询有效商品详情

        预期结果：
            1. 商品详情接口返回code=0
            2. 返回结果中包含商品的完整信息
            3. 商品ID与请求一致
        """
        logger.info("=== TC_PRODUCT_DETAIL_004: 查询有效商品详情 ===")

        api_data = YamlUtil.read_test_data("api_data.yaml")
        product_info = api_data["product_api"]

        response = api_client.get(
            endpoint=product_info["detail_path"],
            params={"id": product_info["valid_product_id"]}
        )

        logger.info(f"有效商品详情响应: {response}")

        if isinstance(response, dict):
            AssertUtil.assert_response_code(
                response,
                expected_code=product_info["success_code"],
                message=f"商品详情接口返回code错误：{response.get('code')}"
            )

            data = response.get("data", {})
            AssertUtil.assert_is_not_none(
                data,
                message="商品详情接口未返回data"
            )

            if isinstance(data, dict):
                product_id = data.get("id", data.get("goods_id"))
                AssertUtil.assert_equal(
                    str(product_id),
                    str(product_info["valid_product_id"]),
                    message=f"商品ID不一致：期望{product_info['valid_product_id']}，实际{product_id}"
                )

                AssertUtil.assert_is_not_none(
                    data.get("name"),
                    message="商品名称为空"
                )

                price = data.get("price", data.get("goods_price"))
                AssertUtil.assert_is_not_none(
                    price,
                    message="商品价格为空"
                )
        else:
            logger.info("商品详情接口返回非JSON响应")

        logger.info("TC_PRODUCT_DETAIL_004 测试通过")

    def test_product_detail_invalid_id_api(self, api_client):
        """
        TC_PRODUCT_DETAIL_005: 查询无效商品ID详情

        预期结果：
            1. 商品详情接口返回错误code
            2. 返回提示信息表示商品不存在
        """
        logger.info("=== TC_PRODUCT_DETAIL_005: 查询无效商品ID详情 ===")

        api_data = YamlUtil.read_test_data("api_data.yaml")
        product_info = api_data["product_api"]

        response = api_client.get(
            endpoint=product_info["detail_path"],
            params={"id": product_info["invalid_product_id"]}
        )

        logger.info(f"无效商品ID详情响应: {response}")

        if isinstance(response, dict):
            code = response.get("code", -1)
            AssertUtil.assert_true(
                code != product_info["success_code"],
                message=f"无效商品ID不应返回成功code：{code}"
            )

            msg = response.get("msg", "")
            AssertUtil.assert_true(
                len(msg) > 0,
                message="无效商品ID查询未返回错误信息"
            )
        else:
            logger.info("无效商品ID查询返回非JSON响应")

        logger.info("TC_PRODUCT_DETAIL_005 测试通过")

    def test_product_detail_fields_api(self, api_client):
        """
        TC_PRODUCT_DETAIL_006: 查询商品详情验证关键字段完整性

        预期结果：
            1. 商品详情接口返回code=0
            2. 返回结果中包含商品的所有关键字段（名称、价格、库存、描述等）
        """
        logger.info("=== TC_PRODUCT_DETAIL_006: 查询商品详情验证关键字段完整性 ===")

        api_data = YamlUtil.read_test_data("api_data.yaml")
        product_info = api_data["product_api"]

        response = api_client.get(
            endpoint=product_info["detail_path"],
            params={"id": product_info["valid_product_id"]}
        )

        logger.info(f"商品详情字段验证响应: {response}")

        if isinstance(response, dict):
            AssertUtil.assert_response_code(
                response,
                expected_code=product_info["success_code"],
                message=f"商品详情接口返回code错误：{response.get('code')}"
            )

            data = response.get("data", {})
            AssertUtil.assert_is_not_none(
                data,
                message="商品详情接口未返回data"
            )

            if isinstance(data, dict):
                required_fields = ["name", "price"]
                optional_fields = ["goods_id", "id", "image", "stock", "description", "spec"]

                for field in required_fields:
                    field_value = data.get(field)
                    if field_value is None:
                        field_value = data.get(field.replace("price", "goods_price"))
                    AssertUtil.assert_is_not_none(
                        field_value,
                        message=f"商品详情缺少必填字段: {field}"
                    )

                found_optional = False
                for field in optional_fields:
                    if data.get(field) is not None:
                        found_optional = True
                        break

                AssertUtil.assert_true(
                    found_optional,
                    message="商品详情缺少可选字段"
                )
        else:
            logger.info("商品详情接口返回非JSON响应")

        logger.info("TC_PRODUCT_DETAIL_006 测试通过")

    def test_search_and_detail_consistency_api(self, api_client):
        """
        TC_PRODUCT_SEARCH_007: 搜索结果与商品详情一致性校验

        预期结果：
            1. 搜索结果中的商品信息与商品详情接口返回的信息一致
            2. 验证商品名称、价格等关键信息的一致性
        """
        logger.info("=== TC_PRODUCT_SEARCH_007: 搜索结果与商品详情一致性校验 ===")

        api_data = YamlUtil.read_test_data("api_data.yaml")
        search_info = api_data["search_api"]
        product_info = api_data["product_api"]

        response = api_client.post(
            endpoint=search_info["path"],
            data={"wd": search_info["valid_keyword"]}
        )

        logger.info(f"搜索响应: {response}")

        products = []
        if isinstance(response, dict):
            AssertUtil.assert_response_code(
                response,
                expected_code=search_info["success_code"],
                message=f"搜索接口返回code错误：{response.get('code')}"
            )

            data = response.get("data", {})
            if isinstance(data, dict):
                products = data.get("list", data.get("data", []))
            elif isinstance(data, list):
                products = data
        else:
            logger.info("搜索接口返回非JSON响应，跳过一致性校验")
            logger.info("TC_PRODUCT_SEARCH_007 测试通过")
            return

        AssertUtil.assert_true(
            len(products) > 0,
            message="搜索结果为空，无法进行一致性校验"
        )

        first_product = products[0]
        search_product_id = first_product.get("id") or first_product.get("goods_id")

        if search_product_id:
            detail_response = api_client.get(
                endpoint=product_info["detail_path"],
                params={"id": search_product_id}
            )

            logger.info(f"商品详情响应: {detail_response}")

            if isinstance(detail_response, dict):
                detail_data = detail_response.get("data", {})
                if isinstance(detail_data, dict):
                    detail_product_name = detail_data.get("name", "")
                    search_product_name = first_product.get("name", "")

                    if search_product_name and detail_product_name:
                        AssertUtil.assert_true(
                            search_product_name in detail_product_name or
                            detail_product_name in search_product_name,
                            message=f"商品名称不一致：搜索结果'{search_product_name}'，详情页'{detail_product_name}'"
                        )

        logger.info("TC_PRODUCT_SEARCH_007 测试通过")