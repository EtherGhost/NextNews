import QtQuick 2.7
import QtQuick.Layouts 1.3
import Lomiri.Components 1.3
import "../backend/NewsApiCore.js" as NewsApiCore

Page {
    id: page

    property int itemId: 0
    property var newsController
    property var article: newsController ? newsController.getItem(itemId) : null

    header: PageHeader {
        id: header
        title: article ? article.title : i18n.tr("Article")

        trailingActionBar.actions: [
            Action {
                iconName: "external-link"
                text: i18n.tr("Open")
                visible: article && article.url.length > 0
                onTriggered: Qt.openUrlExternally(article.url)
            },
            Action {
                iconName: "mail-send"
                text: i18n.tr("Share")
                visible: article && article.url.length > 0
                onTriggered: Qt.openUrlExternally(page.mailtoUrl())
            },
            Action {
                iconName: "starred"
                text: article && article.starred ? i18n.tr("Unstar") : i18n.tr("Star")
                onTriggered: {
                    newsController.toggleStar(page.itemId)
                    page.article = newsController.getItem(page.itemId)
                }
            },
            Action {
                iconName: "ok"
                text: article && article.unread ? i18n.tr("Mark read") : i18n.tr("Mark unread")
                onTriggered: {
                    if (page.article) {
                        newsController.markRead(page.itemId, page.article.unread)
                        page.article = newsController.getItem(page.itemId)
                    }
                }
            }
        ]
    }

    Flickable {
        anchors {
            top: header.bottom
            left: parent.left
            right: parent.right
            bottom: parent.bottom
            margins: units.gu(2)
        }
        contentWidth: width
        contentHeight: contentColumn.height
        clip: true

        Column {
            id: contentColumn
            width: parent.width
            spacing: units.gu(1.4)

            Label {
                width: parent.width
                text: article ? article.title : i18n.tr("Article not cached")
                wrapMode: Text.WordWrap
                fontSize: "x-large"
                font.bold: true
            }

            Label {
                width: parent.width
                visible: article && (article.author.length > 0 || article.pubDate > 0)
                text: article ? [article.author, page.dateText(article.pubDate)].filter(function(v) { return v && v.length > 0 }).join(" - ") : ""
                opacity: 0.65
            }

            Row {
                spacing: units.gu(1)
                visible: article !== null

                Label {
                    text: article && article.unread ? i18n.tr("Unread") : i18n.tr("Read")
                    color: "#2c7fb8"
                }

                Label {
                    visible: article && article.starred
                    text: i18n.tr("Starred")
                    color: "#d9a300"
                }

                Label {
                    visible: article && article.pendingState.length > 0
                    text: i18n.tr("Pending sync")
                    color: "#b37a2a"
                }
            }

            Label {
                width: parent.width
                text: article ? NewsApiCore.stripHtml(article.body) : i18n.tr("Open this article online once to cache it for offline reading.")
                wrapMode: Text.WordWrap
                lineHeight: 1.2
            }

            Button {
                visible: article && article.url.length > 0
                text: i18n.tr("Open original link")
                onClicked: Qt.openUrlExternally(article.url)
            }

            Button {
                visible: article && article.url.length > 0
                text: i18n.tr("Share by email")
                onClicked: Qt.openUrlExternally(page.mailtoUrl())
            }
        }
    }

    Component.onCompleted: {
        if (article && article.unread) {
            newsController.markRead(itemId, true)
            article = newsController.getItem(itemId)
        }
    }

    function dateText(seconds) {
        if (!seconds || seconds <= 0) {
            return ""
        }
        return Qt.formatDateTime(new Date(Number(seconds) * 1000), Qt.DefaultLocaleShortDate)
    }

    function mailtoUrl() {
        if (!article) {
            return "mailto:"
        }
        var subject = encodeURIComponent(article.title || i18n.tr("Article"))
        var body = encodeURIComponent((article.title || "") + "\n" + (article.url || ""))
        return "mailto:?subject=" + subject + "&body=" + body
    }
}
