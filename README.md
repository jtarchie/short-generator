# Generate Youtube Shorts

This tool converts a markdown file into a Youtube Short, focusing specifically
on programming idioms. It is built using Go and Python, with the Python script
handling the video and voiceover generation.

## Limitations

- Currently uses `say` for voiceover; future plans include exploring
  AI-generated voices
- Does not automatically upload to Youtube

## Usage

To use the tool, follow these steps:

1. Install dependencies:

```bash
brew bundle
pip3 install -r requirements.txt
```

2. Run the Go script to process the markdown file:

3. Generate the video using the Python script:

```bash
python3 <markdown-file> <output-directory>
```

4. Manually upload the generated video to Youtube.

## References

- [https://ray.so](https://ray.so), did not use this, but maybe an alternative
  code renderer.
