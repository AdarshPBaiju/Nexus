package notif

import (
	"context"
	"fmt"
	"sync"
	"time"
)

// DispatchTask represents a single or batched notification payload for Go worker.
type DispatchTask struct {
	TenantID    string
	Priority    string
	Channel     string
	Tokens      []string
	PayloadJSON []byte
}

// TokenBucketRateLimiter enforces tenant dispatch limits.
type TokenBucketRateLimiter struct {
	mu         sync.Mutex
	capacity   int
	tokens     int
	refillRate int
	lastRefill time.Time
}

// NewTokenBucket creates a new token bucket with specified capacity and refill rate per second.
func NewTokenBucket(capacity int, refillRate int) *TokenBucketRateLimiter {
	return &TokenBucketRateLimiter{
		capacity:   capacity,
		tokens:     capacity,
		refillRate: refillRate,
		lastRefill: time.Now(),
	}
}

// Allow checks if a token is available and consumes it.
func (tb *TokenBucketRateLimiter) Allow() bool {
	tb.mu.Lock()
	defer tb.mu.Unlock()

	now := time.Now()
	elapsed := now.Sub(tb.lastRefill).Seconds()
	tb.tokens += int(elapsed * float64(tb.refillRate))
	if tb.tokens > tb.capacity {
		tb.tokens = tb.capacity
	}
	tb.lastRefill = now

	if tb.tokens > 0 {
		tb.tokens--
		return true
	}
	return false
}

// NotificationDispatcher orchestrates high-fanout FCM multicast and high-priority queues.
type NotificationDispatcher struct {
	maxBatchSize int
	limiters     sync.Map
}

// NewNotificationDispatcher creates a dispatcher instance.
func NewNotificationDispatcher(maxBatchSize int) *NotificationDispatcher {
	if maxBatchSize <= 0 || maxBatchSize > 500 {
		maxBatchSize = 500
	}
	return &NotificationDispatcher{
		maxBatchSize: maxBatchSize,
	}
}

// BatchTokens partitions a slice of FCM/APNs tokens into chunks of up to maxBatchSize.
func (d *NotificationDispatcher) BatchTokens(tokens []string) [][]string {
	if len(tokens) == 0 {
		return nil
	}
	var batches [][]string
	for i := 0; i < len(tokens); i += d.maxBatchSize {
		end := i + d.maxBatchSize
		if end > len(tokens) {
			end = len(tokens)
		}
		batches = append(batches, tokens[i:end])
	}
	return batches
}

// Dispatch executes dispatch under rate limit guard.
func (d *NotificationDispatcher) Dispatch(ctx context.Context, task DispatchTask) (int, error) {
	if task.TenantID == "" {
		return 0, fmt.Errorf("tenantID is required")
	}

	val, _ := d.limiters.LoadOrStore(task.TenantID, NewTokenBucket(100, 50))
	limiter := val.(*TokenBucketRateLimiter)
	if !limiter.Allow() {
		return 0, fmt.Errorf("rate limit exceeded for tenant %s", task.TenantID)
	}

	batches := d.BatchTokens(task.Tokens)
	sentCount := 0
	for _, batch := range batches {
		sentCount += len(batch)
	}
	return sentCount, nil
}
