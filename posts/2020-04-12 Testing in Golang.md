- tags: [golang](/tags.md#golang)
- date: 2020-04-12

# Testing in Golang

Golang has a default command `go test` to run test code like junit. `go test` will think of the package as a basic unit. Of course you can specify the source files you run, that filename endswith "_test.go". And testing function always signed like `func TestXXX(t testing.T)`.

## Run a test

```go
// main.go
func Add(a int, b int) int {
	return a + b
}

// main_test.go
func TestAdd(t *testing.T) {
    sum := Add(1, 1)
    if sum != 2 {
        t.Fatalf("1 and 1 is: 2, but your answer is: %d", sum)
    }
}

```

Then run `go test` will invoke a compilling of package current directory and run all test function in '_test.go' file on by one.

`go test` has two mode:

1. **local directory mode**: run `go test` or `go test -v` directly. In this mode, caching is disabled. go test will print the summary of result ('ok' or 'FAIL' follwed by package name) after tests finish.
2. **package list mode**: specify the package (like `go test match`,`go test ./...`,even `go test .`) will be tested can enter this mode. go test will cache the test result. In next test run, go test will redisplay the previous output instead of return the binary.

To disable the test cache, you can specify any flag or argument other than the cacheable flags(-cpu, -list, -run -parallel, -short, -v). The idiomatic way is to use `-count=1`.

## TestMain function

Every package can setup a `TestMain` function. It will be called before all TestCase functions. A sample TestMain looks like:

```go
func TestMain(m *testing.M) {
    fmt.Println("======== before test")
    code := m.Run()
    fmt.Println("======== after test")
    os.Exit(code)
}

```

## Specify the single file or function

go test support running test with only one file or one function, command is like:

```bash
go test -file main_test.go
# or
go test main_test.go

go test -run="TestXXX"

```

## Benchmark test

Benchmark test can be used to examine the performance of your go code. Benchmark test's function name must start with Benchmark like `BenchmarkXXX`. Others are like normal testing function.

```go
func BenchmarkAdd(b *testing.B) {
    sum := Add(1, 1)
    if sum != 2 {
        b.Fatalf("1 and 1 is: 2, but your answer is: %d", sum)
    }
}

```

Benchmark tests are run several times by testing package. the value of `b.N` will increase each time until the runner satisfied with the stability of the benchmark. Pass the `-bench` flag value of a valid regular regex. You can also specify `-run` flag to run exact function.

```bash
> main go test -bench=.
======== before test
goos: darwin
goarch: amd64
BenchmarkAdd-12         1000000000               0.000000 ns/op
PASS
======== after test
ok      _/Users/qiqi/Downloads/main     1.428s

```

Test result show the final b.N interactions and average run time each loop.

## Asserts

A golang assertion library [stretchr/testify](https://github.com/stretchr/testify/) provide some common assertions and mocks that plays nicely with the standard library.