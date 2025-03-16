# SPDX-FileCopyrightText: 2022 Jan Tojnar
# SPDX-License-Identifier: MIT

from gi.repository import Ggit
from gi.repository import Gio
from gi.repository import GLib
from gi.repository import GObject
from linkify_it import LinkifyIt
from typing import Optional
import html
import os
import re


def has_changelog_reviewed_tag(regex: str, line: str) -> bool:
    return re.match(regex, line, re.IGNORECASE)


def try_getting_corresponding_github_link(url: str) -> str:
    url = url.replace(
        "https://gitlab.gnome.org/GNOME/",
        "https://github.com/GNOME/",
    )

    for i in ["xfce", "thunar-plugins", "panel-plugins", "apps"]:
        url = url.replace(
            f"https://gitlab.xfce.org/{i}/",
            "https://github.com/xfce-mirror/",
        )

    if "https://github.com/" in url:
        url = url.replace("/-/", "/")
        url = url.replace("...", "..")

    return url


def find_changelog_link(lines: list[str]) -> Optional[str]:
    # Heuristics: First line starting with a URL is likely a changelog.
    for line in lines:
        line = line.strip()
        if line.startswith("https://"):
            return line
    for line in lines:
        ss = re.search(r"([^:]+): (.*?) -> (.*?)$", line)
        if line.startswith("xfce.") and ss:
            prefix = ss.group(1).strip().replace("xfce.", "", 1)
            xfcategory = "xfce"
            if prefix.endswith("plugin"):
                xfcategory = "panel-plugins"
            for xfapp in [
                "catfish",
                "gigolo",
                "mousepad",
                "orage",
                "parole",
                "ristretto",
                "xfburn",
                "xfce4-dict",
                "xfce4-mixer",
                "xfce4-notifyd",
                "xfce4-panel-profiles",
                "xfce4-screensaver",
                "xfce4-screenshooter",
                "xfce4-taskmanager",
                "xfce4-terminal",
                "xfce4-volumed-pulse",
                "xfdashboard",
                "xfmpc",
            ]:
                if xfapp == prefix:
                    xfcategory = "apps"

            version1 = ss.group(2).strip()
            version2 = ss.group(3).strip()
            return f"https://gitlab.xfce.org/{xfcategory}/{prefix}/-/compare/{prefix}-{version1}...{prefix}-{version2}"
    return None


def linkify_html(text: str) -> str:
    linkify = LinkifyIt()

    if not linkify.test(text):
        return ""

    result = ""
    last_index = 0
    for match in linkify.match(text):
        link = f"<a href='{html.escape(match.url)}'>{html.escape(match.text)}</a>"
        result += html.escape(text[last_index : match.index]) + link
        last_index = match.last_index

    result += text[last_index:]

    return result


class CommitInfo(GObject.Object):
    """Wrapper around Ggit.Commit exposing properties as GObject properties."""

    __gtype_name__ = "CommitInfo"

    id_gvariant = GObject.Property(type=GObject.TYPE_VARIANT)

    def __init__(self, repo: Ggit.Repository, commit: Ggit.Commit, **kwargs):
        super().__init__(**kwargs)
        self._repo = repo
        self._commit = commit

        self.bind_property(
            "id",
            self,
            "id-gvariant",
            GObject.BindingFlags.SYNC_CREATE,
            lambda _binding, subject: GLib.Variant.new_string(subject),
        )

    @GObject.Property(type=str)
    def id(self):
        return self._commit.get_id().to_string()

    @GObject.Property(type=str)
    def icon(self):
        subject = self._commit.get_subject()
        assert subject is not None, "subject cannot be empty"

        if subject.startswith("fixup! "):
            message = self._commit.get_message()
            assert message is not None, "message cannot be empty"
            message_body_is_empty = message.strip() == subject.strip()
            return "message-fixup-empty" if message_body_is_empty else "message-fixup"
        elif subject.startswith("amend! "):
            return "message-amend"
        elif subject.startswith("squash! "):
            return "message-squash"
        else:
            return "message-initial"

    @GObject.Property(type=str)
    def description(self):
        commit_parents = self._commit.get_parents()

        if commit_parents.get_size() > 0:
            parent_commit = commit_parents.get(0)
            commit_tree = self._commit.get_tree()
            parent_tree = parent_commit.get_tree()

            diff = Ggit.Diff.new_tree_to_tree(
                self._repo, parent_tree, commit_tree, None
            )

            num_deltas = diff.get_num_deltas()
            return (
                f"{num_deltas} delta in diff"
                if num_deltas == 1
                else f"{num_deltas} deltas in diff"
            )

        return ""

    def get_commit(self) -> Ggit.Commit:
        return self._commit


