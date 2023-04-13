package main

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"strings"

	"github.com/alecthomas/kong"
	"github.com/jtarchie/short-generator/extension"
	"github.com/jtarchie/short-generator/steps"
	"github.com/yuin/goldmark"
	"github.com/yuin/goldmark/ast"
	"github.com/yuin/goldmark/text"
)

type CLI struct {
	Filename  string `type:"existingfile" help:"markdown document to generate script for" required:""`
	OutputDir string `type:"path" help:"output directory for all the artifacts" required:""`
}

func (c *CLI) Run() error {
	err := os.MkdirAll(c.OutputDir, os.ModePerm)
	if err != nil {
		return fmt.Errorf("could not create output directory: %w", err)
	}

	contents, err := os.ReadFile(c.Filename)
	if err != nil {
		return fmt.Errorf("could not open file: %w", err)
	}

	steps, err := markdownToSteps(contents)
	if err != nil {
		return fmt.Errorf("could not convert markdown to steps: %w", err)
	}

	for index, step := range steps {
		err := step.Build()
		if err != nil {
			return fmt.Errorf("could not build %d: %w", index, err)
		}
	}

	outputPath := filepath.Join(c.OutputDir, "script.json")

	file, err := os.Create(outputPath)
	if err != nil {
		return fmt.Errorf("could not create script file: %w", err)
	}
	defer file.Close()

	encoder := json.NewEncoder(file)
	encoder.SetIndent("", "  ")

	err = encoder.Encode(steps)
	if err != nil {
		return fmt.Errorf("could not encode JSON: %w", err)
	}

	return nil
}

func nodeToLines(v ast.Node, source []byte) string {
	var lines []string

	for i := 0; i < v.Lines().Len(); i++ {
		line := v.Lines().At(i)
		lines = append(lines, string(line.Value(source)))
	}

	return strings.Join(lines, "")
}

func markdownToSteps(source []byte) (steps.Steps, error) {
	var s steps.Steps

	markdown := goldmark.New(goldmark.WithExtensions())
	node := markdown.Parser().Parse(text.NewReader(source))

	err := ast.Walk(node, func(n ast.Node, entering bool) (ast.WalkStatus, error) {
		if entering {
			switch v := n.(type) {
			case *ast.Heading:
				if v.Level == 1 {
					header := string(v.Text(source))
					header = strings.ReplaceAll(header, ":", "\n")
					s = append(s, &steps.Heading{
						Content: header,
					})
				}
			case *ast.Paragraph:
				s = append(s, &steps.Voiceover{
					Content: nodeToLines(v, source),
				})
			case *ast.FencedCodeBlock:
				previousStep := s[len(s)-1]
				s = s[:len(s)-1]

				language := string(v.Language(source))
				ext, err := extension.FromLanguageToExtension(language)
				if err != nil {
					return ast.WalkStop, fmt.Errorf("could not find extension: %w", err)
				}

				s = append(s, &steps.Codeblock{
					Content:   previousStep.Text(),
					Extension: ext,
					Language:  language,
					Source:    nodeToLines(v, source),
				})
				// default:
				// 	panic(fmt.Sprintf("cannot walk on node: %s", n.Kind().String()))
			}

		}

		return ast.WalkContinue, nil
	})

	if err != nil {
		return nil, fmt.Errorf("could not walk ast: %w", err)
	}

	return s, nil
}

func main() {
	cli := &CLI{}

	ctx := kong.Parse(cli)
	// Call the Run() method of the selected parsed command.
	err := ctx.Run()
	ctx.FatalIfErrorf(err)
}
