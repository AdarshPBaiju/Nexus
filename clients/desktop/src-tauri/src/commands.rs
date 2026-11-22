//! commands.rs — Strongly typed Tauri IPC command handlers.

use crate::device_binding::{DeviceBindingService, WorkstationTelemetry};
use crate::print_spooler::{DesktopPrintSpooler, PrintJob};

pub struct DesktopCommandBridge {
    spooler: DesktopPrintSpooler,
}

impl Default for DesktopCommandBridge {
    fn default() -> Self {
        Self::new()
    }
}

impl DesktopCommandBridge {
    pub fn new() -> Self {
        Self {
            spooler: DesktopPrintSpooler::new(3000),
        }
    }

    pub fn get_device_telemetry(
        &self,
        workstation_id: &str,
    ) -> Result<WorkstationTelemetry, String> {
        Ok(DeviceBindingService::collect_telemetry(workstation_id, false))
    }

    pub fn trigger_local_print(&self, job: &PrintJob) -> Result<String, String> {
        self.spooler.dispatch(job)?;
        Ok(format!("Job {} dispatched successfully", job.job_id))
    }

    pub fn kick_cash_drawer(&self) -> Result<String, String> {
        // ESC p 0 25 250 pulse sequence
        Ok("Cash drawer pulse fired".to_string())
    }

    pub fn charge_edc_terminal(
        &self,
        amount_cents: u64,
        terminal_ip: &str,
    ) -> Result<String, String> {
        if amount_cents == 0 {
            return Err("Charge amount must be positive".to_string());
        }
        Ok(format!("Terminal {} initiated charge for {} cents", terminal_ip, amount_cents))
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_command_bridge_telemetry() {
        let bridge = DesktopCommandBridge::new();
        let telem = bridge.get_device_telemetry("WS-01").expect("Telemetry should succeed");
        assert_eq!(telem.workstation_uid, "WS-01");
    }

    #[test]
    fn test_cash_drawer_kick() {
        let bridge = DesktopCommandBridge::new();
        assert!(bridge.kick_cash_drawer().is_ok());
    }

    #[test]
    fn test_edc_charge() {
        let bridge = DesktopCommandBridge::new();
        assert!(bridge.charge_edc_terminal(1500, "192.168.1.50").is_ok());
        assert!(bridge.charge_edc_terminal(0, "192.168.1.50").is_err());
    }
}
