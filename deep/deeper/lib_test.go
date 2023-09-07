package deeper

import (
	"testing"
)

// comment
func TestGreet(t *testing.T) {
	if Greet("world") != "hello world" {
		t.Error("greet failed")
	}
}
