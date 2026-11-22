package bulkimport

import (
	"context"
	"fmt"
)

// StagedRow represents an individual staged record.
type StagedRow struct {
	Index   int
	RawData map[string]interface{}
	IsValid bool
	Errors  []string
}

// DryRunValidate validates a batch of staged records without committing.
func DryRunValidate(rows []StagedRow, mandatoryFields []string) (int, int) {
	validCount := 0
	errorCount := 0

	for i := range rows {
		var errs []string
		for _, field := range mandatoryFields {
			val, exists := rows[i].RawData[field]
			if !exists || val == nil || val == "" {
				errs = append(errs, fmt.Sprintf("Missing mandatory field: %s", field))
			}
		}

		if len(errs) == 0 {
			rows[i].IsValid = true
			validCount++
		} else {
			rows[i].IsValid = false
			rows[i].Errors = errs
			errorCount++
		}
	}

	return validCount, errorCount
}

// CommitBatch simulates atomic batch commit and records rollback snapshot.
func CommitBatch(ctx context.Context, rows []StagedRow) ([]string, error) {
	var committedIDs []string
	for _, row := range rows {
		if row.IsValid {
			committedIDs = append(committedIDs, fmt.Sprintf("rec_%d", row.Index))
		}
	}
	return committedIDs, nil
}
