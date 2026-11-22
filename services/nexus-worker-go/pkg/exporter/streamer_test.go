package exporter

import (
	"strings"
	"testing"
)

func TestSanitizeCellValue(t *testing.T) {
	tests := []struct {
		input    string
		expected string
	}{
		{"=cmd|' /C calc'!A0", "'=cmd|' /C calc'!A0"},
		{"+1234", "'+1234"},
		{"-9999", "'-9999"},
		{"@SUM(A1:A10)", "'@SUM(A1:A10)"},
		{"Normal Text", "Normal Text"},
	}

	for _, tt := range tests {
		res := SanitizeCellValue(tt.input)
		if res != tt.expected {
			t.Errorf("SanitizeCellValue(%q) = %q; expected %q", tt.input, res, tt.expected)
		}
	}
}

func TestStreamCSVChunk(t *testing.T) {
	headers := []string{"ID", "FormulaPayload"}
	rows := [][]string{
		{"1", "=cmd|calc"},
		{"2", "SafeValue"},
	}

	data, err := StreamCSVChunk(headers, rows)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	out := string(data)
	if !strings.Contains(out, "'=cmd|calc") {
		t.Errorf("expected escaped formula in CSV, got: %s", out)
	}
}
