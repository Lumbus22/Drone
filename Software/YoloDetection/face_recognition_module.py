#!/usr/bin/env python3
"""
Face Recognition Module for YOLO11 Object Detection
Provides person identification capabilities for team member recognition.
"""

import face_recognition
import cv2
import numpy as np
import os
import pickle
import json
import time
from typing import List, Dict, Tuple, Optional
from config import FACE_RECOGNITION_CONFIG, FACE_COLORS
from datetime import datetime


class FaceDatabase:
    """Manages the database of known faces and their encodings."""
    
    def __init__(self, database_path: str = "faces_database"):
        self.database_path = database_path
        self.encodings_file = os.path.join(database_path, "face_encodings.pkl")
        self.metadata_file = os.path.join(database_path, "face_metadata.json")
        self.known_faces = {}  # name -> list of encodings
        self.face_metadata = {}  # name -> metadata dict
        
        # Create database directory
        os.makedirs(database_path, exist_ok=True)
        
        # Load existing data
        self.load_database()
    
    def add_person(self, name: str, image_path: str, description: str = "") -> bool:
        """
        Add a new person to the database.
        
        Args:
            name: Person's name
            image_path: Path to image file
            description: Optional description
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Load and encode the image
            image = face_recognition.load_image_file(image_path)
            face_encodings = face_recognition.face_encodings(
                image, 
                num_jitters=FACE_RECOGNITION_CONFIG.get("num_jitters", 1)
            )
            
            if len(face_encodings) == 0:
                print(f"❌ No faces found in {image_path}")
                return False
            
            if len(face_encodings) > 1:
                print(f"⚠️  Multiple faces found in {image_path}, using the first one")
            
            # Add to database
            if name not in self.known_faces:
                self.known_faces[name] = []
                self.face_metadata[name] = {
                    "description": description,
                    "added_date": datetime.now().isoformat(),
                    "image_count": 0,
                    "last_seen": None
                }
            
            self.known_faces[name].append(face_encodings[0])
            self.face_metadata[name]["image_count"] += 1
            
            print(f"✅ Added face encoding for {name}")
            return True
            
        except Exception as e:
            print(f"❌ Error adding person {name}: {e}")
            return False
    
    def add_person_from_encodings(self, name: str, encodings: List[np.ndarray], 
                                 description: str = "") -> bool:
        """Add a person using pre-computed face encodings."""
        try:
            if name not in self.known_faces:
                self.known_faces[name] = []
                self.face_metadata[name] = {
                    "description": description,
                    "added_date": datetime.now().isoformat(),
                    "image_count": 0,
                    "last_seen": None
                }
            
            self.known_faces[name].extend(encodings)
            self.face_metadata[name]["image_count"] += len(encodings)
            
            print(f"✅ Added {len(encodings)} face encoding(s) for {name}")
            return True
            
        except Exception as e:
            print(f"❌ Error adding encodings for {name}: {e}")
            return False
    
    def remove_person(self, name: str) -> bool:
        """Remove a person from the database."""
        if name in self.known_faces:
            del self.known_faces[name]
            del self.face_metadata[name]
            print(f"✅ Removed {name} from database")
            return True
        else:
            print(f"❌ {name} not found in database")
            return False
    
    def get_all_encodings(self) -> Tuple[List[np.ndarray], List[str]]:
        """Get all face encodings and corresponding names."""
        all_encodings = []
        all_names = []
        
        for name, encodings in self.known_faces.items():
            all_encodings.extend(encodings)
            all_names.extend([name] * len(encodings))
        
        return all_encodings, all_names
    
    def save_database(self) -> bool:
        """Save the face database to disk."""
        try:
            # Save encodings
            with open(self.encodings_file, 'wb') as f:
                pickle.dump(self.known_faces, f)
            
            # Save metadata
            with open(self.metadata_file, 'w') as f:
                json.dump(self.face_metadata, f, indent=2)
            
            print(f"✅ Database saved to {self.database_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving database: {e}")
            return False
    
    def load_database(self) -> bool:
        """Load the face database from disk."""
        try:
            # Load encodings
            if os.path.exists(self.encodings_file):
                with open(self.encodings_file, 'rb') as f:
                    self.known_faces = pickle.load(f)
            
            # Load metadata
            if os.path.exists(self.metadata_file):
                with open(self.metadata_file, 'r') as f:
                    self.face_metadata = json.load(f)
            
            total_people = len(self.known_faces)
            total_encodings = sum(len(encodings) for encodings in self.known_faces.values())
            
            if total_people > 0:
                print(f"✅ Loaded {total_people} people with {total_encodings} face encodings")
            
            return True
            
        except Exception as e:
            print(f"❌ Error loading database: {e}")
            return False
    
    def list_people(self) -> List[str]:
        """Get list of all known people."""
        return list(self.known_faces.keys())
    
    def get_person_info(self, name: str) -> Dict:
        """Get metadata for a specific person."""
        return self.face_metadata.get(name, {})
    
    def update_last_seen(self, name: str):
        """Update the last seen timestamp for a person."""
        if name in self.face_metadata:
            self.face_metadata[name]["last_seen"] = datetime.now().isoformat()


class FaceRecognizer:
    """Main face recognition class for identifying people."""
    
    def __init__(self, config: Dict = None):
        self.config = config or FACE_RECOGNITION_CONFIG
        self.database = FaceDatabase(self.config.get("database_path", "faces_database"))
        self.recognition_threshold = self.config.get("recognition_threshold", 0.6)
        self.face_detection_model = self.config.get("face_detection_model", "hog")
        self.min_face_size = self.config.get("min_face_size", 50)
        self.recognition_interval = self.config.get("recognition_interval", 5)
        self.frame_count = 0
        
        # Unknown faces handling
        self.save_unknown_faces = self.config.get("save_unknown_faces", True)
        self.unknown_faces_path = self.config.get("unknown_faces_path", "unknown_faces")
        if self.save_unknown_faces:
            os.makedirs(self.unknown_faces_path, exist_ok=True)
        
        # Performance tracking
        self.recognition_times = []
        
        print(f"🎯 Face Recognizer initialized")
        print(f"   Model: {self.face_detection_model}")
        print(f"   Threshold: {self.recognition_threshold}")
        print(f"   Known people: {len(self.database.list_people())}")
    
    def detect_and_recognize_faces(self, frame: np.ndarray) -> Tuple[List[Dict], np.ndarray]:
        """
        Detect and recognize faces in a frame.
        
        Args:
            frame: Input image frame
            
        Returns:
            Tuple of (face_info_list, annotated_frame)
        """
        self.frame_count += 1
        annotated_frame = frame.copy()
        face_info = []
        
        try:
            # Skip recognition on some frames for performance
            if self.frame_count % self.recognition_interval != 0:
                return face_info, annotated_frame
            
            start_time = time.time()
            
            # Convert BGR to RGB for face_recognition library
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Detect face locations
            face_locations = face_recognition.face_locations(
                rgb_frame, 
                model=self.face_detection_model
            )
            
            if len(face_locations) == 0:
                return face_info, annotated_frame
            
            # Filter out small faces
            valid_face_locations = []
            for (top, right, bottom, left) in face_locations:
                face_width = right - left
                face_height = bottom - top
                if face_width >= self.min_face_size and face_height >= self.min_face_size:
                    valid_face_locations.append((top, right, bottom, left))
            
            if len(valid_face_locations) == 0:
                return face_info, annotated_frame
            
            # Get face encodings
            face_encodings = face_recognition.face_encodings(
                rgb_frame, 
                valid_face_locations,
                num_jitters=self.config.get("num_jitters", 1)
            )
            
            # Get known face data
            known_encodings, known_names = self.database.get_all_encodings()
            
            # Recognize faces
            for i, face_encoding in enumerate(face_encodings):
                top, right, bottom, left = valid_face_locations[i]
                
                name = "Unknown"
                confidence = 0.0
                
                if len(known_encodings) > 0:
                    # Calculate distances to known faces
                    face_distances = face_recognition.face_distance(known_encodings, face_encoding)
                    best_match_index = np.argmin(face_distances)
                    
                    if face_distances[best_match_index] < self.recognition_threshold:
                        name = known_names[best_match_index]
                        confidence = 1.0 - face_distances[best_match_index]
                        self.database.update_last_seen(name)
                
                # Save unknown face if enabled
                if name == "Unknown" and self.save_unknown_faces:
                    self._save_unknown_face(frame, (top, right, bottom, left))
                
                # Add to face info
                face_info.append({
                    "name": name,
                    "confidence": confidence,
                    "bbox": (left, top, right, bottom),
                    "known": name != "Unknown"
                })
                
                # Draw on frame
                annotated_frame = self._draw_face_info(
                    annotated_frame, name, confidence, (top, right, bottom, left)
                )
            
            # Track performance
            recognition_time = time.time() - start_time
            self.recognition_times.append(recognition_time)
            if len(self.recognition_times) > 100:
                self.recognition_times.pop(0)
            
        except Exception as e:
            print(f"❌ Face recognition error: {e}")
        
        return face_info, annotated_frame
    
    def _draw_face_info(self, frame: np.ndarray, name: str, confidence: float, 
                       face_location: Tuple) -> np.ndarray:
        """Draw face recognition information on frame."""
        top, right, bottom, left = face_location
        
        # Choose color based on recognition status
        if name == "Unknown":
            color = FACE_COLORS["unknown"]
            label = "Unknown"
        else:
            color = FACE_COLORS["known"]
            if self.config.get("show_confidence", True):
                label = f"{name} ({confidence:.2f})"
            else:
                label = name
        
        # Draw rectangle around face
        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        
        # Draw label background
        label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
        cv2.rectangle(frame, (left, bottom), (left + label_size[0], bottom + 25), color, -1)
        
        # Draw label text
        cv2.putText(frame, label, (left, bottom + 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        return frame
    
    def _save_unknown_face(self, frame: np.ndarray, face_location: Tuple):
        """Save an unknown face for later review."""
        try:
            top, right, bottom, left = face_location
            face_image = frame[top:bottom, left:right]
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
            filename = f"unknown_face_{timestamp}.jpg"
            filepath = os.path.join(self.unknown_faces_path, filename)
            
            cv2.imwrite(filepath, face_image)
        except Exception as e:
            print(f"❌ Error saving unknown face: {e}")
    
    def get_performance_stats(self) -> Dict:
        """Get performance statistics."""
        if not self.recognition_times:
            return {"avg_time": 0, "fps": 0}
        
        avg_time = np.mean(self.recognition_times)
        fps = 1.0 / avg_time if avg_time > 0 else 0
        
        return {
            "avg_time": avg_time,
            "fps": fps,
            "total_recognitions": len(self.recognition_times)
        }
    
    def is_enabled(self) -> bool:
        """Check if face recognition is enabled."""
        return self.config.get("enabled", True)
    
    def set_enabled(self, enabled: bool):
        """Enable or disable face recognition."""
        self.config["enabled"] = enabled
    
    def add_person_from_camera(self, name: str, frame: np.ndarray, description: str = "") -> bool:
        """Add a person directly from a camera frame."""
        try:
            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Get face encodings
            face_encodings = face_recognition.face_encodings(
                rgb_frame,
                num_jitters=self.config.get("num_jitters", 1)
            )
            
            if len(face_encodings) == 0:
                print(f"❌ No faces found in camera frame")
                return False
            
            if len(face_encodings) > 1:
                print(f"⚠️  Multiple faces found, using the first one")
            
            # Add to database
            success = self.database.add_person_from_encodings(
                name, [face_encodings[0]], description
            )
            
            if success:
                self.database.save_database()
            
            return success
            
        except Exception as e:
            print(f"❌ Error adding person from camera: {e}")
            return False
