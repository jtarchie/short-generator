# pylint: disable=invalid-name
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=missing-module-docstring
# pylint: disable=too-many-locals
# pylint: disable=unspecified-encoding

import hashlib
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from typing import List, Union

import frontmatter
import mistune
from elevenlabslib import ElevenLabsUser
from elevenlabslib.helpers import save_bytes_to_path
from moviepy.editor import (
    AudioFileClip,
    ColorClip,
    CompositeVideoClip,
    ImageClip,
    TextClip,
    concatenate_videoclips,
)


@dataclass
class Heading:
    content: str


@dataclass
class Voiceover:
    content: str


@dataclass
class Codeblock:
    content: str
    extension: str
    language: str
    source: str


Step = Union[Heading, Voiceover, Codeblock]


def from_language_to_extension(language: str) -> str:
    extensions = {
        "javascript": ".js",
        "python": ".py",
        "java": ".java",
        "c": ".c",
        "cpp": ".cpp",
        "csharp": ".cs",
        "c#": ".cs",
        "go": ".go",
        "ruby": ".rb",
        "php": ".php",
        "swift": ".swift",
        "kotlin": ".kt",
        "scala": ".scala",
        "rust": ".rs",
        "haskell": ".hs",
        "dart": ".dart",
        "typescript": ".ts",
        "lua": ".lua",
        "perl": ".pl",
        "r": ".r",
    }

    return extensions.get(language.lower(), "")


def markdown_to_steps(source: str) -> List[Step]:
    steps: List[Step] = []
    markdown = mistune.create_markdown(renderer="ast")
    ast = markdown(source)

    for node in ast:
        if node["type"] == "heading":
            header = node["children"][0]["text"]
            header = header.replace(": ", "\n")
            steps.append(Heading(header))
        elif node["type"] == "paragraph":
            text = "".join(n["text"] for n in node["children"])
            steps.append(Voiceover(text))
        elif node["type"] == "block_code":
            previous_step = steps[-1]
            steps = steps[:-1]

            language = node["info"]
            extension = from_language_to_extension(language)

            steps.append(
                Codeblock(previous_step.content, extension, language, node["text"])
            )

    return steps


def digest(*s: str) -> str:
    return hashlib.md5("".join(s).encode()).hexdigest()


def say(voice, output_path: str, message: str) -> str:
    print(f"  say: {message}")
    filename = os.path.join(output_path, digest(voice.initialName, message) + ".wav")
    if not os.path.isfile(filename):
        print(f"     saving file: {filename}")
        save_bytes_to_path(filename, voice.generate_audio_bytes(message))
    return filename


def code(output_path: str, source: str, extension: str) -> str:
    source_digest = digest(source)
    source_filename = os.path.join(output_path, source_digest + extension)
    output_filename = os.path.join(output_path, source_digest + ".png")
    print(f"  code: {source_filename}")

    with open(source_filename, "w") as file:
        print(source, file=file)
    if not os.path.isfile(output_filename):
        print(f"     saving file: {output_filename}")
        subprocess.run(
            [
                "carbon-now",
                source_filename,
                "-h",
                "-t",
                os.path.splitext(output_filename)[0],
            ],
            check=True,
        )

    return output_filename


def main():
    client = ElevenLabsUser(os.getenv("ELEVENLABS_API_KEY"))
    voice = client.get_voices_by_name("Rachel")[0]

    screensize = (1080, 1920)
    markdown_file = sys.argv[1]
    working_dir = sys.argv[2]

    with open(markdown_file, "r") as f:
        markdown = frontmatter.load(f)
        steps = markdown_to_steps(markdown.content)

    clips = []
    for index, step in enumerate(steps):
        print(f"step #{index} - {step.__class__}")
        if isinstance(step, Heading):
            header = step.content.strip()
            words = header.split()
            groups = "\n".join(
                [" ".join(words[i : i + 3]) for i in range(0, len(words), 3)]
            )

            clip = (
                TextClip(groups, fontsize=70, size=screensize, color="white")
                .set_position("center", "center")
                .set_duration(3)
            )

            clips.append(clip)
        elif isinstance(step, Voiceover):
            message = step.content.strip()
            outputWaveFilename = say(voice, working_dir, message)

            audioClip = AudioFileClip(outputWaveFilename)
            clip = (
                TextClip(message, method="caption", size=screensize, color="white")
                .set_position("center", "center")
                .set_audio(audioClip)
                .set_duration(audioClip.duration)
            )

            clips.append(clip)
        elif isinstance(step, Codeblock):
            time.sleep(5)

            outputCodeFilename = code(working_dir, step.source.strip(), step.extension)
            outputWaveFilename = say(voice, working_dir, step.content.strip())

            audioClip = AudioFileClip(outputWaveFilename)
            imageClip = (
                ImageClip(outputCodeFilename, duration=audioClip.duration)
                .set_position("center", "center")
                .resize(width=screensize[0])
                .set_audio(audioClip)
            )
            imageClip.fps = 1
            bgClip = ColorClip(screensize, color=(255, 255, 255))

            clip = CompositeVideoClip(
                clips=[bgClip, imageClip], size=screensize
            ).set_duration(audioClip.duration)

            clips.append(clip)
        else:
            raise f"unknown action {step.__class__}"

    for index, clip in enumerate(clips):
        print(f"clip #{index}: {clip.duration} -- {clip}")

    output_path = os.path.join(working_dir, "output.mp4")

    final_clip = concatenate_videoclips(clips)
    final_clip.write_videofile(output_path, fps=24)
    final_clip.close()


if __name__ == "__main__":
    main()
