import json
import pathlib
import re
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


def read_text(path):
    return (ROOT / path).read_text(encoding="utf-8")


class ProjectIdentityTests(unittest.TestCase):
    def test_manifest_identity_and_hooks_are_nextnews(self):
        manifest = json.loads(read_text("manifest.json.in"))

        self.assertEqual(manifest["name"], "nextnews.cloudsite")
        self.assertEqual(manifest["title"], "NextNews")
        self.assertIn("nextnews", manifest["hooks"])
        self.assertEqual(manifest["hooks"]["nextnews"]["accounts"], "nextnews.accounts")
        self.assertEqual(manifest["hooks"]["nextnews"]["apparmor"], "nextnews.apparmor")
        self.assertEqual(manifest["hooks"]["nextnews"]["desktop"], "nextnews.desktop")

    def test_online_accounts_service_ids_are_current(self):
        page = read_text("qml/pages/AccountSelectionPage.qml")

        self.assertIn("nextnews.cloudsite_nextnews", page)
        self.assertIn("nextnews.cloudsite_nextnews_nextcloud", page)
        self.assertIn("nextnews.cloudsite_nextnews_owncloud", page)
        self.assertIn("findPreferredAppService", page)
        self.assertIn("selectedService.updateServiceEnabled(true)", page)
        self.assertNotIn("accountSetup.exec()", page)
        self.assertNotIn("nextnotes", page.lower())

    def test_apparmor_is_minimal(self):
        apparmor = json.loads(read_text("nextnews.apparmor"))

        self.assertEqual(sorted(apparmor["policy_groups"]), ["accounts", "networking"])
        self.assertNotIn("unconfined", json.dumps(apparmor).lower())

    def test_qml_resources_include_news_runtime_files(self):
        qrc = read_text("qml/qml.qrc")

        for filename in [
            "pages/NewsListPage.qml",
            "pages/ArticleDetailPage.qml",
            "pages/AboutPage.qml",
            "backend/NewsCache.qml",
            "backend/NewsApiClient.qml",
            "backend/NewsApiCore.js",
            "backend/NewsController.qml",
            "backend/SyncPlanner.js",
        ]:
            self.assertIn(filename, qrc)

    def test_desktop_test_auth_is_opt_in_and_env_backed(self):
        main = read_text("main.cpp")
        session = read_text("qml/backend/AccountSessionAdapter.qml")
        controller = read_text("qml/backend/NewsController.qml")
        clickable = read_text("clickable.yaml")
        desktop_script = read_text("scripts/desktop-test.sh")

        for snippet in [
            "NEXTNEWS_DESKTOP_TEST_AUTH",
            "NEXTNEWS_TEST_SERVER",
            "NEXTNEWS_TEST_USERNAME",
            "NEXTNEWS_TEST_APP_PASSWORD",
            "desktopTestAuthEnabled",
            "readDesktopTestEnvFile",
            ".clickable/nextnews-desktop-env.local",
        ]:
            self.assertIn(snippet, main)

        for snippet in [
            "envTestAuthEnabled",
            "desktop-test-env",
            "auth using desktop test environment credentials",
        ]:
            self.assertIn(snippet, session)

        self.assertIn("accountSession.envTestAuthEnabled", controller)
        self.assertIn("accountSettings.serverUrl = serverUrl", controller)
        self.assertIn("desktop-test: bash scripts/desktop-test.sh", clickable)
        self.assertIn("env_vars:", desktop_script)
        self.assertIn("NEXTNEWS_DESKTOP_TEST_AUTH", desktop_script)
        self.assertIn("mktemp .clickable/nextnews-desktop-test", desktop_script)
        self.assertIn("nextnews-desktop-env.local", desktop_script)


