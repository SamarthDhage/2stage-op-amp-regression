import os
import re
import csv
import time
import shutil
import subprocess
import numpy as np

# ✅ Set LTspice Path
LTSPICE_PATH = r"C:\Program Files\LTC\LTspiceXVII\XVIIx64.exe"

# ✅ File Paths
ASC_FILE = "two_stage_opamp.asc"
MODIFIED_ASC_FILE = "two_stage_opamp_modified.asc"
LOG_FILE = "two_stage_opamp_modified.log"
CSV_FILE = "two_stage_opamp_results.csv"

#  Define parameter sweep ranges
# W1_values = [1e-6, 6e-6, 12e-6]
# L1_values = [180e-9, 1e-6, 2e-6]
# W3_values = [2e-6, 5e-6, 10e-6]
# L3_values = [180e-9, 1e-6]
# W5_values = [2e-6, 5e-6, 8e-6]
# L5_values = [180e-9, 1e-6]
# W7_values = [10e-6, 20e-6, 40e-6]
# L7_values = [180e-9, 500e-9]
# W8_values = [5e-6, 10e-6, 20e-6]
# L8_values = [180e-9, 500e-9]
# IB_values = [10e-6, 20e-6, 30e-6]
# CC_values = [0.44e-15, 1.5e-15, 2.99e-15]
# total itrations = 104,976


W1_values = np.arange(1e-6, 12e-6 + 1e-15, 2e-8)  # 1µm-12µm, +1e-15 ensures endpoint inclusion
W3_values = np.arange(2e-6, 10e-6 + 1e-15, 2e-8)  # 2µm-10µm
W5_values = np.arange(2e-6, 8e-6 + 1e-15, 2e-8)   # 2µm-8µm
W7_values = np.arange(10e-6, 40e-6 + 1e-15, 2e-8) # 10µm-40µm
W8_values = np.arange(5e-6, 20e-6 + 1e-15, 2e-8)  # 5µm-20µm

# Length ranges (converted to meters)
L1_values = np.arange(180e-9, 2e-6 + 1e-15, 20e-9)  # 180nm-2µm
L3_values = np.arange(180e-9, 1e-6 + 1e-15, 20e-9)  # 180nm-1µm
L5_values = np.arange(180e-9, 1e-6 + 1e-15, 20e-9)  # Same as L3
L7_values = np.arange(180e-9, 500e-9 + 1e-15, 20e-9) # 180nm-500nm
L8_values = np.arange(180e-9, 500e-9 + 1e-15, 20e-9) # Same as L7

# Original IB and CC values
IB_values = [10e-6, 20e-6, 30e-6]
CC_values = [0.44e-15, 1.5e-15, 2.99e-15]


#total itrations = 1.2e+20
# ✅ Function to modify `.asc` file
def modify_ltspice_asc(W1, L1, W3, L3, W5, L5, W7, L7, W8, L8, IB, CC):
    """Modify LTspice .asc file parameters."""
    with open(ASC_FILE, "r") as file:
        asc_text = file.read()

    # Replace transistor parameters dynamically using regex
    asc_text = re.sub(r"\.param W1=\d+\w*", f".param W1={W1}", asc_text)
    asc_text = re.sub(r"\.param L1=\d+\w*", f".param L1={L1*1e9}n", asc_text)
    asc_text = re.sub(r"\.param W3=\d+\w*", f".param W3={W3}", asc_text)
    asc_text = re.sub(r"\.param L3=\d+\w*", f".param L3={L3*1e9}n", asc_text)
    asc_text = re.sub(r"\.param W5=\d+\w*", f".param W5={W5}", asc_text)
    asc_text = re.sub(r"\.param L5=\d+\w*", f".param L5={L5*1e9}n", asc_text)
    asc_text = re.sub(r"\.param W7=\d+\w*", f".param W7={W7}", asc_text)
    asc_text = re.sub(r"\.param L7=\d+\w*", f".param L7={L7*1e9}n", asc_text)
    asc_text = re.sub(r"\.param W8=\d+\w*", f".param W8={W8}", asc_text)
    asc_text = re.sub(r"\.param L8=\d+\w*", f".param L8={L8*1e9}n", asc_text)
    asc_text = re.sub(r"\.param IB=\d+\w*", f".param IB={IB*1e6}u", asc_text)
    asc_text = re.sub(r"\.param CC=\d+\w*", f".param CC={CC*1e15}f", asc_text)

    # Save modified file
    with open(MODIFIED_ASC_FILE, "w") as file:
        file.write(asc_text)

