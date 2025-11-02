import logging

from core.services import BaseService
from workforce.models import WorkforceEmployeeDependent

logger = logging.getLogger(__name__)


class WorkforceEmployeeDependentServices(BaseService):
    OBJECT_TYPE = WorkforceEmployeeDependent


    def create(self, obj_data):
        return super().create(obj_data)

    def update(self, obj_data):
        return super().update(obj_data)

    def get_gender_by_relation(self, relation_with_worker):
        if relation_with_worker=="workforce.relation.father" or relation_with_worker=="workforce.relation.son" or relation_with_worker=="workforce.relation.husband" or relation_with_worker=="workforce.relation.brother" or relation_with_worker=="workforce.relation.grand_father" or relation_with_worker=="workforce.relation.grand_son":
            return "male"
        else:
            return "female"

    def update_eligibility(self, workforce_application_id):
        try:
            dependents= WorkforceEmployeeDependent.objects.filter(workforce_application_id=workforce_application_id)
            for dependent in dependents:
                dep_obj = WorkforceEmployeeDependent.objects.get(id=dependent.id)
                relation = dep_obj.relation_with_worker
                gender = self.get_gender_by_relation(relation)
                eligible = False

                # FEMALE RELATIONSHIPS
                if gender == "female":
                    if relation == "workforce.relation.mother":
                        # Mother: check if alive
                        if dep_obj.life_status == "alive":
                            eligible = True
                        else:
                            eligible = False

                    elif relation in ["workforce.relation.wife", "workforce.relation.sister",
                                      "workforce.relation.daughter"]:
                        # Wife/Sister/Daughter: check if married
                        if not dep_obj.marital_status == "married":
                            eligible = True
                        else:
                            eligible = False

                # MALE RELATIONSHIPS
                elif gender == "male":
                    if relation == "workforce.relation.father":
                        # Father: check if alive
                        if dep_obj.life_status == "alive":
                            eligible = True
                        else:
                            eligible = False

                    elif relation in ["workforce.relation.son", "workforce.relation.brother"]:
                        # Son/Brother: check if physically challenged, then alive
                        if dep_obj.disability_status=="yes":
                            if dep_obj.life_status == "alive":
                                eligible = True
                            else:
                                eligible = False
                        else:
                            eligible = False

                    elif relation == "workforce.relation.husband":
                        # Husband: check if newly married
                        if dep_obj.marital_status == "married":
                            eligible = False
                        else:
                            eligible = True

                # Finally save
                dep_obj.isEligible = eligible
                dep_obj.save(username=self.user.username)
            return {"status": True, "error": ""}
        except Exception as e:
            return {"status": False, "error": str(e)}
