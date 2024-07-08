from dataclasses import dataclass
from enum import Enum

import transmission_rpc

from transmission_media_manager.settings import settings

_client = transmission_rpc.Client(
    host=settings.transmission_host,
    port=settings.transmission_port,
    username=settings.transmission_username,
    password=settings.transmission_password,
)


class MediaType(Enum):
    MOVIES = 'movies'
    SHOWS = 'shows'
    MUSIC = 'music'

    @classmethod
    def values(cls):
        return [mt.value for mt in MediaType]


class Media:
    BASE_MEDIA = '/downloads/complete/media'

    def __init__(self, username: str):
        self._media = self.BASE_MEDIA + f'/{username}'
        self.movies = self._media + '/' + MediaType.MOVIES.value
        self.shows = self._media + '/' + MediaType.SHOWS.value
        self.music = self._media + '/' + MediaType.MUSIC.value

    def get_media_path(self, media_type: MediaType):
        return self._media + '/' + media_type.value


class UserClient:
    def __init__(self, username: str):
        self.username = username
        self.media = Media(username)

    @property
    def movies(self) -> str:
        return self.get_media_resource(self.media.movies)

    @property
    def shows(self) -> str:
        return self.get_media_resource(self.media.shows)

    @property
    def music(self) -> str:
        return self.get_media_resource(self.media.music)

    def get_media_resource(self, resource: str):
        torrents = _client.get_torrents()
        return '\n\n'.join([
            f'- {torrent.name}'
            for torrent in torrents
            if torrent.download_dir == resource
        ])


def add_torrent(torrent_file, torrent_path):
    _client.add_torrent(torrent=torrent_file, download_dir=torrent_path)


class GeneralClient(UserClient):
    def __init__(self):
        super().__init__('all')
