#!/usr/bin/env python
# -*- coding: utf-8 -*-

from devtools import debug
"""
 MODULE:       r.internal

 AUTHOR(S):    Nikos Alexandris <nik@nikosalexandris.net>
               Based on a shell script developed in 2017-2018

 PURPOSE:      Link GRASS GIS raster maps existing in other Mapsets

 COPYRIGHT:    (C) 2020 by the GRASS Development Team

               This program is free software under the GNU General Public
               License (>=v2). Read the file COPYING that comes with GRASS
               for details.
"""

#%Module
#%  description: Link GRASS GIS raster maps between Mapsets
#%  keywords: raster, link, hardlink, softlink, symlink
#%End

#% flag
#%  key: d
#%  description: Dry run: do not link, show only what would be linked
#% end

#% flag
#%  key: s
#%  description: Create symbolic links instead of hard links
#% end

#% flag
#%  key: u
#%  description: Call the unlink function to remove hardlinked raster map files
#% end

#% flag
#%  key: f
#%  description: Force remove hardlinked raster map files
#% end

#% rules
#%  excludes: -s, -u
#%  excludes: -s, -f
#%  requires: -f, -u
#%  excludes: -f, -d
#% end

#%option G_OPT_R_INPUT
#% key: input
#% key_desc: filename
#% description: Input raster map to link to
#% required : yes
#%end

#%option
#% key: mapset
#% type: string
#% description: Mapset of input raster map to link to
#% required: yes
#%end

#%option
#% key: suffix
#% key_desc: output raster map name suffix
#% key_desc: filename
#% type: string
#% description: Output suffix added after the input raster map name
#% required: no
#%end

import os
import sys
if not os.environ.get("GISBASE"):
    sys.exit("You must be in GRASS GIS to run this program.")
sys.path.insert(
        1,
        os.path.join(os.path.dirname(sys.path[0]),
            'etc',
            'r.internal',
        )
)
import shutil
import shlex
import subprocess
import pathlib
import grass.script as grass
from grass.pygrass.modules.shortcuts import general as g
from constants import CELL
from constants import CELL_MISC
from constants import ELEMENTS
from grassgis import CURRENT_MAPSET
from grassgis import CURRENT_MAPSET_PATH
from messages import MESSAGE_DRY_RUN
from messages import MESSAGE_SOFTLINKING
from messages import MESSAGE_MAP_NOT_FOUND
from messages import MESSAGE_DRY_UNLINKING
from messages import MESSAGE_UNLINKING_WARNING
from messages import MESSAGE_UNLINKING_EMPTY_LIST
from messages import MESSAGE_UNLINKING_WARNING
from messages import MESSAGE_UNLINKING_WARNING
from messages import MESSAGE_UNLINKING
from messages import MESSAGE_UNLINKING_ADDITIONAL_INFORMATION
from helpers import find_raster_map
from helpers import get_mapset_path

