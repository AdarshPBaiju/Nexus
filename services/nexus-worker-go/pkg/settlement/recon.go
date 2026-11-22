package settlement

import (
	"fmt"
	"math"
)

// ReconciliationRecord holds transaction and payout data for matching.
type ReconciliationRecord struct {
	TransactionID   string
	ExpectedAmount  float64
	SettledGross    float64
	SettledFee      float64
	SettledNet      float64
}

// ReconciliationResult summarizes settlement reconciliation audit outcomes.
type ReconciliationResult struct {
	MatchedCount     int
	VarianceCount    int
	TotalFeeVariance float64
}

// SettlementReconciler reconciles gateway settlement files with recorded payment intents.
type SettlementReconciler struct {
	tolerance float64
}

// NewSettlementReconciler creates a new reconciler with floating point comparison tolerance.
func NewSettlementReconciler(tolerance float64) *SettlementReconciler {
	if tolerance <= 0 {
		tolerance = 0.0001
	}
	return &SettlementReconciler{tolerance: tolerance}
}

// Reconcile audits records and detects discrepancies.
func (r *SettlementReconciler) Reconcile(records []ReconciliationRecord) (ReconciliationResult, error) {
	if len(records) == 0 {
		return ReconciliationResult{}, fmt.Errorf("no reconciliation records provided")
	}

	result := ReconciliationResult{}
	for _, rec := range records {
		expectedNet := rec.SettledGross - rec.SettledFee
		if math.Abs(expectedNet-rec.SettledNet) > r.tolerance {
			result.VarianceCount++
			result.TotalFeeVariance += math.Abs(expectedNet - rec.SettledNet)
			continue
		}

		if math.Abs(rec.ExpectedAmount-rec.SettledGross) > r.tolerance {
			result.VarianceCount++
			continue
		}

		result.MatchedCount++
	}
	return result, nil
}
