import os
import pathlib
import profile
import shutil
from subprocess import call
import sys
import time
import traceback

from style import style_application
import downloads
from PySide6.QtCore import QUrl, QTimeZone, QTimer, QCoreApplication, QRect, QMetaObject, Qt, QSize, Signal
from PySide6.QtGui import QIcon, QAction, QCursor, QPixmap, QMouseEvent,QDesktopServices,QGuiApplication
from PySide6.QtWidgets import QApplication, QMainWindow, QStatusBar, QTabWidget, QToolBar, QTabBar, QToolButton, \
    QPushButton, QStyle, QWidget, QHBoxLayout, QLabel, QLineEdit, QVBoxLayout, QSizePolicy, QSplitter,QCheckBox
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineSettings, QWebEngineProfile, QWebEnginePage,QWebEngineFullScreenRequest



class HtmlView(QWebEngineView):
    def createWindow(self, wintype):
        return self
class WebEnginePage(QWebEnginePage):
    def acceptNavigationRequest(self, url,  _type, isMainFrame):
        if _type == QWebEnginePage.NavigationType.NavigationTypeLinkClicked:
            return True
        return QWebEnginePage.acceptNavigationRequest(self, url, _type, isMainFrame)
class WebBrowser(QMainWindow):
    def __init__(self,profile=None):
        super().__init__()
        self.proxy_auth = None
        self.profile = None

        self.tabs = QTabWidget(self)
        self.tabs.tabCloseRequested.connect(lambda index: self.close_current_tab(index))
        self.tabs.tabBarClicked.connect(self.click_to_tab)
        self.downloads = downloads.Downloads(self)

        # Properties
        self.tabs.setTabsClosable(False)
        self.tabs.setMovable(True)
        self.tabs.setDocumentMode(True)
        self.tabs.setElideMode(Qt.ElideRight)
        self.setCentralWidget(self.tabs)
        self.setGeometry(100, 100, 1000, 850)
        self.centralWidget().setPalette(QGuiApplication.palette())
        self.centralWidget().setAttribute(Qt.WA_DeleteOnClose,True)


        toolbar = QToolBar("Navigation")
        self.addToolBar(Qt.ToolBarArea.LeftToolBarArea,toolbar)
        toolbar.visibilityChanged.connect(lambda :toolbar.setVisible(True))
        toolbar.setIconSize(QSize(45, 45))


        vk_but = QAction(QIcon("Vkontakte.ico"),"Вконтакте", self)
        vk_but.setToolTip("Вконтакте")
        vk_but.setStatusTip("Открыть ВКОНТАКТЕ")
        vk_but.triggered.connect(lambda: self.add_new_tab(QUrl('https://vk.com/'), 'VKontakte              '))
        toolbar.addAction(vk_but)

        tg_but = QAction(QIcon("telegramm.ico"), "Телеграмм", self)
        tg_but.setStatusTip("GO TO TELEGRAMM")
        tg_but.triggered.connect(lambda: self.add_new_tab(QUrl('http://web.telegram.org/k'), 'Telegramm              '))
        toolbar.addAction(tg_but)

        mt_but = QAction(QIcon("Mattermost.ico"), "Маттермост", self)
        mt_but.setStatusTip("GO TO MATTERMOST")
        mt_but.triggered.connect(lambda: self.add_new_tab(QUrl('https://mattermost.web.cern.ch/login'), 'Mattermost'))
        toolbar.addAction(mt_but)

        cld_but = QAction(QIcon("Google.ico"), "Календарь", self)
        cld_but.setStatusTip("Открыть календарь")
        cld_but.triggered.connect(lambda: self.add_new_tab(QUrl('https://calendar.google.com'), 'Google'))
        toolbar.addAction(cld_but)



        jv_but = QAction(QIcon("jivo.png"), "Jivo сайт", self)
        jv_but.setStatusTip("Живо сайт")
        jv_but.triggered.connect(lambda: self.add_new_tab(QUrl('https://app.jivosite.com/login'), 'Jivo', ))
        toolbar.addAction(jv_but)


        wapp_but = QAction(QIcon("whatsapp.ico"),"Whatsapp",self)
        wapp_but.triggered.connect(lambda:self.Whatsapp(QUrl("https://web.whatsapp.com/"),"Whatsapp"))
        toolbar.addAction(wapp_but)

        btrx_but = QAction(QIcon("Bitrix24.ico"),'Bitrix',self)
        btrx_but.triggered.connect(lambda:self.add_new_tab(QUrl("https://b24-qr3551.bitrix24.ru/shop/orders/kanban/"),"Bitrix"))
        toolbar.addAction(btrx_but)



        if profile is None:
            self.profile = QWebEngineProfile('WebProfile')
            settings = self.profile.settings()
            settings.setAttribute(QWebEngineSettings.WebAttribute.WebRTCPublicInterfacesOnly, True)
            settings.setAttribute(QWebEngineSettings.WebAttribute.AllowRunningInsecureContent, True)
            settings.setAttribute(QWebEngineSettings.WebAttribute.ScrollAnimatorEnabled,
                                                 True)
            settings.setAttribute(QWebEngineSettings.WebAttribute.ErrorPageEnabled, True)
            settings.setAttribute(QWebEngineSettings.WebAttribute.FullScreenSupportEnabled, True)
            settings.setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, True)
            settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
            settings.setDefaultTextEncoding('utf-8')
            settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls,True)
            settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls,True)
            settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
            settings.setAttribute(QWebEngineSettings.WebAttribute.PlaybackRequiresUserGesture, True)
            settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanOpenWindows,True)
            settings.setAttribute(QWebEngineSettings.WebAttribute.ScreenCaptureEnabled,True)
            settings.setAttribute(QWebEngineSettings.WebAttribute.AllowWindowActivationFromJavaScript,True)

            self.profile.setCachePath(f'C:\\WebMess\\cache')
            self.profile.setPersistentStoragePath(f'C:\\WebMess\\web_storage')
            self.profile.downloadRequested.connect(self.downloads.download_request)
            self.add_new_tab(QUrl("http://www.yandex.ru"))
            self.Whatsapp(QUrl("https://web.whatsapp.com/"), "Whatsapp")
        else:
            self.profile = profile
            self.profile.settings().setDefaultTextEncoding('utf-8')
            self.profile.settings().setAttribute(QWebEngineSettings.WebAttribute.ScrollAnimatorEnabled,
                                                 True)
            self.profile.settings().setAttribute(QWebEngineSettings.WebAttribute.ErrorPageEnabled, True)
            self.profile.settings().setAttribute(QWebEngineSettings.WebAttribute.FullScreenSupportEnabled, True)
            self.profile.settings().setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, True)
            self.profile.settings().setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
            self.profile.settings().setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
            self.profile.settings().setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
            self.profile.settings().setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
            self.profile.settings().setAttribute(QWebEngineSettings.WebAttribute.PlaybackRequiresUserGesture, True)
            self.profile.settings().setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanOpenWindows, True)
            self.profile.settings().setAttribute(QWebEngineSettings.WebAttribute.ScreenCaptureEnabled, True)
            self.profile.settings().setAttribute(QWebEngineSettings.WebAttribute.AllowWindowActivationFromJavaScript,True)
            self.add_new_tab(QUrl("http://www.yandex.ru"))
            self.Whatsapp(QUrl("https://web.whatsapp.com/"), "Whatsapp")


    def click_to_tab(self, index):
        mouse_button = self.mouseButton()

    def mouseButton(self):
        buttons = {Qt.LeftButton: 'LeftButton', Qt.MouseButton.RightButton: 'RightButton', Qt.MouseButton.MiddleButton: 'MidButton'}
        return buttons.get(QApplication.mouseButtons(), 'Unknown')

    def get_page_browser(self, qurl, name_tab, icons):
        global browser
        if self.globalpageagent==1:
            self.profile.setHttpUserAgent(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
                " Chrome/108.0.5359.220 Safari/537.36")
        else:
            self.profile.setHttpUserAgent(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
                " QtWebEngine/6.5.0 Chrome/108.0.5359.220 Safari/537.36")
        verticalLayout_2 = QVBoxLayout(self)
        verticalLayout_2.setObjectName(u"verticalLayout_2")
        widget = QWidget(self)
        widget.setObjectName(u"widget")
        verticalLayout = QVBoxLayout(widget)
        verticalLayout.setSpacing(5)
        verticalLayout.setObjectName(u"verticalLayout")
        verticalLayout.setContentsMargins(0, 0, 0, 0)

        widget_2 = QWidget(widget)
        widget_2.setObjectName(u"widget_2")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(widget_2.sizePolicy().hasHeightForWidth())
        widget_2.setSizePolicy(sizePolicy)
        widget.setSizePolicy(sizePolicy)
        verticalLayout_3 = QVBoxLayout(widget_2)
        verticalLayout_3.setSpacing(0)
        verticalLayout_3.setObjectName(u"verticalLayout_3")
        verticalLayout_3.setContentsMargins(0, 0, 0, 0)

        browser = HtmlView(widget_2)
        browser.page().profile().downloadRequested.connect(self.downloads.download_request)
        verticalLayout_3.addWidget(browser)
        verticalLayout.addWidget(widget_2)
        verticalLayout_2.addWidget(widget)

        verticalLayout.addWidget(widget_2)

        verticalLayout_2.addWidget(widget)
        browser.urlChanged.connect(lambda event: self.update_url_bar(event, browser, name_tab))
        browser.loadFinished.connect(lambda event: self.update_url_bar( event, browser, name_tab))

        page = WebEnginePage(self.profile, browser)
        page.fullScreenRequested.connect(lambda request:request.accept())
        page.triggerAction(QWebEnginePage.InspectElement)
        page.iconChanged.connect(lambda event: self.set_icon_page(event, icons))
        #page.featurePermissionRequested.connect(lambda: self.permissionRequested)
        browser.setPage(page)
        browser.setUrl(qurl)
        #self.start_script(browser)
        self.globalpageagent = 0
        return widget, browser

    #def permissionRequested(self, frame, feature):
        #QWebEnginePage.setFeaturePermission(frame, feature, QWebEnginePage.PermissionPolicy.PermissionGrantedByUser)
    def set_icon_page(self, event, icons):
        # Get the web page icon as a QIcon
        icon_qt = QIcon(event)
        if icon_qt.isNull():
            icon_qt = QIcon("images/load.png")

        # Set the web page icon to the label
        icons.setPixmap(icon_qt.pixmap(60, 60))

    def add_new_tab(self, qurl=None, label=None):
        self.globalpageagent = 0
        self.profile.setHttpUserAgent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
                                      " QtWebEngine/6.5.0 Chrome/108.0.5359.220 Safari/537.36")
        if qurl is None:
            qurl = QUrl('')
        else:
            qurl = QUrl(qurl)

        if label is None:
            label = "Новая вкладка"

        widget = QWidget(self.tabs)
        widget.adjustSize()
        sizePolicy1 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setWidthForHeight(widget.sizePolicy().hasWidthForHeight())
        widget.setSizePolicy(sizePolicy1)

        widget.setStyleSheet("* {"
                             "margin: 0px;"
                             "padding: 0px;"
                             "border: 0px;"
                             "}")
        widget.setObjectName(u"widget")
        horizontalLayout = QHBoxLayout(widget)
        horizontalLayout.setSpacing(9)
        horizontalLayout.setObjectName(u"horizontalLayout")

        toolButton = QPushButton(widget)
        toolButton.setText("")

        name_tab = QLabel(widget)
        name_tab.setText(str(label))
        name_tab.adjustSize()

        size = QSize(20, 20)

        icon = QIcon("images/load.png")
        icons = QLabel(widget)
        icons.setPixmap(icon.pixmap(90, 90))
        icons.setFixedSize(size)
        icons.setScaledContents(True)
        icons.setGeometry(1, 1, 10, 10)

        horizontalLayout.addWidget(icons, 0, Qt.AlignmentFlag.AlignLeft)
        horizontalLayout.addWidget(name_tab, 1, Qt.AlignmentFlag.AlignLeft)
        browser, wid = self.get_page_browser(qurl, name_tab, icons)
        i = self.tabs.addTab(browser, "")
        self.tabs.update()
        self.tabs.setCurrentIndex(i)


        self.tabs.tabBar().setTabButton(i, QTabBar.ButtonPosition.LeftSide, widget)
        if self.tabs.count() > 5:self.tabs.setTabsClosable(True)
        elif self.tabs.count() < 6:self.tabs.setTabsClosable(False)

