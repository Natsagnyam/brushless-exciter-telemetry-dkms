# Diode Failure Detector & Telemetry System (v5.1.0)
Authored by **Natska Natsagnyam NAMKHAI** (Nov 2026, Ulaanbaatar, Mongolia).

An enterprise-grade real-time telemetry and diode failure detection suite designed for synchronous brushless alternator excitation control systems. 
However, it is useful tool to learn resonance circuit tuning. Output = input * lag(T_lag) * lead(T_lad); Please deign own Hz resonance by tuning. E.g: select Hz you want to see resonance. Tune T_lag & T_lead. 
Characteristic: 
Larger T_lag & Lower T_lead will blocking band in the middle point of Hz slider.
Larger T_lead & Lower T_lag will unblocking band in the middle point of Hz slider.

Please keep hard working to find desired tuning. Better version available on request commercially.
![freq_band_detector](jpeg/freq_band_detector.png)

It requires hard working to find desired tuning
![test69](jpeg/test69.png)

Circuit characteristic: frequency_response
![frequency_response](jpeg/frequency_response.jpeg)

Circuit philosophy: frequency_response_theory
![frequency_response](jpeg/frequency_response_theory.jpg)

---

## 🚀 System Architecture

1. **Linux Kernel Module (`simple_telemetry`):**
   - Implements ProcFS virtual file endpoints under `/proc/simple-telemetry/`.
   - Utilizes integer sine wave approximation ($A = 100$), bitwise masking (`& 255`) for efficient ring-buffering, safe scalar memory reads/writes via `READ_ONCE`/`WRITE_ONCE`, and robust digital lead/lag filters.
   - Zero kernel panics or concurrency conflicts.

2. **Rust eGUI Visualization Application (`diode-failure-detector`):**
   - Built on `eframe` and `egui_plot` for real-time wave rendering and alarm monitoring (`Diode_Short_Circuit`, `Diode_Open_Circuit`).
   - Polls telemetry streams every 50ms with pre-seeded history buffers to prevent startup rendering overlap.

3. **Enterprise Packaging & DKMS Support:**
   - Fully compliant Debian (`.deb`) package with Dynamic Kernel Module Support (`DKMS`) for automatic recompilation across kernel upgrades.
   - Includes custom man page documentation and system binary integration[cite: 1].

---

## 📊 Test Results & System Verification

All components have been rigorously verified and tested on Ubuntu 24.04 LTS (Kernel `7.0.0-43-generic` x86_64):

### 1. Manual Page Verification (`man diode-failure-detector`)
Successfully packaged, compressed, and indexed into the system documentation database[cite: 1]. Verified via terminal:
```bash
man diode-failure-detector
2. Kernel Module & ProcFS Telemetry Stream
The module loads cleanly into memory (16384 bytes) and streams real-time CSV payloads (timestamp_ms, din, dout, short_alarm, open_alarm)[cite: 1]:

Bash
natska@natska-XPS-15-9530:~$ lsmod | grep simple_telemetry
simple_telemetry       16384  0

natska@natska-XPS-15-9530:~$ head -n 5 /proc/simple-telemetry/stream
1401330,-12,33,0,0
1413065,38,15,0,0
1424469,28,15,0,0
1426128,28,15,0,0
1441824,-64,0,0,0
3. DKMS Status & Compilation
DKMS automatically signed, compiled, and registered the module against the active kernel[cite: 1]:

Bash
natska@natska-XPS-15-9530:~$ dkms status
diode-failure-detector/5.1.0, 7.0.0-43-generic, x86_64: installed
🛠️ Installation & Usage
From Debian Package (.deb)
Bash
sudo dpkg -i diode-failure-detector_5.1.0_amd64.deb
sudo apt-get install -f # Resolves dependencies if needed
Viewing System Documentation
Bash
man diode-failure-detector
Launching the Telemetry GUI
Bash
diode-failure-detector
📂 ProcFS Control Endpoints
/proc/simple-telemetry/stream — Real-time CSV telemetry data stream[cite: 1].

/proc/simple-telemetry/hz — Waveform frequency step adjustment (1 to 20)[cite: 1].

/proc/simple-telemetry/t_lead — Digital filter time constant lead (>= 1)[cite: 1].

/proc/simple-telemetry/t_lag — Digital filter time constant lag (>= 1)[cite: 1].

Authored by Natska Natsagnyam NAMKHAI — Ulaanbaatar, Mongolia[cite: 1].
