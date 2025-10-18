import cv2
import os
import librosa
import soundfile as sf

video_folder = "~/traffic_project/videos"
video_folder = os.path.expanduser(video_folder)
frames_folder = os.path.join(video_folder, "frames")
audio_folder = os.path.join(video_folder, "audio")

os.makedirs(frames_folder, exist_ok=True)
os.makedirs(audio_folder, exist_ok=True)

# Process each video
for file in os.listdir(video_folder):
    if file.endswith(".mp4"):
        video_path = os.path.join(video_folder, file)
        # --- Extract frames ---
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        count = 0
        success, image = cap.read()
        video_frame_folder = os.path.join(frames_folder, os.path.splitext(file)[0])
        os.makedirs(video_frame_folder, exist_ok=True)
        while success:
            if int(cap.get(cv2.CAP_PROP_POS_FRAMES)) % int(fps) == 0:  # every 1 second
                cv2.imwrite(os.path.join(video_frame_folder, f"frame_{count:05d}.jpg"), image)
                count += 1
            success, image = cap.read()
        cap.release()

        # --- Extract audio ---
        y, sr = librosa.load(video_path, sr=None)
        audio_output_path = os.path.join(audio_folder, os.path.splitext(file)[0] + ".wav")
        sf.write(audio_output_path, y, sr)

print("Frames and audio extracted for all videos!")

