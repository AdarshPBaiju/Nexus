package numseries

import (
	"testing"
)

func TestReserveBlockBatch(t *testing.T) {
	batch := ReserveBlockBatch(1001, 5)
	if len(batch) != 5 {
		t.Fatalf("expected 5 items, got %d", len(batch))
	}
	if batch[0] != 1001 || batch[4] != 1005 {
		t.Errorf("expected range 1001-1005, got [%d, %d]", batch[0], batch[4])
	}
}
