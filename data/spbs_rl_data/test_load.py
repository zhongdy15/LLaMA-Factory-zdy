import pickle

filename = "0710_data_store/0429_Baseline_OCC_PPD_with_energy_const10_A2C_seed1.pkl"

with open(filename, "rb") as f:
        loaded_dict = pickle.load(f)

print(loaded_dict.keys())