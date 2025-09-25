#!/usr/bin/env python3
"""
Face Registration Script
Register yourself and your team members for face recognition.
"""

import cv2
import os
import argparse
import time
from face_recognition_module import FaceRecognizer, FaceDatabase
from config import FACE_RECOGNITION_CONFIG


class FaceRegistrationTool:
    """Tool for registering faces for recognition."""
    
    def __init__(self):
        self.face_recognizer = FaceRecognizer()
        self.database = self.face_recognizer.database
        
    def register_from_images(self, name: str, image_paths: list, description: str = ""):
        """Register a person from image files."""
        print(f"\n📸 Registering {name} from image files...")
        
        success_count = 0
        for image_path in image_paths:
            if not os.path.exists(image_path):
                print(f"❌ Image not found: {image_path}")
                continue
            
            print(f"Processing: {image_path}")
            if self.database.add_person(name, image_path, description):
                success_count += 1
        
        if success_count > 0:
            self.database.save_database()
            print(f"✅ Successfully registered {name} with {success_count} image(s)")
            return True
        else:
            print(f"❌ Failed to register {name}")
            return False
    
    def register_from_camera(self, name: str, description: str = "", camera_id: int = 0):
        """Register a person using live camera feed."""
        print(f"\n📷 Registering {name} from camera...")
        print("Instructions:")
        print("- Look directly at the camera")
        print("- Keep your face well-lit and clearly visible")
        print("- Press 's' to save current face")
        print("- Press 'q' to quit")
        print("- Try to capture 3-5 different angles/expressions")
        
        cap = cv2.VideoCapture(camera_id)
        if not cap.isOpened():
            print(f"❌ Failed to open camera {camera_id}")
            return False
        
        # Set camera properties
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        captured_count = 0
        target_captures = 5
        
        print(f"\nCapturing faces for {name}...")
        print(f"Goal: {target_captures} captures")
        
        while captured_count < target_captures:
            ret, frame = cap.read()
            if not ret:
                print("❌ Failed to read frame")
                break
            
            # Show preview
            preview_frame = frame.copy()
            
            # Add instructions to frame
            cv2.putText(preview_frame, f"Registering: {name}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(preview_frame, f"Captured: {captured_count}/{target_captures}", (10, 70), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(preview_frame, "Press 's' to save, 'q' to quit", (10, 110), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            
            # Detect faces for preview
            try:
                face_locations = self.face_recognizer.detect_and_recognize_faces(frame)[0]
                if face_locations:
                    cv2.putText(preview_frame, "Face detected!", (10, 150), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                else:
                    cv2.putText(preview_frame, "No face detected", (10, 150), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            except:
                pass
            
            cv2.imshow("Face Registration", preview_frame)
            
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('s'):
                # Save current face
                if self.face_recognizer.add_person_from_camera(name, frame, description):
                    captured_count += 1
                    print(f"✅ Captured face {captured_count}/{target_captures}")
                    
                    # Visual feedback
                    feedback_frame = preview_frame.copy()
                    cv2.putText(feedback_frame, "SAVED!", (250, 200), 
                               cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)
                    cv2.imshow("Face Registration", feedback_frame)
                    cv2.waitKey(500)  # Show for 500ms
                else:
                    print("❌ Failed to capture face - make sure your face is clearly visible")
            
            elif key == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
        
        if captured_count > 0:
            self.database.save_database()
            print(f"✅ Successfully registered {name} with {captured_count} captures")
            return True
        else:
            print(f"❌ No faces captured for {name}")
            return False
    
    def register_multiple_people(self):
        """Interactive registration for multiple people."""
        print("\n👥 Multiple People Registration")
        print("=" * 40)
        
        while True:
            print("\nOptions:")
            print("1. Register person from camera")
            print("2. Register person from image files")
            print("3. List registered people")
            print("4. Remove person")
            print("5. Exit")
            
            choice = input("\nEnter your choice (1-5): ").strip()
            
            if choice == "1":
                name = input("Enter person's name: ").strip()
                if name:
                    description = input("Enter description (optional): ").strip()
                    self.register_from_camera(name, description)
                
            elif choice == "2":
                name = input("Enter person's name: ").strip()
                if name:
                    description = input("Enter description (optional): ").strip()
                    image_paths = []
                    
                    print("Enter image file paths (press Enter without input to finish):")
                    while True:
                        path = input("Image path: ").strip()
                        if not path:
                            break
                        image_paths.append(path)
                    
                    if image_paths:
                        self.register_from_images(name, image_paths, description)
                
            elif choice == "3":
                self.list_people()
                
            elif choice == "4":
                name = input("Enter name to remove: ").strip()
                if name:
                    self.database.remove_person(name)
                    self.database.save_database()
                
            elif choice == "5":
                break
            
            else:
                print("Invalid choice. Please try again.")
    
    def list_people(self):
        """List all registered people."""
        people = self.database.list_people()
        
        if not people:
            print("\n📭 No people registered yet.")
            return
        
        print(f"\n👥 Registered People ({len(people)}):")
        print("=" * 40)
        
        for name in people:
            info = self.database.get_person_info(name)
            print(f"• {name}")
            print(f"  Description: {info.get('description', 'N/A')}")
            print(f"  Images: {info.get('image_count', 0)}")
            print(f"  Added: {info.get('added_date', 'N/A')}")
            if info.get('last_seen'):
                print(f"  Last seen: {info['last_seen']}")
            print()
    
    def quick_register_team(self):
        """Quick registration flow for a team."""
        print("\n🚀 Quick Team Registration")
        print("=" * 30)
        print("This will help you quickly register your entire team.")
        print("Make sure each person is available with the camera.")
        
        team_members = []
        
        # Get team member names
        print("\nFirst, let's get the names of your team members.")
        print("Enter names one by one (press Enter without input to finish):")
        
        while True:
            name = input(f"Team member #{len(team_members) + 1} name: ").strip()
            if not name:
                break
            team_members.append(name)
        
        if not team_members:
            print("No team members entered.")
            return
        
        print(f"\n✅ Team members to register: {', '.join(team_members)}")
        
        # Register each team member
        for i, name in enumerate(team_members):
            print(f"\n👤 Registering {name} ({i+1}/{len(team_members)})")
            input(f"Press Enter when {name} is ready at the camera...")
            
            description = f"Team member #{i+1}"
            success = self.register_from_camera(name, description)
            
            if success:
                print(f"✅ {name} registered successfully!")
            else:
                print(f"❌ Failed to register {name}")
                retry = input("Try again? (y/n): ").lower().startswith('y')
                if retry:
                    self.register_from_camera(name, description)
        
        print(f"\n🎉 Team registration complete!")
        self.list_people()


def main():
    parser = argparse.ArgumentParser(description="Face Registration Tool")
    parser.add_argument("--name", help="Person's name to register")
    parser.add_argument("--images", nargs="+", help="Image file paths")
    parser.add_argument("--camera", action="store_true", help="Use camera for registration")
    parser.add_argument("--camera-id", type=int, default=0, help="Camera device ID")
    parser.add_argument("--description", default="", help="Person description")
    parser.add_argument("--interactive", action="store_true", help="Interactive mode")
    parser.add_argument("--team", action="store_true", help="Quick team registration")
    parser.add_argument("--list", action="store_true", help="List registered people")
    
    args = parser.parse_args()
    
    tool = FaceRegistrationTool()
    
    if args.list:
        tool.list_people()
        
    elif args.team:
        tool.quick_register_team()
        
    elif args.interactive:
        tool.register_multiple_people()
        
    elif args.name:
        if args.camera:
            tool.register_from_camera(args.name, args.description, args.camera_id)
        elif args.images:
            tool.register_from_images(args.name, args.images, args.description)
        else:
            print("❌ Please specify --camera or --images for registration method")
    
    else:
        # Default interactive mode
        print("🎯 Face Registration Tool")
        print("=" * 30)
        print("Choose registration method:")
        print("1. Interactive mode (recommended)")
        print("2. Quick team registration")
        print("3. List registered people")
        
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice == "1":
            tool.register_multiple_people()
        elif choice == "2":
            tool.quick_register_team()
        elif choice == "3":
            tool.list_people()
        else:
            print("Starting interactive mode...")
            tool.register_multiple_people()


if __name__ == "__main__":
    main()
