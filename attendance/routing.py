
#this was old code
# from django.urls import re_path
# from . import consumers


# websocket_urlpatterns = [
#     re_path(r'ws/face_recognition/$', consumers.FaceRecognitionConsumer.as_asgi()),
# ]


from django.urls import re_path
from .consumers import FaceRecognitionConsumer

websocket_urlpatterns = [
    re_path(r'ws/face_recognition/$', FaceRecognitionConsumer.as_asgi()),
]