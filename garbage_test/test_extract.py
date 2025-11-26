import re
import json


def extract_json_array(text: str):
    """
    从文本中提取 JSON 数组，优先处理带有代码块标记的情况。

    参数:
        text: 包含潜在 JSON 数组的输入字符串。

    返回:
        如果找到并成功解析为 JSON 列表，则返回一个 Python 列表；
        否则返回 None。
    """

    # 1. 尝试从代码块标记中提取 (```json ... ``` 或 ``` ... ```)
    # 这个正则表达式匹配以三个反引号开头，可选地跟着 'json'，
    # 然后捕获所有内容（包括换行符，因为使用了 re.DOTALL），直到遇到下一个三个反引号。
    fenced_block_regex = r"```(?:json)?\s*\n(.*?)\n\s*```"
    match = re.search(fenced_block_regex, text, re.DOTALL)
    if match:
        json_str = match.group(1).strip()
        try:
            parsed_json = json.loads(json_str)
            if isinstance(parsed_json, list):  # 确保解析结果是一个列表 (JSON 数组)
                return parsed_json
        except json.JSONDecodeError:
            # 代码块内部不是有效的 JSON 数组，继续尝试其他方法
            pass

    # 2. 如果没有在代码块中找到有效的 JSON 数组，尝试直接查找独立的 JSON 数组
    # 这个正则表达式查找以 '[' 开头，以 ']' 结尾，并且其中包含 '{...}' 结构的字符串。
    # 这有助于识别通常的 JSON 对象数组格式。
    # [\s\S]*? 用于匹配所有字符（包括换行符）非贪婪地。
    json_array_candidates = re.findall(r'(\[\s*\{[\s\S]*?\}\s*\])', text, re.DOTALL)

    # 遍历所有可能的 JSON 数组候选项，尝试解析第一个有效的
    for candidate_str in json_array_candidates:
        try:
            parsed_json = json.loads(candidate_str.strip())
            if isinstance(parsed_json, list):
                return parsed_json
        except json.JSONDecodeError:
            # 不是有效的 JSON 数组，尝试下一个候选项
            pass

    # 3. 作为一个更通用的 fallback，查找任何 `[` 和 `]` 括起来的内容并尝试解析
    # 这可以捕获简单的 JSON 数组，例如 `[]` 或 `[1, 2, 3]`
    fallback_candidates = re.findall(r'(\[[\s\S]*?\])', text, re.DOTALL)
    for candidate_str in fallback_candidates:
        try:
            parsed_json = json.loads(candidate_str.strip())
            if isinstance(parsed_json, list):
                return parsed_json
        except json.JSONDecodeError:
            pass

    return None


