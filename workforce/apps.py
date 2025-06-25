from django.apps import AppConfig

MODULE_NAME = "workforce"

DEFAULT_CFG = {
    "gql_query_workforces_perms": ["801000"],

    # WorkforceRepresentative (801xxx)
    "gql_query_workforce_representative_perms": ["801001"],
    "gql_mutation_create_workforce_representative_perms": ["801002"],
    "gql_mutation_update_workforce_representative_perms": ["801003"],
    "gql_mutation_delete_workforce_representative_perms": ["801004"],

    # WorkforceOrganization (802xxx)
    "gql_query_workforce_organization_perms": ["802001"],
    "gql_mutation_create_workforce_organization_perms": ["802002"],
    "gql_mutation_update_workforce_organization_perms": ["802003"],
    "gql_mutation_delete_workforce_organization_perms": ["802004"],

    # WorkforceOrganizationUnit (803xxx)
    "gql_query_workforce_organization_unit_perms": ["803001"],
    "gql_mutation_create_workforce_organization_unit_perms": ["803002"],
    "gql_mutation_update_workforce_organization_unit_perms": ["803003"],
    "gql_mutation_delete_workforce_organization_unit_perms": ["803004"],

    # WorkforceOrganizationUnitDesignation (804xxx)
    "gql_query_workforce_organization_unit_designation_perms": ["804001"],
    "gql_mutation_create_workforce_organization_unit_designation_perms": ["804002"],
    "gql_mutation_update_workforce_organization_unit_designation_perms": ["804003"],
    "gql_mutation_delete_workforce_organization_unit_designation_perms": ["804004"],

    # WorkforceOrganizationEmployee (805xxx)
    "gql_query_workforce_organization_employee_perms": ["805001"],
    "gql_mutation_create_workforce_organization_employee_perms": ["805002"],
    "gql_mutation_update_workforce_organization_employee_perms": ["805003"],
    "gql_mutation_delete_workforce_organization_employee_perms": ["805004"],

    # WorkforceOrganizationEmployeeDesignation (806xxx)
    "gql_query_workforce_organization_employee_designation_perms": ["806001"],
    "gql_mutation_create_workforce_organization_employee_designation_perms": ["806002"],
    "gql_mutation_update_workforce_organization_employee_designation_perms": ["806003"],
    "gql_mutation_delete_workforce_organization_employee_designation_perms": ["806004"],

    # WorkforceEmployer (807xxx)
    "gql_query_workforce_employer_perms": ["807001"],
    "gql_mutation_create_workforce_employer_perms": ["807002"],
    "gql_mutation_update_workforce_employer_perms": ["807003"],
    "gql_mutation_delete_workforce_employer_perms": ["807004"],

    # WorkforceOffice (808xxx)
    "gql_query_workforce_office_perms": ["808001"],
    "gql_mutation_create_workforce_office_perms": ["808002"],
    "gql_mutation_update_workforce_office_perms": ["808003"],
    "gql_mutation_delete_workforce_office_perms": ["808004"],

    # WorkforceFactory (809xxx)
    "gql_query_workforce_factory_perms": ["809001"],
    "gql_mutation_create_workforce_factory_perms": ["809002"],
    "gql_mutation_update_workforce_factory_perms": ["809003"],
    "gql_mutation_delete_workforce_factory_perms": ["809004"],

    # WorkforceEmployee (810xxx)
    "gql_query_workforce_employee_perms": ["810001"],
    "gql_mutation_create_workforce_employee_perms": ["810002"],
    "gql_mutation_update_workforce_employee_perms": ["810003"],
    "gql_mutation_delete_workforce_employee_perms": ["810004"],

    # WorkforceDocument (811xxx)
    "gql_query_workforce_document_perms": ["811001"],
    "gql_mutation_create_workforce_document_perms": ["811002"],
    "gql_mutation_update_workforce_document_perms": ["811003"],
    "gql_mutation_delete_workforce_document_perms": ["811004"],

    # WorkforceChecker (812xxx)
    "gql_workforce_checker_perms": ["812001"],

    # WorkforceApprover (813xxx)
    "gql_workforce_approver_perms": ["813001"],

    # WorkforceFactoryAdmin (814xxx)
    "gql_workforce_factory_admin_perms": ["814001"],

    # WorkforceDirector (815xxx)
    "gql_workforce_director_perms": ["815001"],

    "default_validations_disabled": False,
}


