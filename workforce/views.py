from django.http import Http404, FileResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from .services.file_services import save_uploaded_file, retrieve_file_response
from .services.workforce_sms_services import send_sms
from .models import WorkforceEmployee, generate_otp
from core.models import InteractiveUser
import os
from rest_framework.permissions import AllowAny


class FileUploadView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    # permission_classes = [IsAuthenticated]
    permission_classes = [AllowAny]

    def post(self, request):
        file = request.FILES.get('file')
        name = request.POST.get('name')
        file_url, file_path, error = save_uploaded_file(file, name)
        if error:
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        return Response({'success': True, 'file_url': file_url, 'file_path': file_path}, status=status.HTTP_201_CREATED)


class FileRetrieveView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, filename):
        try:
            return retrieve_file_response(filename)
        except Http404 as e:
            raise e


class LogoRetrieveView(APIView):
    def get(self, request):
        try:
            file_path = os.path.join(os.path.dirname(__file__), 'openIMIS.png')
            logo = open(file_path, 'rb')
            response = FileResponse(logo, content_type="image/png")
            response['Content-Disposition'] = f'inline; filename="Logo"'

            return response
        except FileNotFoundError as e:
            raise Http404(f"Error retrieving logo: {str(e)}")


class SendOtpView(APIView):
    def post(self, request):
        try:
            phone_number = request.POST.get('phone_number')
            try:
                employee = WorkforceEmployee.objects.get(
                    phone_number=phone_number)
            except WorkforceEmployee.DoesNotExist:
                employee = None

            if employee is None:
                return Response({'status': 'error', 'message': 'Invalid phone number', 'key': 'INVALID_PHONE_NUMBER'}, status=status.HTTP_400_BAD_REQUEST)

            # otp = generate_otp()
            otp = "12345"

            messages = [{
                "to": employee.phone_number,
                "message": f"Your OTP is {otp}. This will expire in 5 minutes. Please do not share this code with anyone"
            }]

            # otp_services = send_sms(messages=messages)
            user = InteractiveUser.objects.get(id=employee.related_user_id)
            user.set_password(otp)
            user.save()

            return Response({'status': 'success', 'message': 'OTP sent successfully', 'username': user.login_name}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'status': 'error', 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
