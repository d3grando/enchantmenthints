# Enchantment Hints

A **native** Horizon mod (a horizon-mixins source mixin): every item tooltip
gets a short hint under each enchantment, saying what it does. This covers
enchanted books and enchanted gear, in inventories, the creative screen,
containers, the recipe book and chat's item hovers. Hints show all the time,
or only while Shift is held. Their colour, line width and the items they
apply to are set in game: Options > Mods > Enchantment Hints > Settings.

Inspired by Enchantment Descriptions (https://modrinth.com/mod/enchantment-descriptions); not affiliated, no code from it.
All hint texts were written for this mod.

> **Native mods are not sandboxed.** Unlike `.hmod` (Wasm) mods, a native mod is
> Rust source compiled into your own Horizon executable and runs with your user
> rights. Read the source before you build it. It is small: `mixins/enchantmenthints/`.

## Behaviour

```
Enchanted Book
Mending
 Experience you pick up repairs this item
 before it goes to your level.
Unbreaking III
 The item loses durability less often.
```

- Each enchantment line in a tooltip gets its hint right under it, indented,
  in the hint colour, and wrapped at the line width. Both a book's stored
  enchantments and an item's own enchantments get hints, and curses get them
  too.
- **Shift mode.** Hints show only while either Shift key is held. Otherwise a
  single line under the last enchantment says *Hold Shift for enchantment
  hints*. You can turn that reminder line off.
- If a tooltip hides its enchantments (`minecraft:tooltip_display`), nothing is
  added. An enchantment the mod knows nothing about (a datapack or modded one
  with no text, see below) gets no line.
- The mod only changes what is drawn. Items, the game and servers are left as
  they are, and the mod works in single player, on LAN and on servers.
- If you turn the mod off in Options > Mods, tooltips go back to vanilla at
  once.

## Languages

All 43 enchantments of Minecraft 26.3 have built-in text in **English** and
**Russian**. The game's selected language picks between them (`ru_*` gets
Russian, any other language gets English). The settings page and the Shift
reminder follow the same choice.

Hints are looked up through the game's language system, so a **resource pack**
can change or add them in any language. Each enchantment is looked up in this
order:

1. `enchantmenthints.<namespace>.<path>` in the pack's `lang/<code>.json`,
   e.g. `"enchantmenthints.minecraft.sharpness": "..."`. This beats the
   built-in text. An empty value hides that hint.
2. The built-in text, when the selected language is English or Russian.
3. `enchantment.<namespace>.<path>.desc`: the key that other enchantment
   description packs use, for modded enchantments and for other languages.
4. The built-in English text.

Horizon layers the selected language over `en_us`. A pack that only has
`en_us` keys therefore shows its English text in every language.

## Settings

**Options > Mods** lists Enchantment Hints with its **Settings** button. The
row's own button turns the mod off, and it then does nothing at all; click it
again to turn it back on. Each click on the settings page moves a setting to
its next value. The change applies at once and is saved:

| Button | Key | Values a click cycles through |
|---|---|---|
| Show hints: always | `mode` | always (`"always"`), while Shift is held (`"shift"`) |
| Hold-Shift reminder: ON | `shiftReminder` | ON, OFF (shown in Shift mode only) |
| Colour: dark gray | `colour` | dark gray, gray, white, yellow, gold, green, dark green, aqua, dark aqua, blue, dark blue, light purple, dark purple, red, dark red |
| Line width: 200 px | `wrapWidth` | 120, 160, 200, 240, 320 GUI pixels, no wrapping (0) |
| Items: books and gear | `items` | books and gear (`"all"`), enchanted books only (`"books"`) |
| Reset to defaults | | every setting back to its default |

The page is in Russian when the game is.

The settings are kept in
`horizon-mods/.horizon-mod-data/enchantmenthints/config.json`. That is the
mod's settings folder, beside the game's `options.txt`, in the instance that
plays the native build. If no file exists, the defaults apply:

```json
{
  "mode": "always",
  "shiftReminder": true,
  "colour": "dark_gray",
  "wrapWidth": 200,
  "items": "all"
}
```

By hand, `colour` can also be any `#RRGGBB`, and `wrapWidth` any value from
40 to 1000 or 0. If the file is broken (an unknown key or a bad value), no
hints are shown. The page then shows the error (click it to read the file
again) and a reset button, and stderr gets `Enchantment Hints disabled: ...`.

## Compatibility

Horizon's native mods can use **hook points** (`game/native_hooks.rs`,
`NATIVE_HOOKS_API`). These functions stay stable from release to release.
Enchantment Hints uses them wherever one exists:

- `native_mods`, `native_settings`, `native_settings_click` for the row in
  Options > Mods and its settings page;
- `native_setting`/`native_set_setting` for `config.json`;
- `native_on` for the Options > Mods off switch. Every tooltip passes through
  untouched while the mod is off;
- `native_text_width` to wrap the hints.

There is no hook point for item tooltips, so one game function is hooked
directly, and that **pins** the mod to one Horizon commit:

| Hook | Why it is pinned |
|---|---|
| `stations::Game::stack_tooltip` (HEAD, cancellable) | Every item tooltip the game draws is built here: the slot tooltips of every inventory and container screen, the creative screen, the recipe book, the mod browser, and chat's `show_item` hovers. No hook point exposes tooltip lines. The hook asks the game for its own lines (one re-entrant call, guarded by a flag), puts the hints in under the enchantment lines, and returns the result. Stacks without enchantments go straight on to the game. |

`native.rs` also reads the game's own internals: the enchantment registry and
its `#minecraft:tooltip_order` tag (so it can find each enchantment's line)
and `has_shift_down` (both Shift keys). This is another reason the mod is
pinned.

The mod has no command or tick hook and does not need them. Tooltips are drawn
only by the window's game, so the window's `native_on` is all it reads, and
there is no state for a server thread to share.

Pinned: Horizon `fdc87aecdbd116bf1e08adcd062fcbaea8c2e2ca`, horizon-mixins
`5a64af938ec86b00d53d16a408aabc0038fb3e57`, game 26.3 (Nightly 2026-11-08). Checked on that commit with `horizon-mixins apply`
and `cargo check`, alone and together with LookAt, Mouse Tricks and TreeFall. No other mod in that set hooks `stack_tooltip`.

## Build and try

Enchantment Hints is a source bundle, and the launcher compiles it into a
custom game:

```sh
horizon-launcher native-build <this folder> --version v0.2.97 --trust-native-code
```

## Development

`mixins/enchantmenthints/`:

- `horizon-mixin.toml`: two support modules and four HEAD hooks (see above).
- `runtime.rs`: all the logic, as pure code with unit tests. That covers the
  hint texts and their lookup order, the tooltip order, finding the
  enchantment lines, word wrap, Shift mode, the config, and the settings
  page. It is both this repository's Cargo library and the injected
  `crate::game::enchantmenthints` module.
- `native.rs`: the adapter to the game (`crate::game::enchantmenthints_native`).
- `tooltip.rs`, `list.rs`, `settings.rs`, `click.rs`: the hook helpers.

```sh
cargo test
cargo fmt --check
cargo clippy --all-targets -- -D warnings
python tools/pack_hnmod.py   # dist/enchantmenthints-<version>.hnmod
```

`cargo fmt` only sees the library. Check the game-side files with
`rustfmt --check --edition 2024 mixins/enchantmenthints/*.rs`.

MIT licensed. Original code and text.
