# Mythic Plus for LonelyIce

Mythic Plus server module packaged for LonelyIce. Upstream is an experimental module, including custom progression and item changes. Its original client interface is not present in the upstream repository.

Upstream: https://github.com/araxiaonline/mod-mythic-plus.git

Pinned source: `565922c456902f258b258198a66b842a149a695e`.

This repository contains packaging, build configuration and patches, not a fork of upstream. Add its path to `LONELYICE_PLUGIN_DIRS` when building LonelyIce. Install the resulting package through the launcher or `--pkg install`.

## Building

Requires a LonelyIce build using core ABI `lonelyice-ac-2`, CMake, Git and the core's C++ dependencies. Add this repository's absolute path to the semicolon-separated `LONELYICE_PLUGIN_DIRS` CMake option; CMake fetches the pinned upstream revision and applies the patches in `patches/`. It never modifies your upstream checkout. Windows x64 and Linux x64 are supported.

```sh
cmake -S /path/to/lonelyice -B /path/to/build -DLONELYICE_CORE_DIR=/path/to/core -DLONELYICE_PLUGIN_DIRS=/path/to/mod-mythic-plus-plugin
cmake --build /path/to/build --config RelWithDebInfo --target mod-mythic-plus
```

The plugin folder is written under the build's `bin/plugins` directory (`bin/RelWithDebInfo/plugins` with Visual Studio). Package it with `LonelyIce --pkg pack <plugin-folder> <output-folder>`. The release ZIP contains both platform libraries where applicable. Source revisions are recorded in `plugin.json`; the port's source and patches remain available in this repository under the upstream license.

## Installing and using

This first port is experimental. Back up your world and characters databases before installing on an existing realm: upstream data adds custom items, vendors, progression tables and alters base stats and rewards. It has no dependency on ALE, AIO or another Lua engine. The upstream `MPUi` client interface is not included, because its source is absent from the pinned upstream repository.

Install `mod-mythic-plus` from the catalog and configure it through GUI/TUI; settings are stored in the active YAML profile. Restart to apply settings. Apply the package's client patch to every participating WoW 3.3.5a client; for headless setups distribute the resulting client patch separately. Named advancement spell IDs are allocated through LonelyIce's DBC recipe system rather than fixed very large spell IDs. SQL is adapted to the current schema and uses LonelyIce's database dialect layer, including SQLite. NPCBots wander-node SQL is omitted because that separate module is not present.

Create a group and, as its leader, select `.mp set mythic`, `.mp set legendary`, or `.mp set ascendant` before entering the dungeon. `.mp set normal` and `.mp set heroic` clear the custom group difficulty. `.mp status` shows settings; `.advancement` opens server-side progression information. Difficulty changes are rejected inside dungeons. Death allowance 0 means unlimited. Disabled dungeon IDs and enabled difficulty names are comma-separated lists.

Validated: Windows and Linux compilation, SQL application to an isolated current SQLite schema, SQL adaptation regression tests, and package structure. Dungeon clear, combat balance, reward behavior and client interactions require in-game testing; no gameplay validation is claimed. The upstream module remains experimental and its balance/content limitations remain applicable.

For isolated SQL checks enable `LONELYICE_PORT_TESTS` and build `mythic-sql-check`. Run it with a SQLite schema DDL file and the package's `data/sql/db-world` or `db-characters` directory. Run adapter tests with `python -m unittest discover -s tests`. Python 3 is required at build time only.
