from django.urls import path
from .views import FileUploadView, FileRetrieveView

urlpatterns = [
    path('document/upload', FileUploadView.as_view(), name='document-upload'),
    path('document/view/<str:filename>', FileRetrieveView.as_view(), name='document-view'),
]