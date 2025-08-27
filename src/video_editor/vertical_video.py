
import cv2
import numpy as np
from typing import Tuple
import os
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip

class VerticalVideoCreator:
    def __init__(self, face_cascade_path: str):
        """
        Initialize the vertical video creator with face detection.
        
        Args:
            face_cascade_path: Path to Haar cascade file for face detection.
        """
        if not os.path.exists(face_cascade_path):
            raise ValueError(f"Could not find face cascade classifier at: {face_cascade_path}")
        self.face_cascade = cv2.CascadeClassifier(face_cascade_path)
        if self.face_cascade.empty():
            raise ValueError("Could not load face cascade classifier")

    def detect_faces(self, frame: np.ndarray) -> list:
        """
        Detect faces in a frame.
        
        Args:
            frame: Input frame as numpy array
            
        Returns:
            List of face rectangles [(x, y, w, h), ...]
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
            flags=cv2.CASCADE_SCALE_IMAGE
        )
        return list(faces)

    def get_face_region(self, frame: np.ndarray, face: Tuple[int, int, int, int],
                       padding_factor: float = 0.3) -> np.ndarray:
        """
        Extract face region with padding.
        
        Args:
            frame: Input frame
            face: Face rectangle (x, y, w, h)
            padding_factor: Additional padding around face
            
        Returns:
            Cropped face region
        """
        x, y, w, h = face
        height, width = frame.shape[:2]
        pad_w = int(w * padding_factor)
        pad_h = int(h * padding_factor)
        x1 = max(0, x - pad_w)
        y1 = max(0, y - pad_h)
        x2 = min(width, x + w + pad_w)
        y2 = min(height, y + h + pad_h)
        return frame[y1:y2, x1:x2]

    def create_vertical_frame(self, frame: np.ndarray, target_width: int = 720,
                            target_height: int = 1280, face_height_ratio: float = 0.4) -> np.ndarray:
        """
        Create a vertical frame with face on top and original content below.
        """
        faces = self.detect_faces(frame)
        face_height = int(target_height * face_height_ratio)
        content_height = target_height - face_height
        output_frame = np.zeros((target_height, target_width, 3), dtype=np.uint8)

        if faces:
            largest_face = max(faces, key=lambda f: f[2] * f[3])
            face_region = self.get_face_region(frame, largest_face)
            face_resized = cv2.resize(face_region, (target_width, face_height))
            output_frame[0:face_height, :] = face_resized
        else:
            h, w = frame.shape[:2]
            center_y, center_x = h // 2, w // 2
            crop_h = min(h, int(w * face_height / target_width))
            crop_w = min(w, int(h * target_width / face_height))
            y1 = max(0, center_y - crop_h // 2)
            y2 = min(h, y1 + crop_h)
            x1 = max(0, center_x - crop_w // 2)
            x2 = min(w, x1 + crop_w)
            face_crop = frame[y1:y2, x1:x2]
            face_resized = cv2.resize(face_crop, (target_width, face_height))
            output_frame[0:face_height, :] = face_resized

        content_resized = cv2.resize(frame, (target_width, content_height))
        output_frame[face_height:, :] = content_resized
        cv2.line(output_frame, (0, face_height), (target_width, face_height), (255, 255, 255), 2)
        return output_frame

    def convert_video_to_vertical(self, input_path: str, output_path: str,
                                target_width: int = 720, target_height: int = 1280,
                                face_height_ratio: float = 0.4) -> bool:
        """
        Convert a horizontal video to vertical format.
        """
        cap = cv2.VideoCapture(input_path)
        if not cap.isOpened():
            print(f"Error: Could not open video {input_path}")
            return False

        fps = int(cap.get(cv2.CAP_PROP_FPS))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (target_width, target_height))
        frame_count = 0

        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                vertical_frame = self.create_vertical_frame(
                    frame, target_width, target_height, face_height_ratio
                )
                out.write(vertical_frame)
                frame_count += 1
                if frame_count % 30 == 0:
                    progress = (frame_count / total_frames) * 100
                    print(f"Progress: {progress:.1f}% ({frame_count}/{total_frames})")
        except Exception as e:
            print(f"Error processing video: {e}")
            return False
        finally:
            cap.release()
            out.release()

        print(f"Video conversion completed: {output_path}")
        return True

def trim_video(input_file: str, start_time: float, end_time: float, output_file: str):
    """
    Trims a video file to a specified start and end time.
    """
    ffmpeg_extract_subclip(input_file, start_time, end_time, targetname=output_file)
