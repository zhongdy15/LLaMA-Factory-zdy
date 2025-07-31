import json
import random
import pickle
import os

def init_data_recorder(filename):
    with open(filename, "rb") as f:
        loaded_dict = pickle.load(f)
    return loaded_dict


# def create_sft_dataset(data_recorder):
#     """
#     Converts the raw building control data into the format required for LLM fine-tuning.
#
#     Args:
#         data_recorder (dict): A dictionary containing all building control time-series data.
#
#     Returns:
#         list: A list of dictionaries, where each dictionary is a fine-tuning data point.
#     """
#     sft_dataset = []
#     num_samples = len(data_recorder["sensor_outdoor"]["outdoor_temp"])
#
#     # Define a unified system prompt and instruction for the dataset
#     system_prompt = "You are a professional Building Management System AI assistant. " \
#                     "Your task is to provide precise and energy-efficient HVAC control commands based on the current indoor and outdoor environmental status and occupant information."
#     instruction = "Based on the room status information provided below, generate the next HVAC control command for this room. " \
#                   "Ensure the command maintains a comfortable indoor environment while conserving energy. " \
#                   "The returned command must be in JSON format."
#
#     # Iterate over each room
#     for r in range(1, 8):
#         room_key = f"room{r}"
#         room_control_key = f"room{r}_control"
#
#         # Iterate over each time step
#         for t in range(num_samples):
#             # 1. Construct user input (input)
#             # Format the state data for this time step into a natural language description
#             current_state_input = (
#                 f"Current Status Assessment:\n"
#                 f"- **Room ID**: {r}\n"
#                 f"- **Indoor Temperature**: {data_recorder[room_key]['room_temp'][t]:.1f}°C\n"
#                 f"- **Indoor Relative Humidity**: {data_recorder[room_key]['room_RH'][t]:.1f}%\n"
#                 f"- **Number of Occupants**: {data_recorder[room_key]['occupant_num'][t]}\n"
#                 f"- **Outdoor Temperature**: {data_recorder['sensor_outdoor']['outdoor_temp'][t]:.1f}°C"
#             )
#
#             # 2. Construct model answer (output)
#             # Format the control data for this time step into a JSON string
#             # Convert numerical codes into more understandable text descriptions
#             fcu_onoff_action = "ON" if data_recorder[room_control_key]['FCU_onoff_setpoint'][t] == 1 else "OFF"
#             fcu_fan_speed_action = data_recorder[room_control_key]['FCU_fan_setpoint'][t]
#
#             target_output_dict = {
#                 "description": f"HVAC control command for Room {r}.",
#                 "controls": {
#                     "temperature_setpoint_celsius": data_recorder[room_control_key]['roomtemp_setpoint'][t],
#                     "fcu_power_command": fcu_onoff_action,
#                     "fcu_fan_speed_level": fcu_fan_speed_action
#                 }
#             }
#             # Use json.dumps to ensure correct formatting
#             target_output_json = json.dumps(target_output_dict, indent=2)
#
#             # 3. Assemble into the final data point format
#             sft_datapoint = {
#                 "instruction": instruction,
#                 "input": current_state_input,
#                 "output": target_output_json,
#                 "system": system_prompt,
#                 "history": []  # History is not needed in this scenario
#             }
#
#             sft_dataset.append(sft_datapoint)
#
#     return sft_dataset
def create_sft_dataset(data_recorder):
    """
    Generates an SFT dataset from the building control data, with one record per timestamp,
    containing consolidated state and action for all rooms and central plant.
    """
    sft_dataset = []
    num_timesteps = len(data_recorder["training"]["reward"])

    system_prompt = "You are an expert AI assistant for building management systems. Your task is to analyze comprehensive building sensor data and provide precise control commands for all HVAC components to optimize comfort and energy efficiency."

    for t in range(num_timesteps):
        # Build the input string for the current timestamp
        current_input_str = f"Timestamp index: {t} (August 9th, {9 + t // 60}:{(t % 60):02d}am/pm).\n"
        current_input_str += "Current comprehensive building status:\n"

        # Add room states
        for r in range(1, 8):
            room_key = f"room{r}"
            current_input_str += f"--- Room {r} Status ---\n"
            current_input_str += f"- Room Temperature: {data_recorder[room_key]['room_temp'][t]:.2f}°C\n"
            current_input_str += f"- Room Relative Humidity: {data_recorder[room_key]['room_RH'][t]:.2f}%\n"
            current_input_str += f"- Occupant Count: {data_recorder[room_key]['occupant_num'][t]}\n"
            current_input_str += f"- FCU On/Off Feedback: {'On' if data_recorder[room_key]['FCU_onoff_feedback'][t] else 'Off'}\n"
            current_input_str += f"- FCU Fan Speed Feedback: {data_recorder[room_key]['FCU_fan_feedback'][t]}\n"
            current_input_str += f"- FCU Water Valve Feedback: {data_recorder[room_key]['valve_feedback'][t]:.2f}%\n"
            current_input_str += f"- FCU Power Consumption: {data_recorder[room_key]['FCU_power'][t]:.2f} W\n"
            current_input_str += f"- Room Heat Load: {data_recorder[room_key]['room_Qload'][t]:.2f} W\n"

        # Add outdoor sensor data
        current_input_str += "--- Outdoor Environment Status ---\n"
        current_input_str += f"- Outdoor Temperature: {data_recorder['sensor_outdoor']['outdoor_temp'][t]:.2f}°C\n"
        current_input_str += f"- Outdoor Relative Humidity: {data_recorder['sensor_outdoor']['outdoor_damp'][t]:.2f}%\n"

        # Add pump data
        current_input_str += "--- Central Pump (Pump 1) Status ---\n"
        current_input_str += f"- Pump On/Off Feedback: {'On' if data_recorder['pump1']['pump_onoff_feedback'][t] else 'Off'}\n"
        current_input_str += f"- Pump Frequency Feedback: {data_recorder['pump1']['pump_frequency_feedback'][t]:.2f} Hz\n"
        current_input_str += f"- Pump Water Flow: {data_recorder['pump1']['pump_flow'][t]:.2f} m³/h\n"
        current_input_str += f"- Pump Supply Pressure: {data_recorder['pump1']['pump_supplypressure'][t]:.2f} kPa\n"

        # Add heat pump data
        current_input_str += "--- Heat Pump Status ---\n"
        current_input_str += f"- Heat Pump On/Off Feedback: {'On' if data_recorder['heatpump']['heatpump_onoff_feedback'][t] else 'Off'}\n"
        current_input_str += f"- Heat Pump Supply Temperature Feedback: {data_recorder['heatpump']['heatpump_supplytemp_feedback'][t]:.2f}°C\n"
        current_input_str += f"- Heat Pump Working Mode: {data_recorder['heatpump']['heatpump_workingmode_feedback'][t]}\n"
        current_input_str += f"- Heat Pump Alarm Status: {data_recorder['heatpump']['heatpump_alarm'][t]}\n"

        # # Add pipe network (simplified)
        # current_input_str += "--- Pipe Network Status (Simplified) ---\n"
        # current_input_str += f"- Node Pressure: {data_recorder['pipe_net']['node_pressure'][t]:.2f} kPa\n"
        # current_input_str += f"- Branch Flow: {data_recorder['pipe_net']['branch_flow'][t]:.2f} m³/h\n"

        # Add training metrics (for context)
        current_input_str += "--- Overall Performance Metrics ---\n"
        current_input_str += f"- Reward: {data_recorder['training']['reward'][t]:.3f}\n"
        current_input_str += f"- Temperature Bias: {data_recorder['training']['temperature_bias'][t]:.2f}°C\n"
        current_input_str += f"- Energy Consumption: {data_recorder['training']['energy_consumption'][t]:.2f} kWh\n"
        current_input_str += f"- Mean PMV: {data_recorder['training']['mean_pmv'][t]:.2f}\n"
        current_input_str += f"- Mean PPD: {data_recorder['training']['mean_ppd'][t]:.2f}%\n"

        # Build the output string for the current timestamp (control actions)
        current_output_str = "Execute the following comprehensive control actions for the building:\n"

        # Add room control actions
        for r in range(1, 8):
            room_control_key = f"room{r}_control"
            current_output_str += f"--- Room {r} Controls ---\n"
            current_output_str += f"- Set Room Temperature: {data_recorder[room_control_key]['roomtemp_setpoint'][t]:.2f}°C\n"
            current_output_str += f"- Set Room Relative Humidity: {data_recorder[room_control_key]['roomRH_setpoint'][t]:.2f}%\n"
            current_output_str += f"- Set FCU On/Off: {'On' if data_recorder[room_control_key]['FCU_onoff_setpoint'][t] else 'Off'}\n"
            current_output_str += f"- Set FCU Fan Speed: {data_recorder[room_control_key]['FCU_fan_setpoint'][t]}\n"
            current_output_str += f"- Set FCU Working Mode: {data_recorder[room_control_key]['FCU_workingmode_setpoint'][t]}\n"
            current_output_str += f"- Set FCU Water Valve Opening: {data_recorder[room_control_key]['valve_setpoint'][t]:.2f}%\n"

        # Add pump control actions
        current_output_str += "--- Central Pump (Pump 1) Controls ---\n"
        current_output_str += f"- Set Pump On/Off: {'On' if data_recorder['pump1_control']['pump_onoff_setpoint'][t] else 'Off'}\n"
        current_output_str += f"- Set Pump Frequency: {data_recorder['pump1_control']['pump_frequency_setpoint'][t]:.2f} Hz\n"
        current_output_str += f"- Set Pump Valve: {data_recorder['pump1_control']['pump_valve_setpoint'][t]:.2f}%\n"

        # Add heat pump control actions
        current_output_str += "--- Heat Pump Controls ---\n"
        current_output_str += f"- Set Heat Pump On/Off: {'On' if data_recorder['heatpump_control']['heatpump_onoff_setpoint'][t] else 'Off'}\n"
        current_output_str += f"- Set Heat Pump Supply Temperature: {data_recorder['heatpump_control']['heatpump_supplytemp_setpoint'][t]:.2f}°C\n"
        current_output_str += f"- Set Heat Pump Working Mode: {data_recorder['heatpump_control']['heatpump_workingmode_setpoint'][t]}\n"

        sft_dataset.append({
            "instruction": "Based on the current building status, provide a comprehensive control strategy for all HVAC systems.",
            "input": current_input_str,
            "output": current_output_str,
            "system": system_prompt,
            "history": []
        })

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
