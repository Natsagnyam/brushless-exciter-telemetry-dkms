use crate::tuner::ResonanceOptimizer;
use eframe::egui;

pub fn render_ml_tune_button(
    ui: &mut egui::Ui, 
    current_hz: f32, 
    manual_mode: &mut bool, 
    optimizer: &mut ResonanceOptimizer
) {
    ui.horizontal(|ui: &mut egui::Ui| {
        if ui.button("⚡ ML Tune T_lead & T_lag").clicked() {
            *manual_mode = false; // Disable manual sliders during tuning
            optimizer.start_tuning(current_hz);
        }
    });

    ui.label(format!("Auto-Tuner Status: {}", optimizer.status));
}
