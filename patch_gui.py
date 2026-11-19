import re

with open("eGUI/src/main.rs", "r") as f:
    content = f.read()

# 1. Add module declarations at the top if not present
if "pub mod tuner;" not in content:
    content = "pub mod tuner;\npub mod ui_controls;\nuse tuner::ResonanceOptimizer;\n" + content

# 2. Add optimizer field to struct if not present
if "optimizer:" not in content:
    # Find struct definition and insert optimizer field before the closing brace
    content = re.sub(r'(pub struct \w+ \{[^}]*)(\})', r'\1    pub optimizer: ResonanceOptimizer,\n\2', content)

# 3. Initialize optimizer in struct instantiation (e.g. Self { ... })
if "optimizer:" not in content and "ResonanceOptimizer::new()" not in content:
    content = content.replace("Self {", "Self {\n            optimizer: ResonanceOptimizer::new(),")

# 4. Insert the ML button render call right after T_lag slider section
target_pattern = r'(let slider = egui::Slider::new\(&mut self\.t_lag_val, 1\.\=50\);[^\n]*\n)'
replacement = r'\1\n            // --- Automated ML Auto-Tuner Button ---\n            ui_controls::render_ml_tune_button(ui, self.hz_val as f32, &mut self.manual_mode, &mut self.optimizer);\n'

if "render_ml_tune_button" not in content:
    content = re.sub(target_pattern, replacement, content)

with open("eGUI/src/main.rs", "w") as f:
    f.write(content)

print("[+] Successfully patched eGUI/src/main.rs with ML auto-tuner controls!")
