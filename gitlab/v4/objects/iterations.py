from gitlab.base import RequiredOptional, RESTManager, RESTObject
from gitlab.mixins import (
	CRUDMixin,
	ListMixin
)

__all__ = [
    "GroupIteration",
    "GroupIterationManager"
]

class GroupIteration(ListMixin, RESTObject):
	pass
	
class GroupIterationManager(CRUDMixin, RESTManager):
    _path = "/groups/%(group_id)s/iterations"
    _obj_cls = GroupIteration
    _from_parent_attrs = {"group_id": "id"}
    _list_filters = (
        "state",
        "iids",
        "search",
        "created_after",
        "created_before",
        "updated_after",
        "updated_before",
    )
