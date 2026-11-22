package audit

import (
	"testing"
)

func TestMerkleRootAndChaining(t *testing.T) {
	hashes := []string{
		"1111111111111111111111111111111111111111111111111111111111111111",
		"2222222222222222222222222222222222222222222222222222222222222222",
	}

	root := ComputeMerkleRoot(hashes)
	if len(root) != 64 {
		t.Fatalf("expected 64 char hex root, got %d", len(root))
	}

	merkleRoot, finalChain := SealBatch(GenesisHash, hashes)
	if merkleRoot != root {
		t.Errorf("expected %s, got %s", root, merkleRoot)
	}
	if len(finalChain) != 64 {
		t.Errorf("expected 64 char final chain, got %s", finalChain)
	}
}
