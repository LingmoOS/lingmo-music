# Copyright 2018 The Lingmo Music developers
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

from gi.repository import Gtk


@Gtk.Template(resource_path='/org/lingmo/Music/ui/AboutDialog.ui')
class AboutDialog(Gtk.AboutDialog):
    """About dialog"""

    __gtype_name__ = 'AboutDialog'

    def __init__(self):
        super().__init__()
