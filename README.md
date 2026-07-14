# ShopXO 自动化测试框架

## 环境准备

### 1. Python环境
- Python 3.8+
- 建议使用虚拟环境

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. Chrome浏览器
- 版本：150.0.7871.115

### 4. 驱动配置
- 本地驱动路径：`D:\BcTool\Pycharm\Driver\chromedriver-win64\chromedriver.exe`
- 或使用 webdriver-manager 自动下载（配置文件中可切换模式）

## 执行命令

### 运行所有测试用例
```bash
pytest
```

### 指定用例执行
```bash
pytest testcases/test_example.py
```

### 生成Allure报告

#### 第一步：执行测试并生成原始数据
```bash
pytest --alluredir=report/allure_raw
```

#### 第二步：生成HTML报告
```bash
allure generate report/allure_raw -o report/allure_html --clean
```

#### 第三步：打开报告
```bash
allure serve report/allure_raw
```

## 项目结构

```
shopxo_auto_test/
├── conf/              # 配置文件
├── base/              # 基础封装（无业务逻辑）
├── utils/             # 通用工具类（无业务逻辑）
├── data/              # 测试数据（留白）
├── testcases/         # 测试用例（留白）
├── report/            # 测试报告
├── logs/              # 日志文件
├── page/              # 页面类（留白）
├── conftest.py        # 全局夹具
├── pytest.ini         # pytest配置
└── requirements.txt   # 依赖清单
```

## 框架说明

- **base层**：提供WebDriver基础操作、API请求封装、断言工具，无业务逻辑
- **utils层**：提供路径处理、配置读取、日志记录、截图工具，无业务逻辑
- **conf层**：环境配置、浏览器配置，通过YAML文件管理
- **data层**：测试数据占位，需手动补充业务测试数据
- **page层**：页面类占位，需手动编写业务页面封装
- **testcases层**：测试用例占位，需手动编写业务测试用例