def main():

    # flags
    dry_run = flags['d']
    if dry_run:
        g.message(MESSAGE_DRY_RUN, flags='i')
    softlinking = flags['s']
    if softlinking:
        g.message(MESSAGE_SOFTLINKING, flags='i')
    unlinking = flags['u']
    force = flags['f']

    # options
    target_raster_map = options['input']
    target_mapset = options['mapset']
    link_raster_map_suffix = options['suffix']

    # raster map's whereabout
    raster_map_found = find_raster_map(
            raster_map=target_raster_map,
            mapset=target_mapset,
    )
    # if not raster_map_found:
    #     g.message(MESSAGE_MAP_NOT_FOUND, flags='e')
    #     1/0
    # else:
    #     g.message(f'Input raster map: {raster_map_found}', flags='v')

    target_mapset_path = get_mapset_path(
            raster_map=target_raster_map,
            mapset=target_mapset,
    )

    elements_to_unlink = [] # hold elemets to unlink

    # Loop over elements to hard-link to
    for element in ELEMENTS:
        element_target = os.path.join(CURRENT_MAPSET, element, target_raster_map)
        element_path = os.path.join(CURRENT_MAPSET_PATH, element)
        target = os.path.join(target_mapset_path, element, target_raster_map)
        link = os.path.join(CURRENT_MAPSET_PATH, element, target_raster_map)
        if link_raster_map_suffix:
            link += f'_{link_raster_map_suffix}'
            link = pathlib.Path(link)
        # debug(locals())

        # ----------------------------------------------------------------------
        if element in ELEMENTS:
            if os.path.isfile(target):  # excludes 'cell_misc' directory
                if not unlinking:  # unlinking not requested
                    if not os.path.isdir(element_path):  # create Element
                        # g.message(f'Element: {element}', flags='v')
                        g.message(f'+ Creating element directory {element_path}', flags='v')
                        if not dry_run:  # if dry run not requested
                            pathlib.Path.mkdir(element_path, parents=True)
                    else:
                        if os.path.isfile(link):
                            # map_exists_message = f'A raster map file with the name \'{target_raster_map}\' already exists!'
                            # g.message(map_exists_message, flags='w')
                            element = os.path.join(element, link)
                            g.message(f'Element \'{element}\' already exists', flags='w')

                    if not os.path.isfile(link):  # if hardlink does not exist
                        link_to_target(
                                target=target,
                                link=link,
                                dry_run=dry_run,
                                softlinking=softlinking,
                        )
                        g.message('\n', flags='v')

                if unlinking:
                    target_inode = os.stat(target).st_ino
                    target_inode_hardlinks = os.stat(target).st_nlink

                    if os.path.isfile(link):  # exclude directories
                        if os.path.islink(link) or target_inode_hardlinks > 1:
                            if not dry_run:
                                elements_to_unlink.append(link)

                        elif not os.path.islink(link) and target_inode_hardlinks == 1:
                            g.message(f'The element/map \'{link}\' is the only hardlink for the inode \'{target_inode}\'. Will NOT unlink!', flags='i')

                    else:
                        g.message(f'There is no raster map file \'{link}\' to remove', flags='v')

        # ----------------------------------------------------------------------
        if element == CELL_MISC:  # 'cell_misc' is a directory
            if (
                    not os.path.isdir(link)  # if directory does NOT exist
                    and not unlinking  # include only directories, i.e. 'cell_misc'
            ):
                g.message(f'+ Creating sub-element directory \'{link}\'', flags='v')
                if not dry_run:
                    pathlib.Path.mkdir(link, parents=True)
                    command = f'touch {link}/r.InternalLink'
                    command = shlex.split(command)
                    try:
                        subprocess.run(command)
                    except subprocess.CalledProcessError as e:
                        print(e.output)
                g.message('\n', flags='v')

            else:
                if os.path.isdir(link) and not unlinking:
                    g.message(f'Sub-element \'{os.path.join(element, target_raster_map)}\' already exists', flags='w')
                if os.path.isdir(link) and unlinking:
                    target_inode = os.stat(link).st_ino
                    target_inode_hardlinks = os.stat(link).st_nlink

                    if (
                            pathlib.PurePosixPath(link).joinpath('r.InternalLink')
                            in pathlib.Path(link).glob('**/r.InternalLink')
                    ):
                        if not os.path.islink(link):
                            if not force:
                                g.message(f'Directory \'{link}\' appears to be an r.internal product. Adding it to list of elements to unlink! Please Review!', flags='w')
                                g.message('\n')
                            elements_to_unlink.append(link)

            # for cell_misc_element in os.listdir(target):
            for cell_misc_element in pathlib.Path(target).glob('**/*'):
                cell_misc_element_basename = os.path.basename(cell_misc_element)
                cell_misc_link = pathlib.PurePosixPath(link).joinpath(cell_misc_element_basename)

                if not unlinking:
                    if os.path.isdir(link) and os.path.isfile(cell_misc_link):
                        g.message(f'Meta-element \'{os.path.join(target_raster_map, cell_misc_element_basename)}\' already exists', flags='w')

                    if not os.path.isfile(cell_misc_link):  # if hardlink does not exist
                        link_to_target(
                                target=cell_misc_element,
                                link=cell_misc_link,
                                dry_run=dry_run,
                                softlinking=softlinking,
                        )
                        g.message('\n', flags='v')


                elif unlinking:
                    target_inode = os.stat(cell_misc_element).st_ino
                    target_inode_hardlinks = os.stat(cell_misc_element).st_nlink

                    if os.path.isfile(cell_misc_link):
                        if not os.path.islink(cell_misc_link) and target_inode_hardlinks == 1 :
                            g.message(f'The meta-element \'{cell_misc_link}\' is the only hardlink for the inode \'{target_inode}\'. Will NOT unlink!', flags='i')
                        elif os.path.islink(cell_misc_link) or target_inode_hardlinks > 1:
                            # g.message(f'Adding \'{cell_misc_link}\' to list of elements to unlink!', flags='w')
                            if not dry_run:
                                elements_to_unlink.append(cell_misc_link)


                    if os.path.isdir(cell_misc_link):
                        # g.message(f'There is no raster map file \'{link}\' to remove', flags='v')
                        g.message(f'The element {cell_misc_link} is a directory...', flags='v')

    # unlinking
    if elements_to_unlink:
        if unlinking:
            if not force:
                elements_to_unlink = [str(element) for element in elements_to_unlink]
                elements_to_unlink.insert(0, MESSAGE_DRY_UNLINKING)
                elements_to_unlink = f'{chr(10).join(elements_to_unlink)}'
                g.message(elements_to_unlink)
                g.message('\n')
                g.message(MESSAGE_UNLINKING_WARNING, flags='w')

            elif force:
                for element in elements_to_unlink:
                    unlinking_element = f'Removing link: {element}'
                    g.message(unlinking_element, flags='i')
                    if os.path.isdir(element):
                        shutil.rmtree(element)
                    if os.path.isfile(element):
                        element=pathlib.Path(element)
                        pathlib.Path.unlink(element)

    elif elements_to_unlink == [] and unlinking:
        g.message(MESSAGE_UNLINKING_EMPTY_LIST, flags='i')

if __name__ == "__main__":
    options, flags = grass.parser()
    sys.exit(main())
