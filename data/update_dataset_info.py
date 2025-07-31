import os
import json
import re
import argparse
from collections import OrderedDict


def generate_dataset_entries(directory, base_path):
    """
    扫描目录，为每个匹配的json文件生成条目。

    Args:
        directory (str): 要扫描的包含json文件的目录。
        base_path (str): 在生成的json中，用作文件路径前缀的字符串。

    Returns:
        dict: 一个包含新生成条目的字典。
    """
    # 正则表达式，用于从文件名中提取算法名称和种子编号
    # 例如: 0429_..._A2C_seed1.json -> 提取 "A2C" 和 "1"
    pattern = re.compile(r'_([A-Z0-9]+)_seed(\d+)\.json$')

    new_entries = {}
    print(f"🔍 正在扫描目录: {directory}")

    # 遍历目录中的所有文件
    for filename in sorted(os.listdir(directory)):
        if filename.endswith('.json'):
            match = pattern.search(filename)
            if match:
                # 提取算法和种子ID
                algo = match.group(1)
                seed = match.group(2)

                # 构建唯一的键，例如 "A2C_seed1"
                unique_key = f"{algo}_seed{seed}"

                # 构建文件路径值，使用 os.path.join 保证路径分隔符正确
                # 在Windows上会是 \，在Linux上会是 /
                file_path_value = os.path.join(base_path, filename).replace("\\", "/")  # 保证输出为 a/b/c 格式

                # 创建条目
                new_entries[unique_key] = {"file_name": file_path_value}
                print(f"  ✅ 匹配成功: {filename} -> {unique_key}")
            else:
                print(f"  ⚠️  跳过文件 (格式不匹配): {filename}")

    return new_entries


def main():
    """主函数，用于解析命令行参数并执行更新逻辑。"""
    parser = argparse.ArgumentParser(
        description="自动扫描目录中的JSON文件，并更新或创建 dataset_info.json 文件。",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        '-d', '--directory',
        required=True,
        help="包含源JSON文件的目标目录。\n例如: /path/to/your/json_files"
    )
    parser.add_argument(
        '-b', '--base_path',
        required=True,
        help="在输出的JSON文件中，为每个文件路径指定的前缀。\n例如: spbs_rl_data/0710_sft_spbsrl"
    )
    parser.add_argument(
        '-o', '--output_file',
        default='dataset_info.json',
        help="要更新或创建的输出JSON文件的路径。\n(默认为: dataset_info.json)"
    )

    args = parser.parse_args()

    # 1. 如果输出文件存在，则读取现有数据
    existing_data = OrderedDict()
    if os.path.exists(args.output_file):
        try:
            with open(args.output_file, 'r', encoding='utf-8') as f:
                existing_data = json.load(f, object_pairs_hook=OrderedDict)
            print(f"📖 已成功读取现有文件: {args.output_file}")
        except json.JSONDecodeError:
            print(f"🚨 错误: 现有文件 {args.output_file} 不是一个有效的JSON文件。脚本将中断。")
            return
    else:
        print(f"ℹ️  输出文件 {args.output_file} 不存在，将创建新文件。")

    # 2. 从目标目录生成新的条目
    new_entries = generate_dataset_entries(args.directory, args.base_path)

    if not new_entries:
        print("🔚 在指定目录中未找到匹配的JSON文件。未做任何更改。")
        return

    # 3. 合并数据：将新条目添加到现有数据中（如果键已存在，则会覆盖）
    existing_data.update(new_entries)

    # 4. 将合并后的数据写回文件
    try:
        with open(args.output_file, 'w', encoding='utf-8') as f:
            # indent=2 使JSON文件格式化，易于阅读
            # ensure_ascii=False 保证中文字符正常显示
            json.dump(existing_data, f, indent=2, ensure_ascii=False)
        print(f"\n🎉 成功! 数据已写入到: {args.output_file}")
    except IOError as e:
        print(f"🚨 错误: 无法写入文件 {args.output_file}。错误信息: {e}")


if __name__ == '__main__':
    main()
