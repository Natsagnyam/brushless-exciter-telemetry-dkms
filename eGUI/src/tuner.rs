use std::fs::File;
use std::io::Read;
use std::thread;
use std::time::Duration;

pub struct ResonanceOptimizer {
    pub is_running: bool,
    pub status: String,
    pub best_tlag: f32,
    pub best_tlead: f32,
    pub best_dout: f32,
}

impl ResonanceOptimizer {
    pub fn new() -> Self {
        Self {
            is_running: false,
            status: "Idle".to_string(),
            best_tlag: 0.0,
            best_tlead: 0.0,
            best_dout: 0.0,
        }
    }

    pub fn start_tuning(&mut self, target_hz: f32) {
        self.is_running = true;
        self.status = format!("Tuning T_lead & T_lag for resonance at {:.1} Hz...", target_hz);
        
        let target_hz_val = target_hz;

        thread::spawn(move || {
            // Write current Hz slider value to kernel module
            let _ = std::fs::write("/proc/simple-telemetry/hz", target_hz_val.to_string());

            let mut max_dout = 0.0;
            let mut opt_tlag = 0.0;
            let mut opt_tlead = 0.0;

            // Automated Grid Search over T_lag and T_lead space
            let steps = 30;
            for i in 0..steps {
                let tlag = i as f32 * 0.2;
                for j in 0..steps {
                    let tlead = j as f32 * 0.2;

                    let _ = std::fs::write("/proc/simple-telemetry/t_lag", tlag.to_string());
                    let _ = std::fs::write("/proc/simple-telemetry/t_lead", tlead.to_string());

                    // Allow filter to settle
                    thread::sleep(Duration::from_millis(15));

                    // Read response 'dout' from kernel telemetry stream
                    if let Ok(mut file) = File::open("/proc/simple-telemetry/stream") {
                        let mut contents = String::new();
                        if file.read_to_string(&mut contents).is_ok() {
                            if let Some(last_line) = contents.lines().last() {
                                let parts: Vec<&str> = last_line.split(',').collect();
                                if parts.len() >= 3 {
                                    if let Ok(dout_val) = parts[2].trim().parse::<f32>() {
                                        if dout_val > max_dout {
                                            max_dout = dout_val;
                                            opt_tlag = tlag;
                                            opt_tlead = tlead;
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }

            // Lock in optimal T_lag and T_lead values
            let _ = std::fs::write("/proc/simple-telemetry/t_lag", opt_tlag.to_string());
            let _ = std::fs::write("/proc/simple-telemetry/t_lead", opt_tlead.to_string());
            
            println!("[+] Resonance Found at {:.1}Hz! T_lag: {:.2}, T_lead: {:.2}, Peak Dout: {:.2}", 
                     target_hz_val, opt_tlag, opt_tlead, max_dout);
        });
    }
}
