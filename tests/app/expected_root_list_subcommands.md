# root

Root command with subgroups.

**Usage:**

```text
root [OPTIONS] COMMAND [ARGS]...
```

**Options:**

```text
  --help  Show this message and exit.
```

**Subcommands:**

- [admin](#admin): Admin commands.
- [hello](#hello): Simple program that greets NAME.

## admin

Admin commands.

**Usage:**

```text
root admin [OPTIONS] COMMAND [ARGS]...
```

**Options:**

```text
  --help  Show this message and exit.
```

### reset

Reset the system to defaults.

**Usage:**

```text
root admin reset [OPTIONS]
```

**Options:**

```text
  --force  Force the reset.
  --help   Show this message and exit.
```

### status

Check system status.

**Usage:**

```text
root admin status [OPTIONS]
```

**Options:**

```text
  --help  Show this message and exit.
```

## hello

Simple program that greets NAME.

**Usage:**

```text
root hello [OPTIONS]
```

**Options:**

```text
  --name TEXT  The person to greet.  [required]
  --help       Show this message and exit.
```
