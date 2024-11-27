# consumers.py (in attendance app)
import json
import cv2
import face_recognition
import numpy as np
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from attendance.models import Employee, Attendance
from datetime import datetime
import base64

class FaceRecognitionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        data = json.loads(text_data)
        frame_data = base64.b64decode(data['frame'])
        
        # Convert frame data to numpy array
        nparr = np.frombuffer(frame_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Process face recognition
        face_locations = face_recognition.face_locations(frame)
        if face_locations:
            face_encoding = face_recognition.face_encodings(frame, face_locations)[0]
            
            # Find matching employee
            employee = await self.find_matching_employee(face_encoding)
            if employee:
                # Record attendance
                attendance = await self.record_attendance(employee, frame)
                
                await self.send(text_data=json.dumps({
                    'type': 'recognition_result',
                    'success': True,
                    'employee': employee.user.username,
                    'attendance_type': 'IN' if attendance.time_out is None else 'OUT',
                    'time': datetime.now().strftime('%I:%M %p')
                }))
            else:
                await self.send(text_data=json.dumps({
                    'type': 'recognition_result',
                    'success': False,
                    'message': 'No matching employee found'
                }))

    @database_sync_to_async
    def find_matching_employee(self, face_encoding):
        employees = Employee.objects.filter(is_active=True)
        for employee in employees:
            stored_encoding = np.frombuffer(employee.face_encoding)
            if face_recognition.compare_faces([stored_encoding], face_encoding)[0]:
                return employee
        return None

    @database_sync_to_async
    def record_attendance(self, employee, frame):
        today = datetime.now().date()
        attendance, created = Attendance.objects.get_or_create(
            employee=employee,
            date=today
        )
        
        current_time = datetime.now().time()
        if not attendance.time_in:
            attendance.time_in = current_time
            # Save video for time in
            video_path = f'attendance_videos/in/{employee.user.username}_{today}_in.mp4'
            self.save_video(frame, video_path)
            attendance.video_in = video_path
        else:
            attendance.time_out = current_time
            # Save video for time out
            video_path = f'attendance_videos/out/{employee.user.username}_{today}_out.mp4'
            self.save_video(frame, video_path)
            attendance.video_out = video_path
        
        attendance.save()
        return attendance

    def save_video(self, frame, path):
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(path, fourcc, 20.0, (640, 480))
        out.write(frame)
        out.release()



