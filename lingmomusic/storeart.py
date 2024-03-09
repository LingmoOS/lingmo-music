# Copyright 2020 The Lingmo Music developers
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

import gi
gi.require_versions({"MediaArt": "2.0", "Soup": "3.0"})
from gi.repository import Gio, GLib, GObject, MediaArt, Soup, GdkPixbuf

from lingmomusic.musiclogger import MusicLogger
from lingmomusic.utils import CoreObjectType


class StoreArt(GObject.Object):
    """Stores Art in the MediaArt cache.
    """

    __gsignals__ = {
        "finished": (GObject.SignalFlags.RUN_FIRST, None, ())
    }

    def __init__(self):
        """Initialize StoreArtistArt

        :param coreobject: The CoreArtist or CoreAlbum to store art for
        :param string uri: The art uri
        """
        super().__init__()

        self._coreobject = None

        self._file = None
        self._log = MusicLogger()
        self._soup_session = Soup.Session.new()

    def start(self, coreobject, uri, coreobjecttype):
        self._coreobject = coreobject

        if (uri is None
                or uri == ""):
            self.emit("finished")
            return

        if coreobjecttype == CoreObjectType.ARTIST:
            success, self._file = MediaArt.get_file(
                self._coreobject.props.artist, None, "artist")
        elif coreobjecttype == CoreObjectType.ALBUM:
            success, self._file = MediaArt.get_file(
                self._coreobject.props.artist, self._coreobject.props.title,
                "album")
        elif coreobjecttype == CoreObjectType.SONG:
            success, self._file = MediaArt.get_file(
                self._coreobject.props.artist, self._coreobject.props.album,
                "album")
        else:
            success = False

        if not success:
            self.emit("finished")
            return

        cache_dir = GLib.build_filenamev(
            [GLib.get_user_cache_dir(), "media-art"])
        cache_dir_file = Gio.File.new_for_path(cache_dir)
        cache_dir_file.query_info_async(
            Gio.FILE_ATTRIBUTE_ACCESS_CAN_READ, Gio.FileQueryInfoFlags.NONE,
            GLib.PRIORITY_DEFAULT_IDLE, None, self._cache_dir_info_read, uri)

    def _cache_dir_info_read(self, cache_dir_file, res, uri):
        try:
            cache_dir_file.query_info_finish(res)
        except GLib.Error:
            # directory does not exist yet
            try:
                cache_dir_file.make_directory(None)
            except GLib.Error as error:
                self._log.warning(
                    "Error: {}, {}".format(error.domain, error.message))
                self.emit("finished")
                return

        msg = Soup.Message.new("GET", uri)
        self._soup_session.send_and_read_async(
            msg, GLib.PRIORITY_DEFAULT, None, self._read_callback)

    def _read_callback(
            self, session: Soup.Session, result: Gio.AsyncResult) -> None:
        try:
            bytes = session.send_and_read_finish(result)
        except GLib.Error as error:
            self._log.debug(
                f"Failed to get remote art: {error.domain}, {error.message}")
            self.emit("finished")

        istream = Gio.MemoryInputStream.new_from_bytes(bytes)
        GdkPixbuf.Pixbuf.new_from_stream_async(
            istream, None, self._pixbuf_from_stream_finished)

    def _pixbuf_from_stream_finished(
            self, stream: Gio.MemoryInputStream,
            result: Gio.AsyncResult) -> None:
        try:
            pixbuf = GdkPixbuf.Pixbuf.new_from_stream_finish(result)
        except GLib.Error as error:
            self._log.warning(f"Error: {error.domain}, {error.message}")
            self.emit("finished")
        else:
            self._file.create_async(
                Gio.FileCreateFlags.NONE, GLib.PRIORITY_DEFAULT_IDLE, None,
                self._output_stream_created, pixbuf)
        finally:
            stream.close_async(
                GLib.PRIORITY_DEFAULT_IDLE, None, self._stream_closed)

    def _output_stream_created(
            self, stream: Gio.FileOutputStream, result: Gio.AsyncResult,
            pixbuf: GdkPixbuf.Pixbuf) -> None:
        try:
            output_stream = stream.create_finish(result)
        except GLib.Error as error:
            # File already exists.
            self._log.info(f"Error: {error.domain}, {error.message}")
            self.emit("finished")
        else:
            pixbuf.save_to_streamv_async(
                output_stream, "jpeg", None, None, None,
                self._output_stream_saved, output_stream)

    def _output_stream_saved(
            self, pixbuf: GdkPixbuf.Pixbuf, result: Gio.AsyncResult,
            output_stream: Gio.FileOutputStream) -> None:
        try:
            pixbuf.save_to_stream_finish(result)
        except GLib.Error as error:
            self._log.warning(f"Error: {error.domain}, {error.message}")
        else:
            self._coreobject.props.thumbnail = self._file.get_uri()
        finally:
            self.emit("finished")
            output_stream.close_async(
                GLib.PRIORITY_DEFAULT_IDLE, None, self._stream_closed)

    def _stream_closed(
            self, stream: Gio.OutputStream, result: Gio.AsyncResult) -> None:
        try:
            stream.close_finish(result)
        except GLib.Error as error:
            self._log.warning(f"Error: {error.domain}, {error.message}")
