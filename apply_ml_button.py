import subprocess

# Reset file to be 100% sure
subprocess.run(["git", "checkout", "eGUI/src/main.rs"])

with open("eGUI/src/main.rs", "r") as f:
    code = f.read()

# 1. Add module includes at the top
code = "pub mod tuner;\npub mod ui_controls;\nuse tuner::ResonanceOptimizer;\n" + code

# 2. Add fields to TelemetryApp struct definition
code = code.replace(
    "struct TelemetryApp {", 
    "struct TelemetryApp {\n    optimizer: ResonanceOptimizer,\n    manual_mode: bool,"
)

# 3. Initialize fields inside default() right after Self {
code = code.replace(
    "Self {", 
    "Self {\n            optimizer: ResonanceOptimizer::new(),\n            manual_mode: true,"
)

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

code = code.replace(target, ml_btn_call)

with open("eGUI/src/main.rs", "w") as f:
    f.write(code)

print("[+] Successfully applied clean patch to main.rs!")
