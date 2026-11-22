package notif

import (
	"context"
	"fmt"
	"testing"
)

func TestBatchTokens(t *testing.T) {
	dispatcher := NewNotificationDispatcher(500)

	tokens := make([]string, 1250)
	for i := 0; i < 1250; i++ {
		tokens[i] = fmt.Sprintf("token_%d", i)
	}

	batches := dispatcher.BatchTokens(tokens)
	if len(batches) != 3 {
		t.Fatalf("expected 3 batches, got %d", len(batches))
	}
	if len(batches[0]) != 500 {
		t.Errorf("expected batch 0 to have 500 tokens, got %d", len(batches[0]))
	}
	if len(batches[1]) != 500 {
		t.Errorf("expected batch 1 to have 500 tokens, got %d", len(batches[1]))
	}
	if len(batches[2]) != 250 {
		t.Errorf("expected batch 2 to have 250 tokens, got %d", len(batches[2]))
	}
}

func TestDispatchRateLimit(t *testing.T) {
	dispatcher := NewNotificationDispatcher(500)
	ctx := context.Background()

	task := DispatchTask{
		TenantID: "tenant_abc",
		Priority: "CRITICAL_AUTH",
		Channel:  "PUSH",
		Tokens:   []string{"tok1", "tok2"},
	}

	sent, err := dispatcher.Dispatch(ctx, task)
	if err != nil {
		t.Fatalf("expected dispatch to succeed, got %v", err)
	}
	if sent != 2 {
		t.Fatalf("expected 2 tokens sent, got %d", sent)
	}
}
