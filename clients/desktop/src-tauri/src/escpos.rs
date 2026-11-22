//! escpos.rs — ESC/POS binary command encoder for thermal POS printers.

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum EscPosAlignment {
    Left = 0,
    Center = 1,
    Right = 2,
}

pub struct EscPosEncoder {
    buffer: Vec<u8>,
}

impl Default for EscPosEncoder {
    fn default() -> Self {
        Self::new()
    }
}

impl EscPosEncoder {
    pub const ESC_INIT: [u8; 2] = [0x1B, 0x40];
    pub const ESC_ALIGN: [u8; 2] = [0x1B, 0x61];
    pub const ESC_BOLD: [u8; 2] = [0x1B, 0x45];
    pub const GS_FONT_SIZE: [u8; 2] = [0x1D, 0x21];
    pub const GS_CUT_PARTIAL: [u8; 4] = [0x1D, 0x56, 0x42, 0x00];
    pub const RJ11_DRAWER_KICK: [u8; 5] = [0x1B, 0x70, 0x00, 0x19, 0xFA];

    pub fn new() -> Self {
        let mut enc = Self { buffer: Vec::new() };
        enc.init();
        enc
    }

    pub fn init(&mut self) -> &mut Self {
        self.buffer.extend_from_slice(&Self::ESC_INIT);
        self
    }

    pub fn align(&mut self, alignment: EscPosAlignment) -> &mut Self {
        self.buffer.extend_from_slice(&Self::ESC_ALIGN);
        self.buffer.push(alignment as u8);
        self
    }

    pub fn bold(&mut self, enable: bool) -> &mut Self {
        self.buffer.extend_from_slice(&Self::ESC_BOLD);
        self.buffer.push(if enable { 1 } else { 0 });
        self
    }

    pub fn font_size(&mut self, double_width: bool, double_height: bool) -> &mut Self {
        let mut byte: u8 = 0;
        if double_width {
            byte |= 0x10;
        }
        if double_height {
            byte |= 0x01;
        }
        self.buffer.extend_from_slice(&Self::GS_FONT_SIZE);
        self.buffer.push(byte);
        self
    }

    pub fn text(&mut self, content: &str) -> &mut Self {
        self.buffer.extend_from_slice(content.as_bytes());
        self
    }

    pub fn line(&mut self, content: &str) -> &mut Self {
        self.text(content);
        self.buffer.push(b'\n');
        self
    }

    pub fn feed(&mut self, lines: u8) -> &mut Self {
        for _ in 0..lines {
            self.buffer.push(b'\n');
        }
        self
    }

    pub fn cut(&mut self) -> &mut Self {
        self.feed(3);
        self.buffer.extend_from_slice(&Self::GS_CUT_PARTIAL);
        self
    }

    pub fn kick_cash_drawer(&mut self) -> &mut Self {
        self.buffer.extend_from_slice(&Self::RJ11_DRAWER_KICK);
        self
    }

    pub fn build(self) -> Vec<u8> {
        self.buffer
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_escpos_initialization() {
        let encoder = EscPosEncoder::new();
        let bytes = encoder.build();
        assert_eq!(&bytes[..2], &EscPosEncoder::ESC_INIT);
    }

    #[test]
    fn test_cash_drawer_kick_sequence() {
        let mut encoder = EscPosEncoder::new();
        encoder.kick_cash_drawer();
        let bytes = encoder.build();
        assert!(bytes.windows(5).any(|w| w == EscPosEncoder::RJ11_DRAWER_KICK));
    }

    #[test]
    fn test_cut_sequence() {
        let mut encoder = EscPosEncoder::new();
        encoder.cut();
        let bytes = encoder.build();
        assert!(bytes.windows(4).any(|w| w == EscPosEncoder::GS_CUT_PARTIAL));
    }
}
