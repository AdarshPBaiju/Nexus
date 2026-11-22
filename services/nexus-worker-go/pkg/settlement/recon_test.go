package settlement

import (
	"testing"
)

func TestSettlementReconciliation(t *testing.T) {
	reconciler := NewSettlementReconciler(0.001)

	records := []ReconciliationRecord{
		{
			TransactionID:  "tx_1",
			ExpectedAmount: 100.0,
			SettledGross:   100.0,
			SettledFee:     2.9,
			SettledNet:     97.1,
		},
		{
			TransactionID:  "tx_2_variance",
			ExpectedAmount: 50.0,
			SettledGross:   50.0,
			SettledFee:     1.5,
			SettledNet:     45.0, // Variance: 50 - 1.5 = 48.5 != 45.0
		},
	}

	res, err := reconciler.Reconcile(records)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	if res.MatchedCount != 1 {
		t.Errorf("expected 1 matched, got %d", res.MatchedCount)
	}
	if res.VarianceCount != 1 {
		t.Errorf("expected 1 variance, got %d", res.VarianceCount)
	}
}
