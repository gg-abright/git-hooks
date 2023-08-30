package deeper

import (
	"testing"
)

func TestGreet(t *testing.T) {
	if Greet("world") != "hello world" {
		t.Error("greet failed")
	}
}
