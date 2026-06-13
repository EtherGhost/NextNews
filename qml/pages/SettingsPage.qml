import QtQuick 2.7
import QtQuick.Layouts 1.3
import Lomiri.Components 1.3

Page {
    id: page

    property var newsController

    header: PageHeader {
        id: header
        title: i18n.tr("Settings")
    }

    Flickable {
        anchors {
            top: header.bottom
            left: parent.left
            right: parent.right
            bottom: parent.bottom
        }
        contentWidth: width
        contentHeight: contentColumn.height + units.gu(4)
        clip: true

        ColumnLayout {
            id: contentColumn
            width: parent.width - units.gu(4)
            x: units.gu(2)
            spacing: units.gu(1.4)

            Label {
                Layout.fillWidth: true
                text: i18n.tr("Sync")
                fontSize: "large"
                font.bold: true
            }

            CheckBox {
                text: i18n.tr("Sync while app is active")
                checked: newsController.autoSyncEnabled
                onCheckedChanged: newsController.setAutoSyncEnabled(checked)
            }

            CheckBox {
                text: i18n.tr("Sync on startup")
                checked: newsController.syncOnStartup
                onCheckedChanged: newsController.setSyncOnStartup(checked)
            }

            RowLayout {
                Layout.fillWidth: true
                spacing: units.gu(1)

                Label {
                    Layout.fillWidth: true
                    text: i18n.tr("Active sync interval")
                }

                Button {
                    text: "5m"
                    color: newsController.syncIntervalMinutes === 5 ? "#2c7fb8" : theme.palette.normal.background
                    onClicked: newsController.setSyncIntervalMinutes(5)
                }

                Button {
                    text: "15m"
                    color: newsController.syncIntervalMinutes === 15 ? "#2c7fb8" : theme.palette.normal.background
                    onClicked: newsController.setSyncIntervalMinutes(15)
                }

                Button {
                    text: "30m"
                    color: newsController.syncIntervalMinutes === 30 ? "#2c7fb8" : theme.palette.normal.background
                    onClicked: newsController.setSyncIntervalMinutes(30)
                }
            }

            Label {
                Layout.fillWidth: true
                text: i18n.tr("Ubuntu Touch does not provide Android-style background services for this app. Sync runs while NextNews is open or activated.")
                wrapMode: Text.WordWrap
                opacity: 0.68
            }

            Label {
                Layout.fillWidth: true
                text: i18n.tr("List")
                fontSize: "large"
                font.bold: true
            }

            CheckBox {
                text: i18n.tr("Oldest articles first")
                checked: newsController.sortOldestFirst
                onCheckedChanged: newsController.setSortOldestFirst(checked)
            }

            CheckBox {
                text: i18n.tr("Open articles in browser directly")
                checked: newsController.openInBrowserDirectly
                onCheckedChanged: newsController.setOpenInBrowserDirectly(checked)
            }

            Label {
                Layout.fillWidth: true
                text: i18n.tr("Search")
                fontSize: "large"
                font.bold: true
            }

            RowLayout {
                Layout.fillWidth: true
                spacing: units.gu(1)

                Button {
                    Layout.fillWidth: true
                    text: i18n.tr("Title")
                    color: newsController.searchIn === "title" ? "#2c7fb8" : theme.palette.normal.background
                    onClicked: newsController.setSearchIn("title")
                }

                Button {
                    Layout.fillWidth: true
                    text: i18n.tr("Content")
                    color: newsController.searchIn === "body" ? "#2c7fb8" : theme.palette.normal.background
                    onClicked: newsController.setSearchIn("body")
                }

                Button {
                    Layout.fillWidth: true
                    text: i18n.tr("Both")
                    color: newsController.searchIn === "both" ? "#2c7fb8" : theme.palette.normal.background
                    onClicked: newsController.setSearchIn("both")
                }
            }
        }
    }
}
