import os
import pandas as pd
import numpy as np

# Define paths
input_folder = "Test_files"
output_folder = "Test_files_Noise"

# Create the output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)


# Function to add Gaussian noise to RSSI values
def add_noise_to_rssi(df, noise_level=100, round_decimals=0, rssi_min=-100, rssi_max=-30):
    df = df.copy()
    if 'RSSI' in df.columns:
        noise = np.random.normal(0, noise_level, size=len(df))
        df['RSSI'] = df['RSSI'] + noise
        df['RSSI'] = df['RSSI'].clip(lower=rssi_min, upper=rssi_max)
        df['RSSI'] = df['RSSI'].round(round_decimals)
    return df

"""def add_noise_to_rssi(df, noise_range=(-50, 50)):
    df.copy()
    if 'RSSI' in df.columns:
        noise = np.random.randint(noise_range[0], noise_range[1] + 1, size=len(df))
        df['RSSI'] = df['RSSI'] + noise
    return df"""

# Process each file in the input folder
for filename in os.listdir(input_folder):
    if filename.endswith(".txt") or filename.endswith(".csv"):
        input_path = os.path.join(input_folder, filename)
        base_filename = os.path.splitext(filename)[0]
        output_path = os.path.join(output_folder, base_filename + "_noise.txt")

        # Read the file
        try:
            df = pd.read_csv(input_path, sep='\t', engine='python')
        except:
            df = pd.read_csv(input_path)

        # Add noise
        noisy_df = add_noise_to_rssi(df)

        # Save to output folder
        noisy_df.to_csv(output_path, index=False, sep='\t')

output_folder

