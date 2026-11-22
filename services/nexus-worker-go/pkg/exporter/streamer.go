package exporter

import (
	"bytes"
	"encoding/csv"
	"strings"
)

var dangerousPrefixes = []string{"=", "+", "-", "@", "|", "%"}

// SanitizeCellValue escapes dangerous spreadsheet formula triggers.
func SanitizeCellValue(val string) string {
	trimmed := strings.TrimSpace(val)
	for _, p := range dangerousPrefixes {
		if strings.HasPrefix(trimmed, p) {
			return "'" + val
		}
	}
	return val
}

// StreamCSVChunk serializes rows with formula sanitization.
func StreamCSVChunk(headers []string, rows [][]string) ([]byte, error) {
	var buf bytes.Buffer
	writer := csv.NewWriter(&buf)

	if err := writer.Write(headers); err != nil {
		return nil, err
	}

	for _, row := range rows {
		sanitizedRow := make([]string, len(row))
		for i, cell := range row {
			sanitizedRow[i] = SanitizeCellValue(cell)
		}
		if err := writer.Write(sanitizedRow); err != nil {
			return nil, err
		}
	}

	writer.Flush()
	return buf.Bytes(), writer.Error()
}
