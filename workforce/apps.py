from django.apps import AppConfig

MODULE_NAME = "workforce"

DEFAULT_CFG = {
    "gql_query_workforces_perms": ["801001"],
    "gql_mutation_create_workforces_perms": ["801002"],
    "gql_mutation_update_workforces_perms": ["801003"],
    "gql_mutation_delete_workforces_perms": ["801004"],
    "default_validations_disabled": False,
}


class WorkforceConfig(AppConfig):
    name = MODULE_NAME

    gql_query_workforces_perms = []
    gql_mutation_create_workforces_perms = []
    gql_mutation_update_workforces_perms = []
    gql_mutation_delete_workforces_perms = []
    default_validations_disabled = None

    def __load_config(self, cfg):
        for field in cfg:
            if hasattr(WorkforceConfig, field):
                setattr(WorkforceConfig, field, cfg[field])

    def ready(self):
        from core.models import ModuleConfiguration
        cfg = ModuleConfiguration.get_or_default(MODULE_NAME, DEFAULT_CFG)
        self.__load_config(cfg)

