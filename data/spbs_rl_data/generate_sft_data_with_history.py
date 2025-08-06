import json
import random
import pickle
import os

def init_data_recorder(filename):
    with open(filename, "rb") as f:
        loaded_dict = pickle.load(f)
    return loaded_dict


def create_sft_dataset(data_recorder, history_length=3):
    """
    Generates an SFT dataset from the building control data, with one record per timestamp.
    Each record's 'history' field contains the states and actions of the previous N timesteps.
    """
    sft_dataset = []
    num_timesteps = len(data_recorder["training"]["reward"])

    # Load system prompt
    with open("system_prompt.txt", "r") as f:
        system_prompt = f.read()
    # system_prompt = "You are an expert AI assistant for building management systems. Your task is to analyze current and historical room and outdoor sensor data to provide precise FCU fan speed control commands for each room, optimizing comfort and energy efficiency."

    room_input_keys = ["room_temp", "FCU_fan_feedback", "supply_temp", "return_temp", "occupant_num"]
    outdoor_input_key = "outdoor_temp"
    room_output_key = "FCU_fan_setpoint"

    for t in range(num_timesteps):
        # --- 1. Build the history for the current timestep 't' ---
        history_list = []
        # Iterate backwards from t-1 for N steps
        for i in range(1, history_length + 1):
            past_t = t - i
            if past_t < 0:
                break  # Stop if we've reached the beginning of the data

            # User turn for the historical data point
            past_user_turn = f"This was the situation at timestep {past_t}. What action was taken?"

            # Model turn for the historical data point (summarizing past state and action)
            past_model_turn = f"Status at timestep {past_t}:\n"
            past_model_turn += f"- Outdoor Temp: {data_recorder['sensor_outdoor'][outdoor_input_key][past_t]:.2f}°C\n"
            for r in range(1, 8):
                room_key = f"room{r}"
                room_control_key = f"room{r}_control"
                past_model_turn += (
                    f"- Room {r}: Temp={data_recorder[room_key]['room_temp'][past_t]:.2f}°C, "
                    f"Fan Speed={data_recorder[room_key]['FCU_fan_feedback'][past_t]}, "
                    f"Occupants={data_recorder[room_key]['occupant_num'][past_t]}\n"
                )
            past_model_turn += "Action taken:\n"
            for r in range(1, 8):
                room_control_key = f"room{r}_control"
                past_model_turn += f"- Room {r} Fan Setpoint: {data_recorder[room_control_key][room_output_key][past_t]}\n"

            # Prepend to history to keep chronological order (oldest first)
            history_list.insert(0, [past_user_turn, past_model_turn])

        # --- 2. Build the main input and output for the current timestep 't' ---
        # Build the input string for the current timestamp
        current_input_str = f"Timestamp index: {t} (August 9th, {9 + t // 60}:{(t % 60):02d}am/pm).\n"
        current_input_str += "Current building conditions:\n"

        # Add outdoor temperature
        current_input_str += "--- Outdoor Environment Status ---\n"
        current_input_str += f"- Outdoor Temperature: {data_recorder['sensor_outdoor'][outdoor_input_key][t]:.2f}°C\n"

        # Add room states for each room
        for r in range(1, 8):
            room_key = f"room{r}"
            current_input_str += f"--- Room {r} Status ---\n"
            for key in room_input_keys:
                value = data_recorder[room_key][key][t]
                display_name = key.replace('_', ' ').title()
                unit = "°C" if "temp" in key else ""
                current_input_str += f"- {display_name}: {value}{unit}\n" if "temp" not in key else f"- {display_name}: {value:.2f}{unit}\n"

        # Build the output string for the current timestamp (control actions)
        current_output_str = "Execute the following FCU fan speed control actions for all rooms:\n"
        for r in range(1, 8):
            room_control_key = f"room{r}_control"
            current_output_str += f"--- Room {r} FCU Fan Controls ---\n"
            current_output_str += f"- Set FCU Fan Speed: {data_recorder[room_control_key][room_output_key][t]}\n"

        # --- 3. Assemble the final SFT record ---
        sft_dataset.append({
            "instruction": "Considering the historical context and current conditions, provide the optimal FCU fan speed settings for each room.",
            "input": current_input_str,
            "output": current_output_str,
            "system": system_prompt,
            "history": history_list
        })

    return sft_dataset


# --- Main program entry point ---
if __name__ == "__main__":

    original_data_dir = "0710_data_store"
    sft_data_dir = "0710_sft_spbsrl_with_history"
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