######################WHATSAPP##################################

    def Whatsapp(self, qurl=None, label=None):
        self.globalpageagent = 1
        self.profile.setHttpUserAgent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
                                      " Chrome/108.0.5359.220 Safari/537.36")

        if qurl is None:
            qurl = QUrl('')
        else:
            qurl = QUrl(qurl)

        if label is None:
            label = "Новая вкладка"

        widget = QWidget(self.tabs)
        widget.adjustSize()
        sizePolicy1 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setWidthForHeight(widget.sizePolicy().hasWidthForHeight())
        widget.setSizePolicy(sizePolicy1)

        widget.setStyleSheet("* {"
                             "margin: 0px;"
                             "padding: 0px;"
                             "border: 0px;"
                             "}")
        widget.setObjectName(u"widget")
        horizontalLayout = QHBoxLayout(widget)
        horizontalLayout.setSpacing(9)
        horizontalLayout.setObjectName(u"horizontalLayout")

        toolButton = QPushButton(widget)
        toolButton.setText("")

        name_tab = QLabel(widget)
        name_tab.setText(str(label))
        name_tab.adjustSize()

        size = QSize(20, 20)

        icon = QIcon("images/load.png")
        icons = QLabel(widget)
        icons.setPixmap(icon.pixmap(90, 90))
        icons.setFixedSize(size)
        icons.setScaledContents(True)
        icons.setGeometry(1, 1, 10, 10)

        horizontalLayout.addWidget(icons, 0, Qt.AlignmentFlag.AlignLeft)
        horizontalLayout.addWidget(name_tab, 1, Qt.AlignmentFlag.AlignLeft)
        browser, wid = self.get_page_browser(qurl, name_tab, icons)
        i = self.tabs.addTab(browser, "")
        self.tabs.update()
        self.tabs.setCurrentIndex(i)


        self.tabs.tabBar().setTabButton(i, QTabBar.ButtonPosition.LeftSide, widget)
        if self.tabs.count() > 5:
            self.tabs.setTabsClosable(True)
        elif self.tabs.count() < 6:
            self.tabs.setTabsClosable(False)
#############################ГРАНИЦА WHATSAPP#################################################
    def close_current_tab(self, index):
        if self.tabs.count() == 1:
            self.close()
        else:
            self.tabs.removeTab(index)
        if self.tabs.count() < 2:self.tabs.setTabsClosable(False)

    @staticmethod
    def navigate_to_url(url_bar, brow):
        url = url_bar.text()
        brow.load(QUrl(url))

    def update_url_bar(self, q, brow, name_tab):
        title = brow.title()

        if not title:
            title = "Новая вкладка"

        if title == "about:blank":
            title = "Новая вкладка"

        if title.startswith("http"):
            title = "Загрузка..."

        try:
            name_tab.setText(title)
        except:
            pass



if __name__ == '__main__':
    try:
        app = QApplication(["",'--no-sandbox','--proprietary-codecs'])
        app.setStyleSheet(style_application)
        app.setApplicationName(" Web v1.3")
        app.setWindowIcon(QPixmap(""))
        browser = WebBrowser()
        browser.show()
        sys.exit(app.exec())
    except:
        print(ConnectionAbortedError)
    finally:
        call("DeleteCache.bat")

