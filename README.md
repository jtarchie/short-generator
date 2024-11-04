# Generate Youtube Shorts

This tool converts a markdown file into a Youtube Short, focusing specifically
on programming idioms. It is built using Python, with the script handling the
video and voiceover generation.

## Limitations

- Currently uses AI-generated voices from ElevenLabs.
- Does not automatically upload to Youtube

## Usage

To use the tool, follow these steps:

1. Install dependencies:

```bash
brew bundle
pip3 install -r requirements.txt
```

2. Generate the video using the Python script:

```bash
python3 <markdown-file> <output-directory>
```

3. Manually upload the generated video to Youtube.

## References

- [https://ray.so](https://ray.so), did not use this, but maybe an alternative
  code renderer.