class WorkforceConfig(AppConfig):
    name = MODULE_NAME

    gql_query_workforces_perms = []

    gql_query_workforce_representative_perms = []
    gql_mutation_create_workforce_representative_perms = []
    gql_mutation_update_workforce_representative_perms = []
    gql_mutation_delete_workforce_representative_perms = []

    # WorkforceOrganization (802xxx)
    gql_query_workforce_organization_perms = []
    gql_mutation_create_workforce_organization_perms = []
    gql_mutation_update_workforce_organization_perms = []
    gql_mutation_delete_workforce_organization_perms = []

    # WorkforceOrganizationUnit (803xxx)
    gql_query_workforce_organization_unit_perms = []
    gql_mutation_create_workforce_organization_unit_perms = []
    gql_mutation_update_workforce_organization_unit_perms = []
    gql_mutation_delete_workforce_organization_unit_perms = []

    # WorkforceOrganizationUnitDesignation (804xxx)
    gql_query_workforce_organization_unit_designation_perms = []
    gql_mutation_create_workforce_organization_unit_designation_perms = []
    gql_mutation_update_workforce_organization_unit_designation_perms = []
    gql_mutation_delete_workforce_organization_unit_designation_perms = []

    # WorkforceOrganizationEmployee (805xxx)
    gql_query_workforce_organization_employee_perms = []
    gql_mutation_create_workforce_organization_employee_perms = []
    gql_mutation_update_workforce_organization_employee_perms = []
    gql_mutation_delete_workforce_organization_employee_perms = []

    # WorkforceOrganizationEmployeeDesignation (806xxx)
    gql_query_workforce_organization_employee_designation_perms = []
    gql_mutation_create_workforce_organization_employee_designation_perms = []
    gql_mutation_update_workforce_organization_employee_designation_perms = []
    gql_mutation_delete_workforce_organization_employee_designation_perms = []

    # WorkforceEmployer (807xxx)
    gql_query_workforce_employer_perms = []
    gql_mutation_create_workforce_employer_perms = []
    gql_mutation_update_workforce_employer_perms = []
    gql_mutation_delete_workforce_employer_perms = []

    # WorkforceOffice (808xxx)
    gql_query_workforce_office_perms = []
    gql_mutation_create_workforce_office_perms = []
    gql_mutation_update_workforce_office_perms = []
    gql_mutation_delete_workforce_office_perms = []

    # WorkforceFactory (809xxx)
    gql_query_workforce_factory_perms = []
    gql_mutation_create_workforce_factory_perms = []
    gql_mutation_update_workforce_factory_perms = []
    gql_mutation_delete_workforce_factory_perms = []

    # WorkforceEmployee (810xxx)
    gql_query_workforce_employee_perms = []
    gql_mutation_create_workforce_employee_perms = []
    gql_mutation_update_workforce_employee_perms = []
    gql_mutation_delete_workforce_employee_perms = []

    # WorkforceDocument (811xxx)
    gql_query_workforce_document_perms = []
    gql_mutation_create_workforce_document_perms = []
    gql_mutation_update_workforce_document_perms = []
    gql_mutation_delete_workforce_document_perms = []

    # WorkforceChecker (812xxx)
    gql_workforce_checker_perms = []

    # WorkforceChecker (813xxx)
    gql_workforce_approver_perms = []

    # WorkforceFactoryAdmin (814xxx)
    gql_workforce_factory_admin_perms = []

    # WorkforceDirector (815xxx)
    gql_workforce_director_perms = []

    default_validations_disabled = None

    def __load_config(self, cfg):
        for field in cfg:
            if hasattr(WorkforceConfig, field):
                setattr(WorkforceConfig, field, cfg[field])

    def ready(self):
        from core.models import ModuleConfiguration
        cfg = ModuleConfiguration.get_or_default(MODULE_NAME, DEFAULT_CFG)
        self.__load_config(cfg)
