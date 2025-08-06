import re
import numpy as np
import json

def parse_llm_response_to_array(response_text: str) -> list[int]:
    """
    Parses the natural language response from an LLM to extract FCU fan speed
    setpoints and returns them as a list of integers.

    This function uses regular expressions to find all occurrences of the fan speed
    setting command.

    Args:
        response_text: The string output from the language model.

    Returns:
        A list of integers representing the fan speed control values for each room.
        Returns an empty list if no matches are found.
    """
    # The regex pattern looks for the literal string "Set FCU Fan Speed: "
    # and then captures one or more digits (\d+) that follow.
    # The `re.findall` function returns a list of all captured groups.
    pattern = r"Set FCU Fan Speed: (\d+)"

    # Find all matches of the pattern in the input text
    matches = re.findall(pattern, response_text)

    # Convert the list of string matches (e.g., ['2', '2', '1']) to a list of integers
    control_array = [int(match) for match in matches]

    return control_array

# --- Example Usage ---
if __name__ == "__main__":
    # with open("./0710_sft_spbsrl/0429_Baseline_OCC_PPD_with_energy_const10_A2C_seed1.json") as f:
    #     dic = json.load(f)[100]   # <── fixed: load JSON and take first element
    # llm_output_string = dic["output"]
    llm_output_string = "Execute the following FCU fan speed control actions for all rooms: \n --- Room 1 FCU Fan Controls ---\n- Set FCU Fan Speed: 2\n--- Room 2 FCU Fan Controls ---\n- Set FCU Fan Speed: 2\n--- Room 3 FCU Fan Controls ---\n- Set FCU Fan Speed: 1\n--- Room 4 FCU Fan Controls ---\n- Set FCU Fan Speed: 0\n--- Room 5 FCU Fan Controls ---\n- Set FCU Fan Speed: 0\n--- Room 6 FCU Fan Controls ---\n- Set FCU Fan Speed: 1\n--- Room 7 FCU Fan Controls ---\n- Set FCU Fan Speed: 1"

    print("--- Using Regular Expressions (Recommended Method) ---")
    # Call the function to parse the string
    fan_speed_commands = parse_llm_response_to_array(llm_output_string)

    # Print the results
    print(f"Original LLM Response:\n{llm_output_string}")
    print(f"Parsed Control Array (Python List): {fan_speed_commands}")

    # You can easily convert this list to a NumPy array if needed for further calculations
    fan_speed_numpy_array = np.array(fan_speed_commands)
    print(f"Parsed Control Array (NumPy Array): {fan_speed_numpy_array}")

    # Example of accessing a specific command
    if len(fan_speed_commands) > 2:
        print(f"\nThe command for Room 3 is: {fan_speed_commands[2]}") # Accessing by index (0-based)
