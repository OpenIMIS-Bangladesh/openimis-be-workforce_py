from django.urls import path
from .views import (FileUploadView,FileDeleteView, FileRetrieveView, LogoRetrieveView,
                    SendOtpView, EisSiteData, EisCaseData, EisRoutingNumberUpdate,
                    CorrectBnEn, CorrectAccountHolderName, DeleteOrphanFiles,
                    FixPayDates, UpdateSerialNumber, UpdateInstallment, UpdateDocumentDirectory,
                    UpdateSkippedDocuments
                    )

urlpatterns = [
    path('document/upload', FileUploadView.as_view(), name='document-upload'),
    path('document/delete/<str:filename>', FileDeleteView.as_view(), name='document-delete'),
    path('document/view/<str:filename>', FileRetrieveView.as_view(), name='document-view'),
    path('logo', LogoRetrieveView.as_view(), name='logo-view'),
    path('send/otp', SendOtpView.as_view(), name='send-otp'),
    path('eis/site-data', EisSiteData.as_view(), name='eis-site-data'),
    path('eis/case-data', EisCaseData.as_view(), name='eis-case-data'),
    path('eis/update-routing-number', EisRoutingNumberUpdate.as_view(), name='update-routing-number'),
    path('eis/correct-bn-en', CorrectBnEn.as_view(), name='correct-bn-en'),
    path('eis/correct-account-holder-name', CorrectAccountHolderName.as_view(), name='correct-account-holder-name'),
    path('eis/delete-orphan-files', DeleteOrphanFiles.as_view(), name='delete-orphan-files'),
    path('eis/fix-pay-dates', FixPayDates.as_view(), name='fix-pay-dates'),
    path('eis/update-serial-number', UpdateSerialNumber.as_view(), name='update-serial-number'),
    path('eis/update-installment', UpdateInstallment.as_view(), name='update-installment'),
    path('eis/update-document-directory', UpdateDocumentDirectory.as_view(), name='update-document-directory'),
    path('eis/update-skipped-documents', UpdateSkippedDocuments.as_view(), name='update-skipped-documents')
]
