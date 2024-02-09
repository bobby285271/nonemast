# SPDX-FileCopyrightText: 2022 Jan Tojnar
# SPDX-License-Identifier: MIT

import os
import sys

from gi.repository import Adw
from gi.repository import Ggit
from gi.repository import Gio
from gi.repository import GLib
from gi.repository import Gtk
from .window import NonemastWindow, PreferencesWindow
from typing import Callable, Optional, Sequence, TypeVar


class NonemastApplication(Adw.Application):
    """The main application singleton class."""

    def __init__(self, version: str):
        super().__init__(
            application_id="cz.ogion.Nonemast",
            flags=Gio.ApplicationFlags.HANDLES_OPEN,
        )
        Ggit.init()
        self.version = version
        self.create_action("quit", self.on_quit_action, ["<primary>q"])
        self.create_action("about", self.on_about_action)
        self.create_action("preferences", self.on_preferences_action)

        if os.environ.get("NONEMAST_NO_GSCHEMA") == "1":
            self._settings = None
        else:
            self._settings = Gio.Settings(schema_id="cz.ogion.Nonemast")

    def do_activate(self, repo_path: Optional[Gio.File] = None) -> None:
        win = self.props.active_window
        if not win:
            if self._settings != None:
                repo_path = Gio.File.new_for_path(
                    str(self._settings.get_value("nixpkgs-path").unpack())
                )
            else:
                repo_path = Gio.File.new_for_path("/home/bobby285271/nixpkgs")
            win = NonemastWindow(application=self, repo_path=repo_path)
        win.present()

    def do_open(self, files: Sequence[Gio.File], n_files: int, hint: str) -> None:
        sys.exit("error: arguments shouldn't be handled by do_open.")

    def on_quit_action(
        self,
        action: Gio.SimpleAction,
        _parameter: None,
    ) -> None:
        self.quit()

    def on_about_action(
        self,
        action: Gio.SimpleAction,
        _parameter: None,
    ) -> None:
        """Callback for the app.about action."""
        about = Adw.AboutWindow(
            transient_for=self.props.active_window,
            application_name="Not Nearly Enough Masking Tape",
            application_icon="cz.ogion.Nonemast",
            license_type=Gtk.License.MIT_X11,
            version=self.version,
            developers=["Jan Tojnar"],
            copyright="© 2022 Jan Tojnar",
        )
        about.present()

    def on_preferences_action(self, widget, _):
        """Callback for the app.preferences action."""
        # print("app.preferences action activated")
        preferences = PreferencesWindow(self.props.active_window)
        preferences.present()

    T = TypeVar("T", bound=GLib.Variant | None)

    def create_action(
        self,
        name: str,
        callback: Callable[[Gio.SimpleAction, T], None],
        shortcuts: list[str] = [],
    ) -> None:
        """Add an application action.

        Args:
            name: the name of the action
            callback: the function to be called when the action is
              activated
            shortcuts: an optional list of accelerators
        """
        action = Gio.SimpleAction.new(name, None)
        action.connect("activate", callback)
        self.add_action(action)
        if shortcuts:
            self.set_accels_for_action(f"app.{name}", shortcuts)


def main(version: str) -> int:
    """The application's entry point."""
    app = NonemastApplication(
        version=version,
    )
    return app.run(sys.argv)
