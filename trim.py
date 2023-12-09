# pylint: disable=invalid-name
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=missing-module-docstring
# pylint: disable=too-many-locals
# pylint: disable=unspecified-encoding

import argparse
import os
import subprocess

from moviepy.editor import TextClip, VideoFileClip, concatenate_videoclips


def create_text_clip(
    text, video_size, bg_color="lightblue", txt_color="white", duration=3
):
    """Create a text clip with given background and text color."""
    return TextClip(
        text, fontsize=70, color=txt_color, bg_color=bg_color, size=video_size
    ).set_duration(duration)


def main():
    parser = argparse.ArgumentParser(description="Video Editing Script")
    parser.add_argument(
        "--filename", help="Filename of the video to edit", required=True
    )
    parser.add_argument("--title", help="Title for the video", required=True)
    args = parser.parse_args()

    filename = args.filename
    title = args.title

    print(f"Received filename: {filename}")
    print(f"Video title: {title}")


    # Generate a custom output filename
    basename, ext = os.path.splitext(filename)
    altered_filename = f"{basename}-edited{ext}"

    print("Starting auto-editor process...")
    # Step 2: Run auto-editor with custom output filename
    subprocess.run(
        [
            "auto-editor",
            filename,
            "--edit",
            "(or audio:1% motion:1%)",
            "--no-open",
            "--output_file",
            altered_filename,
        ],
        check=True,
    )
    print(f"Auto-editor process completed. Edited file: {altered_filename}")

    print("Loading the edited video...")
    # Load the altered video to get its dimensions
    edited_clip = VideoFileClip(altered_filename)
    video_size = edited_clip.size

    print("Creating intro clip...")
    # Step 3: Create an intro clip
    intro_clip = create_text_clip("Just me programming", video_size)

    print("Creating title card...")
    # Step 4: Create a title card
    title_clip = (
        create_text_clip(title, video_size)
        .set_start(intro_clip.duration)
        .crossfadein(1)
    )

    print("Creating outro clip...")
    # Step 5: Create an outro clip
    outro_clip = create_text_clip(
        "Thanks for watching. Like and subscribe.", video_size
    ).set_start(intro_clip.duration + edited_clip.duration + title_clip.duration)

    print("Concatenating all clips...")
    # Concatenate all clips
    final_clip = concatenate_videoclips(
        [intro_clip, title_clip, edited_clip, outro_clip], method="compose"
    )

    # Output the final video
    final_output_filename = f"{basename}-final{ext}"
    print(f"Writing the final video to {final_output_filename}")
    final_clip.write_videofile(
        final_output_filename, codec="libx264", audio_codec="aac"
    )

    print("Video processing complete!")

if __name__ == "__main__":
    main()