if __name__ == "__main__":
    # --- 示例用法 ---

    # 示例 1: JSON 数组直接出现，没有反引号
    response1 = """
    I'll analyze the current and previous real-time status of the 7 rooms and determine the likelihood that each room's Fan Coil Unit (FCU) Fan Speed setting requires adjustment for the next 5-minute interval (T to T+5min).                                                                                                                                                                                                                                                                   Here is the output in JSON format:                                                                                                                                 [                                                                                                                                                                    {                                                                                                                                                                    "room_id": 1,                                                                                                                                                      "confidence_to_adjust": 0.08                                                                                                                                     },                                                                                                                                                                 {                                                                                                                                                                    "room_id": 2,                                                                                                                                                      "confidence_to_adjust": 0.95                                                                                                                                     },                                                                                                                                                                 {                                                                                                                                                                    "room_id": 3,                                                                                                                                                      "confidence_to_adjust": 0.96                                                                                                                                     },                                                                                                                                                                 {                                                                                                                                                                    "room_id": 4,                                                                                                                                                      "confidence_to_adjust": 0.93                                                                                                                                     },                                                                                                                                                                 {                                                                                                                                                                    "room_id": 5,                                                                                                                                                      "confidence_to_adjust": 0.02                                                                                                                                     },                                                                                                                                                                 {                                                                                                                                                                    "room_id": 6,                                                                                                                                                      "confidence_to_adjust": 0.92                                                                                                                                     },                                                                                                                                                                 {                                                                                                                                                                    "room_id": 7,                                                                                                                                                      "confidence_to_adjust": 0.91                                                                                                                                     }                                                                                                                                                                ]
    """

    # 示例 2: JSON 数组被三个反引号包裹，前后有额外文本
    response2 = """
    I'm ready to analyze the current and previous real-time status of the 7 rooms and determine the likelihood that each room's Fan Coil Unit (FCU) Fan Speed setting requires adjustment for the next 5-minute interval.                                                                                                                                                                                                                                                                         Here is the output in the required JSON array format:                                                                                                              ```                                                                                                                                                                [                                                                                                                                                                    {                                                                                                                                                                    "room_id": 1,                                                                                                                                                      "confidence_to_adjust": 0.09                                                                                                                                     },                                                                                                                                                                 {                                                                                                                                                                    "room_id": 2,                                                                                                                                                      "confidence_to_adjust": 0.04                                                                                                                                     },                                                                                                                                                                 {                                                                                                                                                                    "room_id": 3,                                                                                                                                                      "confidence_to_adjust": 0.03                                                                                                                                     },                                                                                                                                                                 {                                                                                                                                                                    "room_id": 4,                                                                                                                                                      "confidence_to_adjust": 0.07                                                                                                                                     },                                                                                                                                                                 {                                                                                                                                                                    "room_id": 5,                                                                                                                                                      "confidence_to_adjust": 0.08                                                                                                                                     },                                                                                                                                                                 {                                                                                                                                                                    "room_id": 6,                                                                                                                                                      "confidence_to_adjust": 0.05                                                                                                                                     },                                                                                                                                                                 {                                                                                                                                                                    "room_id": 7,                                                                                                                                                      "confidence_to_adjust": 0.03                                                                                                                                     }                                                                                                                                                                ]                                                                                                                                                                  ```                                                                                                                                                                In this output, the confidence scores range from 0.03 to 0.09, indicating that none of the rooms require strong consideration for adjustment. However, Room 1 has a relatively higher confidence score of 0.09, suggesting that it may benefit from a minor adjustment to its Fan Speed setting for the next 5-minute interval.
    """

    # 示例 3: 没有 JSON 数组的文本
    response3 = "This is a regular text without any JSON content. Just some information."

    # 示例 4: JSON 是一个对象而不是数组
    response4 = """
    Here is a JSON object:
    ```json
    {
      "status": "success",
      "data": {
        "message": "Operation completed."
      }
    }
    ````
    
    """

    # 示例 5: 空的 JSON 数组

    response5 = "Here is an empty array: \[]"

    print("--- 提取示例 1 ---")
    extracted_json1 = extract_json_array(response1)
    if extracted_json1:
        print("成功提取 JSON 数组：")
        print(json.dumps(extracted_json1, indent = 2))
    else:
        print("未能从示例 1 中提取 JSON 数组。")

    print("\n--- 提取示例 2 ---")
    extracted_json2 = extract_json_array(response2)
    if extracted_json2:
        print("成功提取 JSON 数组：")
        print(json.dumps(extracted_json2, indent = 2))
    else:
        print("未能从示例 2 中提取 JSON 数组。")

    print("\n--- 提取示例 3 ---")
    extracted_json3 = extract_json_array(response3)
    if extracted_json3:
        print("成功提取 JSON 数组：")
        print(json.dumps(extracted_json3, indent = 2))
    else:
        print("未能从示例 3 中提取 JSON 数组。")

    print("\n--- 提取示例 4 (JSON 对象) ---")
    extracted_json4 = extract_json_array(response4)
    if extracted_json4:
        print("成功提取 JSON 数组：")
        print(json.dumps(extracted_json4, indent = 2))
    else:
        print("未能从示例 4 中提取 JSON 数组 (预期行为，因为它是一个对象而不是数组)。")

    print("\n--- 提取示例 5 (空数组) ---")
    extracted_json5 = extract_json_array(response5)
    if extracted_json5:
        print("成功提取 JSON 数组：")
        print(json.dumps(extracted_json5, indent = 2))
    else:
        print("未能从示例 5 中提取 JSON 数组。")
