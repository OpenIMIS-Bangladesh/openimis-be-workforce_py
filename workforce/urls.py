from django.urls import path
from .views import FileUploadView, FileRetrieveView, LogoRetrieveView, SendOtpView, EisSiteData, EisCaseData

urlpatterns = [
    path('document/upload', FileUploadView.as_view(), name='document-upload'),
    path('document/view/<str:filename>', FileRetrieveView.as_view(), name='document-view'),
    path('logo', LogoRetrieveView.as_view(), name='logo-view'),
    path('send/otp', SendOtpView.as_view(), name='send-otp'),
    path('eis/site-data', EisSiteData.as_view(), name='eis-site-data'),
    path('eis/case-data', EisCaseData.as_view(), name='eis-case-data'),
]
