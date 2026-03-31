# click-docs

Generate Markdown documentation for a Click application.

MODULE_PATH is a file system path to the Python module containing the Click command.

**Usage:**

```text
click-docs [OPTIONS] MODULE_PATH
```

**Options:**

| Name | Type | Description |
| --- | --- | --- |
| --command-name | TEXT | Dotted attribute path to the Click command object. |
| --program-name | TEXT | Display name for the command in headings and usage lines. |
| --header-depth | 1<=x<=6 | Markdown header level for the command title (1-6). |
| --style | one of: plain, table | Options rendering style. |
| --output | TEXT | Write output to FILE instead of stdout. |
| --depth | 0<=x | Maximum subcommand recursion depth (0=root only; default=unlimited). |
| --exclude | TEXT | Dotted command path to exclude (e.g. root.admin.reset). Repeatable. |
| --show-hidden | BOOLEAN | Include commands and options marked hidden=True. |
| --list-subcommands | BOOLEAN | Prepend a bulleted TOC of subcommands at the root level. |
| --remove-ascii-art | BOOLEAN | Strip \b-prefixed blocks (ASCII art) from help text. |
| --full-command-path | BOOLEAN | Use the full command path in headers (e.g. 'cli admin' instead of 'admin'). |
