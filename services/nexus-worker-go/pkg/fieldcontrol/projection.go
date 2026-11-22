// Package fieldcontrol handles strict attribute-level masking.
package fieldcontrol

import (
	"strings"
)

// BuildSelectQuery generates a SQL SELECT fragment containing only asked columns.
func BuildSelectQuery(tableName string, allowedColumns []string, requestedColumns []string) string {
	allowedMap := make(map[string]bool, len(allowedColumns))
	for _, col := range allowedColumns {
		allowedMap[col] = true
	}

	// Always mandate id and tenant_id
	selected := []string{"id", "tenant_id"}
	seen := map[string]bool{"id": true, "tenant_id": true}

	for _, col := range requestedColumns {
		if allowedMap[col] && !seen[col] {
			selected = append(selected, col)
			seen[col] = true
		}
	}

	return "SELECT " + strings.Join(selected, ", ") + " FROM " + tableName
}
