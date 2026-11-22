package pdfrender

import (
	"testing"
)

func TestRenderer_RenderHTMLAndParse(t *testing.T) {
	r := NewRenderer()

	astJSON := []byte(`{
		"version": "1.0",
		"type": "RECEIPT_THERMAL",
		"header": {
			"name": "Nexus Artisan Cafe",
			"tax_id": "GST-123456",
			"address": "123 Coffee Lane",
			"phone": "+1-555-0199"
		},
		"metadata": {
			"document_number": "REC-2026-0001",
			"order_token": "#042",
			"cashier_name": "Alice",
			"issued_at": "2026-11-22T12:00:00Z"
		},
		"line_items": [
			{
				"name": "Espresso Double",
				"quantity": "1",
				"unit_price": "3.50",
				"modifiers": [],
				"line_total": "3.50"
			}
		],
		"totals": {
			"subtotal": "3.50",
			"discount": "0.00",
			"taxes": [
				{
					"rate_percent": "5.00",
					"taxable_amount": "3.50",
					"tax_amount": "0.18",
					"label": "GST 5%"
				}
			],
			"grand_total": "3.68",
			"tenders": [
				{
					"type": "CASH",
					"tendered": "5.00",
					"change": "1.32"
				}
			]
		},
		"footer": {
			"wifi": "NexusGuest",
			"notice": "Thank you for dining with us!",
			"qr_payload": "https://verify.nexus.internal/receipt/REC-2026-0001/"
		},
		"digest": "abc123"
	}`)

	ast, err := r.ParseAst(astJSON)
	if err != nil {
		t.Fatalf("ParseAst failed: %v", err)
	}

	html, err := r.RenderHTML(ast)
	if err != nil {
		t.Fatalf("RenderHTML failed: %v", err)
	}

	if len(html) == 0 {
		t.Fatal("Expected non-empty HTML output")
	}

	// Verify cryptographic hash check
	valid := r.VerifyHash([]byte("hello world"), "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9")
	if !valid {
		t.Fatal("Expected hash verification to succeed for known sha256")
	}
}
