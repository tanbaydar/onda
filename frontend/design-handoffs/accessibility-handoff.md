# CROSS-CUTTING ACCESSIBILITY AND RECOVERY — public-beta ruling

Ruled 2026-08-27 by the current operator. Scope: every frontend route and component at mobile and desktop widths. This handoff supersedes earlier color, focus, target-size, loading-language, and recoverable-error clauses only where they conflict.

## Readable quiet hierarchy

- `--text-muted` is `#6E6E6E`, a readable 5.10:1 step on white for normal-size text. Ink and secondary text remain unchanged.
- `--border-strong` is `#949494`, a 3.03:1 functional boundary on white. Use it for inputs, menus, dialogs, and quiet controls whose boundary communicates the control.
- `--border` and `--border-muted` remain quiet structural hairlines. They are not substitutes for a required control boundary.
- Green remains judgment-only. Accessibility changes do not turn green into focus, navigation, success, or generic action color.

## Focus grammar

- Every keyboard-operable link, button, form field, custom trigger, option, tab, slider, and dialog action has a visible 2px `--action` focus treatment.
- A bordered input uses an inset focus treatment so it remains one rectangle and does not move layout. This preserves the Search field ruling.
- A menu/listbox option may retain its quiet wash, but keyboard focus also receives the 2px action outline. Wash or text-color change alone is insufficient.
- Authored outlines may replace the browser default only when this treatment is present. Focus must not be clipped by fixed chrome, panels, or overflow containers.

## Target size

- Essential mobile actions target 44×44px: primary navigation, account/auth controls, tabs, menu and listbox triggers/options, pagination/recovery actions, Follow, review expansion, row removal, and dialog actions.
- A visibly compact text or glyph may use invisible padding to reach the target without changing the editorial register.
- All other pointer targets meet at least 24×24px or the spacing/equivalent-control exceptions. Desktop text links may remain typographically compact when they satisfy that floor.

## Loading and recovery

- Work in progress uses an ellipsis: `Loading…`, `Searching…`, `Saving…`, `Retrying…`. Stable statements and errors use a period.
- A recoverable error uses one local sentence plus `Retry`. Successful content remains mounted when a continuation request, relationship action, or read-state bookkeeping request fails.
- A session lookup failure does not block public browsing. The viewer receives guest navigation, public routes remain usable, and the persistent account-status line offers Retry.
- Danger color is reserved for the local error and recovery treatment. Recovery must not become a stack of banners or cards.

## Motion

- Motion is optional feedback, never required to understand state. The favorite commit may use the existing 120ms ease-out pulse; un-favorite remains instant.
- `prefers-reduced-motion: reduce` disables the pulse. No other decorative motion inherits permission from this exception.
