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
from .services.workforce_application_services import WorkforceApplicationServices
from .services.workforce_sms_services import send_sms
from .models import WorkforceEmployee, generate_otp, WorkforceEisPaymentProcess, WorkforceOtherCompensationInfo, \
    WorkforceEmployeeDependent, WorkforceApplication, WorkforceApplicationMovement
from core.models import InteractiveUser
import os
from rest_framework.permissions import AllowAny
from django.db.models import F, Sum
from django.db.models.fields.json import KeyTextTransform
from datetime import datetime, timezone, date
import json
from workforce.services.workforce_employee_dependent_services import WorkforceEmployeeDependentServices
import base64

def extract_uuid(encoded_str):
    decoded = base64.b64decode(encoded_str).decode()
    return decoded.split(":")[1]

def safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default
def get_district_name_by_location_id(location_id):
    district_name = None
    try:
        location = Location.objects.get(id=location_id)
        upazilla = Location.objects.get(id=location.parent_id)
        district = Location.objects.get(id=upazilla.parent_id)
        district_name = district.name
        return district_name
    except Exception as e:
        return None

def getAccidentType(key):
    accident_type = {}
    accident_type["workforce.accident.mainType.workplace"] = "কর্মস্থলে দুর্ঘটনা"
    accident_type["workforce.accident.mainType.onDutyRTA"] = "কর্মস্থলের কাজে যাওয়ার পথে সড়ক দুর্ঘটনা"
    accident_type["workforce.accident.mainType.commuting"] = "বাসা থেকে কর্মস্থল/কর্মস্থল থেকে বাসায় যাওয়ার পথে দুর্ঘটনা"
    return accident_type[key]


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
                        final_data_item['accident_district'] = get_district_name_by_location_id(
                            item.get('factory_location_id'))
                    else:
                        final_data_item['accident_district'] = None
                else:
                    final_data_item['accident_district'] = None

                if worker_accident_info.get('accidentMainType'):
                    final_data_item["accident_type"] = getAccidentType(worker_accident_info.get('accidentMainType'))

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
                        final_data_item['beneficiary_permanent_district'] = get_district_name_by_location_id(
                            item.get('dependent_permanent_location_id'))
                    else:
                        final_data_item['beneficiary_permanent_district']= None

                    if item.get('dependent_present_location_id'):
                        final_data_item['beneficiary_present_district'] = get_district_name_by_location_id(
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
                        final_data_item['beneficiary_permanent_district'] = get_district_name_by_location_id(
                            item.get('worker_permanent_location_id'))
                    else:
                        final_data_item["beneficiary_permanent_district"] = None

                    if item.get('worker_present_location_id'):
                        final_data_item['beneficiary_present_district'] = get_district_name_by_location_id(
                            item.get('worker_present_location_id'))
                    else:
                        final_data_item["beneficiary_present_district"] = None


                if item.get('factory_location_id'):
                    final_data_item['factory_district'] = get_district_name_by_location_id(item.get('factory_location_id'))
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


class EisCaseData(APIView):
    def get(self, request):
        try:
            user= InteractiveUser.objects.get(id=1)
            dependent_service= WorkforceEmployeeDependentServices(user)
            application_service= WorkforceApplicationServices(user)
            application_data= (WorkforceApplication.objects.filter(status__in=["approved_by_committee"], organization_type="eis").
                values(
                case_id= F('id'),
                case_type= F('application_type'),
                worker_name_en=F('workforce_employee__first_name_en'),
                worker_name_bn=F('workforce_employee__first_name_bn'),
                worker_gender=F('workforce_employee__gender'),
                worker_date_of_birth=F('workforce_employee__birth_date'),
                worker_permanent_location_id=F('workforce_employee__permanent_location_id'),
                worker_present_location_id=F('workforce_employee__present_location_id'),
                factory_id= F('employee_factory_id'),
                factory_name_en= F('employee_factory__name_en'),
                factory_name_bn= F('employee_factory__name_bn'),
                factory_address= F('employee_factory__address'),
                factory_location_id= F('employee_factory__location_id'),
                association_id= F('employee_factory__all_association_id'),
                association_name_en= F('employee_factory__all_association__name_en'),
                association_name_bn= F('employee_factory__all_association__name_bn'),
                association_short_name_en= F('employee_factory__all_association__short_name_en'),
                association_short_name_bn= F('employee_factory__all_association__short_name_bn'),
                worker_accident_info= F('employee_accident_info'),
                dead_worker_info= F('deceased_worker_info'),
                monthly_benefit= F('eis_monthly_amount')
            ))

            final_data= []

            for data in application_data:
                #set query result first
                final_data_item= data
                final_data_item["worker_beneficiary_count"]= 0

                if data.get('factory_location_id'):
                    final_data_item['factory_district'] = get_district_name_by_location_id(data.get('factory_location_id'))
                else:
                    final_data_item['factory_district'] = None


                ######## Set data from accident #######
                worker_accident_info= json.loads(data.get("worker_accident_info")) if data.get("worker_accident_info") else None
                # first_payment_process= WorkforceEisPaymentProcess.objects.filter(workforce_application_id=data.get("case_id"), status="active", approved="yes").first()
                movement_data= WorkforceApplicationMovement.objects.filter(application_id=data.get("case_id"), status__in=["approved_by_committee"]).order_by("-date_created").first()
                if movement_data is None:
                    continue
                accident_date= worker_accident_info.get("accidentDate", None)
                accident_place= worker_accident_info.get('inOutsideFactory', None)
                endorsement_date= movement_data.date_created.date()
                total_days_of_endorsement = dependent_service.calculate_days(worker_accident_info.get("accidentDate"), endorsement_date)
                accident_type=  getAccidentType(worker_accident_info.get('accidentMainType')) if worker_accident_info.get('accidentMainType') else None
                if worker_accident_info.get('inOutsideFactory') and worker_accident_info[
                    'inOutsideFactory'] != "অন্যস্থানে":
                    if data.get('factory_location_id'):
                        accident_district = get_district_name_by_location_id(
                            data.get('factory_location_id'))
                    else:
                        accident_district = None
                else:
                    accident_district = None
                worker_place_of_death = worker_accident_info.get('placeOfDeath', None)
                worker_age= dependent_service.calculate_age_custom(final_data_item["worker_date_of_birth"])
                ######## Set data from accident END #######


                ######## Change worker data if death case #######
                if data.get('case_type')== "financialAssistance":
                    dead_worker_info = json.loads(data.get("dead_worker_info")) if data.get(
                        "dead_worker_info") is not None else None
                    final_data_item["worker_name_en"] = dead_worker_info.get("nameEn")
                    final_data_item["worker_name_bn"] = dead_worker_info.get("nameBn")
                    final_data_item["worker_gender"] = dead_worker_info.get("gender").get("name")
                    final_data_item["worker_date_of_birth"] = dead_worker_info.get("birthDate")
                    final_data_item["worker_permanent_location_id"] = extract_uuid(dead_worker_info.get("permanentLocation").get("id"))
                    final_data_item["worker_present_location_id"] = extract_uuid(dead_worker_info.get("presentLocation").get("id"))
                    worker_age = dependent_service.calculate_age_custom(dead_worker_info.get("birthDate"), dead_worker_info.get("deathDate"))
                    dependents= WorkforceEmployeeDependent.objects.filter(workforce_application_id=data.get("case_id"), is_eligible=True).values("id","eis_monthly_amount")
                    total_benefit=0
                    dep_count=0
                    for dependent in dependents:
                        total_benefit+= safe_float(dependent["eis_monthly_amount"])
                        dep_count+=1
                    final_data_item["monthly_benefit"]= total_benefit

                    final_data_item["worker_beneficiary_count"]= dep_count

                other_compensations= WorkforceOtherCompensationInfo.objects.filter(workforce_application_id=data.get("case_id"), is_eis_benefit_adjustment_eligible="true")
                total_compensations= 0
                for compensation in other_compensations:
                    total_compensations+= compensation.amount

                ############# Final Data curating #############
                final_data_item["worker_permanent_district"] = get_district_name_by_location_id(final_data_item["worker_permanent_location_id"])
                final_data_item["worker_present_district"] = get_district_name_by_location_id(final_data_item["worker_present_location_id"])
                final_data_item["worker_age"] = worker_age
                final_data_item["endorsement_date"] = endorsement_date
                final_data_item["total_days_of_endorsement"] = total_days_of_endorsement
                final_data_item["accident_date"] = accident_date
                final_data_item["accident_type"] = accident_type
                final_data_item["accident_place"] = accident_place
                final_data_item["accident_district"] = accident_district
                final_data_item["worker_death_place"] = worker_place_of_death
                final_data_item["total_compensations_by_other_entities"] = total_compensations

                final_data.append(final_data_item)




            return Response({'status': 'success', 'message': 'Data Retrieved Successfully', 'data': list(final_data)}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'status': 'error', 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


