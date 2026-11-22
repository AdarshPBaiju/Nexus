// Package pdfrender provides thermal receipt AST compiling and rendering.
package pdfrender

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"strings"
)

// ReceiptHeader matches AST header block.
type ReceiptHeader struct {
	Name    string `json:"name"`
	TaxID   string `json:"tax_id"`
	Address string `json:"address"`
	Phone   string `json:"phone"`
}

// ReceiptMetadata matches AST metadata block.
type ReceiptMetadata struct {
	DocumentNumber string `json:"document_number"`
	OrderToken     string `json:"order_token"`
	CashierName    string `json:"cashier_name"`
	IssuedAt       string `json:"issued_at"`
}

// ReceiptLineItem represents an itemized line item.
type ReceiptLineItem struct {
	Name      string   `json:"name"`
	Quantity  string   `json:"quantity"`
	UnitPrice string   `json:"unit_price"`
	Modifiers []string `json:"modifiers"`
	LineTotal string   `json:"line_total"`
}

// ReceiptTaxLine represents an itemized tax breakdown.
type ReceiptTaxLine struct {
	RatePercent   string `json:"rate_percent"`
	TaxableAmount string `json:"taxable_amount"`
	TaxAmount     string `json:"tax_amount"`
	Label         string `json:"label"`
}

// ReceiptTender represents tender payment details.
type ReceiptTender struct {
	Type     string `json:"type"`
	Tendered string `json:"tendered"`
	Change   string `json:"change"`
}

// ReceiptTotals represents the financial totals block.
type ReceiptTotals struct {
	Subtotal   string           `json:"subtotal"`
	Discount   string           `json:"discount"`
	Taxes      []ReceiptTaxLine `json:"taxes"`
	GrandTotal string           `json:"grand_total"`
	Tenders    []ReceiptTender  `json:"tenders"`
}

// ReceiptFooter represents footer and QR payload.
type ReceiptFooter struct {
	WiFi      string `json:"wifi"`
	Notice    string `json:"notice"`
	QRPayload string `json:"qr_payload"`
}

// ReceiptAst represents the complete normalized receipt document AST.
type ReceiptAst struct {
	Version   string          `json:"version"`
	Type      string          `json:"type"`
	Header    ReceiptHeader   `json:"header"`
	Metadata  ReceiptMetadata `json:"metadata"`
	LineItems []ReceiptLineItem `json:"line_items"`
	Totals    ReceiptTotals   `json:"totals"`
	Footer    ReceiptFooter   `json:"footer"`
	Digest    string          `json:"digest"`
}

// Renderer compiles Receipt AST into thermal printable HTML and verifies cryptographic integrity.
type Renderer struct{}

// NewRenderer creates a new receipt document renderer.
func NewRenderer() *Renderer {
	return &Renderer{}
}

// RenderHTML generates a lightweight, 80mm-width receipt HTML representation.
func (r *Renderer) RenderHTML(ast *ReceiptAst) (string, error) {
	if ast == nil {
		return "", fmt.Errorf("receipt AST cannot be nil")
	}

	var sb strings.Builder
	sb.WriteString("<!DOCTYPE html><html><head><meta charset='utf-8'>")
	sb.WriteString("<style>body{font-family:monospace;width:80mm;margin:0 auto;padding:8px;font-size:12px;}")
	sb.WriteString(".center{text-align:center;}.bold{font-weight:bold;}.row{display:flex;justify-content:space-between;}")
	sb.WriteString(".divider{border-bottom:1px dashed #000;margin:6px 0;}</style></head><body>")

	// Header
	sb.WriteString(fmt.Sprintf("<div class='center bold'>%s</div>", ast.Header.Name))
	sb.WriteString(fmt.Sprintf("<div class='center'>Tax ID: %s</div>", ast.Header.TaxID))
	sb.WriteString(fmt.Sprintf("<div class='center'>%s</div>", ast.Header.Address))
	sb.WriteString("<div class='divider'></div>")

	// Metadata
	sb.WriteString(fmt.Sprintf("<div class='row'><span>Doc: %s</span><span>Token: %s</span></div>",
		ast.Metadata.DocumentNumber, ast.Metadata.OrderToken))
	sb.WriteString(fmt.Sprintf("<div class='row'><span>Cashier: %s</span><span>%s</span></div>",
		ast.Metadata.CashierName, ast.Metadata.IssuedAt))
	sb.WriteString("<div class='divider'></div>")

	// Items
	for _, it := range ast.LineItems {
		sb.WriteString(fmt.Sprintf("<div class='row'><span>%s x%s</span><span>%s</span></div>",
			it.Name, it.Quantity, it.LineTotal))
	}
	sb.WriteString("<div class='divider'></div>")

	// Totals
	sb.WriteString(fmt.Sprintf("<div class='row bold'><span>TOTAL</span><span>%s</span></div>",
		ast.Totals.GrandTotal))
	sb.WriteString("<div class='divider'></div>")

	// Footer
	sb.WriteString(fmt.Sprintf("<div class='center'>%s</div>", ast.Footer.Notice))
	if ast.Footer.WiFi != "" {
		sb.WriteString(fmt.Sprintf("<div class='center'>Wi-Fi: %s</div>", ast.Footer.WiFi))
	}
	sb.WriteString("</body></html>")

	return sb.String(), nil
}

// VerifyHash checks if the provided canonical JSON matches the SHA-256 digest.
func (r *Renderer) VerifyHash(canonicalJSON []byte, expectedHash string) bool {
	sum := sha256.Sum256(canonicalJSON)
	computed := hex.EncodeToString(sum[:])
	return computed == expectedHash
}

// ParseAst deserializes JSON bytes into a strongly typed ReceiptAst.
func (r *Renderer) ParseAst(data []byte) (*ReceiptAst, error) {
	var ast ReceiptAst
	if err := json.Unmarshal(data, &ast); err != nil {
		return nil, fmt.Errorf("failed to parse receipt ast: %w", err)
	}
	return &ast, nil
}
