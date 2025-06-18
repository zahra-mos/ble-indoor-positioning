# make_fp_db.py
import os
import csv
import pandas as pd
from collections import defaultdict

# Path to raw RSSI data
RAW_PATH = "Ref_files"
METADATA_FILE = r"CSV\New_RF1.csv"

# Load metadata
metadata = pd.read_csv(METADATA_FILE)

def build_fingerprint_db(rssi_dir, output_file):
    fingerprint_rows = []
    all_macs = set()

    for _, row in metadata.iterrows():
        rp_id = row['ID']
        x = row['X']
        y = row['Y']
        file_name = row['File']

        # Only RAW data is used
        full_path = os.path.join(rssi_dir, f"{file_name}.txt")
        delimiter = '\t'

        if not os.path.isfile(full_path):
            print(f"Missing file: {full_path}, skipping...")
            continue

        mac_rssi = defaultdict(list)

        with open(full_path, newline='') as f:
            reader = csv.DictReader(f, delimiter=delimiter)
            for line in reader:
                mac = line.get('Device Address')
                rssi = line.get('RSSI')

                if mac and rssi:
                    try:
                        mac_rssi[mac].append(float(rssi))
                    except ValueError:
                        continue

        if not mac_rssi:
            print(f"No valid RSSI data in {full_path}")
            continue

        averaged_rssi = {mac: sum(vals) / len(vals) for mac, vals in mac_rssi.items()}
        all_macs.update(averaged_rssi.keys())
        averaged_rssi.update({'RP_ID': rp_id, 'X': x, 'Y': y})
        fingerprint_rows.append(averaged_rssi)

    all_macs_sorted = sorted(all_macs)
    fieldnames = ['RP_ID', 'X', 'Y'] + all_macs_sorted

    with open(output_file, 'w', newline='') as out:
        writer = csv.DictWriter(out, fieldnames=fieldnames)
        writer.writeheader()
        for row in fingerprint_rows:
            writer.writerow({key: row.get(key, -100) for key in fieldnames})

    return output_file

# Generate fingerprint database using only raw data
raw_fp = build_fingerprint_db(RAW_PATH, "fingerprints_raw.csv")
print(f"Fingerprint database created: {raw_fp}")
