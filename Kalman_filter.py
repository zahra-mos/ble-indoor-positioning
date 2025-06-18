import csv
import glob
import os
import numpy as np
from collections import defaultdict
import matplotlib.pyplot as plt  # Optional, for visualization

class KalmanFilter:
    def __init__(self):
        pass  # We'll dynamically set Q and R in apply_kalman

    def apply_kalman(self, values, Q=None, R=None, visualize=False):
        if not values:
            return [] 

        values = np.array(values)
        values = values[~np.isnan(values)]

        if len(values) == 0:
            return []
        
        signar_var = np.var(values) if len(values) > 1 else 1.0

        Q = 0.1 
        R = 10000

        # Initialization
        init_values = values[:5] if len(values) >= 5 else values
        x = np.mean(init_values)
        P = np.var(init_values) if len(init_values) > 1 else 1.0

        A = H = 1.0
        result = []

        for z in values:
            x_pred = A * x
            P_pred = A * P * A + Q

            K = P_pred * H / (H * P_pred * H + R)

            x = x_pred + K * (z - H * x_pred)
            P = (1 - K * H) * P_pred

            result.append(x)

        if visualize:
            plt.figure(figsize=(8, 3))
            plt.plot(values, label="Raw RSSI", alpha=0.5)
            plt.plot(result, label="Kalman Filtered", linewidth=2)
            plt.title("Kalman Filter Output")
            plt.xlabel("Sample Index")
            plt.ylabel("RSSI")
            plt.grid(True)
            plt.legend()
            plt.tight_layout()
            plt.show()

        return result

    def read_and_filter_txt(self):
        txt_files = glob.glob("Test_files_Noise/*.txt")
        output_dir = "filtered_kalman_test"
        os.makedirs(output_dir, exist_ok=True)

        for file in txt_files:
            mac_data = defaultdict(list)
            mac_timestamps = defaultdict(list)

            with open(file, newline='') as txtfile:
                reader = csv.reader(txtfile, delimiter="\t")
                header = next(reader)

                try:
                    ts_idx = header.index("Timestamp")
                    mac_idx = header.index("Device Address")
                    rssi_idx = header.index("RSSI")
                except ValueError:
                    print(f"Header error in {file}, skipping...")
                    continue

                for row in reader:
                    try:
                        mac = row[mac_idx]
                        rssi = float(row[rssi_idx])
                        timestamp = row[ts_idx]
                        mac_data[mac].append(rssi)
                        mac_timestamps[mac].append(timestamp)
                    except:
                        continue

            base = os.path.basename(file).replace(".txt", "")
            base = base.replace("_noise", "")
            base += "_filtered.txt"
            out_path = os.path.join(output_dir, base)

            with open(out_path, 'w', newline='') as out:
                writer = csv.writer(out)
                writer.writerow(["Timestamp", "Device Address", "Filtered_RSSI"])

                for mac in mac_data:
                    filtered = self.apply_kalman(mac_data[mac])
                    for t, r in zip(mac_timestamps[mac], filtered):
                        writer.writerow([t, mac, r])

            print(f"Kalman filtered saved: {out_path}")

if __name__ == "__main__":
    KalmanFilter().read_and_filter_txt()