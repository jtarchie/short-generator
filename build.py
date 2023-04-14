# pylint: disable=invalid-name
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=missing-module-docstring
# pylint: disable=too-many-locals
# pylint: disable=unspecified-encoding

import os
import pprint
import subprocess
import sys
from dataclasses import dataclass
from typing import List, Union

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
    steps = []
    markdown = mistune.create_markdown(renderer="ast")
    ast = markdown(source)
    print(ast)

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

    pprint.pprint(steps)
    return steps


def say(voice, filename: str, message: str):
    print(f"  say: {message}")
    save_bytes_to_path(filename, voice.generate_audio_bytes(message))


def code(source_filename: str, output_filename: str, source: str):
    print(f"  code: {source_filename}")

    with open(source_filename, "w") as file:
        print(source, file=file)
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


def main():
    client = ElevenLabsUser(os.getenv("ELEVENLABS_API_KEY"))
    voice = client.get_voices_by_name("Josh")[0]

    screensize = (1080, 1920)
    markdown_file = sys.argv[1]
    working_dir = sys.argv[2]

    with open(markdown_file, "r") as f:
        steps = markdown_to_steps(f.read())

    clips = []
    for index, step in enumerate(steps):
        print(f"step #{index} - {step.__class__}")
        if isinstance(step, Heading):
            header = step.content.strip()
            clip = (
                TextClip(header, fontsize=70, size=screensize, color="white")
                .set_position("center", "center")
                .set_duration(2)
            )

            clips.append(clip)
        elif isinstance(step, Voiceover):
            message = step.content.strip()
            outputWaveFilename = os.path.join(working_dir, f"say_{index}.aiff")
            say(voice, outputWaveFilename, message)

            audioClip = AudioFileClip(outputWaveFilename)
            clip = (
                TextClip(message, method="caption", size=screensize, color="white")
                .set_position("center", "center")
                .set_audio(audioClip)
                .set_duration(audioClip.duration)
            )

            clips.append(clip)
        elif isinstance(step, Codeblock):
            filename = f"code_{index}"
            sourceCodeFilename = os.path.join(
                working_dir, f"{filename}{step.extension}"
            )
            outputCodeFilename = os.path.join(working_dir, f"{filename}.png")
            outputWaveFilename = os.path.join(working_dir, f"{filename}.aiff")

            code(sourceCodeFilename, outputCodeFilename, step.source.strip())
            say(voice, outputWaveFilename, step.content.strip())

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
