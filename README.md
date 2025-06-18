# BLE-Based Indoor Positioning Framework using KNN and Signal Filtering

This repository contains the full code and data used for the thesis **"BLE-Based Efficient Indoor Positioning Framework for Healthcare"**. The project explores indoor localization using Bluetooth Low Energy (BLE) RSSI fingerprinting and K-Nearest Neighbors (KNN) algorithms, incorporating signal filtering techniques (raw, median, and Kalman) to improve accuracy.

## 📘 Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [How to Run](#how-to-run)
- [Key Features](#key-features)
- [Contact](#contact)

## 🔍 Overview

Indoor positioning is essential in environments such as hospitals and elderly care homes, where GPS is unreliable. This project leverages BLE beacons, RSSI fingerprinting, and machine learning to estimate positions accurately indoors.

Key components:
- RSSI data collection and fingerprinting
- Signal filtering (raw, median, Kalman)
- KNN-based localization and performance evaluation

## 📁 Project Structure

.
├── Ref_files/ # Fingerprint data (raw, median, Kalman)
├── Test_files/ # RSSI logs for testing
├── CSV/ # Ground-truth coordinates (test metadata)
├── images/ # Floorplan and visualizations
├── knn_error_results.csv # Localization error metrics
├── KNN_Algorithms.py # Main KNN localization script
├── kalman_filter.py # Kalman filtering function
├── median_filter.py # Median filtering function
├── add_noise.py # Functions to inject Gaussian/Uniform noise
├── make_fb_db.py # Creates fingerprint database
├── fingerprints_raw.py # Generates raw fingerprints
├── README.md # Project documentation


## 📦 Requirements

- Python 3.8+
- pandas  
- numpy  
- matplotlib  
- opencv-python  
- glob  
- os  
- csv  
- collections  

Install dependencies using:

pip install -r requirements.txt

## ▶️ How to Run
Clone the repository:

git clone https://github.com/zahra-mos/ble-indoor-positioning.git
cd ble-indoor-positioning
Run the scripts in the following order:


python add_noise.py
python kalman_filter.py
python median_filter.py
python KNN_Algorithms.py
Outputs include predicted positions, visualization images, and localization error metrics in knn_error_results.csv.

## ✨ Key Features
Compare raw, median-filtered, and Kalman-filtered RSSI
Custom KNN-based localization
Visualization of predictions on a floorplan
Mean and standard deviation of localization errors
Simulated noise injection for robustness testing

## 📫 Contact
Author: Zahra Mosavi and Divine Ezeilo
GitHub: @zahra-mos, Divine-Nelson
Email:divineezeilo123@gmail.com, zahra.mos2003@gmail.com
Thesis Supervisor: Ali Hassan Sudhro.

Feel free to open issues or pull requests with questions or contributions.
