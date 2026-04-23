"""
测试Property API是否能正确返回IfcProject的属性
"""

import requests
import json
from openrouter.settings import settings

def test_property_api():
    """测试IFC Property API"""

    print(f"\n{'='*80}")
    print(f"Testing IFC Property API")
    print(f"{'='*80}\n")

    # API配置
    url = settings.ifc_entity_pset_api_url
    print(f"API URL: {url}\n")

    # 测试查询
    test_cases = [
        {
            "entityName": "IfcProject",
            "schemaVersions": ["IFC4"]
        },
        {
            "entityName": "IfcWall",
            "schemaVersions": ["IFC4"]
        }
    ]

    for i, params in enumerate(test_cases, 1):
        print(f"\n{'='*80}")
        print(f"Test Case {i}: {params['entityName']}")
        print(f"{'='*80}\n")

        try:
            response = requests.post(url, json=params, timeout=10)
            response.raise_for_status()
            result = response.json()

            if result:
                print(f"✓ API返回成功")
                print(f"  返回的IFC版本数: {len(result)}")

                for version, psets in result.items():
                    print(f"\n  IFC版本: {version}")
                    print(f"  属性集数量: {len(psets)}")

                    if psets:
                        print(f"\n  前3个属性集:")
                        for j, pset in enumerate(psets[:3], 1):
                            pset_name = pset.get("name", "Unknown")
                            props = pset.get("properties", [])
                            print(f"    {j}. {pset_name} ({len(props)} properties)")

                            if props:
                                print(f"       前5个属性:")
                                for k, prop in enumerate(props[:5], 1):
                                    prop_name = prop.get("name", "Unknown")
                                    prop_def = prop.get("definition", "")[:60]
                                    print(f"         {k}. {prop_name}: {prop_def}...")
            else:
                print(f"✗ API返回空结果")

        except requests.exceptions.ConnectionError as e:
            print(f"✗ 连接错误: {e}")
        except requests.exceptions.Timeout:
            print(f"✗ 请求超时")
        except requests.exceptions.RequestException as e:
            print(f"✗ 请求失败: {e}")
        except Exception as e:
            print(f"✗ 未知错误: {e}")

    print(f"\n{'='*80}")
    print(f"Test completed")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    test_property_api()
