import logging
import uuid
import json
import base64
from django.core.exceptions import ValidationError
from core.services import BaseService
from core.models.user import Role, RoleRight
from workforce.models import WorkforceCommittee, WorkforceCommitteeAssociationMap, WorkforceAllAssociation

logger = logging.getLogger(__name__)

def extract_uuid(encoded_str):
    decoded = base64.b64decode(encoded_str).decode()
    return decoded.split(":")[1]

class WorkforceCommitteeServices(BaseService):
    OBJECT_TYPE = WorkforceCommittee

    def create(self, obj_data):
        """
        Create a WorkforceCommittee with the following logic:
        1. Create a Role with name_en
        2. Copy RoleRights from role_id=58 to the new role
        3. Create the committee with the new role_id
        4. Create association mappings from JSON data
        """
        # Extract committee data
        name_en = obj_data.get("name_en")
        name_bn = obj_data.get("name_bn")
        associations_json = obj_data.get("associations")
        
        if not name_en:
            raise ValidationError("name_en is required for creating a committee")
        
        # Step 1: Create a Role
        try:
            new_role = Role(
                uuid=uuid.uuid4(),
                name=name_en,
                is_system=0,
                is_blocked=False,
                audit_user_id=1
            )
            new_role.save()
            logger.info(f"Created new role {new_role.id} for committee {name_en}")
        except Exception as e:
            logger.error(f"Error creating role: {str(e)}")
            raise ValidationError(f"Error creating role: {str(e)}")
        
        # Step 2: Copy RoleRights from role_id=58
        try:
            association_roles= Role.objects.filter(id__in=[66,58,49]).first()
            source_role_rights = RoleRight.objects.filter(role_id=association_roles.id)
            if not source_role_rights.exists():
                logger.warning("No RoleRights found for role_id=58")
            
            for source_right in source_role_rights:
                new_role_right = RoleRight(
                    role_id=new_role.id,
                    right_id=source_right.right_id,
                    audit_user_id=1
                )
                new_role_right.save()
            
            logger.info(f"Copied {source_role_rights.count()} role rights to new role {new_role.id}")
        except Exception as e:
            logger.error(f"Error copying role rights: {str(e)}")
            raise ValidationError(f"Error copying role rights: {str(e)}")
        
        # Step 3: Create the committee with the new role_id
        obj_data["assigned_role_id"] = new_role.id
        
        try:
            committee = super().create(obj_data)
            logger.info(f"Created committee with role_id {new_role.id}")
        except Exception as e:
            logger.error(f"Error creating committee: {str(e)}")
            raise ValidationError(f"Error creating committee: {str(e)}")
        
        # Step 4: Create association mappings
        if associations_json:
            try:
                # Parse JSON if it's a string
                if isinstance(associations_json, str):
                    associations_data = json.loads(associations_json)
                else:
                    associations_data = associations_json
                
                # Create mapping for each association
                associations_list = associations_data
                
                for record in associations_list:
                    try:
                        node= record["node"]
                        association_id= extract_uuid(node["id"])
                        # Verify the association exists
                        association = WorkforceAllAssociation.objects.get(id=association_id)
                        
                        association_map = WorkforceCommitteeAssociationMap(
                            committee_id=committee.get("data").get("id"),
                            all_association_id=association.id
                        )
                        association_map.save(username= self.user.username)
                        logger.info(f"Created association mapping for committee and association {association_id}")
                    except WorkforceAllAssociation.DoesNotExist:
                        logger.warning(f"Association with id {association_id} not found")
                        raise ValidationError(f"Association with id {association_id} not found")
                    except Exception as e:
                        logger.error(f"Error creating association mapping: {str(e)}")
                        raise ValidationError(f"Error creating association mapping: {str(e)}")
                
                logger.info(f"Created {len(associations_list)} association mappings for committee")
            except json.JSONDecodeError:
                logger.warning("Invalid JSON format for associations")
                raise ValidationError("Invalid JSON format for associations")
            except Exception as e:
                logger.error(f"Error processing associations: {str(e)}")
                raise ValidationError(f"Error processing associations: {str(e)}")
        
        return committee

    def update(self, obj_data):
        return super().update(obj_data)
