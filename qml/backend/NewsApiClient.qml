import QtQuick 2.7
import "NewsApiCore.js" as NewsApiCore

Item {
    id: client

    property int requestGeneration: 0

    signal foldersLoaded(var folders, int generation)
    signal folderCreated(var folders, int generation)
    signal folderRenamed(int folderId, string name, int generation)
    signal folderDeleted(int folderId, int generation)
    signal feedsLoaded(var feeds, int generation)
    signal feedCreated(int generation)
    signal feedRenamed(int feedId, string title, int generation)
    signal feedMoved(int generation)
    signal feedDeleted(int feedId, int generation)
    signal itemsLoaded(var items, int generation)
    signal itemStateUploaded(int itemId, bool unread, bool starred, int generation)
    signal itemStatesUploaded(var itemIds, bool unread, int generation)
    signal failed(string message, int generation)

    function fetchFolders(serverUrl, userName, secret) {
        requestJson("GET", NewsApiCore.foldersUrl(serverUrl), userName, secret, null, function(responseText, generation) {
            var result = NewsApiCore.parseFolders(responseText)
            if (!result.ok) {
                console.log("NextNews NewsApi parse folders error=" + result.error)
                failed(i18n.tr("Could not parse folders from Nextcloud News."), generation)
                return
            }
            console.log("NextNews NewsApi GET /folders success count=" + result.folders.length)
            foldersLoaded(result.folders, generation)
        }, "GET /folders")
    }

    function createFolder(serverUrl, userName, secret, name) {
        var payload = NewsApiCore.createFolderPayload(name)
        requestJson("POST", NewsApiCore.foldersUrl(serverUrl), userName, secret, payload, function(responseText, generation) {
            var result = NewsApiCore.parseFolders(responseText)
            if (!result.ok) {
                console.log("NextNews NewsApi parse created folder response error=" + result.error)
                failed(i18n.tr("Folder was created, but NextNews could not read the updated folder list. Refresh and try again."), generation)
                return
            }
            console.log("NextNews NewsApi POST /folders success count=" + result.folders.length)
            folderCreated(result.folders, generation)
        }, "POST /folders")
    }

    function deleteFolder(serverUrl, userName, secret, folderId) {
        requestJson("DELETE", NewsApiCore.folderUrl(serverUrl, folderId), userName, secret, null, function(responseText, generation) {
            console.log("NextNews NewsApi DELETE /folders/{id} success folderId=" + folderId)
            folderDeleted(Number(folderId || 0), generation)
        }, "DELETE /folders/{id}")
    }

    function renameFolder(serverUrl, userName, secret, folderId, name) {
        var payload = NewsApiCore.renameFolderPayload(name)
        requestJson("PUT", NewsApiCore.folderUrl(serverUrl, folderId), userName, secret, payload, function(responseText, generation) {
            console.log("NextNews NewsApi PUT /folders/{id} success folderId=" + folderId)
            folderRenamed(Number(folderId || 0), payload.name, generation)
        }, "PUT /folders/{id}")
    }

    function fetchFeeds(serverUrl, userName, secret) {
        requestJson("GET", NewsApiCore.feedsUrl(serverUrl), userName, secret, null, function(responseText, generation) {
            var result = NewsApiCore.parseFeeds(responseText)
            if (!result.ok) {
                console.log("NextNews NewsApi parse feeds error=" + result.error)
                failed(i18n.tr("Could not parse feeds from Nextcloud News."), generation)
                return
            }
            console.log("NextNews NewsApi GET /feeds success count=" + result.feeds.length)
            feedsLoaded(result.feeds, generation)
        }, "GET /feeds")
    }

    function createFeed(serverUrl, userName, secret, feedUrl, folderId) {
        var payload = NewsApiCore.createFeedPayload(feedUrl, folderId)
        requestForm("POST", NewsApiCore.feedsUrl(serverUrl), userName, secret, payload, function(responseText, generation) {
            console.log("NextNews NewsApi POST /feeds success folderId=" + payload.folderId)
            feedCreated(generation)
        }, "POST /feeds")
    }

    function moveFeed(serverUrl, userName, secret, feedId, folderId) {
        var payload = NewsApiCore.moveFeedPayload(folderId)
        requestJson("PUT", NewsApiCore.moveFeedUrl(serverUrl, feedId), userName, secret, payload, function(responseText, generation) {
            console.log("NextNews NewsApi PUT /feeds/{id}/move success feedId=" + feedId + " folderId=" + payload.folderId)
            feedMoved(generation)
        }, "PUT /feeds/{id}/move")
    }

    function renameFeed(serverUrl, userName, secret, feedId, title) {
        var payload = NewsApiCore.renameFeedPayload(title)
        requestJson("PUT", NewsApiCore.renameFeedUrl(serverUrl, feedId), userName, secret, payload, function(responseText, generation) {
            console.log("NextNews NewsApi PUT /feeds/{id}/rename success feedId=" + feedId)
            feedRenamed(Number(feedId || 0), payload.feedTitle, generation)
        }, "PUT /feeds/{id}/rename")
    }

    function deleteFeed(serverUrl, userName, secret, feedId) {
        requestJson("DELETE", NewsApiCore.feedUrl(serverUrl, feedId), userName, secret, null, function(responseText, generation) {
            console.log("NextNews NewsApi DELETE /feeds/{id} success feedId=" + feedId)
            feedDeleted(Number(feedId || 0), generation)
        }, "DELETE /feeds/{id}")
    }

    function fetchItems(serverUrl, userName, secret, type, id, getRead) {
        requestJson("GET", NewsApiCore.itemsUrl(serverUrl, type, id, getRead), userName, secret, null, function(responseText, generation) {
            var result = NewsApiCore.parseItems(responseText)
            if (!result.ok) {
                console.log("NextNews NewsApi parse items error=" + result.error)
                failed(i18n.tr("Could not parse articles from Nextcloud News."), generation)
                return
            }
            console.log("NextNews NewsApi GET /items success count=" + result.items.length + " type=" + type + " id=" + id)
            itemsLoaded(result.items, generation)
        }, "GET /items")
    }

    function markItemRead(serverUrl, userName, secret, itemId, read) {
        var payload = NewsApiCore.idsPayload([itemId])
        requestJson("PUT", NewsApiCore.markReadUrl(serverUrl, read), userName, secret, payload, function(responseText, generation) {
            console.log("NextNews NewsApi PUT read-state success itemId=" + itemId + " read=" + read)
            itemStateUploaded(itemId, !read, undefined, generation)
        }, read ? "PUT /items/read/multiple" : "PUT /items/unread/multiple")
    }

    function markItemsRead(serverUrl, userName, secret, itemIds, read) {
        var payload = NewsApiCore.idsPayload(itemIds)
        requestJson("PUT", NewsApiCore.markReadUrl(serverUrl, read), userName, secret, payload, function(responseText, generation) {
            console.log("NextNews NewsApi PUT read-state batch success count=" + payload.items.length + " read=" + read)
            itemStatesUploaded(payload.items, !read, generation)
        }, read ? "PUT /items/read/multiple" : "PUT /items/unread/multiple")
    }

    function starItem(serverUrl, userName, secret, item, starred) {
        var payload = NewsApiCore.starPayload([item])
        requestJson("PUT", NewsApiCore.starUrl(serverUrl, starred), userName, secret, payload, function(responseText, generation) {
            console.log("NextNews NewsApi PUT star-state success itemId=" + item.itemId + " starred=" + starred)
            itemStateUploaded(item.itemId, undefined, starred, generation)
        }, starred ? "PUT /items/star/multiple" : "PUT /items/unstar/multiple")
    }

    function requestJson(method, url, userName, secret, payload, onSuccess, label) {
        var generation = requestGeneration
        var request = new XMLHttpRequest()
        console.log("NextNews NewsApi " + label + " requesting serverUrlConfigured=" + (url.indexOf("http") === 0 ? "true" : "false"))

        request.onreadystatechange = function() {
            if (request.readyState !== XMLHttpRequest.DONE) {
                return
            }
            if (request.status < 200 || request.status >= 300) {
                console.log("NextNews NewsApi " + label + " error status=" + request.status)
                failed(i18n.tr("Nextcloud News request failed with HTTP %1.").arg(request.status), generation)
                return
            }
            onSuccess(request.responseText || "", generation)
        }

        request.open(method, url)
        request.setRequestHeader("Authorization", "Basic " + Qt.btoa(userName + ":" + secret))
        request.setRequestHeader("Accept", "application/json")
        if (payload !== null && payload !== undefined) {
            request.setRequestHeader("Content-Type", "application/json")
            request.send(JSON.stringify(payload))
        } else {
            request.send()
        }
    }

    function requestForm(method, url, userName, secret, payload, onSuccess, label) {
        var generation = requestGeneration
        var request = new XMLHttpRequest()
        console.log("NextNews NewsApi " + label + " requesting serverUrlConfigured=" + (url.indexOf("http") === 0 ? "true" : "false"))

        request.onreadystatechange = function() {
            if (request.readyState !== XMLHttpRequest.DONE) {
                return
            }
            if (request.status < 200 || request.status >= 300) {
                console.log("NextNews NewsApi " + label + " error status=" + request.status)
                failed(feedCreateErrorMessage(request.status, request.responseText || ""), generation)
                return
            }
            onSuccess(request.responseText || "", generation)
        }

        var formValues = []
        for (var key in payload) {
            if (payload.hasOwnProperty(key)) {
                formValues.push(encodeURIComponent(key) + "=" + encodeURIComponent(payload[key]))
            }
        }

        request.open(method, url)
        request.setRequestHeader("Authorization", "Basic " + Qt.btoa(userName + ":" + secret))
        request.setRequestHeader("Accept", "application/json")
        request.setRequestHeader("Content-Type", "application/x-www-form-urlencoded")
        request.send(formValues.join("&"))
    }

    function feedCreateErrorMessage(status, responseText) {
        var message = ""
        try {
            var parsed = JSON.parse(responseText)
            if (parsed && parsed.message) {
                message = String(parsed.message)
            }
        } catch (error) {
            message = ""
        }
        if (message.length > 160) {
            message = message.slice(0, 157) + "..."
        }
        if (message.length > 0) {
            return i18n.tr("Could not add feed: %1").arg(message)
        }
        if (Number(status) === 409) {
            return i18n.tr("That feed already exists.")
        }
        if (Number(status) === 422) {
            return i18n.tr("Nextcloud could not read that feed URL.")
        }
        return i18n.tr("Could not add feed. Nextcloud News returned HTTP %1.").arg(status)
    }
}
