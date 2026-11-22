//! device_binding.rs — Workstation hardware identity, telemetry and pairing.

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct WorkstationTelemetry {
    pub workstation_uid: String,
    pub os_platform: String,
    pub desktop_app_version: String,
    pub memory_free_mb: u64,
    pub is_kiosk_locked: bool,
}

pub struct DeviceBindingService;

impl DeviceBindingService {
    pub fn collect_telemetry(workstation_uid: &str, is_kiosk: bool) -> WorkstationTelemetry {
        let os = if cfg!(target_os = "windows") {
            "desktop_windows"
        } else if cfg!(target_os = "macos") {
            "desktop_macos"
        } else {
            "desktop_linux"
        };

        WorkstationTelemetry {
            workstation_uid: workstation_uid.to_string(),
            os_platform: os.to_string(),
            desktop_app_version: "0.1.0".to_string(),
            memory_free_mb: 2048,
            is_kiosk_locked: is_kiosk,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_telemetry_collection() {
        let telem = DeviceBindingService::collect_telemetry("WS-LND-01", true);
        assert_eq!(telem.workstation_uid, "WS-LND-01");
        assert!(telem.is_kiosk_locked);
        assert!(!telem.os_platform.is_empty());
    }
}
