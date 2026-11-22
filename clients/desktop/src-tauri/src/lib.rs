//! lib.rs — Nexus Desktop Runtime Shell library (Tauri 2.0).

pub mod commands;
pub mod device_binding;
pub mod escpos;
pub mod offline_outbox;
pub mod print_spooler;
pub mod protocol;

pub use commands::DesktopCommandBridge;
pub use device_binding::{DeviceBindingService, WorkstationTelemetry};
pub use escpos::{EscPosAlignment, EscPosEncoder};
pub use offline_outbox::{OfflineOrderEnvelope, OfflineOutboxStore, OutboxStatus};
pub use print_spooler::{DesktopPrintSpooler, PrintJob, PrinterTransport};
pub use protocol::{ProtocolLaunchIntent, ProtocolRouter};
