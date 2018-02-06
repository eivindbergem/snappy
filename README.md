# Snappy
Snappy is a simple tool for making directory snapshot. It uses a content-addressable filesystem inspiered by git, but is much simpler and provides no VCS functionality.

# Use cases

Snappy is intended as a light weight tool to create snapshots. My personal use is for use with HPC workload managers like SLURM where I need to copy files to a separate file system for each job. With snappy I can take a snapshot when the job is created and be safe that the files won't change by the time the job runs.

# Usage

To start, in the directory you want snapshot, run:

```
$ snappy init
```

This will create `.snappy`.

## Snapshots

To create a snapshot:

```
$ snappy snapshot
```

This will return a sha256 hash that is the identifier of the snapshot. All files at the time the snapshot was created will be stored in `.snappy/storage`.

List all snapshots by running:

```
$ snappy ls
```

To delete a snapshot, run:

```
$ snappy rm <snapshot-hash>
```

Note that this will not remove the objects in storage, but only remove the directory tree described by the snapshot. To remove unrefrenced objects, run:

```
$ snappy clean
```

To view changes since the last snapshot:

```
$ snappy diff
```

## Ignoring files

Snappy can ignore files just like git. Patterns can be added to `.snappy/ignore`. The pattern matching works like regular UNIX wildcard expansion.

## Loading snapshots

Snapshots can be loaded by either copying out all the files, or by symlinking to the objects.

To copy files, run:

```
$ snappy checkout <snapshot-hash> [dst]
```

If `dst` is ommitted, the snapshot will be checked out in the working directory.

To link a snapshot, run:

```
$ snappy link <snapshot-hash> <dst>
```

This will create symlinks to all the files in the snapshot in the directory `dst`. This is good if you only need read-only access to the files.
