import os
import csv
import cv2 # type: ignore
import pandas as pd
import numpy as np
from collections import defaultdict
from math import sqrt
import time


K= 3
image_path = "./image/New_RPs.png"
# Paths for test metadata CSVs
TEST_METADATA_FILES = {
    "Raw": "CSV/test_raw.csv",
    "Median": "CSV/test_median.csv",
    "Kalman": "CSV/test_kalman.csv"
}

FINGERPRINT_FILES = {
    "Raw": "fingerprints_raw.csv",
    "Median": "fingerprints_raw.csv",
    "Kalman": "fingerprints_raw.csv"
}

TEST_FOLDERS = {
    "Raw": "Test_files_Noise",
    "Median": "filtered_median_test",
    "Kalman": "filtered_kalman_test"
}



def load_fingerprint_db(path):
    return pd.read_csv(path)

def load_test_data(file_path):
    mac_rssi = defaultdict(list)
    delimiter = '\t' if 'Test_files' in file_path or file_path.endswith("RS1.txt") else ','

    try:
        with open(file_path, newline='') as f:
            reader = csv.DictReader(f, delimiter=delimiter)
            for line in reader:
                try:
                    mac = line.get('Device Address')
                    rssi = float(line.get('Filtered_RSSI') or line.get('RSSI'))
                    mac_rssi[mac].append(rssi)
                except (ValueError, TypeError):
                    continue
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return {}

    if not mac_rssi:
        print(f"No valid RSSI data in {file_path}")
    averaged = {mac: np.mean(rssis) for mac, rssis in mac_rssi.items()}
    return averaged

def knn_predict(test_sample, fingerprint_df, k=K):
    distances = []
    for _, row in fingerprint_df.iterrows():
        ref_map = {mac: row[mac] for mac in fingerprint_df.columns[3:] if pd.notna(row[mac])}
        common_macs = set(test_sample.keys()) & set(ref_map.keys())
        if not common_macs:
            continue
        diff_sq = [(test_sample[mac] - ref_map[mac])**2 for mac in common_macs]
        dist = sqrt(sum(diff_sq) / len(common_macs))
        distances.append((dist, row['X'], row['Y']))

    if not distances:
        return None, None

    distances.sort(key=lambda x: x[0])
    top_k = distances[:k]

    weighted_sum_x = 0
    weighted_sum_y = 0
    total_weight = 0
    for dist, x, y in top_k:
        weight = 1 / (dist + 1e-6)
        weighted_sum_x += x * weight
        weighted_sum_y += y * weight
        total_weight += weight

    if total_weight > 0:
        return weighted_sum_x / total_weight, weighted_sum_y / total_weight
    else:
        return None, None

def evaluate(fingerprint_db, test_meta_df, label, test_folder, suffix=""):
    errors = []
    total_time = 0
    predictions = 0

    for _, row in test_meta_df.iterrows():
        test_file = os.path.join(test_folder, f"{row['File']}.txt")
        if not os.path.exists(test_file):
            print(f"Missing test file: {test_file}")
            continue

        test_rssi = load_test_data(test_file)
        if not test_rssi:
            continue

        start_time = time.time()
        pred_x, pred_y = knn_predict(test_rssi, fingerprint_db, K)
        total_time += time.time() - start_time

        if pred_x is None:
            continue

        true_x, true_y = row['X'], row['Y']
        error = sqrt((pred_x - true_x) ** 2 + (pred_y - true_y) ** 2)
        errors.append(error)
        predictions += 1

    print(f"\n== {label.upper()} Results ==")
    if errors:
        mean_latency = (total_time / predictions) * 1000
        throughput = predictions / total_time
        print(f"Mean Error: {np.mean(errors):.2f} units")
        print(f"Std Dev Error: {np.std(errors):.2f} units")
        print(f"Mean Latency: {mean_latency:.2f} ms")
        print(f"Throughput: {throughput:.2f} samples/sec")
    else:
        print("No valid test predictions made.")
        mean_latency = 0
        throughput = 0

    return errors, mean_latency, throughput

def visualize_predictions(fingerprint_dbs, test_metadata_dfs, test_folders, background_img_path=image_path, k= K):
    img = cv2.imread(background_img_path)
    if img is None:
        print("Failed to load background image.")
        return

    vis_img = img.copy()
    colors = {
        "Raw": (0, 0, 255),
        "Median": (255, 0, 0),
        "Kalman": (0, 165, 255),
        "GT": (0, 255, 0)
    }

    for label in ["Raw", "Median", "Kalman"]:
        df = test_metadata_dfs[label]
        db = fingerprint_dbs[label]
        test_folder = test_folders[label]

        for _, row in df.iterrows():
            true_x, true_y = int(row['X']), int(row['Y'])
            cv2.circle(vis_img, (true_x, true_y), 6, colors["GT"], -1)
            cv2.putText(vis_img, "GT", (true_x + 5, true_y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, colors["GT"], 1)

            test_file = os.path.join(test_folder, f"{row['File']}.txt")
            if not os.path.exists(test_file):
                continue
            test_rssi = load_test_data(test_file)
            if not test_rssi:
                continue
            pred_x, pred_y = knn_predict(test_rssi, db, k)
            if pred_x is None:
                continue
            pred_x, pred_y = int(pred_x), int(pred_y)
            cv2.circle(vis_img, (pred_x, pred_y), 6, colors[label], -1)
            cv2.line(vis_img, (true_x, true_y), (pred_x, pred_y), colors[label], 1)
            cv2.putText(vis_img, label[0], (pred_x + 5, pred_y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, colors[label], 1)

    cv2.imwrite("prediction_visualization.png", vis_img)
    cv2.imshow("Predictions", vis_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def log_results_to_csv(results, output_file="knn_error_results.csv"):
    file_exists = os.path.isfile(output_file)
    with open(output_file, mode='a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["k", "method", "mean_error", "std_error", "latency_ms", "throughput"])
        if not file_exists:
            writer.writeheader()
        for result in results:
            writer.writerow(result)

def main():
    fingerprint_dbs = {label: load_fingerprint_db(fp_file) for label, fp_file in FINGERPRINT_FILES.items()}
    test_metadata = {label: pd.read_csv(meta_file) for label, meta_file in TEST_METADATA_FILES.items()}

    results_summary = []

    for label in ["Raw", "Median", "Kalman"]:
        suffix = "" if label == "Raw" else ("_medianfilter" if label == "Median" else "_filtered")
        errors, latency, throughput = evaluate(
            fingerprint_dbs[label],
            test_metadata[label],
            label,
            TEST_FOLDERS[label],
            suffix=suffix
        )
        results_summary.append({
            "k": K,
            "method": label,
            "mean_error": np.mean(errors) if errors else 0,
            "std_error": np.std(errors) if errors else 0,
            "latency_ms": latency,
            "throughput": throughput
        })

    log_results_to_csv(results_summary)
    visualize_predictions(fingerprint_dbs, test_metadata, TEST_FOLDERS)

if __name__ == "__main__":
    main()

