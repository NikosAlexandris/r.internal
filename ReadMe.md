*`r.internal`* links raster maps between Mapsets inside a GRASS GIS data base so as
to save space (and time).

*`r.internal`* will **not** remove a file or a directory that features a single
hardlink (for files, or 2 hardlinks for directories).

> Experimental or not, you decide.  Under development, for sure.

**Always run with `-d` first.**

Quick examples
==============

...


Linking
=======

In a file system,

* a file is a link to an `inode`
* deleting a file, removes one *link* to the underlying `inode`
* an `inode` is only deleted when *all (hard) links* to the `inode` have been
  deleted

## Types of Links

* **hard**: another file linking to the same underlying inode
* **symbolic**, a link to another file name in the file system

### Hard links

* point to the same `inode` as the target file to link-to
* deleting, renaming or moving the original file, will *not* affect a hard link
as it links to the underlying `inode`
* changes to the data on the `inode` are reflected in all files that refer to
  that `inode`

#### +

[+] share the same inode
[+] have the size of the content
[+] take less disk space as they only take up a directory entry
[+] require negligible amount of space (a few bytes), as there are no new
inodes created while creating hard links.
[+] take less time to resolve
[+] performance will be slightly better while accessing directly the disk
pointer instead of going through another file
[+] moving the source file to another location, on the same filesystem, will
not break the link
[+] redundancy: data are not deleted until all links to the files are deleted
[+] useful when the original file is moved
[+] Hard links, on the same file system, are always resolved in a single
look-up, and never involve network latency (if it's a hardlink on an NFS
filesystem, the NFS server would do the resolution, and it would be invisible
to the client system). Sometimes this is important. Not for me, but I can
imagine high-performance systems where this might be important.

#### ?

[?] "I also think things like mmap(2) and even open(2) use the same
functionality as hardlinks to keep a file's inode active so that even if the
file gets unlink(2)ed, the inode remains to allow the process continued access,
and only once the process closes it does the file really go away. This allows
for safer temporary files where you can read/write your data without anyone
being able to access it."

#### -

[-] can't cross file systems: different inode indexing across difference file
systems
[-] you need to explore the whole file system to find files sharing the same
inode
[-] hard-links cannot point to directories.
[-] can "break" if the original file is recreated instead of modified
in-place--a new inode will be created, but the hard link will still point to
the old inode.

### Symbolic links

* point to a file name
* a name of another file
* do not share the same inode

#### +

[+] show instantly the full path they point to
[+] can cross file systems: a soft link contains the full path pointing to
another file

#### -

[-] need their own inode to store the name they point to
[-] have the file name size [?]
[-] consume space (usually 4KB, depending upon the filesystem)
[-] symlink to files that are/will be moved are/will be broken
[-] can point to other symlinks that are in symlinked directories
[-] symbolic links pointing to symbolic links that are on high-latency file
systems, could result in network traffic to resolve

To Do
=====

- unlinking is done via `-u`. Will be replaced with an
  `operation=link[,unlink]` option.
- overwriting existing links is not possible -- first unlink (`-u`) then
  (re-)link.  Implement/use `--o`?

* Clean and summarise even further the Notes.
* Test for if target to link-to and "link" Mapsets are in the same Location
  (that is, they are defined under the same spatial reference system).

Sources
=======

* http://man7.org/linux/man-pages/man7/inode.7.html
* http://man7.org/linux/man-pages/man2/link.2.html
* http://man7.org/linux/man-pages/man1/ln.1.html
* http://man7.org/linux/man-pages/man2/unlink.2.html 
* http://www.geekride.com/understanding-unix-linux-filesystem-inodes/
* https://stackoverflow.com/a/28389692/1172302
* https://stackoverflow.com/a/185903/1172302
* https://stackoverflow.com/a/185997/1172302
* https://stackoverflow.com/a/23422478/1172302
* https://stackoverflow.com/a/20070006/1172302
* http://www.geekride.com/hard-link-vs-soft-link/
* (Personal discussion with a great System Administrator!)