class NewsApiContractTests(unittest.TestCase):
    def test_news_api_endpoints_are_v1_2(self):
        core = read_text("qml/backend/NewsApiCore.js")
        client = read_text("qml/backend/NewsApiClient.qml")

        for endpoint in [
            "/index.php/apps/news/api/v1-2",
            "/folders",
            "/feeds",
            "/move",
            "/items?",
            "/items/read/multiple",
            "/items/unread/multiple",
            "/items/star/multiple",
            "/items/unstar/multiple",
        ]:
            self.assertIn(endpoint, core)

        self.assertIn('requestJson("GET"', client)
        self.assertIn('requestJson("PUT"', client)
        self.assertIn('requestJson("POST"', client)
        self.assertIn('requestJson("DELETE"', client)
        self.assertIn('requestForm("POST"', client)
        self.assertIn("request.open(method, url)", client)
        self.assertIn('"Authorization", "Basic " + Qt.btoa(userName + ":" + secret)', client)
        self.assertNotRegex(client, r"console\.log\([^\\n]*(secret|password|Secret|Password)")

    def test_feed_creation_matches_nextcloud_news_contract(self):
        core = read_text("qml/backend/NewsApiCore.js")
        client = read_text("qml/backend/NewsApiClient.qml")
        controller = read_text("qml/backend/NewsController.qml")
        page = read_text("qml/pages/NewsListPage.qml")

        self.assertIn("createFeedPayload", core)
        self.assertIn('"url"', core)
        self.assertIn('"folderId"', core)
        self.assertIn("function createFeed", client)
        self.assertIn("Content-Type\", \"application/x-www-form-urlencoded", client)
        self.assertIn("api.createFeed", controller)
        self.assertIn("onFeedCreated", controller)
        self.assertIn("Add feed", page)
        self.assertIn("addFeedPanelOpen", page)
        self.assertIn("openAddFeedPanel", page)
        self.assertIn('"openExternal": false', core)

    def test_feed_and_folder_management_contract(self):
        core = read_text("qml/backend/NewsApiCore.js")
        client = read_text("qml/backend/NewsApiClient.qml")
        controller = read_text("qml/backend/NewsController.qml")
        page = read_text("qml/pages/NewsListPage.qml")

        for snippet in [
            "createFolderPayload",
            "moveFeedPayload",
            "moveFeedUrl",
            "renameFeedUrl",
            "renameFeedPayload",
            "renameFolderPayload",
            "feedUrl",
            "folderUrl",
        ]:
            self.assertIn(snippet, core)
        for snippet in [
            "function createFolder",
            "function moveFeed",
            "function renameFeed",
            "function renameFolder",
            "function deleteFeed",
            "function deleteFolder",
        ]:
            self.assertIn(snippet, client)
            self.assertIn(snippet, controller)
        for snippet in ["folderCreated", "folderRenamed", "folderDeleted", "feedRenamed", "feedMoved", "feedDeleted"]:
            self.assertIn(snippet, client)
        self.assertIn("folderCreated(result.folders)", client)
        self.assertIn("folderDeleted(Number(folderId || 0))", client)
        for snippet in ["onFolderCreated", "onFolderDeleted", "onFeedMoved", "onFeedDeleted"]:
            self.assertIn(snippet, controller)
        self.assertIn("cache.saveFolders(folders)", controller)
        self.assertIn("rebuildFolderFeedModels", controller)
        self.assertIn("foldersModel.append", controller)
        self.assertIn("feedsModel.append", controller)
        self.assertIn("deleteNextFeedInFolder", controller)
        for snippet in [
            "feedOptionsDialog",
            "folderOptionsDialog",
            "renameFeedDialog",
            "renameFolderDialog",
            "deleteFeedConfirmDialog",
            "deleteFolderConfirmDialog",
            "New folder",
            "Move to folder",
            "Rename feed",
            "Rename folder",
            "Delete feed",
            "Delete folder",
        ]:
            self.assertIn(snippet, page)

    def test_star_payload_preserves_feed_id_and_guid_hash(self):
        core = read_text("qml/backend/NewsApiCore.js")

        self.assertIn('"feedId"', core)
        self.assertIn('"guidHash"', core)
        self.assertIn("starPayload", core)


