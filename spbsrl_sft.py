import os
import time

base_model_path = "/data/zhongdianyu/models/Meta-Llama-3-8B-Instruct"
# data_set_path = "data/spbs_rl_data/0710_sft_spbsrl"
output_path = "./saves/LLaMA3-8B/lora/sft/spbs_rl"


data_set_str = "A2C_seed1,A2C_seed2,A2C_seed3," + \
               "BDQ_seed1,BDQ_seed2,BDQ_seed3," + \
               "HGQN_seed1,HGQN_seed2,HGQN_seed3," + \
               "PPO_seed1,PPO_seed3,PPO_seed3 "

print(data_set_str)
print("\n")

cmd_line = f"CUDA_VISIBLE_DEVICES=0 " \
           f"llamafactory-cli train " \
           f"--stage sft " \
           f"--do_train " \
           f"--model_name_or_path {base_model_path} " \
           f"--dataset {data_set_str} " \
           f"--dataset_dir ./data " \
           f"--template llama3 " \
           f"--finetuning_type lora " \
           f"--output_dir {output_path} " \
           f"--overwrite_cache " \
           f"--overwrite_output_dir " \
           f"--cutoff_len 1024 " \
           f"--preprocessing_num_workers 16 " \
           f"--per_device_train_batch_size 2 " \
           f"--per_device_eval_batch_size 1 " \
           f"--gradient_accumulation_steps 8 " \
           f"--lr_scheduler_type cosine " \
           f"--logging_steps 50 " \
           f"--warmup_steps 20 " \
           f"--save_steps 100 " \
           f"--eval_steps 50 " \
           f"--eval_strategy steps " \
           f"--load_best_model_at_end " \
           f"--learning_rate 5e-5 " \
           f"--num_train_epochs 5.0 " \
           f"--max_samples 1000 " \
           f"--val_size 0.1 " \
           f"--plot_loss " \
           f"--fp16"

print(cmd_line)
os.system(cmd_line)