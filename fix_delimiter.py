import re

with open("eGUI/src/main.rs", "r") as f:
    code = f.read()

# Replace the entire broken impl Default block with a clean, correct one
clean_default_block = """impl Default for TelemetryApp {
    fn default() -> Self {
        Self {
            optimizer: ResonanceOptimizer::new(),
            manual_mode: true,
            hz_val: 1,
            t_lead_val: 45,
            t_lag_val: 1,
            detector_input: 0,
            detector_output: 0,
            diode_short_circuit: false,
            diode_open_circuit: false,
        }
    }
}"""

# Use regex to find and replace any existing impl Default for TelemetryApp block
pattern = r'impl\s+Default\s+for\s+TelemetryApp\s*\{.*?\n\}\s*\}?'
if re.search(pattern, code, re.DOTALL):
    code = re.sub(pattern, clean_default_block, code, flags=re.DOTALL)
else:
    # If regex doesn't match, let us insert it right above update()
    code = code.replace("impl TelemetryApp {", clean_default_block + "\n\nimpl TelemetryApp {")

with open("eGUI/src/main.rs", "w") as f:
    f.write(code)

print("[+] Successfully balanced delimiters and fixed impl Default!")
