import sys

from PyQt6.QtCore import pyqtSlot, QUrl, QJsonDocument
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtNetwork import (QNetworkRequest,
    QNetworkAccessManager, QSslConfiguration, QSsl,
    QNetworkReply,
)
from PyQt6.QtWidgets import QMessageBox

from . import app_globals as ag

URL = 'https://sourceforge.net/projects/fileo'

def check4update():
    request = QNetworkRequest()
    manager = QNetworkAccessManager(ag.app)
    config = QSslConfiguration(QSslConfiguration.defaultConfiguration())
    config.setProtocol(QSsl.SslProtocol.SecureProtocols)

    request.setSslConfiguration(config)
    request.setUrl(QUrl(f'{URL}/best_release.json'))
    request.setHeader(QNetworkRequest.KnownHeaders.ContentTypeHeader, "application/json")

    manager.get(request)
    manager.finished.connect(installer_update_replay)


@pyqtSlot(QNetworkReply)
def installer_update_replay(replay: QNetworkReply):
    if replay.error() is QNetworkReply.NetworkError.NoError:
        rep = replay.readAll()
        json_rep = QJsonDocument.fromJson(rep)
        obj = json_rep.object()
        release = obj['platform_releases']['windows']
        filename = release['filename'].toString()
        if filename.count('.') <= 1:
            ag.show_message_box(
                'Fileo',
                "Something went wrong, can't find any app.version in the repository. "
                'Please try again later.',
                icon=QMessageBox.Icon.Critical
            )
            return
        ver = filename[filename.find('.')+1:filename.rfind('.')]
        if ag.app_version() < ver:
            if getattr(sys, "frozen", False):
                get_sourceforge(ver)
            else:
                ag.show_message_box(
                    'Fileo',
                    f'New version "{ver}" available.'
                    'You can itstall it with "pip install md2fileo" command',
                    btn=QMessageBox.StandardButton.Ok
                )
        else:
            ag.show_message_box(
                'Fileo',
                'There are currently no updates available.',
                btn=QMessageBox.StandardButton.Ok
            )

def get_sourceforge(ver: str):
    btn_clicked = ag.show_message_box(
        'Fileo',
        f'New version "{ver}" available.',
        custom_btns=(
            ('Go to download', QMessageBox.ButtonRole.YesRole),
            ('Cancel', QMessageBox.ButtonRole.NoRole),
        )
    )
    if btn_clicked == 0:
        QDesktopServices.openUrl(QUrl(URL))
