from moviepy.editor import *
import json
import os
import subprocess
import sys

clips = []
screensize = (1080, 1920)
script_file = sys.argv[1]
working_dir = os.path.dirname(script_file)

with open(script_file, 'r') as f:
    steps = json.loads(f.read())


def say(filename: str, message: str):
    print(f"  say: {message}")
    subprocess.run(
        ["say",
         "-o", filename,
         "-v", "Daniel",
         message], check=True)


def code(sourceFilename: str, outputFilename: str, source: str):
    print(f"  code: {sourceFilename}")

    print(source, file=open(sourceFilename, 'w'))
    subprocess.run(["carbon-now",
                    sourceFilename,
                    "-h",
                    "-t", os.path.splitext(outputFilename)[0]
                    ], check=True)


for index, step in enumerate(steps):
    action = step[0]
    payload = step[1]

    print(f"step #{index} - {action}")
    if action == "heading":
        header = payload['content'].strip()
        clip = TextClip(header, fontsize=70, size=screensize, color='white').set_position(
            "center", "center").set_duration(2)

        clips.append(clip)
    elif action == "voiceover":
        message = payload['content'].strip()
        outputWaveFilename = os.path.join(working_dir, f"say_{index}.aiff")
        say(outputWaveFilename, message)

        audioClip = AudioFileClip(outputWaveFilename)
        clip = TextClip(message, method="caption", size=screensize, color='white').set_position(
            "center", "center").set_audio(audioClip).set_duration(audioClip.duration)

        clips.append(clip)
    elif action == "code":
        source = payload['source'].strip()
        message = payload['content'].strip()

        filename = f"code_{index}"
        sourceCodeFilename = os.path.join(working_dir, f"{filename}{payload['extension']}")
        outputCodeFilename = os.path.join(working_dir, f"{filename}.png")
        outputWaveFilename = os.path.join(working_dir, f"{filename}.aiff")

        code(sourceCodeFilename, outputCodeFilename, source)
        say(outputWaveFilename, message)

        audioClip = AudioFileClip(outputWaveFilename)
        imageClip = ImageClip(outputCodeFilename, duration=audioClip.duration).set_position(
            "center", "center").resize(width=screensize[0]).set_audio(audioClip)
        imageClip.fps = 1
        bgClip = ColorClip(screensize, color=(255, 255, 255))

        clip = CompositeVideoClip(
            clips=[bgClip, imageClip],
            size=screensize
        ).set_duration(audioClip.duration)

        clips.append(clip)
    else:
        raise f"unknown action {action}"

for index, clip in enumerate(clips):
    print(f"clip #{index}: {clip.duration} -- {clip}")

output_path = os.path.join(working_dir, "output.mp4")

final_clip = concatenate_videoclips(clips)
final_clip.write_videofile(output_path, fps=24)
final_clip.close()
