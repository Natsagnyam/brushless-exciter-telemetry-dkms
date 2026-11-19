import subprocess

# 1. Fully reset main.rs to pristine git state
subprocess.run(["git", "checkout", "eGUI/src/main.rs"])

with open("eGUI/src/main.rs", "r") as f:
    code = f.read()

# 2. Add module includes at the top
code = "pub mod tuner;\npub mod ui_controls;\nuse tuner::ResonanceOptimizer;\n" + code

# 3. Add fields to TelemetryApp struct definition
code = code.replace(
    "struct TelemetryApp {", 
    "struct TelemetryApp {\n    optimizer: ResonanceOptimizer,\n    manual_mode: bool,"
)

# 4. Inject optimizer and manual_mode right inside the existing Self { block of default()
code = code.replace(
    "Self {", 
    "Self {\n            optimizer: ResonanceOptimizer::new(),\n            manual_mode: true,"
)

# 5. Insert the ML button call right below the T_lag slider block
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

print("[+] Successfully patched main.rs while preserving all original history fields!")
