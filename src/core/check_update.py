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

def check4update(silently: bool=False):
    request = QNetworkRequest()
    manager = QNetworkAccessManager(ag.app)
    config = QSslConfiguration(QSslConfiguration.defaultConfiguration())
    config.setProtocol(QSsl.SslProtocol.SecureProtocols)

    request.setSslConfiguration(config)
    request.setUrl(QUrl(f'{URL}/best_release.json'))
    request.setHeader(QNetworkRequest.KnownHeaders.ContentTypeHeader, "application/json")

    manager.get(request)
    manager.finished.connect(lambda replay, cond=silently: installer_update_replay(replay, cond))

@pyqtSlot(QNetworkReply, bool)
def installer_update_replay(replay: QNetworkReply, silently: bool):
    if replay.error() is QNetworkReply.NetworkError.NoError:
        rep = replay.readAll()
        json_rep = QJsonDocument.fromJson(rep)
        obj = json_rep.object()
        release = obj['platform_releases']['windows']
        filename = release['filename'].toString()
        if filename.count('.') <= 1:
            if not silently:
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
                open_sourceforge(ver)
            else:
                ag.show_message_box(
                    'Fileo',
                    f'New version "{ver}" available.'
                    'You can itstall it with "pip install md2fileo" command',
                    btn=QMessageBox.StandardButton.Ok
                )
        elif not silently:
            ag.show_message_box(
                'Fileo',
                'There are currently no updates available.',
                btn=QMessageBox.StandardButton.Ok
            )

def open_sourceforge(ver: str):
    msgbox = QMessageBox(ag.app)
    msgbox.setWindowTitle('Fileo')
    msgbox.setText(f'New version "{ver}" available.',)
    go_btn = msgbox.addButton('Go to download', QMessageBox.ButtonRole.YesRole)
    msgbox.addButton('Cancel', QMessageBox.ButtonRole.YesRole)
    msgbox.setIcon(QMessageBox.Icon.Information)

    msgbox.exec()

    if msgbox.clickedButton() is go_btn:
        QDesktopServices.openUrl(QUrl(URL))
