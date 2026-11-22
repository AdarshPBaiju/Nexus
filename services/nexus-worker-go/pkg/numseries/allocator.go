// Package numseries handles lock-free monotonic number series allocation.
package numseries

// ReserveBlockBatch allocates a contiguous slice of sequence numbers.
func ReserveBlockBatch(startVal int, count int) []int {
	if count <= 0 {
		return []int{}
	}
	block := make([]int, count)
	for i := 0; i < count; i++ {
		block[i] = startVal + i
	}
	return block
}
