with open("eGUI/src/main.rs", "r") as f:
    content = f.read()

# Fix the incorrect default impl block syntax
old_default = """impl Default for TelemetryApp {
    fn default() -> Self {
            optimizer: ResonanceOptimizer::new(),
            manual_mode: true,"""

new_default = """impl Default for TelemetryApp {
    fn default() -> Self {
        Self {"""

# Also ensure the closing bracket matches if needed
content = content.replace(old_default, new_default)

# Make sure we close the Self struct initialization properly before the end of default()
content = content.replace("""            diode_open_circuit: false,
    }
}""", """            diode_open_circuit: false,
        }
    }
}""")

with open("eGUI/src/main.rs", "w") as f:
    f.write(content)

print("[+] Fixed default implementation syntax in eGUI/src/main.rs!")
