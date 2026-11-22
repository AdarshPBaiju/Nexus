// Package db provides tenant-scoped database isolation and row-level security.
package db

import (
	"context"
	"fmt"
)

// QueryExecutor defines the interface for running queries on an active DB pool or transaction.
type QueryExecutor interface {
	Exec(ctx context.Context, sql string, arguments ...any) error
}

// TenantTransaction executes a callback within an isolated PostgreSQL RLS session.
// Sets LOCAL app.current_tenant_id for the duration of the transaction.
func TenantTransaction(ctx context.Context, exec QueryExecutor, tenantID string, fn func(ctx context.Context) error) error {
	if tenantID == "" {
		return fmt.Errorf("tenantID cannot be empty")
	}

	setSQL := fmt.Sprintf("SELECT set_config('app.current_tenant_id', '%s', true)", tenantID)
	if err := exec.Exec(ctx, setSQL); err != nil {
		return fmt.Errorf("failed to set tenant RLS context: %w", err)
	}

	return fn(ctx)
}