# ✅ Function to run LTspice
def run_ltspice():
    """Run LTspice simulation."""
    cmd = f'"{LTSPICE_PATH}" -b {MODIFIED_ASC_FILE}'
    subprocess.run(cmd, shell=True)

    # Wait for log file to be created
    start_time = time.time()
    while not os.path.exists(LOG_FILE):
        if time.time() - start_time > 10:  # Timeout after 10 seconds
            print("Error: LTspice log file not found.")
            return False
        time.sleep(1)

    return True


# def extract_ltspice_log():
#     """Extract Gain (dB), UGBW (Hz), PM (degrees) from LTspice log."""
#     with open(LOG_FILE, "r") as file:
#         log_data = file.read()

#     # Extract values using regex patterns
#     gain_match = re.search(r"gain:\s.*?\(([\d.]+)dB", log_data)
#     ugbw_match = re.search(r"ugbw:\s.*?AT\s([\d.e+]+)", log_data)
#     pm_match = re.search(r"pm:\s.*?\([^,]+,\s*([\d.-]+)°\)", log_data)

#     return {
#         'Gain (dB)': float(gain_match.group(1)) if gain_match else None,
#         'UGBW (Hz)': float(ugbw_match.group(1)) if ugbw_match else None,
#         'Phase Margin (°)': float(pm_match.group(1)) if pm_match else None,
#         'Slew Rate': None,  # Not present in log - requires .measure commands
#         'Power': None       # Not present in log - requires current measurements
#     }

# ✅ Function to extract results from LTspice log
def extract_ltspice_log():
    """Extract Gain, UGBW, PM, Slew Rate, and Power from LTspice log."""
    with open(LOG_FILE, "r") as file:
        log_data = file.read()

    # Extract Gain, UGBW, PM
    gain_match = re.search(r"gain:\s.*?\(([\d.]+)dB", log_data)
    ugbw_match = re.search(r"ugbw:\s.*?AT\s([\d.e+]+)", log_data)
    pm_match = re.search(r"pm:\s.*?\([^,]+,\s*([\d.-]+)°\)", log_data)

    gain = float(gain_match.group(1)) if gain_match else None
    ugbw = float(ugbw_match.group(1)) if ugbw_match else None
    pm = float(pm_match.group(1)) if pm_match else None

    return [gain, ugbw, pm]

# ✅ Create CSV file and run full parameter sweep
with open(CSV_FILE, "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["W1", "L1", "W3", "L3", "W5", "L5", "W7", "L7", "W8", "L8", "IB", "CC", "Gain", "UGBW", "PM"])

    for W1 in W1_values:
        for L1 in L1_values:
            for W3 in W3_values:
                for L3 in L3_values:
                    for W5 in W5_values:
                        for L5 in L5_values:
                            for W7 in W7_values:
                                for L7 in L7_values:
                                    for W8 in W8_values:
                                        for L8 in L8_values:
                                            for IB in IB_values:
                                                for CC in CC_values:
                                                    print(f"Running simulation for W1={W1}, L1={L1}, IB={IB}, CC={CC}")

                                                    # Modify LTspice file
                                                    modify_ltspice_asc(W1, L1, W3, L3, W5, L5, W7, L7, W8, L8, IB, CC)

                                                    # Run LTspice
                                                    if run_ltspice():
                                                        results = extract_ltspice_log()
                                                        writer.writerow([W1, L1, W3, L3, W5, L5, W7, L7, W8, L8, IB, CC] + results)
                                                    else:
                                                        print("Skipping due to simulation error.")
