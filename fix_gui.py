with open("eGUI/src/main.rs", "r") as f:
    content = f.read()

# Strip any accidental duplicate code appended at the bottom
if "fn main()" in content:
    content = content.split("fn main()")[0]

# Add modules at the very top if not present
top_includes = "pub mod tuner;\npub mod ui_controls;\nuse tuner::ResonanceOptimizer;\n"
if top_includes not in content:
    content = top_includes + content

# Add optimizer and manual_mode fields to TelemetryApp struct
if "optimizer: ResonanceOptimizer" not in content:
    content = content.replace("struct TelemetryApp {", "struct TelemetryApp {\n    optimizer: ResonanceOptimizer,\n    manual_mode: bool,")

# Initialize fields in TelemetryApp::default()
if "optimizer: ResonanceOptimizer::new()" not in content:
    content = content.replace("Self {", "Self {\n            optimizer: ResonanceOptimizer::new(),\n            manual_mode: true,")

# Insert the ML button call right below the T_lag slider block
t_lag_block = """ui.horizontal(|ui| {
                ui.label("T_lag Slider:");
                let slider = egui::Slider::new(&mut self.t_lag_val, 1..=50);
                if ui.add(slider).changed() {
                    let _ = fs::write("/proc/simple-telemetry/t_lag", self.t_lag_val.to_string());
                }
            });"""

ml_call = t_lag_block + """

            // --- Automated ML Auto-Tuner Button ---
            ui_controls::render_ml_tune_button(ui, self.hz_val as f32, &mut self.manual_mode, &mut self.optimizer);"""

if "render_ml_tune_button" not in content:
    content = content.replace(t_lag_block, ml_call)

# Re-append the main entry point at the end
main_code = """
fn main() -> Result<(), eframe::Error> {
    let options = eframe::NativeOptions {
        viewport: egui::ViewportBuilder::default().with_maximized(true),
        ..Default::default()
    };
    eframe::run_native(
        "Diode Failure Detector GUI",
        options,
        Box::new(|_cc| Ok(Box::new(TelemetryApp::default()))),
    )
}
"""
content += main_code

with open("eGUI/src/main.rs", "w") as f:
    f.write(content)

print("[+] Successfully updated eGUI/src/main.rs with integrated ML button!")
