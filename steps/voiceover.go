package steps

import (
	"encoding/json"
	"fmt"
)

type Voiceover struct {
	Content string `json:"content"`
}

func (v *Voiceover) MarshalJSON() ([]byte, error) {
	type Alias Voiceover

	contents, err := json.Marshal(&struct {
		*Alias
	}{
		Alias: (*Alias)(v),
	})

	return []byte(fmt.Sprintf(`["voiceover", %s]`, contents)), err
}

func (*Voiceover) Build() error {
	return nil
}

func (v *Voiceover) Text() string {
	return v.Content
}

var _ Step = &Voiceover{}
