from pathlib import Path

readme_path = Path("README.md") if Path("README.md").exists() else Path("README")
existing = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

tuner_path = Path("eGUI/src/tuner.rs")
ui_controls_path = Path("eGUI/src/ui_controls.rs")

tuner_src = tuner_path.read_text(encoding="utf-8") if tuner_path.exists() else ""
ui_src = ui_controls_path.read_text(encoding="utf-8") if ui_controls_path.exists() else ""

ml_section = """
---

## ML / Automated Resonance Tuning (`T_lead` & `T_lag`)

The `diode-failure-detector` Rust `egui` application includes an automated tuning engine (`ResonanceOptimizer` in `eGUI/src/tuner.rs`, paired with UI controls in `eGUI/src/ui_controls.rs`) designed to find `T_lead` and `T_lag` settings that maximize output amplitude / resonance at the **currently selected frequency (`Hz`)** without freezing the UI thread.

### Core Tuning Constraints & Behavior
* **Fixed Frequency (`Hz` Preserved):** The tuner operates at the user-selected `Hz` setting and must **not** alter `Hz` during parameter search.
* **Slider & Kernel Sync:** Candidate `T_lead` and `T_lag` values drive the corresponding GUI sliders and update the Linux kernel `simple_telemetry` ProcFS endpoints (`/proc/simple-telemetry/t_lead` and `/proc/simple-telemetry/t_lag`) so the series lag/lead filter stage in the kernel module responds in real time.
* **Non-Blocking Execution:** Parameter evaluation runs asynchronously / in step-wise background updates rather than blocking the `egui` render/event loop, keeping waveform plotting and alarms responsive.
* **Peak Retention:** Each tested `(T_lead, T_lag)` candidate is evaluated against the observed `dout` (`detector_output`) peak/amplitude response so the tuner converges on and retains high-output / resonance configurations rather than ending on a low-amplitude sample.

### How the Search Process Works
1. **Initialization & Mode Switch:** Triggered from the **ML Tune T_lead & T_lag** control in the UI, switching from manual slider adjustment into automated search mode while locking in the active `Hz` target.
2. **Candidate Generation & Exploration/Exploitation:** Proposes `(T_lead, T_lag)` candidates across the valid parameter bounds—combining broad exploration across the `(T_lead, T_lag)` grid/space with focused refinement around high-scoring regions.
3. **Actuation & Telemetry Observation:** Applies each candidate `(T_lead, T_lag)` pair to the sliders/ProcFS interface and observes the resulting `dout` signal amplitude and peak response from the telemetry stream.
4. **Scoring & Best-Point Lock-In:** Ranks candidate pairs by peak `dout` output / resonance strength at the fixed `Hz`, tracks the best `(T_lead, T_lag)` found so far, and applies the winning pair when tuning completes.

### Function-by-Function Reference (`eGUI/src/tuner.rs` & `eGUI/src/ui_controls.rs`)
"""

# Extract actual `fn ` signatures if present so the README matches the exact code on disk
fn_lines = []
for label, src in [("eGUI/src/tuner.rs", tuner_src), ("eGUI/src/ui_controls.rs", ui_src)]:
    if src:
        fn_lines.append(f"\n#### `{label}`\n")
        found = [line.strip() for line in src.splitlines() if "fn " in line and ("pub " in line or line.lstrip().startswith("fn "))]
        if found:
            for sig in found:
                fn_lines.append(f"* `{sig}` — Evaluates or coordinates resonance tuning state, candidate `(T_lead, T_lag)` selection, peak `dout` tracking, or UI trigger/status rendering.\n")
        else:
            fn_lines.append("* Inspect `eGUI/src/tuner.rs` and `eGUI/src/ui_controls.rs` for internal helper functions and state transitions.\n")

full_addition = ml_section + "".join(fn_lines)

marker = "## ML / Automated Resonance Tuning (`T_lead` & `T_lag`)"
if marker in existing:
    idx = existing.index("\n---\n\n" + marker) if "\n---\n\n" + marker in existing else existing.index(marker)
    updated = existing[:idx] + full_addition.lstrip("\n")
else:
    updated = existing.rstrip() + "\n" + full_addition

readme_path.write_text(updated, encoding="utf-8")
print(f"[+] Updated {readme_path} successfully.")
