import json
import random
import pickle
import os

def init_data_recorder(filename):
    with open(filename, "rb") as f:
        loaded_dict = pickle.load(f)
    return loaded_dict

# ------------------------------------------------------------------
# 新增：外部函数，负责生成单条 SFT 样本
# ------------------------------------------------------------------
def build_single_record(t, recorder, in_keys, outdoor_input_key, out_key, sys_prompt):
    """根据时间步 t 生成一条 SFT 样本"""
    # 构造输入字符串
    input_str = f"Timestamp index: {t} (August 9th, {9 + t // 60}:{(t % 60):02d}am/pm).\n"
    input_str += "Current building conditions:\n"

    # 室外温度
    input_str += "--- Outdoor Environment Status ---\n"
    temp = recorder["sensor_outdoor"].get(outdoor_input_key, [None] * (t + 1))[t]
    input_str += f"- Outdoor Temperature: {temp:.2f}°C\n" if temp is not None else "- Outdoor Temperature: N/A\n"

    # 各房间状态
    for r in range(1, 8):
        room_key = f"room{r}"
        input_str += f"--- Room {r} Status ---\n"
        for k in in_keys:
            val = recorder[room_key].get(k, [None] * (t + 1))[t]
            name = k.replace('_', ' ').title()
            if val is None:
                input_str += f"- {name}: N/A\n"
            elif "temp" in k:
                input_str += f"- {name}: {val:.2f}°C\n"
            else:
                input_str += f"- {name}: {val}\n"

    # 构造输出字符串
    output_str = "Execute the following FCU fan speed control actions for all rooms:\n"
    for r in range(1, 8):
        ctrl_key = f"room{r}_control"
        val = recorder[ctrl_key].get(out_key, [None] * (t + 1))[t]
        output_str += f"--- Room {r} FCU Fan Controls ---\n"
        output_str += f"- Set FCU Fan Speed: {val}\n" if val is not None else "- Set FCU Fan Speed: N/A\n"

    return {
        "instruction": "Provide the optimal FCU fan speed settings for each room based on the current room temperatures, FCU feedback, occupant numbers, and outdoor temperature.",
        "input": input_str,
        "output": output_str,
        "system": sys_prompt,
        "history": []
    }


def create_sft_dataset(data_recorder):
    """
    Generates an SFT dataset from the building control data, with one record per timestamp,
    containing consolidated state and action for all rooms based on the specified keys.
    """
    sft_dataset = []
    num_timesteps = len(data_recorder["training"]["reward"])  # Assuming training data exists for timesteps

    # Load system prompt
    with open("system_prompt.txt", "r") as f:
        system_prompt = f.read()

    # Define the specific keys to be included in the input and output
    room_input_keys = [
        "room_temp",  # Room temperature
        "FCU_fan_feedback",  # FCU fan speed feedback
        "supply_temp",  # FCU supply water temperature
        "return_temp",  # FCU return water temperature
        "occupant_num",  # Number of occupants
    ]
    outdoor_input_key = "outdoor_temp"  # Only outdoor temperature
    room_output_key = "FCU_fan_setpoint"  # Only FCU fan setpoint


    # ------------------------------------------------------------------
    # 主循环：调用外部函数收集结果
    # ------------------------------------------------------------------
    for t in range(num_timesteps):
        sft_dataset.append(
            build_single_record(
                t,
                data_recorder,
                room_input_keys,
                outdoor_input_key,
                room_output_key,
                system_prompt
            )
        )



    return sft_dataset


# --- Main program entry point ---
if __name__ == "__main__":

    original_data_dir = "0710_data_store"
    sft_data_dir = "0710_sft_spbsrl"
    if not os.path.exists(sft_data_dir):
        os.makedirs(sft_data_dir)

    # Get all files and directories in the path
    all_entries = os.listdir(original_data_dir)

    # Filter for files that end with .pkl
    pkl_files = [file for file in all_entries if file.endswith('.pkl')]

    # Print the results
    print(f"Found .pkl files in '{original_data_dir}':")
    for filename in pkl_files:
        filepath = os.path.join(original_data_dir,filename)
        my_data_recorder = init_data_recorder(filepath)

        # 3. Create the SFT fine-tuning dataset
        print("\nConverting data to SFT format...")
        fine_tuning_dataset = create_sft_dataset(my_data_recorder)
        print("Data conversion complete.")

        # 4. Print some samples to verify the result
        print(f"\nSuccessfully generated {len(fine_tuning_dataset)} fine-tuning data entries.")
        print("\n--- Dataset Samples (First 2) ---\n")
        for i in range(2):
            print(json.dumps(fine_tuning_dataset[i], indent=2))
            print("\n" + "=" * 50 + "\n")

        # 5. Save the dataset to a file
        output_filename = os.path.join(sft_data_dir ,filename.split(".pkl")[0] + ".json")
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(fine_tuning_dataset, f, indent=2)
        print(f"Dataset has been saved to file: {output_filename}")
