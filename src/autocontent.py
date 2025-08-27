import argparse
import os
from utils import (
    youtube_downloader,
    extract_audio,
    load_and_match_from_files,
)
from video_editor.vertical_video import (
    VerticalVideoCreator,
    trim_video,
)

def main():
    parser = argparse.ArgumentParser(description="AutoContent: A tool for automatic video content creation.")

    parser.add_argument("--link", type=str, required=True, help="YouTube video link.")
    parser.add_argument("--project_name", type=str, required=True, help="Name of the project folder.")
    parser.add_argument("--viral_segments_file", type=str, required=True, help="Path to the JSON file containing viral segments.")
    parser.add_argument("--audio_transcript_file", type=str, required=True, help="Path to the JSON file containing the audio transcript.")
    parser.add_argument("--similarity_threshold", type=float, default=0.6, help="Similarity threshold for matching transcripts.")
    parser.add_argument("--face_cascade_path", type=str, default="src/cascade.xml", help="Path to the Haar cascade file for face detection.")

    args = parser.parse_args()

    project_folder = os.path.join("./videos_projects", args.project_name)
    os.makedirs(project_folder, exist_ok=True)

    print("Downloading video...")
    video_path = youtube_downloader(url=args.link, folder=project_folder)
    print(f"Video downloaded to: {video_path}")

    audio_output_path = os.path.join(project_folder, "audio.mp3")
    print("Extracting audio...")
    extract_audio(input_path=video_path, output_path=audio_output_path)
    print(f"Audio extracted to: {audio_output_path}")

    print("Creating vertical video...")
    vertical_video_path = os.path.join(project_folder, "vertical_video.mp4")
    video_creator = VerticalVideoCreator(face_cascade_path=args.face_cascade_path)
    video_creator.convert_video_to_vertical(input_path=video_path, output_path=vertical_video_path)
    print(f"Vertical video created at: {vertical_video_path}")

    print("Matching transcripts and finding timestamps...")
    timestamps = load_and_match_from_files(
        viral_segments_file=args.viral_segments_file,
        audio_transcript_file=args.audio_transcript_file,
        similarity_threshold=args.similarity_threshold,
    )
    print("Timestamps found:")
    for ts in timestamps:
        print(f"  Segment: {ts['segment']}, Start: {ts['start_time']}, End: {ts['end_time']}")

    print("Trimming video clips...")
    clips_folder = os.path.join(project_folder, "CLIPS")
    os.makedirs(clips_folder, exist_ok=True)
    for i, ts in enumerate(timestamps):
        clip_path = os.path.join(clips_folder, f"clip_{i+1}.mp4")
        trim_video(
            input_file=vertical_video_path,
            start_time=ts['start_time'],
            end_time=ts['end_time'],
            output_file=clip_path,
        )
        print(f"  Created clip: {clip_path}")

if __name__ == "__main__":
    main()