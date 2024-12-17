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
            "private_key": "C1C224B03CD9BC7B6A86D77F5DACE40191766C485CD55DC48CAF9AC873335D6F",
            "password": "59E66831C680C19E8736751D5480A7C3291BD8775DF47C19C4D0361FBC1C3438"
        }
    )

    return user

class UserServices:
    pass
