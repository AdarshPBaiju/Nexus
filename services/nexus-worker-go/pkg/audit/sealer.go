// Package audit provides cryptographic receipt sealing and audit chaining.
package audit

import (
	"crypto/sha256"
	"encoding/hex"
)

const GenesisHash = "0000000000000000000000000000000000000000000000000000000000000000"

// ComputeEntrySHA256 computes the SHA-256 hex digest of raw payload.
func ComputeEntrySHA256(payload []byte) string {
	hash := sha256.Sum256(payload)
	return hex.EncodeToString(hash[:])
}

// ComputeChainedHash computes cumulative chained hash: SHA256(prevHash || entrySHA256).
func ComputeChainedHash(prevHash, entrySHA256 string) string {
	combined := []byte(prevHash + entrySHA256)
	hash := sha256.Sum256(combined)
	return hex.EncodeToString(hash[:])
}

// ComputeMerkleRoot calculates the pairwise Merkle root hash for a slice of leaf hashes.
func ComputeMerkleRoot(hashes []string) string {
	if len(hashes) == 0 {
		return GenesisHash
	}
	current := make([]string, len(hashes))
	copy(current, hashes)

	for len(current) > 1 {
		var next []string
		for i := 0; i < len(current); i += 2 {
			left := current[i]
			right := left
			if i+1 < len(current) {
				right = current[i+1]
			}
			combined := []byte(left + right)
			h := sha256.Sum256(combined)
			next = append(next, hex.EncodeToString(h[:]))
		}
		current = next
	}
	return current[0]
}

// SealBatch computes the Merkle root and chained hash for an ordered slice of entry hashes.
func SealBatch(prevAnchorHash string, entryHashes []string) (string, string) {
	merkleRoot := ComputeMerkleRoot(entryHashes)
	chainHash := prevAnchorHash
	for _, entryHash := range entryHashes {
		chainHash = ComputeChainedHash(chainHash, entryHash)
	}
	return merkleRoot, chainHash
}
