from core.models import InteractiveUser


def create_interactive_user(last_name, other_names, login_name, role_id):
    user = InteractiveUser.objects.create(
        **{
            "language_id": "en",
            "last_name": last_name,
            "other_names": other_names,
            "login_name": login_name,
            "audit_user_id": -1,
            "role_id": role_id,
            "private_key": "facc88f5a86653bcec225d60265b853e991dde3d519e2838a45269646db3c3e3ffd8b1ff657f0c7981c49b81710048afcfb09fa17627bcc17382343dcaf86aac98cac232a7bac94c10bbbd32870b22ef2feaf888fc57b51ea9bfdd315d1d7c0e5bc170c70e113a2c9444cd412f8e02c98b248321300d354da7e025c0fb0b309f",
            "password": "2E94AA4A6B2DD9B359949449443F100C850DC516D6E94F1730AF218529FA9564"
        }
    )

    return user


class UserServices:
    pass
