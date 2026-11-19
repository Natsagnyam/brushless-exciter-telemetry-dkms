pub mod tuner;
pub mod ui_controls;
use tuner::ResonanceOptimizer;
use eframe::egui;
use egui_plot::{Line, Plot, PlotPoints};
use std::fs;
use std::time::{Instant, Duration};

struct TelemetryApp {
    optimizer: ResonanceOptimizer,
    manual_mode: bool,
    hz_val: i32,
    t_lead_val: i32,
    t_lag_val: i32,
    detector_input: i32,
    detector_output: i32,
    diode_short_circuit: bool,
    diode_open_circuit: bool,
    history_input: Vec<[f64; 2]>,
    history_output: Vec<[f64; 2]>,
    start_time: Instant,
    last_poll: Instant,
}

impl Default for TelemetryApp {
    fn default() -> Self {

        let start_time = Instant::now();
        // Pre-seed initial points so egui_plot renders the lines immediately on launch
        let initial_elapsed = 0.0;
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
            // Pre-populate with at least 2 points to draw the initial line segment
            history_input: vec![[-0.1, 0.0], [initial_elapsed, 0.0]],
            history_output: vec![[-0.1, -15.0], [0.0, -15.0]],
            start_time,
            last_poll: Instant::now(),
        }
    }
}

impl eframe::App for TelemetryApp {
    fn update(&mut self, ctx: &egui::Context, _frame: &mut eframe::Frame) {
        // Poll kernel stream VF every 50ms for latest state snapshot
        if self.last_poll.elapsed() >= Duration::from_millis(50) {
            self.last_poll = Instant::now();
            
            if let Ok(data) = fs::read_to_string("/proc/simple-telemetry/stream") {
                let trimmed = data.trim();
                if !trimmed.is_empty() {
                    let parts: Vec<&str> = trimmed.split(',').collect();
                    if parts.len() == 5 {
                        if let (Ok(_t), Ok(din), Ok(dout), Ok(dsc), Ok(doc)) = (
                            parts[0].parse::<u64>(),
                            parts[1].parse::<i32>(),
                            parts[2].parse::<i32>(),
                            parts[3].parse::<i32>(),
                            parts[4].parse::<i32>(),
                        ) {
                            let elapsed = self.start_time.elapsed().as_secs_f64();
                            self.detector_input = din;
                            self.detector_output = dout;
                            self.diode_short_circuit = dsc == 1;
                            self.diode_open_circuit = doc == 1;

                            self.history_input.push([elapsed, din as f64]);
                            self.history_output.push([elapsed, dout as f64]);

                            if self.history_input.len() > 300 {
                                self.history_input.remove(0);
                                self.history_output.remove(0);
                            }
                        }
                    }
                }
            }
        }

        egui::CentralPanel::default().show(ctx, |ui| {
            ui.heading("Resonance band detector. Diode failure detector for synchronous brushless excitation control system. Please desing band filter tuning Hz, Tlag & Tlead. Lag and Lead filters are in series ");
            ui.label("Author: Natska Natsagnyam NAMKHAI, 2026 Nov 17th. Ulaanbaatar, MONGOLIA");
            ui.separator();

            // Sliders with text labels strictly placed on the LEFT side
            ui.horizontal(|ui| {
                ui.label("Hz Slider:");
                let slider = egui::Slider::new(&mut self.hz_val, 1..=100);
                if ui.add(slider).changed() {
                    let _ = fs::write("/proc/simple-telemetry/hz", self.hz_val.to_string());
                }
            });

            ui.horizontal(|ui| {
                ui.label("T_lead Slider:");
                let slider = egui::Slider::new(&mut self.t_lead_val, 1..=50);
                if ui.add(slider).changed() {
                    let _ = fs::write("/proc/simple-telemetry/t_lead", self.t_lead_val.to_string());
                }
            });

            ui.horizontal(|ui| {
                ui.label("T_lag Slider:");
                let slider = egui::Slider::new(&mut self.t_lag_val, 1..=50);
                if ui.add(slider).changed() {
                    let _ = fs::write("/proc/simple-telemetry/t_lag", self.t_lag_val.to_string());
                }
            });

            // --- Automated ML Auto-Tuner Button ---
            ui_controls::render_ml_tune_button(ui, self.hz_val as f32, &mut self.manual_mode, &mut self.optimizer);

            ui.add_space(5.0);
            
            // Status and Alarm LEDs Display
            ui.horizontal(|ui| {
                ui.label(format!("Detector_input: {} | Detector_output: {}  |  Alarms:", self.detector_input, self.detector_output));
                
                ui.add_space(10.0);
                // Diode_Short_Circuit LED Indicator
                let color1 = if self.diode_short_circuit { egui::Color32::RED } else { egui::Color32::DARK_GRAY };
                let (rect1, _) = ui.allocate_exact_size(egui::Vec2::splat(16.0), egui::Sense::hover());
                ui.painter().circle_filled(rect1.center(), 8.0, color1);
                ui.label("Diode_Short_Circuit");

                ui.add_space(10.0);
                // Diode_Open_Circuit LED Indicator
                let color2 = if self.diode_open_circuit { egui::Color32::RED } else { egui::Color32::DARK_GRAY };
                let (rect2, _) = ui.allocate_exact_size(egui::Vec2::splat(16.0), egui::Sense::hover());
                ui.painter().circle_filled(rect2.center(), 8.0, color2);
                ui.label("Diode_Open_Circuit");
            });

            ui.add_space(10.0);

            // Real-time eGUI Plot with both Detector_input (Red) and Detector_output (Green)
            let plot_in = PlotPoints::from(self.history_input.clone());
            let plot_out = PlotPoints::from(self.history_output.clone());

            Plot::new("detector_plot")
                .view_aspect(2.5)
                .legend(egui_plot::Legend::default())
                .show(ui, |plot_ui| {
                    plot_ui.line(Line::new(plot_in).name("Detector_input").color(egui::Color32::RED));
                    plot_ui.line(Line::new(plot_out).name("Detector_output").color(egui::Color32::GREEN));
                });
        });

        ctx.request_repaint();
    }
}

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