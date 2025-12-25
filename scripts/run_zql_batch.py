#!/usr/bin/env python3
"""
Run zql_eval.py repeatedly across instance indices and outer repeats.

- Inner loop: --instance_index i for i in [0, 9], log_path=/mnt/public/quanlu/behavior_log_{i}
- Outer loop: repeat the above 4 times (total 40 executions).
"""

import os
import subprocess
import sys


def main():
    zql_eval_path = "/opt/BEHAVIOR-1K/OmniGibson/omnigibson/learning/zql_eval.py"
    base_args = [
        "policy=websocket",
        "task.name=turning_on_radio",
        "env_wrapper._target_=behavior.learning.wrappers.RGBWrapper",
    ]
    outer_repeats = 4
    # instance_range = range(10)
    instance_range = range(10, 19)

    # Set CUDA_VISIBLE_DEVICES environment variable
    env = os.environ.copy()
    env["CUDA_VISIBLE_DEVICES"] = "0"

    for repeat in range(outer_repeats):
        print(f"[run_zql_batch] Repeat {repeat + 1}/{outer_repeats}")
        for i in instance_range:
            log_path = f"/mnt/public/quanlu/behavior_log_{repeat}_{i}"
            log_file = f"/mnt/public/quanlu/behavior_log_{repeat}_{i}.log"
            cmd = [
                sys.executable,
                zql_eval_path,
                f"--instance_index",
                str(i),
                *base_args,
                f"log_path={log_path}",
            ]
            print(f"[run_zql_batch] Running: CUDA_VISIBLE_DEVICES=0 {' '.join(cmd)}")
            print(f"[run_zql_batch] Logging to: {log_file}")
            with open(log_file, "w") as f:
                result = subprocess.run(
                    cmd,
                    env=env,
                    stdout=f,
                    stderr=subprocess.STDOUT,  # Combine stderr into stdout
                )
            if result.returncode != 0:
                print(f"[run_zql_batch] Command failed with code {result.returncode}, aborting.")
                print(f"[run_zql_batch] Check log file: {log_file}")
                sys.exit(result.returncode)


if __name__ == "__main__":
    main()

