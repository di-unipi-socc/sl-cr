import json
from pathlib import Path

import pandas as pd


def merge_ray_tune_results(root_dir: str, prefix: str = "sl_cr_grid_") -> pd.DataFrame:
    """
    Merges results from multiple Ray Tune grid search runs into a single DataFrame.

    Args:
        root_dir (str): Root directory containing subdirectories with Ray Tune results.
        output_file (str): Path to save the merged Parquet file.
    """
    root_path = Path(root_dir)
    experiment_dirs = [
        subdir
        for subdir in root_path.iterdir()
        if subdir.is_dir() and subdir.name.startswith(prefix)
    ]

    all_data = []
    tot_processed = 0
    tot_skipped = 0
    i = 0
    for exp in experiment_dirs:
        try:
            i += 1
            infr_csv_path = exp / "output" / "csv" / "infrastructure.csv"
            params_path = exp / "params.json"

            if not infr_csv_path.exists():
                print(f"Skipping {exp}: infrastructure.csv not found")
                tot_skipped += 1
                continue  # Skip if infrastructure.csv is missing (experiment not ended)

            df = pd.read_csv(infr_csv_path)

            if params_path.exists():
                with open(params_path, "r", encoding="utf-8") as f:
                    params = json.load(f)
                    for key, value in params.items():
                        df[key] = value

            all_data.append(df)
            print(
                f"Processed {i}/{tot_processed}",
                end=("\r" if i < tot_processed else "\n"),
                flush=True,
            )
            tot_processed += 1
        except Exception as e:
            print(f"Error processing {exp}: {e}")
            tot_skipped += 1

    print(f"Processed: {tot_processed}, Skipped: {tot_skipped}")
    df = pd.concat(all_data, ignore_index=True)
    return df


def clean_and_dump(df: pd.DataFrame, output_file: Path = "results.parquet"):

    df.to_parquet(output_file, index=False)
    print(f"Successfully saved merged results to {output_file}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Merge Ray Tune results into a single Parquet file."
    )
    parser.add_argument(
        "-r",
        "--root_dir",
        type=str,
        default="../results",
        help="Root directory containing experiment subdirectories.",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="results.parquet",
        help="Output Parquet file path.",
    )
    parser.add_argument(
        "-p",
        "--prefix",
        type=str,
        default="sl_cr_grid_",
        help="Prefix for experiment directories.",
    )

    args = parser.parse_args()

    df = merge_ray_tune_results(args.root_dir, args.prefix)
    if not df.empty:
        clean_and_dump(df, args.output)
    else:
        print(f"No results found in {args.root_dir}")
