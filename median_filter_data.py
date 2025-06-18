import csv
import glob
import os
from collections import defaultdict
import numpy as np

class MedianFilter:
    def __init__(self, window_size=3):
        self.window_size = window_size

    def apply_median(self, values):
        if len(values) < self.window_size:
            return values

        filtered = []
        padded_values = values[:self.window_size - 1] + values  # Padding for initial values

        for i in range(len(values)):
            window = padded_values[i:i + self.window_size]
            filtered.append(np.median(window))

        return filtered

    def read_and_filter_txt(self):
        txt_files = glob.glob("Test_files_Noise/*.txt")
        output_dir = "filtered_median_test"
        os.makedirs(output_dir, exist_ok=True)

        for file in txt_files:
            mac_data = defaultdict(list)
            mac_timestamps = defaultdict(list)

            with open(file, newline='') as txtfile:
                reader = csv.reader(txtfile, delimiter="\t")
                header = next(reader)

                try:
                    ts_idx = header.index("Timestamp")
                    rf_idx = header.index("Reference Point")
                    mac_idx = header.index("Device Address")
                    name_idx = header.index("Device Name")
                    rssi_idx = header.index("RSSI")
                except ValueError as e:
                    print(f"Header error in {file}: {e}, skipping...")
                    continue

                for row in reader:
                    try:
                        mac = row[mac_idx]
                        rssi = float(row[rssi_idx])
                        timestamps = row[ts_idx]
                        mac_data[mac].append(rssi)
                        mac_timestamps[mac].append(timestamps)
                    except:
                        continue
            
            base = os.path.basename(file).replace(".txt", "")
            base = base.replace("_noise", "")
            base += "_medianfilter.txt"
            out_path = os.path.join(output_dir, base)

            with open(out_path, 'w', newline='') as out:
                writer = csv.writer(out)
                writer.writerow(["Timestamp", "Device Address", "Filtered_RSSI"])

                for mac in mac_data:
                    filtered = self.apply_median(mac_data[mac])
                    for t, r in zip(mac_timestamps[mac], filtered):
                        writer.writerow([t, mac, r])

            print(f"Median filtered saved: {out_path}")

if __name__ == "__main__":
    MedianFilter(window_size=3).read_and_filter_txt()
