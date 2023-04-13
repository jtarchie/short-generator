package steps

type Step interface {
	Build() error
	MarshalJSON() ([]byte, error)
	Text() string
}
type Steps []Step
