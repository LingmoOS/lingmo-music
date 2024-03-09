# Copyright 2020 The Lingmo Music Developers
#
# Lingmo Music is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Lingmo Music is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with Lingmo Music; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# The Lingmo Music authors hereby grant permission for non-GPL compatible
# GStreamer plugins to be used and distributed together with GStreamer
# and Lingmo Music.  This permission is above and beyond the permissions
# granted by the GPL license by which Lingmo Music is covered.  If you
# modify this code, you may extend this exception to your version of the
# code, but you are not obligated to do so.  If you do not wish to do so,
# delete this exception statement from your version.

from gi.repository import GLib, GObject


class NotificationManager(GObject.Object):
    """Managing wrapper around the notification widgets
    """

    _pulse_id = 0
    _loading_counter = 0

    def __init__(self, application):
        """Initialize the notification manager

       :param Application application: The Application instance
       """
        super().__init__()

        self._application = application
        self._window = application.props.window

        if self._window is None:
            application.connect(
                "notify::window", self._on_window_changed)

    def _on_window_changed(self, klass, value):
        self._window = self._application.props.window
        if self._loading_counter > 0:
            self._window.loading_visible(True)

    def push_loading(self):
        """Push a loading notifcation."""
        self._loading_counter += 1

        if (self._pulse_id == 0
                and self._window):
            self._window.loading_visible(True)
            self._pulse_id = GLib.timeout_add(100, self._window.loading_pulse)

    def pop_loading(self):
        self._loading_counter -= 1

        if (self._loading_counter == 0
                and self._pulse_id != 0):
            GLib.Source.remove(self._pulse_id)
            self._pulse_id = 0
            if self._window:
                self._window.loading_visible(False)
