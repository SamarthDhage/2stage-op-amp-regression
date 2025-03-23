import os
import re
import csv
import time
import subprocess
import numpy as np

# Set LTspice Path
LTSPICE_PATH = r"C:\Program Files\LTC\LTspiceXVII\XVIIx64.exe"

# File Paths
NETLIST_FILE = "D:\\jupyter\\Practice\\VLSI\\python\\two_stage_opamp_copy.net"
MODIFIED_NETLIST_FILE = "two_stage_opamp_modified.net"
LOG_FILE = "two_stage_opamp_modified.log"
CSV_FILE = "two_stage_opamp_results.csv"
MOSFET_CSV_FILE = "mosfet_parameters.csv"

# Define random parameter sweep ranges
NUM_SAMPLES = 10  # Limit total simulations

W1_values = np.random.uniform(2e-6, 24e-6, NUM_SAMPLES)
W3_values = np.random.uniform(3e-6, 28e-6, NUM_SAMPLES)
W5_values = np.random.uniform(2e-6, 24e-6, NUM_SAMPLES)
W7_values = np.random.uniform(32e-6, 360e-6, NUM_SAMPLES)
W8_values = np.random.uniform(14e-6, 150e-6, NUM_SAMPLES)

L1_values = np.random.uniform(180e-9, 2e-6, NUM_SAMPLES)
L3_values = np.random.uniform(180e-9, 2e-6, NUM_SAMPLES)
L5_values = np.random.uniform(180e-9, 2e-6, NUM_SAMPLES)
L7_values = np.random.uniform(180e-9, 2e-6, NUM_SAMPLES)
L8_values = np.random.uniform(180e-9, 2e-6, NUM_SAMPLES)

IB_values = np.random.uniform(10e-6, 30e-6, NUM_SAMPLES)
CC_values = np.random.uniform(0.44e-12, 2.99e-12, NUM_SAMPLES)




# Function to modify .net file
def modify_ltspice_netlist(W1, L1, W3, L3, W5, L5, W7, L7, W8, L8, IB, CC):
    with open(NETLIST_FILE, "r") as file:
        netlist_text = file.read()

    # Replace parameters
    replacements = {
        "{W1}": f"{W1}", "{L1}": f"{L1}",
        "{W3}": f"{W3}", "{L3}": f"{L3}",
        "{W5}": f"{W5}", "{L5}": f"{L5}",
        "{W7}": f"{W7}", "{L7}": f"{L7}",
        "{W8}": f"{W8}", "{L8}": f"{L8}",
        "{IB}": f"{IB}", "{CC}": f"{CC}"
    }

    for key, val in replacements.items():
        netlist_text = netlist_text.replace(key, val)

    with open(MODIFIED_NETLIST_FILE, "w") as file:
        file.write(netlist_text)

# Function to run LTspice
def run_ltspice():
    cmd = f'"{LTSPICE_PATH}" -b {MODIFIED_NETLIST_FILE}'
    subprocess.run(cmd, shell=True)
    
    start_time = time.time()
    while not os.path.exists(LOG_FILE):
        if time.time() - start_time > 10:
            print("Error: LTspice log file not found.")
            return False
        time.sleep(1)
    return True

# Function to extract results from LTspice log
def extract_ltspice_log():
    with open(LOG_FILE, "r") as file:
        log_data = file.read()
    
    gain_match = re.search(r"gain:\s.*?\(([\d.]+)dB,([\d.]+)°\)", log_data)
    # Extract UGBW
    ugbw_match = re.search(r"ugbw:\s.*?AT\s([\d.e+]+)", log_data)
    # Extract phase margin (PM) in dB and degrees
    pm_match = re.search(r"pm:\s.*?\(([\d.]+)dB,([\d.-]+)°\)", log_data)
    
    gain = float(gain_match.group(1)) if gain_match else None
    gain_phase = float(gain_match.group(2)) if gain_match else None
    ugbw = float(ugbw_match.group(1)) if ugbw_match else None
    pm_db = float(pm_match.group(1)) if pm_match else None
    pm_ph = float(pm_match.group(2)) if pm_match else None
    
    return [gain, gain_phase, ugbw, pm_db, pm_ph]



# Create CSV and run parameter sweep
with open(CSV_FILE, "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["W1", "L1", "W3", "L3", "W5", "L5", "W7", "L7", "W8", "L8", "IB", "CC", "Gain", "Gain_Phase", "UGBW", "PM_db", "PM_PH"])
    
    for i in range(NUM_SAMPLES):
        W1, L1 = W1_values[i], L1_values[i]
        W3, L3 = W3_values[i], L3_values[i]
        W5, L5 = W5_values[i], L5_values[i]
        W7, L7 = W7_values[i], L7_values[i]
        W8, L8 = W8_values[i], L8_values[i]
        IB, CC = IB_values[i], CC_values[i]
        
        print(f"Running simulation {i+1}/{NUM_SAMPLES}...")
        modify_ltspice_netlist(W1, L1, W3, L3, W5, L5, W7, L7, W8, L8, IB, CC)
        
        if run_ltspice():
            results = extract_ltspice_log()
            writer.writerow([W1, L1, W3, L3, W5, L5, W7, L7, W8, L8, IB, CC] + results)
        else:
            print("Skipping due to simulation error.")
