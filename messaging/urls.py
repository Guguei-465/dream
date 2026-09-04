from django.urls import path
from . import views

urlpatterns = [
    path("messages/conversations", views.conversations, name="conversations"),
    path("messages/conversations/<int:conversation_id>/messages", views.conversation_messages, name="conversation_messages"),
    path("messages/conversations/<int:conversation_id>/status", views.conversation_status, name="conversation_status"),
]
