import logging
from core.models import InteractiveUser, User

logger = logging.getLogger(__name__)


class UpdateInteractiveUserServices():
    OBJECT_TYPE = InteractiveUser

    def update(self, obj_data: dict):
        user_id = obj_data.get("id")
        if not user_id:
            raise ValueError("id is required to update InteractiveUser")

        user = InteractiveUser.objects.get(id=user_id)

        for field in ("last_name", "other_names", "phone"):
            value = obj_data.get(field)
            if value is not None:
                setattr(user, field, value)

        email = obj_data.get("email_id") or obj_data.get("emailId")
        if email:
            user.email = email

        user.save()
        return user

