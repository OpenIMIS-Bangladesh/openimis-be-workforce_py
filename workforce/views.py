import json
from typing import List

from django.http import Http404, FileResponse
from location.models import Location
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from .services.file_services import save_uploaded_file, retrieve_file_response
from .services.workforce_sms_services import send_sms
from .models import WorkforceEmployee, generate_otp, WorkforceEisPaymentProcess, WorkforceOtherCompensationInfo, WorkforceEmployeeDependent
from core.models import InteractiveUser
import os
from rest_framework.permissions import AllowAny
from django.db.models import F, Sum
from django.db.models.fields.json import KeyTextTransform
from datetime import datetime, timezone, date
import json
from workforce.services.workforce_employee_dependent_services import WorkforceEmployeeDependentServices

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
            if os.environ.get("TEST_LOGIN_OTP"):
                otp = os.environ.get("TEST_LOGIN_OTP")
            else:
                otp = generate_otp()
            message = f"Your OTP is {otp}. This will expire in 5 minutes. Please do not share this code with anyone."
            send_sms(sms_to=employee.phone_number, message=message)
            user = InteractiveUser.objects.get(id=employee.related_user_id)
            user.set_password(otp)
            user.save()

            return Response({'status': 'success', 'message': 'OTP sent successfully', 'username': user.login_name}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'status': 'error', 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class EisSiteData(APIView):
    def get_district_name_by_location_id(self, location_id):
        district_name = None
        try:
            location = Location.objects.get(id=location_id)
            upazilla = Location.objects.get(id=location.parent_id)
            district = Location.objects.get(id=upazilla.parent_id)
            district_name = district.name
            return district_name
        except Exception as e:
            return None

    def getAccidentType(self, key):
        accident_type = {}
        accident_type["workforce.accident.mainType.workplace"] = "কর্মস্থলে দুর্ঘটনা"
        accident_type["workforce.accident.mainType.onDutyRTA"] = "কর্মস্থলের কাজে যাওয়ার পথে সড়ক দুর্ঘটনা"
        accident_type["workforce.accident.mainType.commuting"] = "বাসা থেকে কর্মস্থল/কর্মস্থল থেকে বাসায় যাওয়ার পথে দুর্ঘটনা"
        return accident_type[key]

    def get(self, request):
        try:
            user= InteractiveUser.objects.get(id=1)
            dependent_service= WorkforceEmployeeDependentServices(user)
            payment_process_data= (WorkforceEisPaymentProcess.objects.filter(status="active", approved="yes").
                values(
                process_id= F('id'),
                process_application_id= F('workforce_application_id'),
                dependent_id= F('workforce_employee_dependent_id'),
                eis_beneficiary_id= F('beneficiary_id'),
                case_type= F('workforce_application__application_type'),
                worker_name_en= F('workforce_application__workforce_employee__first_name_en'),
                worker_name_bn= F('workforce_application__workforce_employee__first_name_bn'),
                worker_gender= F('workforce_application__workforce_employee__gender'),
                worker_date_of_birth= F('workforce_application__workforce_employee__birth_date'),
                worker_permanent_location_id= F('workforce_application__workforce_employee__permanent_location_id'),
                worker_present_location_id= F('workforce_application__workforce_employee__present_location_id'),
                dependent_name_en= F('workforce_employee_dependent__name_en'),
                dependent_name_bn= F('workforce_employee_dependent__name_bn'),
                dependent_relation_with_worker= F('workforce_employee_dependent__relation_with_worker'),
                dependent_date_of_birth= F('workforce_employee_dependent__birth_date'),
                dependent_permanent_location_id= F('workforce_employee_dependent__permanent_location_id'),
                dependent_present_location_id= F('workforce_employee_dependent__present_location_id'),
                factory_id= F('workforce_application__employee_factory_id'),
                factory_name_en= F('workforce_application__employee_factory__name_en'),
                factory_name_bn= F('workforce_application__employee_factory__name_bn'),
                factory_address= F('workforce_application__employee_factory__address'),
                factory_location_id= F('workforce_application__employee_factory__location_id'),
                association_id= F('workforce_application__employee_factory__all_association_id'),
                association_name_en= F('workforce_application__employee_factory__all_association__name_en'),
                association_name_bn= F('workforce_application__employee_factory__all_association__name_bn'),
                association_short_name_en= F('workforce_application__employee_factory__all_association__short_name_en'),
                association_short_name_bn= F('workforce_application__employee_factory__all_association__short_name_bn'),
                worker_accident_info= F('workforce_application__employee_accident_info'),
                deceased_worker_info= F('workforce_application__deceased_worker_info'),
                monthly_benefit= F('eis_monthly_amount'),
                date_of_endorsement= F('approval_date')
            ))

            final_data= []

            for item in payment_process_data:
                final_data_item= {}
                final_data_item['case_type']= item.get('case_type')
                final_data_item['worker_name_en']= item.get('worker_name_en')
                final_data_item['worker_name_bn']= item.get('worker_name_bn')
                final_data_item['worker_gender']= item.get('worker_gender')
                final_data_item['factory_name_en']= item.get('factory_name_en')
                final_data_item['factory_name_bn']= item.get('factory_name_bn')
                final_data_item['association_name_en']= item.get('association_name_en')
                final_data_item['association_name_bn']= item.get('association_name_bn')
                final_data_item['association_short_name_en']= item.get('association_short_name_en')
                final_data_item['association_short_name_bn']= item.get('association_short_name_bn')
                final_data_item['worker_accident_info']= item.get('worker_accident_info')
                final_data_item['deceased_worker_info']= item.get('deceased_worker_info')
                final_data_item['monthly_benefit']= item.get('monthly_benefit')
                final_data_item['endorsement_date']= item.get('approval_date')

                worker_accident_info= json.loads(item.get('worker_accident_info', None))
                if worker_accident_info.get('inOutsideFactory') and worker_accident_info[
                    'inOutsideFactory'] != "অন্যস্থানে":
                    if item.get('factory_location_id'):
                        final_data_item['accident_district'] = self.get_district_name_by_location_id(
                            item.get('factory_location_id'))
                    else:
                        final_data_item['accident_district'] = None
                else:
                    final_data_item['accident_district'] = None

                if worker_accident_info.get('accidentMainType'):
                    final_data_item["accident_type"] = self.getAccidentType(worker_accident_info.get('accidentMainType'))

                if item.get('case_type') == 'financialAssistance':

                    deceased_worker_info= json.loads(item.get('deceased_worker_info', None))
                    worker_date_of_birth= deceased_worker_info.get('birthDate', None)
                    worker_date_of_death= worker_accident_info.get('dateOfDeath', None)
                    final_data_item["worker_date_of_birth"]= worker_date_of_birth
                    final_data_item["worker_date_of_death"]= worker_date_of_death
                    final_data_item["worker_age"]= dependent_service.calculate_age_custom(worker_date_of_birth, worker_date_of_death)
                    final_data_item["worker_place_of_death"]= worker_accident_info.get('placeOfDeath', None)
                    final_data_item["worker_date_of_accident"]= worker_accident_info.get('accidentDate', None)
                    final_data_item['total_days_of_endorsement'] = dependent_service.calculate_days(final_data_item['endorsement_date'], final_data_item['worker_date_of_accident'])
                    final_data_item["beneficiary_age"]= dependent_service.calculate_age_custom(item.get("dependent_date_of_birth", None))
                    final_data_item["beneficiary_name_en"] = item.get('dependent_name_en')
                    final_data_item["beneficiary_name_bn"] = item.get('dependent_name_bn')
                    dependent= WorkforceEmployeeDependent.objects.get(id= item.get('dependent_id'))
                    final_data_item["beneficiary_relation_with_worker"] = dependent_service.get_relation_for_api(dependent, final_data_item["worker_age"])
                    final_data_item["beneficiary_date_of_birth"] = item.get('dependent_date_of_birth')
                    if item.get('dependent_permanent_location_id'):
                        final_data_item['beneficiary_permanent_district'] = self.get_district_name_by_location_id(
                            item.get('dependent_permanent_location_id'))
                    else:
                        final_data_item['beneficiary_permanent_district']= None

                    if item.get('dependent_present_location_id'):
                        final_data_item['beneficiary_present_district'] = self.get_district_name_by_location_id(
                            item.get('dependent_present_location_id'))
                    else:
                        final_data_item['beneficiary_present_district']= None
                else:


                    worker_date_of_birth = item.get('worker_date_of_birth')
                    worker_date_of_accident = worker_accident_info.get('accidentDate')
                    final_data_item["worker_accident_type"] = worker_accident_info.get('inOutsideFactory')
                    final_data_item["beneficiary_name_en"] = item.get('worker_name_en')
                    final_data_item["beneficiary_name_bn"] = item.get('worker_name_bn')
                    final_data_item["beneficiary_relation_with_worker"] = "Self"
                    final_data_item["beneficiary_date_of_birth"] = worker_date_of_birth
                    final_data_item["worker_date_of_death"] = None
                    final_data_item["worker_date_of_accident"] = worker_date_of_accident
                    final_data_item['total_days_of_endorsement'] = dependent_service.calculate_days(final_data_item['endorsement_date'], final_data_item['worker_date_of_accident'])
                    final_data_item["beneficiary_age"] = dependent_service.calculate_age_custom(worker_date_of_birth)
                    final_data_item["worker_place_of_death"] = None
                    if item.get('worker_permanent_location_id'):
                        final_data_item['beneficiary_permanent_district'] = self.get_district_name_by_location_id(
                            item.get('worker_permanent_location_id'))
                    else:
                        final_data_item["beneficiary_permanent_district"] = None

                    if item.get('worker_present_location_id'):
                        final_data_item['beneficiary_present_district'] = self.get_district_name_by_location_id(
                            item.get('worker_present_location_id'))
                    else:
                        final_data_item["beneficiary_present_district"] = None


                if item.get('factory_location_id'):
                    final_data_item['factory_district'] = self.get_district_name_by_location_id(item.get('factory_location_id'))
                else:
                    final_data_item['factory_district'] = None

                total_other_payment = (
                                      WorkforceOtherCompensationInfo.objects
                                      .filter(
                                          workforce_application_id=item.get('process_application_id'),
                                          is_eis_benefit_adjustment_eligible="true"
                                      )
                                      .aggregate(total=Sum('amount'))
                                  )['total'] or 0

                final_data_item["total_compensations_by_other_entities"]=  total_other_payment
                final_data.append(final_data_item)






            return Response({'status': 'success', 'message': 'Data Retrieved Successfully', 'data': list(final_data)}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'status': 'error', 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
