package bulkimport

import (
	"context"
	"testing"
)

func TestDryRunValidateAndCommit(t *testing.T) {
	rows := []StagedRow{
		{
			Index:   0,
			RawData: map[string]interface{}{"name": "Croissant", "price": "3.50"},
		},
		{
			Index:   1,
			RawData: map[string]interface{}{"name": "", "price": "4.00"},
		},
	}

	mandatory := []string{"name", "price"}
	valid, errors := DryRunValidate(rows, mandatory)

	if valid != 1 || errors != 1 {
		t.Fatalf("expected 1 valid and 1 error, got %d valid, %d errors", valid, errors)
	}

	committed, err := CommitBatch(context.Background(), rows)
	if err != nil {
		t.Fatalf("unexpected commit error: %v", err)
	}
	if len(committed) != 1 {
		t.Errorf("expected 1 committed record, got %d", len(committed))
	}
}
