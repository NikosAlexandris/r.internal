## About

r.internal links raster maps between Mapsets inside a GRASS GIS data base so as to save space (and time).

`r.internal` will **not** remove a file or a directory that features a single hardlink (for files, or 2 hardlinks for directories).

( Experimental or not, you decide.  Under development, for sure. )

Always run with `-d` first.

## Notes

Currently,


- unlinking is done via `-u`. Will be replaced with an `operation=link[,unlink]` option.

- overwriting existing links is not possible -- first unlink (`-u`) then (re-)link
