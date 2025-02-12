from gitlab import cli
from gitlab import exceptions as exc
from gitlab import types
from gitlab.base import RequiredOptional, RESTManager, RESTObject
from gitlab.mixins import (
    CreateMixin,
    CRUDMixin,
    DeleteMixin,
    ListMixin,
    ObjectDeleteMixin,
    ParticipantsMixin,
    RetrieveMixin,
    SaveMixin,
    SubscribableMixin,
    TimeTrackingMixin,
    TodoMixin,
    UserAgentDetailMixin,
)

from .award_emojis import ProjectIssueAwardEmojiManager  # noqa: F401
from .discussions import ProjectIssueDiscussionManager  # noqa: F401
from .events import (  # noqa: F401
    ProjectIssueResourceLabelEventManager,
    ProjectIssueResourceMilestoneEventManager,
    ProjectIssueResourceStateEventManager,
)
from .notes import ProjectIssueNoteManager  # noqa: F401

__all__ = [
    "Issue",
    "IssueManager",
    "GroupIssue",
    "GroupIssueManager",
    "ProjectIssue",
    "ProjectIssueManager",
    "ProjectIssueLink",
    "ProjectIssueLinkManager",
]


class Issue(RESTObject):
    _url = "/issues"
    _short_print_attr = "title"


class IssueManager(RetrieveMixin, RESTManager):
    _path = "/issues"
    _obj_cls = Issue
    _list_filters = (
        "state",
        "labels",
        "milestone",
        "scope",
        "author_id",
        "assignee_id",
        "my_reaction_emoji",
        "iids",
        "order_by",
        "sort",
        "search",
        "created_after",
        "created_before",
        "updated_after",
        "updated_before",
    )
    _types = {"iids": types.ListAttribute, "labels": types.ListAttribute}


class GroupIssue(RESTObject):
    pass


class GroupIssueManager(ListMixin, RESTManager):
    _path = "/groups/%(group_id)s/issues"
    _obj_cls = GroupIssue
    _from_parent_attrs = {"group_id": "id"}
    _list_filters = (
        "state",
        "labels",
        "milestone",
        "order_by",
        "sort",
        "iids",
        "author_id",
        "assignee_id",
        "my_reaction_emoji",
        "search",
        "created_after",
        "created_before",
        "updated_after",
        "updated_before",
    )
    _types = {"iids": types.ListAttribute, "labels": types.ListAttribute}


class ProjectIssue(
    UserAgentDetailMixin,
    SubscribableMixin,
    TodoMixin,
    TimeTrackingMixin,
    ParticipantsMixin,
    SaveMixin,
    ObjectDeleteMixin,
    RESTObject,
):
    _short_print_attr = "title"
    _id_attr = "iid"

    awardemojis: ProjectIssueAwardEmojiManager
    discussions: ProjectIssueDiscussionManager
    links: "ProjectIssueLinkManager"
    notes: ProjectIssueNoteManager
    resourcelabelevents: ProjectIssueResourceLabelEventManager
    resourcemilestoneevents: ProjectIssueResourceMilestoneEventManager
    resourcestateevents: ProjectIssueResourceStateEventManager

    @cli.register_custom_action("ProjectIssue", ("to_project_id",))
    @exc.on_http_error(exc.GitlabUpdateError)
    def move(self, to_project_id, **kwargs):
        """Move the issue to another project.

        Args:
            to_project_id(int): ID of the target project
            **kwargs: Extra options to send to the server (e.g. sudo)

        Raises:
            GitlabAuthenticationError: If authentication is not correct
            GitlabUpdateError: If the issue could not be moved
        """
        path = "%s/%s/move" % (self.manager.path, self.get_id())
        data = {"to_project_id": to_project_id}
        server_data = self.manager.gitlab.http_post(path, post_data=data, **kwargs)
        self._update_attrs(server_data)

    @cli.register_custom_action("ProjectIssue")
    @exc.on_http_error(exc.GitlabGetError)
    def related_merge_requests(self, **kwargs):
        """List merge requests related to the issue.

        Args:
            **kwargs: Extra options to send to the server (e.g. sudo)

        Raises:
            GitlabAuthenticationError: If authentication is not correct
            GitlabGetErrot: If the merge requests could not be retrieved

        Returns:
            list: The list of merge requests.
        """
        path = "%s/%s/related_merge_requests" % (self.manager.path, self.get_id())
        return self.manager.gitlab.http_get(path, **kwargs)

    @cli.register_custom_action("ProjectIssue")
    @exc.on_http_error(exc.GitlabGetError)
    def closed_by(self, **kwargs):
        """List merge requests that will close the issue when merged.

        Args:
            **kwargs: Extra options to send to the server (e.g. sudo)

        Raises:
            GitlabAuthenticationError: If authentication is not correct
            GitlabGetErrot: If the merge requests could not be retrieved

        Returns:
            list: The list of merge requests.
        """
        path = "%s/%s/closed_by" % (self.manager.path, self.get_id())
        return self.manager.gitlab.http_get(path, **kwargs)


class ProjectIssueManager(CRUDMixin, RESTManager):
    _path = "/projects/%(project_id)s/issues"
    _obj_cls = ProjectIssue
    _from_parent_attrs = {"project_id": "id"}
    _list_filters = (
        "iids",
        "state",
        "labels",
        "milestone",
        "scope",
        "author_id",
        "assignee_id",
        "my_reaction_emoji",
        "order_by",
        "sort",
        "search",
        "created_after",
        "created_before",
        "updated_after",
        "updated_before",
    )
    _create_attrs = RequiredOptional(
        required=("title",),
        optional=(
            "description",
            "confidential",
            "assignee_ids",
            "assignee_id",
            "milestone_id",
            "labels",
            "created_at",
            "due_date",
            "merge_request_to_resolve_discussions_of",
            "discussion_to_resolve",
        ),
    )
    _update_attrs = RequiredOptional(
        optional=(
            "title",
            "description",
            "confidential",
            "assignee_ids",
            "assignee_id",
            "milestone_id",
            "labels",
            "state_event",
            "updated_at",
            "due_date",
            "discussion_locked",
        ),
    )
    _types = {"iids": types.ListAttribute, "labels": types.ListAttribute}


class ProjectIssueLink(ObjectDeleteMixin, RESTObject):
    _id_attr = "issue_link_id"


class ProjectIssueLinkManager(ListMixin, CreateMixin, DeleteMixin, RESTManager):
    _path = "/projects/%(project_id)s/issues/%(issue_iid)s/links"
    _obj_cls = ProjectIssueLink
    _from_parent_attrs = {"project_id": "project_id", "issue_iid": "iid"}
    _create_attrs = RequiredOptional(required=("target_project_id", "target_issue_iid"))

    @exc.on_http_error(exc.GitlabCreateError)
    def create(self, data, **kwargs):
        """Create a new object.

        Args:
            data (dict): parameters to send to the server to create the
                         resource
            **kwargs: Extra options to send to the server (e.g. sudo)

        Returns:
            RESTObject, RESTObject: The source and target issues

        Raises:
            GitlabAuthenticationError: If authentication is not correct
            GitlabCreateError: If the server cannot perform the request
        """
        self._check_missing_create_attrs(data)
        server_data = self.gitlab.http_post(self.path, post_data=data, **kwargs)
        source_issue = ProjectIssue(self._parent.manager, server_data["source_issue"])
        target_issue = ProjectIssue(self._parent.manager, server_data["target_issue"])
        return source_issue, target_issue
