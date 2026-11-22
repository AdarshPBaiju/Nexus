package fieldcontrol

import (
	"strings"
	"testing"
)

func TestBuildSelectQuery(t *testing.T) {
	allowed := []string{"id", "tenant_id", "name", "slug", "balance"}
	requested := []string{"name", "balance", "forbidden_col"}

	query := BuildSelectQuery("branch", allowed, requested)

	if !strings.Contains(query, "name") || !strings.Contains(query, "balance") {
		t.Errorf("expected requested columns in query, got: %s", query)
	}
	if strings.Contains(query, "forbidden_col") {
		t.Errorf("unallowed column found in query: %s", query)
	}
	if !strings.Contains(query, "id") || !strings.Contains(query, "tenant_id") {
		t.Errorf("mandatory columns missing in query: %s", query)
	}
}
