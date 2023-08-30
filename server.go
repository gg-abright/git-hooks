package main

import (
	"fmt"

	"github.com/gg-abright/githooks/deep/deeper"
	"github.com/gg-abright/githooks/nest"
)

func main() {
	fmt.Println(nest.Greet("world"))
	fmt.Println(deeper.Greet("world"))

	fmt.Println("extra")
}
