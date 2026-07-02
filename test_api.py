"""测试图集速查 API 功能"""
import requests

BASE_URL = "http://localhost:8000"

def test_categories():
    """测试获取分类列表"""
    print("\n=== 测试 1: 获取分类列表 ===")
    response = requests.get(f"{BASE_URL}/api/v1/specification/categories")
    print(f"状态码：{response.status_code}")
    print(f"响应：{response.json()}")
    return response.json()

def test_by_category(category: str):
    """测试按分类获取条文"""
    print(f"\n=== 测试 2: 按分类获取条文 (category={category}) ===")
    response = requests.get(f"{BASE_URL}/api/v1/specification/by-category", params={"category": category})
    print(f"状态码：{response.status_code}")
    result = response.json()
    print(f"条文数量：{result.get('count', 0)}")
    for spec in result.get("specifications", []):
        print(f"  - {spec['id']}: {spec['title']}")
    return result

def test_detail(spec_id: str):
    """测试获取条文详情"""
    print(f"\n=== 测试 3: 获取条文详情 (id={spec_id}) ===")
    response = requests.get(f"{BASE_URL}/api/v1/specification/detail/{spec_id}")
    print(f"状态码：{response.status_code}")
    result = response.json()
    print(f"条文号：{result.get('clause_number')}")
    print(f"标题：{result.get('title')}")
    print(f"分类：{result.get('category')}")
    print(f"内容 HTML (前 100 字符): {result.get('content_html', '')[:100]}...")
    return result

def test_search(keyword: str):
    """测试搜索条文"""
    print(f"\n=== 测试 4: 搜索条文 (keyword={keyword}) ===")
    response = requests.get(f"{BASE_URL}/api/v1/specification/search", params={"keyword": keyword})
    print(f"状态码：{response.status_code}")
    result = response.json()
    print(f"搜索结果数量：{result.get('count', 0)}")
    for spec in result.get("results", []):
        print(f"  - {spec['id']}: {spec['title']}")
    return result

if __name__ == "__main__":
    try:
        # 测试 1: 获取分类列表
        categories_result = test_categories()

        # 测试 2: 按分类获取条文
        if "categories" in categories_result and len(categories_result["categories"]) > 0:
            for category in categories_result["categories"]:
                test_by_category(category)

        # 测试 3: 获取条文详情
        test_detail("spec-beam-notation")
        test_detail("spec-column-longitudinal")
        test_detail("spec-anchor-general")

        # 测试 4: 搜索条文
        test_search("锚固")
        test_search("梁")

        print("\n=== 所有测试完成 ===")
    except Exception as e:
        print(f"测试失败：{e}")
