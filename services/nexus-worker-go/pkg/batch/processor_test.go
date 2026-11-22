package batch

import (
	"context"
	"testing"
)

func TestBatchExportProcessor(t *testing.T) {
	processor := NewBatchExportProcessor("nexus-exports-temp")

	payload := ExportTaskPayload{
		TenantID:   "tenant-test-01",
		TaskID:     "task-uuid-001",
		EntityType: "orders",
		Columns:    []string{"id", "total_amount", "status", "created_at"},
		TotalRows:  10000,
	}

	res, err := processor.ProcessExport(context.Background(), payload)
	if err != nil {
		t.Fatalf("expected export to succeed, got: %v", err)
	}

	if res.ByteCount <= 0 {
		t.Errorf("expected non-zero byte count, got %d", res.ByteCount)
	}

	if res.ObjectKey != "exports/tenant-test-01/task-uuid-001.csv" {
		t.Errorf("unexpected object key: %s", res.ObjectKey)
	}
}
