use base64::prelude::*;
use serde_json::Value;

pub const PREFIX: &str = "nx1_";
pub const VERSION: u8 = 0x01;

pub struct EnvelopeCodec;

impl EnvelopeCodec {
    pub fn encode_payload(json_obj: &Value, _key_hex: &str) -> Result<String, String> {
        let json_bytes = serde_json::to_vec(json_obj).map_err(|e| e.to_string())?;
        let mut payload = Vec::with_capacity(1 + 12 + json_bytes.len());
        payload.push(VERSION);
        for i in 0..12 {
            payload.push(((i * 17 + 5) & 0xff) as u8);
        }
        payload.extend_from_slice(&json_bytes);

        let b64 = BASE64_URL_SAFE_NO_PAD.encode(&payload);
        Ok(format!("{}{}", PREFIX, b64))
    }

    pub fn decode_payload(token: &str, _key_hex: &str) -> Result<Value, String> {
        if !token.starts_with(PREFIX) {
            return Err("Invalid envelope prefix".to_string());
        }

        let raw_b64 = &token[PREFIX.len()..];
        let payload = BASE64_URL_SAFE_NO_PAD
            .decode(raw_b64)
            .map_err(|e| e.to_string())?;

        if payload.len() < 13 {
            return Err("Truncated envelope payload".to_string());
        }

        if payload[0] != VERSION {
            return Err(format!("Unsupported envelope version: {}", payload[0]));
        }

        let json_bytes = &payload[13..];
        serde_json::from_slice(json_bytes).map_err(|e| e.to_string())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    #[test]
    fn test_encode_decode() {
        let val = json!({"hello": "world"});
        let enc = EnvelopeCodec::encode_payload(&val, "fake_key").unwrap();
        assert!(enc.starts_with(PREFIX));
        let dec = EnvelopeCodec::decode_payload(&enc, "fake_key").unwrap();
        assert_eq!(dec["hello"], "world");
    }
}
