#!/usr/bin/env python3
"""
Parse zql_eval.py log files and extract success rate information.

Extracts success information from log files in the format:
  behavior_log_{repeat}_{instance_index}.log

Produces a table showing success rates for each instance across all trials.
"""

import re
import sys
from pathlib import Path
from collections import defaultdict


def parse_log_file(log_path: Path) -> dict | None:
    """Parse a single log file and extract success information.
    
    Returns:
        dict with keys: 'success_trials', 'total_trials', 'success_rate', 'repeat', 'instance'
        or None if the file couldn't be parsed
    """
    try:
        with open(log_path, "r") as f:
            content = f.read()
        
        # Extract repeat and instance from filename
        match = re.search(r"behavior_log_(\d+)_(\d+)\.log", log_path.name)
        if not match:
            return None
        repeat = int(match.group(1))
        instance = int(match.group(2))
        
        # Look for success information lines
        success_trials_match = re.search(r"Total success trials:\s*(\d+)", content)
        total_trials_match = re.search(r"Total trials:\s*(\d+)", content)
        success_rate_match = re.search(r"Success rate:\s*([\d.]+)", content)
        
        if not (success_trials_match and total_trials_match and success_rate_match):
            return None
        
        return {
            "repeat": repeat,
            "instance": instance,
            "success_trials": int(success_trials_match.group(1)),
            "total_trials": int(total_trials_match.group(1)),
            "success_rate": float(success_rate_match.group(1)),
        }
    except Exception as e:
        print(f"Error parsing {log_path}: {e}", file=sys.stderr)
        return None


def main():
    log_dir = Path("/mnt/public/quanlu")
    
    # Find all log files matching the pattern
    log_files = sorted(log_dir.glob("behavior_log_*.log"))
    
    if not log_files:
        print(f"No log files found in {log_dir}", file=sys.stderr)
        sys.exit(1)
    
    # Parse all log files
    results = []
    for log_file in log_files:
        result = parse_log_file(log_file)
        if result:
            results.append(result)
    
    if not results:
        print("No valid results found in log files", file=sys.stderr)
        sys.exit(1)
    
    # Group by instance ID
    by_instance = defaultdict(list)
    for result in results:
        by_instance[result["instance"]].append(result)
    
    # Sort instances
    sorted_instances = sorted(by_instance.keys())
    
    # Print table header
    print("\n" + "=" * 80)
    print("ZQL Evaluation Results Summary")
    print("=" * 80)
    print(f"\n{'Instance':<10} {'Repeat':<8} {'Success':<10} {'Total':<8} {'Rate':<10} {'Status':<10}")
    print("-" * 80)
    
    # Print results for each instance
    for instance in sorted_instances:
        instance_results = sorted(by_instance[instance], key=lambda x: x["repeat"])
        for result in instance_results:
            status = "✓ SUCCESS" if result["success_rate"] > 0 else "✗ FAILED"
            print(
                f"{instance:<10} "
                f"{result['repeat']:<8} "
                f"{result['success_trials']:<10} "
                f"{result['total_trials']:<8} "
                f"{result['success_rate']:<10.2f} "
                f"{status:<10}"
            )
    
    # Print summary statistics
    print("\n" + "-" * 80)
    print("Summary Statistics:")
    print("-" * 80)
    
    total_success = sum(r["success_trials"] for r in results)
    total_trials = sum(r["total_trials"] for r in results)
    overall_rate = (total_success / total_trials * 100) if total_trials > 0 else 0.0
    
    # Per-instance summary
    print(f"\nPer-Instance Summary:")
    for instance in sorted_instances:
        instance_results = by_instance[instance]
        inst_success = sum(r["success_trials"] for r in instance_results)
        inst_total = sum(r["total_trials"] for r in instance_results)
        inst_rate = (inst_success / inst_total * 100) if inst_total > 0 else 0.0
        print(f"  Instance {instance}: {inst_success}/{inst_total} ({inst_rate:.1f}%)")
    
    print(f"\nOverall: {total_success}/{total_trials} ({overall_rate:.1f}%)")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()