class PackageUpdate(GObject.Object):
    __gtype_name__ = "PackageUpdate"

    subject_gvariant = GObject.Property(type=GObject.TYPE_VARIANT)
    commit_message_is_edited = GObject.Property(type=bool, default=False)
    editing_stack_page = GObject.Property(type=str, default="not-editing")
    final_commit_message_rich = GObject.Property(type=str)
    changelog_reviewed_by_suggestion = GObject.Property(
        type=str, default="Changelog-reviewed-by: Foo bar <abc@example.com>"
    )

    def __init__(
        self,
        repo: Ggit.Repository,
        subject: str,
        commits: list[Ggit.Commit],
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._repo = repo
        self._subject = subject
        self._commits = Gio.ListStore.new(CommitInfo)
        self._message_lines: list[str] = []
        if os.environ.get("NONEMAST_NO_GSCHEMA") == "1":
            self._settings = None
        else:
            # self._settings = None
            self._settings = Gio.Settings(schema_id="cz.ogion.Nonemast")

        try:
            a_config: Ggit.Config = self._repo.get_config().snapshot()
            s_author_name = a_config.get_string("user.name")
            s_author_email = a_config.get_string("user.email")
        except:
            s_author_name, s_author_email = "Foo bar", "123@example.com"

        self.changelog_reviewed_by_suggestion = GLib.markup_escape_text(
            f"Changelog-reviewed-by: {s_author_name} <{s_author_email}>"
        )

        self.bind_property(
            "subject",
            self,
            "subject-gvariant",
            GObject.BindingFlags.SYNC_CREATE,
            lambda _binding, subject: GLib.Variant.new_string(subject),
        )

        for commit in commits:
            self.add_commit(commit)

        self.bind_property(
            "final-commit-message",
            self,
            "final-commit-message-rich",
            GObject.BindingFlags.SYNC_CREATE,
            lambda _binding, message: linkify_html(message),
        )

        self.bind_property(
            "commit-message-is-edited",
            self,
            "editing-stack-page",
            GObject.BindingFlags.SYNC_CREATE,
            lambda _binding, editing: "editing" if editing else "not-editing",
        )

    def add_commit(self, commit: Ggit.Commit) -> None:
        self._commits.append(CommitInfo(repo=self._repo, commit=commit))

        subject, *msg_lines = commit.get_message().splitlines()
        # Clone list so we can detect changes.
        old_message_lines = list(self._message_lines)
        if subject.startswith("fixup! "):
            return
        elif subject.startswith("amend! "):
            # Starting from scratch.
            self._message_lines = []
            # Drop empty line after subject.
            match msg_lines:
                case ["", *rest]:
                    msg_lines = rest
        elif not subject.startswith("squash! "):
            # The subject from non-squash commits remains.
            self._message_lines += [subject]

        self._message_lines += msg_lines
        if old_message_lines != self._message_lines:
            self.notify("final-commit-message")

        if self._settings != None:
            regex = str(self._settings.get_value("reviewed-regex").unpack())
        else:
            regex = r"^Changelog-reviewed-by: "

        self.props.changes_reviewed = any(
            has_changelog_reviewed_tag(regex, line) for line in self._message_lines
        )
        url = find_changelog_link(self._message_lines)
        if url is None:
            self.props.changelog_link = "No changelog detected."
        else:
            url_github = try_getting_corresponding_github_link(url)
            if url_github != url:
                self.props.changelog_link = f"<b><a href='{html.escape(url_github)}'>{html.escape(
                        url_github)}</a></b>\n\n<a href='{html.escape(url)}'>{html.escape(url)}</a>"
            else:
                self.props.changelog_link = (
                    f"<a href='{html.escape(url)}'>{html.escape(url)}</a>"
                )

    @GObject.Property(type=str)
    def subject(self):
        return self._subject

    @GObject.Property(type=str)
    def final_commit_message(self):
        return "\n".join(self._message_lines)

    @final_commit_message.setter
    def final_commit_message(self, message):
        self._message_lines = message.splitlines()

    @GObject.Property(type=str)
    def changelog_link(self):
        return self._changelog_link

    @changelog_link.setter
    def changelog_link(self, changelog_link: str) -> None:
        self._changelog_link = changelog_link

    @GObject.Property(type=bool, default=False)
    def changes_reviewed(self):
        return self._changes_reviewed

    @changes_reviewed.setter
    def changes_reviewed(self, changes_reviewed):
        self._changes_reviewed = changes_reviewed

    @GObject.Property(type=Gio.ListStore)
    def commits(self):
        return self._commits
