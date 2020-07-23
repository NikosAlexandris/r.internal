#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
from messages import MESSAGE_ELEMENT_EXISTS
from messages import MESSAGE_SUB_ELEMENT_EXISTS
from messages import MESSAGE_META_ELEMENT_EXISTS
from messages import MESSAGE_CREATE_ELEMENT_DIRECTORY
from messages import MESSAGE_CREATE_SUBELEMENT_DIRECTORY
from helpers import find_raster_map
from helpers import get_mapset_path
from linking import link_to_target
from linking import unlink_for_target
from linking import unlink_directory

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
    link_suffix = options['suffix']

    # raster map's whereabout
    raster_map_found = find_raster_map(
            raster_map=target_raster_map,
            mapset=target_mapset,
    )
    target_mapset_path = get_mapset_path(
            raster_map=target_raster_map,
            mapset=target_mapset,
    )

    global elements_to_unlink  # hold elemets to unlink
    elements_to_unlink = []

    # Loop over elements to hard-link to
    for element in ELEMENTS:
        element_target = os.path.join(CURRENT_MAPSET, element, target_raster_map)
        element_path = pathlib.Path(CURRENT_MAPSET_PATH).joinpath(element)
        target = os.path.join(target_mapset_path, element, target_raster_map)
        link = os.path.join(CURRENT_MAPSET_PATH, element, target_raster_map)
        if link_suffix:
            link += f'_{link_suffix}'
            link = pathlib.Path(link)

        if element in ELEMENTS:
            if os.path.isfile(target):  # excludes 'cell_misc' directory
                if not unlinking:  # unlinking not requested
                    if not os.path.isdir(element_path):  # create Element
                        create_directory = MESSAGE_CREATE_ELEMENT_DIRECTORY.format(
                                path=element_path,
                        )
                        g.message(create_directory, flags='v')
                        if not dry_run:  # if dry run not requested
                            pathlib.Path.mkdir(element_path, parents=True)
                    elif os.path.isfile(link):
                        element = os.path.join(element, link)
                        element_exists = MESSAGE_ELEMENT_EXISTS.format(
                                element=element,
                        )
                        g.message(element_exists, flags='w')
                    if not os.path.isfile(link):  # if hardlink does not exist
                        link_to_target(
                                target=target,
                                link=link,
                                dry_run=dry_run,
                                softlinking=softlinking,
                        )
                        g.message('\n', flags='v')

                if unlinking:
                    unlink_for_target(
                            target=target,
                            link=link,
                            dry_run=dry_run,
                            elements_to_unlink=elements_to_unlink,
                    )

        if element == CELL_MISC:  # 'cell_misc' is a directory
            if (
                    not os.path.isdir(link)  # if directory does NOT exist
                    and not unlinking  # include only directories, i.e. 'cell_misc'
            ):
                create_subelement = MESSAGE_CREATE_SUBELEMENT_DIRECTORY.format(
                        path=link,
                )
                g.message(create_subelement, flags='v')
                if not dry_run:
                    pathlib.Path.mkdir(link, parents=True)
                    command = f'touch {link}/r.InternalLink'  # Chances this already exists?
                    command = shlex.split(command)
                    try:
                        subprocess.run(command)
                    except subprocess.CalledProcessError as e:
                        print(e.output)
                g.message('\n', flags='v')

            else:
                if os.path.isdir(link) and not unlinking:
                    element_exists = MESSAGE_SUB_ELEMENT_EXISTS.format(
                            element=os.path.join(element, target_raster_map)
                    )
                    g.message(element_exists, flags='w')
                if os.path.isdir(link) and unlinking:
                    unlink_directory(
                            directory=link,
                            elements_to_unlink=elements_to_unlink,
                            dry_run=dry_run,
                            force=force,
                    )

            for cell_misc_element in pathlib.Path(target).glob('**/*'):
                cell_misc_element_basename = os.path.basename(cell_misc_element)
                cell_misc_link = pathlib.Path(link).joinpath(cell_misc_element_basename)

                if not unlinking:
                    if os.path.isdir(link) and os.path.isfile(cell_misc_link):
                        element_exists = MESSAGE_META_ELEMENT_EXISTS.format(
                                element=os.path.join(target_raster_map, cell_misc_element_basename)
                        )
                        g.message(element_exists, flags='w')

                    if not os.path.isfile(cell_misc_link):  # if hardlink does not exist
                        link_to_target(
                                target=cell_misc_element,
                                link=cell_misc_link,
                                dry_run=dry_run,
                                softlinking=softlinking,
                        )
                        g.message('\n', flags='v')

                elif unlinking:
                    unlink_for_target(
                            target=cell_misc_element,
                            link=cell_misc_link,
                            dry_run=dry_run,
                            elements_to_unlink=elements_to_unlink,
                    )

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
