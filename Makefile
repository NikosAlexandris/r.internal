MODULE_TOPDIR = ../..

PGM = r.internal

ETCFILES = constants grassgis helpers linking messages

include $(MODULE_TOPDIR)/include/Make/Script.make
include $(MODULE_TOPDIR)/include/Make/Python.make

default: script
