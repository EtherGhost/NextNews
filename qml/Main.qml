import QtQuick 2.7
import QtQuick.Layouts 1.3
import Lomiri.Components 1.3
import "backend"

MainView {
    id: root
    objectName: "mainView"
    applicationName: "nextnews.cloudsite"
    automaticOrientation: true

    width: desktopLarge ? units.gu(90) : units.gu(85)
    height: desktopLarge ? units.gu(120) : units.gu(80)

    Component.onCompleted: {
        if (desktopDarkMode) {
            theme.name = "Ubuntu.Components.Themes.SuruDark"
        }
    }

    NewsController {
        id: appNewsController
    }

    Connections {
        target: Qt.application

        onActiveChanged: {
            if (Qt.application.active) {
                appNewsController.handleApplicationActivated()
            } else {
                appNewsController.handleApplicationDeactivated()
            }
        }
    }

    PageStack {
        id: pageStack
        anchors.fill: parent

        Component.onCompleted: push(Qt.resolvedUrl("pages/NewsListPage.qml"), {
            "newsController": appNewsController
        })
    }
}