class CacheAndSyncContractTests(unittest.TestCase):
    def test_cache_schema_tracks_folders_feeds_items_and_pending_state(self):
        cache = read_text("qml/backend/NewsCache.qml")

        for table in [
            "CREATE TABLE IF NOT EXISTS folders",
            "CREATE TABLE IF NOT EXISTS feeds",
            "CREATE TABLE IF NOT EXISTS items",
            "pending_state IS NULL OR pending_state = ''",
            "AND feed_id NOT IN",
            "function removeFeed",
            "function removeFolder",
            "pending_management",
            "function queueManagementOperation",
            "function loadPendingManagementOperations",
            "function removePendingManagementOperation",
            "existingOpenExternal",
            "pending_state",
            "guid_hash",
            "feed_id",
            "pub_date",
            "starred",
            "unread",
        ]:
            self.assertIn(table, cache)

    def test_controller_uses_cached_first_and_uploads_pending_before_pull(self):
        controller = read_text("qml/backend/NewsController.qml")

        self.assertIn("loadCached()", controller)
        self.assertIn("syncPendingThenPull", controller)
        self.assertIn("processNextManagementOperation", controller)
        self.assertIn("localStateUploadOnly", controller)
        self.assertIn("localStateUploadTimer", controller)
        self.assertIn("scheduleLocalStateUpload", controller)
        self.assertIn("clearPendingInModels", controller)
        self.assertIn("updateLocalReadStateInModels", controller)
        self.assertIn("updateLocalStarStateInModels", controller)
        self.assertIn("queueCurrentManagementOperation", controller)
        self.assertIn("processNextPending", controller)
        self.assertIn("api.fetchFolders", controller)
        self.assertIn("api.fetchFeeds", controller)
        self.assertIn("api.fetchItems", controller)
        self.assertIn("handleApplicationActivated", controller)
        self.assertIn("runtimeUserName", controller)
        self.assertIn("runtimeSecret", controller)

    def test_sync_planner_classifies_local_state(self):
        planner = read_text("qml/backend/SyncPlanner.js")

        self.assertIn('item.pendingState === "state"', planner)
        self.assertIn('item.pendingState === "star"', planner)


