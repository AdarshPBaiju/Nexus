//! protocol.rs — OS Custom Protocol Handler for `nexus://` deep-links.

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ProtocolLaunchIntent {
    pub tenant_slug: String,
    pub route: String,
    pub workstation_id: Option<String>,
}

pub struct ProtocolRouter;

impl ProtocolRouter {
    pub fn parse_url(raw_url: &str) -> Result<ProtocolLaunchIntent, String> {
        if !raw_url.starts_with("nexus://") {
            return Err("Invalid protocol scheme: must start with nexus://".to_string());
        }

        let without_scheme = &raw_url["nexus://".len()..];
        let mut parts = without_scheme.splitn(2, '?');
        let action = parts.next().unwrap_or("");

        if action != "open" {
            return Err(format!("Unsupported action '{}': expected 'open'", action));
        }

        let query_str = parts.next().unwrap_or("");
        let mut tenant = None;
        let mut route = None;
        let mut workstation = None;

        for pair in query_str.split('&') {
            if pair.is_empty() {
                continue;
            }
            let mut kv = pair.splitn(2, '=');
            let key = kv.next().unwrap_or("");
            let val = kv.next().unwrap_or("");
            match key {
                "tenant" => tenant = Some(val.to_string()),
                "route" => route = Some(val.to_string()),
                "workstation" => workstation = Some(val.to_string()),
                _ => {}
            }
        }

        let tenant_slug =
            tenant.ok_or_else(|| "Missing required query parameter: tenant".to_string())?;
        let route_str = route.unwrap_or_else(|| "/pos".to_string());

        Ok(ProtocolLaunchIntent {
            tenant_slug,
            route: route_str,
            workstation_id: workstation,
        })
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_valid_protocol_parsing() {
        let uri = "nexus://open?tenant=artisan-coffee&route=/pos/counter&workstation=POS-01";
        let intent = ProtocolRouter::parse_url(uri).expect("Should parse valid uri");
        assert_eq!(intent.tenant_slug, "artisan-coffee");
        assert_eq!(intent.route, "/pos/counter");
        assert_eq!(intent.workstation_id, Some("POS-01".to_string()));
    }

    #[test]
    fn test_missing_tenant_fails() {
        let uri = "nexus://open?route=/pos";
        assert!(ProtocolRouter::parse_url(uri).is_err());
    }

    #[test]
    fn test_invalid_scheme_fails() {
        let uri = "https://open?tenant=test";
        assert!(ProtocolRouter::parse_url(uri).is_err());
    }
}
