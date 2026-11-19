with open("eGUI/src/main.rs", "r") as f:
    code = f.read()

# Let us locate the default impl block and replace it with a clean, perfectly structured version
import re

# Find where impl Default for TelemetryApp begins
default_pattern = r'impl Default for TelemetryApp\s*\{[^}]*fn default\(\)\s*->\s*Self\s*\{([^}]*)\}\s*\}'

# We want the default function to correctly return Self { optimizer: ..., manual_mode: ..., ... }
new_default_impl = """impl Default for TelemetryApp {
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

# If the regex matches, replace the whole default block cleanly
if re.search(default_pattern, code, re.DOTALL):
    code = re.sub(default_pattern, new_default_impl, code, flags=re.DOTALL)
else:
    # Fallback: if exact match fails, let us do a direct string replacement of the broken lines
    code = code.replace(
        "    fn default() -> Self {\n            optimizer: ResonanceOptimizer::new(),",
        "    fn default() -> Self {\n        Self {\n            optimizer: ResonanceOptimizer::new(),\n            manual_mode: true,"
    )

with open("eGUI/src/main.rs", "w") as f:
    f.write(code)

print("[+] Successfully corrected TelemetryApp default implementation!")
