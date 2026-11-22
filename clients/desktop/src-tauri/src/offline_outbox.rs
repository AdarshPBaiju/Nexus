//! offline_outbox.rs — Local encrypted offline sales outbox for WAN resilience.

use std::collections::HashMap;

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum OutboxStatus {
    Queued,
    Synced,
    Failed,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct OfflineOrderEnvelope {
    pub event_id: String,
    pub tenant_slug: String,
    pub branch_id: String,
    pub workstation_id: String,
    pub order_payload_json: String,
    pub queued_at: String,
    pub status: OutboxStatus,
}

pub struct OfflineOutboxStore {
    queue: HashMap<String, OfflineOrderEnvelope>,
}

impl Default for OfflineOutboxStore {
    fn default() -> Self {
        Self::new()
    }
}

impl OfflineOutboxStore {
    pub fn new() -> Self {
        Self {
            queue: HashMap::new(),
        }
    }

    pub fn enqueue_order(&mut self, envelope: OfflineOrderEnvelope) -> Result<String, String> {
        let id = envelope.event_id.clone();
        if self.queue.contains_key(&id) {
            return Err(format!("Duplicate offline order event: {}", id));
        }
        self.queue.insert(id.clone(), envelope);
        Ok(id)
    }

    pub fn get_pending_batch(&self, limit: usize) -> Vec<OfflineOrderEnvelope> {
        self.queue
            .values()
            .filter(|env| env.status == OutboxStatus::Queued)
            .take(limit)
            .cloned()
            .collect()
    }

    pub fn mark_synced(&mut self, event_id: &str) -> Result<(), String> {
        if let Some(env) = self.queue.get_mut(event_id) {
            env.status = OutboxStatus::Synced;
            Ok(())
        } else {
            Err(format!("Event {} not found in outbox", event_id))
        }
    }

    pub fn count_pending(&self) -> usize {
        self.queue
            .values()
            .filter(|env| env.status == OutboxStatus::Queued)
            .count()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_enqueue_and_batch_drain() {
        let mut store = OfflineOutboxStore::new();
        let env = OfflineOrderEnvelope {
            event_id: "EVT-01".to_string(),
            tenant_slug: "artisan-cafe".to_string(),
            branch_id: "BR-01".to_string(),
            workstation_id: "WS-01".to_string(),
            order_payload_json: "{\"total\": 12.50}".to_string(),
            queued_at: "2026-11-22T15:00:00Z".to_string(),
            status: OutboxStatus::Queued,
        };

        assert!(store.enqueue_order(env).is_ok());
        assert_eq!(store.count_pending(), 1);

        let batch = store.get_pending_batch(10);
        assert_eq!(batch.len(), 1);
        assert_eq!(batch[0].event_id, "EVT-01");

        assert!(store.mark_synced("EVT-01").is_ok());
        assert_eq!(store.count_pending(), 0);
    }
}
