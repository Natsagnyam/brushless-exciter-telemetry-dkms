with open("eGUI/src/main.rs", "r") as f:
    code = f.read()

# Let us find where fn default() is and ensure Self { is correct
old_default_block = """impl Default for TelemetryApp {
    fn default() -> Self {"""

new_default_block = """impl Default for TelemetryApp {
    fn default() -> Self {
        Self {"""

code = code.replace(old_default_block, new_default_block)

# Clean up duplicate Self { if any were introduced
code = code.replace("Self {\n        Self {", "Self {")

with open("eGUI/src/main.rs", "w") as f:
    f.write(code)

print("[+] Fixed default implementation block!")
