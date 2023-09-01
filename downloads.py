from datetime import datetime
from pathlib import Path
import sqlite3
import json

import main
from PySide6.QtCore import Signal, QObject, Slot
from PySide6.QtWebEngineCore import QWebEngineDownloadRequest,QWebEngineNotification
from PySide6.QtWidgets import QMessageBox, QFileDialog
from plyer import notification
from sqlalchemy import String, Column, DateTime, Integer
from sqlalchemy.orm import Session, declarative_base
from sqlalchemy import create_engine


class UserBase:
    db = declarative_base()
    filename = 'userbase.db'
    window = main.WebBrowser
    def __init__(self, window):
        self.window = window
        self.__db_path = None
        Path("C:\\WebMess").mkdir(parents=True,exist_ok=True)
        self.engine = None
        self.__db_path = Path("C:\\WebMess",self.filename)
        sqlite3.connect(self.__db_path)
        self.engine = create_engine(f'sqlite:///{self.__db_path}')
        self.session = Session(bind=self.engine)
        UserBase.db.metadata.create_all(self.engine)

class _DownloadsT(UserBase.db):
    __tablename__ = 'Downloads'
    name = Column(String, primary_key=True)
    url = Column(String)
    total_bytes = Column(Integer, default=-1)
    received_bytes = Column(Integer, default=-1)
    path = Column(String)
    date = Column(DateTime, default=datetime.now)
    status = Column(String, default='Неизвестно')


class Downloads(QObject):
    download_add = Signal(object)
    download_remove = Signal(object)
    download_remove_all = Signal()
    state_dict = {
        QWebEngineDownloadRequest.DownloadState.DownloadCompleted: {
            'notify_title': 'Файл загружен',
            'status': 'Завершен'
        },
        QWebEngineDownloadRequest.DownloadState.DownloadInterrupted: {
            'notify_title': 'Ошибка загрузки файла',
            'status': 'Ошибка'
        },
        QWebEngineDownloadRequest.DownloadState.DownloadCancelled: {
            'notify_title': 'Загрузка файла отменена',
            'status': 'Отменен'
        }
    }

    def __init__(self, window):
        super().__init__(window)
        self.window = window
        self.session = Session(self)
        self.userbase = UserBase(self)
        self.session = self.userbase.session

    def get_all(self) -> list:
        """Возвращает список объектов из таблицы"""
        return self.session.query(_DownloadsT).all()

    @Slot(QWebEngineDownloadRequest)
    def download_request(self, request: QWebEngineDownloadRequest):
        """Срабатывает, когда страница посылает запрос на загрузку файла"""
        if DownloadMethod.Method(self, request):
            download_item = self.session.query(_DownloadsT).filter_by(name=request.downloadFileName()).first()
            if download_item is None:
                download_item = _DownloadsT(name=request.downloadFileName(),
                                            url=request.url().toString(),
                                            path=request.downloadDirectory(),
                                            received_bytes=request.receivedBytes(),
                                            total_bytes=request.totalBytes())
                self.session.add(download_item)
            else:
                download_item.url = request.url().toString()
                download_item.path = request.downloadDirectory()
                download_item.received_bytes = request.receivedBytes()
                download_item.total_bytes = request.totalBytes()
            self.session.commit()
            download_item.request = request
            request.accept()
            self.download_add.emit(download_item)
            request.receivedBytesChanged.connect(lambda: self.received_bytes_changed(download_item))
            request.totalBytesChanged.connect(lambda: self.total_bytes_changed(download_item))
            request.isFinishedChanged.connect(lambda: self.finished(download_item))
            print(f'[Загрузки]: Началась загрузка файла ({download_item.name})')
        else:
            request.cancel()
        DownloadMethod.Method = DownloadMethod.MessageBox

    def remove(self, item: _DownloadsT) -> None:
        """Удаляет запись о загрузке из таблицы"""
        if hasattr(item, 'request'):
            item.request.cancel()
        self.session.delete(item)
        self.session.commit()
        self.download_remove.emit(item)

    def remove_all(self) -> None:
        """Удаляет все записи о загрузках из таблицы"""
        self.session.query(_DownloadsT).delete()
        self.session.commit()
        self.download_remove_all.emit()

    @Slot(_DownloadsT)
    def received_bytes_changed(self, item: _DownloadsT):
        """Обновляет данные о полученных байтах"""
        item.received_bytes = item.request.receivedBytes()

    @Slot(_DownloadsT)
    def total_bytes_changed(self, item: _DownloadsT):
        """Обновляет данные о размере файла"""
        item.total_bytes = item.request.totalBytes()
        self.session.commit()

    @Slot(_DownloadsT)
    def finished(self, item: _DownloadsT):
        """Выводит уведомление и удаляет запрос"""
        state = self.state_dict.get(item.request.state(), {
            'notify_title': 'Файл не был загружен',
            'status': 'Неизвестно'
        })
        item.status = state['status']
        notification.notify(
            title=state['notify_title'],
            message=item.path,
            app_name='Python',
        )
        item.request.deleteLater()
        del item.request
        self.session.commit()


class DownloadMethod(QObject):
    @classmethod
    def MessageBox(cls, parent, request: QWebEngineDownloadRequest):
        message_box = QMessageBox(parent.window)
        message_box.setWindowTitle('Подтверждение операции')
        message_box.setIcon(QMessageBox.Question)
        message_box.setText('Сохранить в загрузках?')
        message_box.setInformativeText(request.downloadFileName())
        message_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.StandardButton.Reset)
        message_box.button(QMessageBox.Yes).setText('Сохранить')
        message_box.button(QMessageBox.No).setText('Отменить')
        message_box.button(QMessageBox.Reset).setText('Выбрать место')
        btn = message_box.exec()

        if btn == QMessageBox.Yes:
            return True
        elif btn == QMessageBox.Reset:
            path = Path(QFileDialog.getSaveFileName(parent.window, 'Сохранить файл как', request.downloadFileName())[0])
            if str(path) != '.':
                request.setDownloadFileName(path.name)
                request.setDownloadDirectory(str(path.parent))
                return True
        return False

    @classmethod
    def SaveAs(cls, parent, request: QWebEngineDownloadRequest):
        path = Path(QFileDialog.getSaveFileName(parent.window, 'Сохранить файл как', request.downloadFileName())[0])

        if str(path) != '.':
            request.setDownloadFileName(path.name)
            request.setDownloadDirectory(str(path.parent))
            return True
        return False

    Method = MessageBox