class UiContractTests(unittest.TestCase):
    def test_main_owns_one_shared_news_controller(self):
        main = read_text("qml/Main.qml")
        pages = read_text("qml/pages/NewsListPage.qml") + read_text("qml/pages/ArticleDetailPage.qml")

        self.assertEqual(main.count("NewsController {"), 1)
        self.assertIn("handleApplicationActivated", main)
        self.assertNotIn("NewsController {", pages)

    def test_news_list_has_android_inspired_affordances(self):
        page = read_text("qml/pages/NewsListPage.qml")
        controller = read_text("qml/backend/NewsController.qml")

        for snippet in [
            "\\u2630",
            "Search articles",
            "Refresh",
            "section.property: \"sectionKey\"",
            "displaySectionLabel",
            "markVisibleViewportArticlesRead",
            "section.property: \"groupLabel\"",
            "New folder name",
            "pendingAddFeedFolderName",
            "pendingFolderSelectTimer",
            "selectPendingAddFeedFolder",
            "addFeedCommitTimer",
            "addFeedCreateFolderCommitTimer",
            "Qt.inputMethod.commit()",
            "oskOverlap",
            "Clear feed URL",
            "Waiting for folder",
            "section === i18n.tr(\"Folders\")",
            "section === i18n.tr(\"Feeds\")",
            "userScrolledArticleList",
            "markAllFab",
            "markAllTarget",
            "Mark read",
            "Mark unread",
            "cardContent.x > 0",
            "navigationRowSelected",
            "color: page.navigationRowSelected(model.type, model.id) ? \"white\" : theme.palette.normal.backgroundText",
            "rightMargin: model.type === \"feed\" || model.type === \"folder\" ? units.gu(5) : 0",
            "toggleStar",
            "toggleRead",
            "markVisibleRead",
            "\\u2605",
            "\\u2606",
            "pullRefreshThreshold",
            "ArticleDetailPage.qml",
            "AboutPage.qml",
            "SettingsPage.qml",
            "OpacityMask",
            "accountAvatarSource",
            "Rename feed",
            "Rename folder",
            "Open in browser",
        ]:
            self.assertIn(snippet, page)
        for snippet in ["All articles", "Unread", "Starred", "Folders", "Feeds", "Today", "Yesterday", "emitRequestedFolderIfAvailable(folders)", "setAutoSyncEnabled", "setSortOldestFirst", "setSearchIn", "leftId", "rightId", "sectionKeyForTimestamp"]:
            self.assertIn(snippet, controller)
        for snippet in ["folderCreateRunning", "feedCreateRunning"]:
            self.assertIn(snippet, controller)
        self.assertNotIn("enabled: !newsController.folderCreateRunning && addFeedPanelFolderNameField.text.trim().length > 0", page)

    def test_account_page_has_editable_server_address_without_manual_login(self):
        page = read_text("qml/pages/AccountSelectionPage.qml")

        self.assertIn("Server address", page)
        self.assertIn("serverUrlField", page)
        self.assertIn("serverUrlCommitTimer", page)
        self.assertIn("commitServerUrlInput", page)
        self.assertIn("The account still comes from Ubuntu Touch Online Accounts", page)
        self.assertNotIn("app password", page.lower())

    def test_settings_page_controls_sync_search_and_reading_options(self):
        page = read_text("qml/pages/SettingsPage.qml")
        qrc = read_text("qml/qml.qrc")
        controller = read_text("qml/backend/NewsController.qml")

        self.assertIn("pages/SettingsPage.qml", qrc)
        for snippet in [
            "Sync while app is active",
            "Sync on startup",
            "Active sync interval",
            "Oldest articles first",
            "Open articles in browser directly",
            "Title",
            "Content",
            "Both",
        ]:
            self.assertIn(snippet, page)
        self.assertNotIn("Mark articles read while scrolling", page)
        for snippet in [
            "autoSyncEnabled",
            "syncIntervalMinutes",
            "sortOldestFirst",
            "searchIn",
            "openInBrowserDirectly",
            "markReadWhileScrolling",
        ]:
            self.assertIn(snippet, controller)
        self.assertIn("property bool markReadWhileScrolling: false", controller)

    def test_account_page_and_controller_match_avatar_contract(self):
        account_page = read_text("qml/pages/AccountSelectionPage.qml")
        controller = read_text("qml/backend/NewsController.qml")

        self.assertNotIn("Server from Ubuntu Touch account", account_page)
        self.assertIn("avatarUrl(accountSettings.serverUrl, userName)", account_page)
        self.assertIn("property string avatarUrl", account_page)
        self.assertIn("/index.php/avatar/", account_page)
        self.assertIn("accountSettings.avatarUrl", controller)
        self.assertIn("function avatarUrl", controller)

    def test_article_detail_has_read_and_star_actions(self):
        page = read_text("qml/pages/ArticleDetailPage.qml")

        for snippet in [
            "Mark read",
            "Mark unread",
            "Star",
            "Unstar",
            "Open original link",
            "Share by email",
            "mailto:",
            "stripHtml",
        ]:
            self.assertIn(snippet, page)

    def test_about_page_records_version_license_and_disclaimer(self):
        page = read_text("qml/pages/AboutPage.qml")
        manifest = json.loads(read_text("manifest.json.in"))
        changelog = read_text("CHANGELOG.md")

        for snippet in [
            "0.1.1",
            "Version %1",
            "MIT License",
            "Etherghost",
            "not affiliated",
            "qrc:/assets/logo.svg",
        ]:
            self.assertIn(snippet, page)
        self.assertEqual(manifest["version"], "0.1.1")
        self.assertIn("## 0.1.1", changelog)
        self.assertIn("## 0.1.0", changelog)


class DocumentationTests(unittest.TestCase):
    def test_docs_record_template_auth_api_and_status(self):
        readme = read_text("README.md")
        license_text = read_text("LICENSE")

        self.assertIn("NextNotes as its technical implementation template", readme)
        self.assertIn("Ubuntu Touch Online Accounts only", readme)
        self.assertIn("/index.php/apps/news/api/v1-2/", readme)
        self.assertIn("MIT License", readme)
        self.assertIn("MIT License", license_text)

    def test_no_accidental_nextnotes_leftovers_in_runtime_files(self):
        runtime_files = [
            "manifest.json.in",
            "CMakeLists.txt",
            "main.cpp",
            "nextnews.accounts",
            "nextnews.apparmor",
            "nextnews.desktop.in",
            "qml/Main.qml",
            "qml/backend/NewsApiClient.qml",
            "qml/backend/NewsCache.qml",
            "qml/backend/NewsController.qml",
            "qml/pages/NewsListPage.qml",
            "qml/pages/ArticleDetailPage.qml",
        ]
        for path in runtime_files:
            self.assertNotIn("nextnotes", read_text(path).lower(), path)


if __name__ == "__main__":
    unittest.main(verbosity=2)
