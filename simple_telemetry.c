#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/proc_fs.h>
#include <linux/uaccess.h>
#include <linux/jiffies.h>
#include <linux/string.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Natska Natsagnyam NAMKHAI");
MODULE_DESCRIPTION("Diode failure detector for synchronous brushless excitation control system");
MODULE_VERSION("5.1");

/* Control and wave parameters (atomic/safe scalar variables) */
static uint32_t sine_phase;
static int hz_step = 1;
static int t_lead = 45;
static int t_lag = 2;

static struct proc_dir_entry *proc_dir;

/* Integer Sine approximation function for Amplitude A = 100 over phase [0..255] */
static int compute_sine_100(uint32_t phase) {
    uint32_t p = phase & 255;
    int sign = 1;
    if (p >= 128) {
        p -= 128;
        sign = -1;
    }
    if (p >= 64) {
        p = 128 - p;
    }
    int val = (int)(4 * p * (64 - p));
    val = (val * 100) / 4096;
    return sign * val;
}

/* =========================================================================
 * TELEMETRY VIRTUAL FILESYSTEM (VF) ACCESS HANDLERS
 * ========================================================================= */

static ssize_t hz_read(struct file *file, char __user *buf, size_t count, loff_t *pos) {
    char b[32]; 
    int len = snprintf(b, sizeof(b), "%d\n", READ_ONCE(hz_step));
    return simple_read_from_buffer(buf, count, pos, b, len);
}

static ssize_t hz_write(struct file *file, const char __user *buf, size_t count, loff_t *pos) {
    char b[32]; 
    int val;
    if (count >= sizeof(b)) return -EINVAL;
    if (copy_from_user(b, buf, count)) return -EFAULT;
    b[count] = '\0'; 
    if (kstrtoint(b, 10, &val) < 0) return -EINVAL;
    if (val < 1) val = 1; 
    if (val > 20) val = 20;
    WRITE_ONCE(hz_step, val);
    return count;
}
static const struct proc_ops hz_ops = { .proc_read = hz_read, .proc_write = hz_write };

static ssize_t t_lead_read(struct file *file, char __user *buf, size_t count, loff_t *pos) {
    char b[32]; 
    int len = snprintf(b, sizeof(b), "%d\n", READ_ONCE(t_lead));
    return simple_read_from_buffer(buf, count, pos, b, len);
}

static ssize_t t_lead_write(struct file *file, const char __user *buf, size_t count, loff_t *pos) {
    char b[32]; 
    int val;
    if (count >= sizeof(b)) return -EINVAL;
    if (copy_from_user(b, buf, count)) return -EFAULT;
    b[count] = '\0'; 
    if (kstrtoint(b, 10, &val) < 0) return -EINVAL;
    if (val < 1) val = 1; /* Prevent division by zero */
    WRITE_ONCE(t_lead, val);
    return count;
}
static const struct proc_ops t_lead_ops = { .proc_read = t_lead_read, .proc_write = t_lead_write };

static ssize_t t_lag_read(struct file *file, char __user *buf, size_t count, loff_t *pos) {
    char b[32]; 
    int len = snprintf(b, sizeof(b), "%d\n", READ_ONCE(t_lag));
    return simple_read_from_buffer(buf, count, pos, b, len);
}

static ssize_t t_lag_write(struct file *file, const char __user *buf, size_t count, loff_t *pos) {
    char b[32]; 
    int val;
    if (count >= sizeof(b)) return -EINVAL;
    if (copy_from_user(b, buf, count)) return -EFAULT;
    b[count] = '\0'; 
    if (kstrtoint(b, 10, &val) < 0) return -EINVAL;
    if (val < 1) val = 1; /* Prevent division by zero */
    WRITE_ONCE(t_lag, val);
    return count;
}
static const struct proc_ops t_lag_ops = { .proc_read = t_lag_read, .proc_write = t_lag_write };

/* VF Access: Stream latest calculated telemetry snapshot directly on demand */
static ssize_t stream_read(struct file *file, char __user *buf, size_t count, loff_t *pos) {
    char line_buf[128];
    int len;
    int current_hz = READ_ONCE(hz_step);
    int current_lead = READ_ONCE(t_lead);
    int current_lag = READ_ONCE(t_lag);
    int din, dout, lag_out, lead_out, dout_alarm, alarm_in;
    int diode_short, diode_open;
    unsigned long time_ms = jiffies_to_msecs(jiffies);
    
    /* Persistent filter state per file descriptor or global instance */
    static int lag_out_prev, lead_out_prev, cpy_dout_alarm;

    /* Advance phase safely using bitwise mask (Rule: No % modulo operation) */
    sine_phase = (sine_phase + current_hz) & 255;
    
    /* Compute Detector_input and Detector_output */
    din = compute_sine_100(sine_phase);
    
    /* Natska filter algorithms */
    lag_out = lag_out_prev + ((din - lag_out_prev) / current_lag);
    lag_out_prev = lag_out;
    
    lead_out = lead_out_prev + ((lag_out - lead_out_prev) / current_lead);
    lead_out_prev = lead_out;
    lead_out = lag_out - lead_out; 
    
    dout = lead_out;
    alarm_in = lead_out;
    
    if (alarm_in < 0) { 
        alarm_in *= -1;
    }  
    
    dout_alarm = cpy_dout_alarm + ((alarm_in - cpy_dout_alarm) >> 5);
    cpy_dout_alarm = dout_alarm;  
    
    diode_short = (dout_alarm > 40) ? 1 : 0;
    diode_open = ((dout_alarm > 25) && (dout_alarm < 40)) ? 1 : 0;
    dout = lead_out;

    len = snprintf(line_buf, sizeof(line_buf), "%lu,%d,%d,%d,%d\n", 
                   time_ms, din, dout, diode_short, diode_open);

    return simple_read_from_buffer(buf, count, pos, line_buf, len);
}

static const struct proc_ops stream_proc_ops = {
    .proc_read = stream_read,
};

static int __init simple_telemetry_init(void) {
    sine_phase = 32; 
    hz_step = 1;
    t_lead = 45; 
    t_lag = 2; 

    proc_dir = proc_mkdir("simple-telemetry", NULL);
    if (!proc_dir) return -ENOMEM;

    proc_create("hz", 0666, proc_dir, &hz_ops);
    proc_create("t_lead", 0666, proc_dir, &t_lead_ops);
    proc_create("t_lag", 0666, proc_dir, &t_lag_ops);
    proc_create("stream", 0444, proc_dir, &stream_proc_ops);

    pr_info("Diode failure detector module loaded successfully. Author: Natska Natsagnyam NAMKHAI\n");
    return 0;
}

static void __exit simple_telemetry_exit(void) {
    remove_proc_entry("stream", proc_dir);
    remove_proc_entry("hz", proc_dir);
    remove_proc_entry("t_lead", proc_dir);
    remove_proc_entry("t_lag", proc_dir);
    remove_proc_entry("simple-telemetry", NULL);
    pr_info("simple-telemetry unloaded.\n");
}

module_init(simple_telemetry_init);
module_exit(simple_telemetry_exit);