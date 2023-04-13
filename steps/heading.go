package steps

import (
	"encoding/json"
	"fmt"
)

type Heading struct {
	Content string `json:"content"`
}

func (h *Heading) MarshalJSON() ([]byte, error) {
	type Alias Heading

	contents, err := json.Marshal(&struct {
		*Alias
	}{
		Alias: (*Alias)(h),
	})

	return []byte(fmt.Sprintf(`["heading", %s]`, contents)), err
}

func (*Heading) Build() error {
	return nil
}

func (h *Heading) Text() string {
	return h.Content
}

var _ Step = &Heading{}
