# Changelog

## Unreleased

- Aligned the account page with the shared Nextcloud suite flow: clickable account rows, guided Ubuntu Touch account-setting approval, automatic verification after account selection, and immediate controller refresh after changing account.
- Added the Content Hub AppArmor permissions required by NextNews external link and email sharing actions, while keeping Online Accounts and networking unchanged.

## 0.1.3 - 2026-06-14

- Improved article list cards with a cleaner NextNotes-inspired layout, better spacing, and a subtler read/unread visual treatment.
- Added feed identity to article cards, including feed favicon or fallback initial, feed name, and a visual favorite star for starred articles.
- Fixed short article titles so they align to the top of the card instead of appearing on the second line.
- Added pull-to-refresh status text in the article list: pull, release, and refreshing states now match the NextNotes behavior.
- Added visible language choices matching NextNotes: English, Swedish, German, French, Dutch, Danish, Norwegian Bokmal, Spanish, and Finnish.
- Added partial AI-assisted starter translation catalogs for German, French, Dutch, Danish, Norwegian Bokmal, Spanish, and Finnish. Untranslated strings fall back to English.
- Added dark desktop debug launch scripts for development and translation testing.

## 0.1.2 - 2026-06-13

- Fixed Online Accounts authorization so selecting an existing Ubuntu Touch account does not open the provider login page.

## 0.1.1 - 2026-06-13

- Fixed article swipe actions: swipe right now toggles star/favorite, and swipe left toggles read/unread.
- Fixed unreadable navigation drawer row text in light mode for Views, Folders, and Feeds.

## 0.1.0 - 2026-06-13

- Initial OpenStore release.
- Supports Ubuntu Touch Online Accounts for Nextcloud/ownCloud authentication.
- Lists Nextcloud News folders, feeds, and articles.
- Supports cached/offline reading of previously loaded articles.
- Supports adding, renaming, moving, and deleting feeds.
- Supports creating, renaming, and deleting folders.
- Supports marking articles read/unread and starring/unstarring articles.
- Supports pull-to-refresh, active sync while the app is open, and pending read/star changes after network failures.
- Includes article search, settings, Swedish translation, About page, and OpenStore-ready app identity.
