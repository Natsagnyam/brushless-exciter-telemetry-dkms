import re

with open("eGUI/src/main.rs", "r") as f:
    code = f.read()

# 1. Add module includes at the top if not present
if "pub mod tuner;" not in code:
    code = "pub mod tuner;\npub mod ui_controls;\nuse tuner::ResonanceOptimizer;\n" + code

# 2. Add fields to TelemetryApp struct definition if not present
if "optimizer: ResonanceOptimizer" not in code:
    code = code.replace(
        "struct TelemetryApp {", 
        "struct TelemetryApp {\n    optimizer: ResonanceOptimizer,\n    manual_mode: bool,"
    )

# 3. Properly initialize fields inside TelemetryApp::default() using regex
if "optimizer: ResonanceOptimizer::new()" not in code:
    pattern = r'(fn default\(\)\s*->\s*Self\s*\{\s*Self\s*\{)'
    replacement = r'\1\n            optimizer: ResonanceOptimizer::new(),\n            manual_mode: true,'
    code, count = re.subn(pattern, replacement, code)
    if count == 0:
        # Fallback replacement
        code = code.replace("Self {", "Self {\n            optimizer: ResonanceOptimizer::new(),\n            manual_mode: true,", 1)

# 4. Insert the ML button call right below the T_lag slider block
target = """ui.horizontal(|ui| {
                ui.label("T_lag Slider:");
                let slider = egui::Slider::new(&mut self.t_lag_val, 1..=50);
                if ui.add(slider).changed() {
                    let _ = fs::write("/proc/simple-telemetry/t_lag", self.t_lag_val.to_string());
                }
            });"""

ml_btn_call = target + """

            // --- Automated ML Auto-Tuner Button ---
            ui_controls::render_ml_tune_button(ui, self.hz_val as f32, &mut self.manual_mode, &mut self.optimizer);"""

if "render_ml_tune_button" not in code:
    code = code.replace(target, ml_btn_call)

with open("eGUI/src/main.rs", "w") as f:
    f.write(code)

print("[+] Successfully patched eGUI/src/main.rs cleanly with regex!")
