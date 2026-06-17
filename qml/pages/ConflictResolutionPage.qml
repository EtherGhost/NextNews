import QtQuick 2.7
import QtQuick.Layouts 1.3
import Lomiri.Components 1.3

Page {
    id: page

    property var newsController
    property var pendingRows: newsController ? newsController.pendingChangeRows() : []

    header: PageHeader {
        title: i18n.tr("Sync conflict")
    }

    Flickable {
        anchors {
            top: parent.top
            topMargin: page.header.height
            left: parent.left
            right: parent.right
            bottom: actionRow.top
            margins: units.gu(2)
        }
        contentWidth: width
        contentHeight: contentColumn.height + units.gu(2)
        clip: true

        ColumnLayout {
            id: contentColumn
            width: parent.width
            spacing: units.gu(1.4)

            Label {
                Layout.fillWidth: true
                text: i18n.tr("NextNews has local article or subscription changes that are not confirmed by the server yet.")
                wrapMode: Text.WordWrap
                font.bold: true
            }

            Label {
                Layout.fillWidth: true
                text: i18n.tr("Keep them to retry later, retry now, or discard the local pending changes and refresh from the server.")
                wrapMode: Text.WordWrap
                opacity: 0.78
            }

            Repeater {
                model: page.pendingRows

                delegate: Rectangle {
                    Layout.fillWidth: true
                    height: pendingItemColumn.height + units.gu(1.6)
                    radius: units.gu(0.6)
                    color: theme.palette.normal.foreground
                    border.width: 1
                    border.color: "#7a7a7a"

                    Column {
                        id: pendingItemColumn
                        anchors {
                            left: parent.left
                            right: parent.right
                            verticalCenter: parent.verticalCenter
                            margins: units.gu(1)
                        }
                        spacing: units.gu(0.35)

                        Label {
                            width: parent.width
                            text: modelData.kind
                            color: "#c65d00"
                            font.bold: true
                            elide: Text.ElideRight
                        }

                        Label {
                            width: parent.width
                            text: modelData.title
                            font.bold: true
                            wrapMode: Text.WordWrap
                            maximumLineCount: 2
                            elide: Text.ElideRight
                        }

                        Label {
                            width: parent.width
                            text: modelData.detail
                            wrapMode: Text.WordWrap
                            opacity: 0.72
                        }
                    }
                }
            }

            Label {
                Layout.fillWidth: true
                visible: page.pendingRows.length === 0
                text: i18n.tr("There are no pending local changes.")
                horizontalAlignment: Text.AlignHCenter
                wrapMode: Text.WordWrap
                opacity: 0.72
            }
        }
    }

    RowLayout {
        id: actionRow
        anchors {
            left: parent.left
            right: parent.right
            bottom: parent.bottom
            margins: units.gu(2)
        }
        spacing: units.gu(1)

        Button {
            Layout.fillWidth: true
            text: i18n.tr("Keep local")
            onClicked: pageStack.pop()
        }

        Button {
            Layout.fillWidth: true
            text: i18n.tr("Retry now")
            enabled: page.pendingRows.length > 0
            onClicked: {
                if (newsController.retryPendingChanges()) {
                    pageStack.pop()
                }
            }
        }

        Button {
            Layout.fillWidth: true
            text: i18n.tr("Discard")
            color: "#c7162b"
            enabled: page.pendingRows.length > 0
            onClicked: {
                newsController.discardPendingChangesAndRefresh()
                pageStack.pop()
            }
        }
    }
}
