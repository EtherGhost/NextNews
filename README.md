# NextNews

NextNews is a native Ubuntu Touch client for the official Nextcloud News app.

The project uses NextNotes as its technical implementation template, but NextNews is a separate application focused on feeds and articles. The Android Nextcloud News app is used only as a functional and layout reference.

NextNews is not affiliated with, endorsed by, or sponsored by Nextcloud GmbH or the Nextcloud project. Nextcloud is a trademark of its respective owners.

## Features

Current V1 scaffold:

- Use an existing Nextcloud or ownCloud account from Ubuntu Touch Online Accounts.
- Authorize the app with the same Online Accounts setup flow used by NextNotes.
- Show the selected account avatar from the Nextcloud account when available.
- Use runtime-only Online Accounts credentials.
- Read the server address from the selected Ubuntu Touch account, with an editable server-address field if the system account does not expose the correct host.
- Connect to the Nextcloud News API at `/index.php/apps/news/api/v1-2/`.
- Load folders, feeds, and article items.
- Add feeds to the selected Nextcloud News account.
- Create folders, rename folders, move feeds to folders, rename feeds, and delete feeds.
- Create a folder directly from the Add feed dialog and wait for the server folder id before posting the feed.
- Delete folders; feeds inside the folder are deleted first, matching the Android client behavior.
- Keep folder/feed selector models in sync with the cached/server folder list.
- Show cached articles first, then refresh from the server.
- Group articles by date sections such as Today, Yesterday, and calendar date.
- Read cached articles offline.
- Retry failed feed/folder rename, move, and delete operations on the next successful sync.
- Mark articles read or unread.
- Swipe article rows right to star/unstar and left to toggle read/unread state.
- Star or unstar articles when the API has the required `feedId` and `guidHash`.
- Mark all unread articles in the current view as read with the drag-up floating action button.
- Preserve pending local read/star state when upload fails.
- Refresh while the app is active, with settings for active sync, startup sync, and interval.
- Search cached titles, authors, and cached article text.
- Choose title/content/both search scope.
- Show unread counts in the navigation drawer.
- Separate views, folders, and feeds in the navigation drawer.
- Configure oldest/newest sort order, open articles directly in the browser, and mark articles read while scrolling.
- Configure individual feeds to open directly in the browser.
- Open or share article links from the article detail page.
- Use a local SQLite cache through Qt LocalStorage.
- Show an About page with version, license, copyright, and Nextcloud affiliation disclaimer.

## Not Included

The first version intentionally does not implement:

- In-app username/password/app-password login
- Android-style always-running background service
- Background push notifications
- Full-text web archive download
- Podcast playback
- Image caching
- Native content-hub sharing
- Complex conflict UI
- Rich article rendering

## Authentication

NextNews uses Ubuntu Touch Online Accounts only.

Add a Nextcloud or ownCloud account in Ubuntu Touch System Settings > Accounts, then authorize that account inside NextNews. Credentials are taken from the selected system account. The server address is read from the account when available and can be corrected in the account page if Ubuntu Touch does not expose the correct host. Credentials are requested from Online Accounts at runtime and are not stored by NextNews. After successful runtime authentication, credentials may be kept only in process memory for the current app session.

## Architecture

NextNews is a Clickable QML/C++ Ubuntu Touch application.

Important areas:

- `qml/pages/`: Ubuntu Touch UI pages.
- `qml/backend/AccountSessionAdapter.qml`: Online Accounts runtime authentication.
- `qml/backend/NewsApiClient.qml`: Nextcloud News API requests.
- `qml/backend/NewsApiCore.js`: URL, payload, and JSON parsing helpers.
- `qml/backend/NewsCache.qml`: local SQLite cache.
- `qml/backend/NewsController.qml`: cached-first loading, filtering, sync orchestration, and UI-facing state.
- `qml/backend/SyncPlanner.js`: pending local state upload planning.
- `po/`: gettext translation catalogs.
- `tests/`: local contract and regression tests.
- `tests_live/`: opt-in live Nextcloud News API tests.

The backend boundary is intentionally similar to NextNotes so future improvements can reuse the same testing and synchronization patterns.

## Build

Install Clickable, then build from the repository root:

```bash
~/.local/bin/clickable build --arch amd64
~/.local/bin/clickable build --arch arm64
```

Successful builds produce click packages under:

```text
build/x86_64-linux-gnu/app/
build/aarch64-linux-gnu/app/
```

## Run

Desktop mode:

```bash
~/.local/bin/clickable desktop --arch amd64
```

Larger desktop debug window:

```bash
~/.local/bin/clickable script desktop-large
```

Desktop mode can also use the dedicated live-test account from `.env.test.local`
for faster debugging without Ubuntu Touch Online Accounts:

```bash
cp .env.test.local.example .env.test.local
# edit .env.test.local with a dedicated test account
~/.local/bin/clickable script desktop-test
```

This path is only enabled for desktop debugging when `NEXTNEWS_DESKTOP_TEST_AUTH=1`
is set by the script. Ubuntu Touch builds continue to use Online Accounts only.

Install on a connected Ubuntu Touch device:

```bash
~/.local/bin/clickable install --arch arm64
```

## Test

Run the local regression suite:

```bash
~/.local/bin/clickable script test
```

Optional live Nextcloud News API tests are available for a dedicated test account. They create, rename, move, and delete test folders/feeds with a `NextNewsLiveTest-` prefix and should never be run against a personal account:

```bash
cp .env.test.local.example .env.test.local
# edit .env.test.local with a dedicated test account
~/.local/bin/clickable script test-live
```

Never use a personal account for live tests. `.env.test.local` is ignored by git. The live suite also tests read/unread and star/unstar when the configured test feed returns articles quickly enough.

## Deployment

NextNews is intended for OpenStore distribution as a click package.

Before release:

- Build and review amd64 and arm64 packages.
- Test on Ubuntu Touch Stable.
- Prepare OpenStore screenshots and banner.
- Verify Online Accounts setup on a fresh install.
- Verify Nextcloud News API behavior against a dedicated test account.

## Dependencies

- Ubuntu Touch
- Clickable
- Qt/QML with Lomiri Components
- Qt LocalStorage
- Ubuntu Touch Online Accounts
- Nextcloud News server app

## Permissions

The AppArmor profile uses:

- `networking`: connect to the configured Nextcloud server.
- `accounts`: access Ubuntu Touch Online Accounts after user authorization.

NextNews does not request unconfined mode.

## Current Status

Initial NextNews scaffold is complete. The app builds as `nextnews.cloudsite`, includes a News-specific API/cache/controller boundary, passes local contract tests, and has been installed on Ubuntu Touch for Online Accounts testing. The account flow is intentionally OS-account-only and does not expose manual login. Feed creation, folder creation, feed/folder rename, feed move/delete, folder delete, active sync settings, unread navigation counts, search scope, sort settings, direct browser opening, and mail sharing are implemented. The first public release is prepared as version 0.1.0. The experimental mark-read-while-scrolling option is disabled and hidden because device testing showed unreliable behavior; it is deferred to a future release.

## License

NextNews is licensed under the MIT License.

Copyright (c) 2026 Etherghost. See [LICENSE](LICENSE).
