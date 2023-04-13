package steps

import (
	"encoding/json"
	"fmt"
)

type Codeblock struct {
	Content   string `json:"content"`
	Extension string `json:"extension"`
	Language  string `json:"language"`
	Source    string `json:"source"`
}

func (c *Codeblock) MarshalJSON() ([]byte, error) {
	type Alias Codeblock

	contents, err := json.Marshal(&struct {
		*Alias
	}{
		Alias: (*Alias)(c),
	})

	return []byte(fmt.Sprintf(`["code", %s]`, contents)), err
}

func (*Codeblock) Build() error {
	return nil
}

func (c *Codeblock) Text() string {
	return c.Content
}

var _ Step = &Codeblock{}
