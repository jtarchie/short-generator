package extension

import (
	_ "embed"
	"encoding/json"
	"fmt"
	"strings"
)

//go:embed source.json
var source []byte

type Language struct {
	Name       string   `json:"name"`
	Type       string   `json:"type"`
	Extensions []string `json:"extensions"`
}

func FromLanguageToExtension(name string) (string, error) {
	var languages []Language

	err := json.Unmarshal(source, &languages)
	if err != nil {
		return "", fmt.Errorf("could not parse sources: %w", err)
	}

	name = strings.ToLower(name)

	for _, language := range languages {
		if strings.HasPrefix(strings.ToLower(language.Name), name) {
			return language.Extensions[0], nil
		}
	}

	return "", fmt.Errorf("could not find language %s", name)
}
