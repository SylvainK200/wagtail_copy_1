import logging

from django.core.exceptions import PermissionDenied
from django.db import transaction
from treebeard.mp_tree import MP_MoveHandler

from wagtail.log_actions import log
from wagtail.signals import post_page_move, pre_page_move

logger = logging.getLogger("wagtail")


class MovePagePermissionError(PermissionDenied):
    """
    Raised when the page move cannot be performed due to insufficient permissions.
    """

    pass


class MovePageAction:
    def __init__(self, page, target, pos=None, user=None):
        self.page = page
        self.target = target
        self.pos = pos
        self.user = user

    def check(self, parent_after, skip_permission_checks=False):
        if self.user and not skip_permission_checks:
            if not self.page.permissions_for_user(self.user).can_move_to(parent_after):
                raise MovePagePermissionError(
                    "You do not have permission to move the page to the target specified."
                )

    def _move_page(self, page, target, parent_after):
        from wagtail.models import Page

        # Determine old and new url_paths
        # Fetching new object to avoid affecting `page`
        page = Page.objects.get(id=page.id)
        old_url_path = page.url_path
        old_path = page.path
        old_depth = page.depth

        if self.pos == "first-child":
            new_path = parent_after.path + "0001"
        elif self.pos == "last-child":
            new_path = parent_after.path + "%04d" % (parent_after.get_children_count() + 1)
        elif self.pos == "sorted-child":
            new_path = parent_after.path + "%04d" % (
                target.get_next_siblings().count() + 1
            )
        else:
            new_path = target.path

        # Move the page
        with transaction.atomic():
            pre_page_move.send(sender=page.specific_class, instance=page, user=self.user)

            # Move the page
            page.move(new_path, pos=self.pos)

            # Update the url_path of the page and all its descendants
            page.url_path = page.get_url_path()
            page.save()

            # Update the url_paths of all pages that were moved as a result of this operation
            for moved_page in Page.objects.filter(path__startswith=old_path).exclude(
                path=old_path
            ):
                moved_page.url_path = moved_page.get_url_path()
                moved_page.save()

            post_page_move.send(
                sender=page.specific_class, instance=page, user=self.user
            )

        # Log the action
        log(
            "wagtail.pages.move",
            self.user,
            page,
            extra_data={
                "old_url_path": old_url_path,
                "old_path": old_path,
                "old_depth": old_depth,
                "new_path": page.path,
                "new_url_path": page.url_path,
                "new_depth": page.depth,
            },
        )

        return page
    def execute(self, skip_permission_checks=False):
        if self.pos in ("first-child", "last-child", "sorted-child"):
            parent_after = self.target
        else:
            parent_after = self.target.get_parent()

        self.check(parent_after, skip_permission_checks=skip_permission_checks)

        return self._move_page(self.page, self.target, parent_after)
