from constants import CELL
import os
import grass.script as grass
from grass.script import CalledModuleError
from messages import MESSAGE_MAP_NOT_FOUND

def find_raster_map(raster_map, mapset):
    """
    """
    try:
        found = grass.parse_command(
                'g.findfile',
                flags='n',
                mapset=mapset,
                element=CELL,
                file=raster_map,
                )
                # |grep ^name |cut -d"=" -f2)
    except:
        message = MESSAGE_MAP_NOT_FOUND.format(target=raster_map)
        grass.fatal(message)
    return found['name']

def get_mapset_path(raster_map, mapset):
    """
    """
    raster_info = grass.parse_command(
            'r.info',
            flags='e',
            map=f'{raster_map}@{mapset}',  # |grep -v ^comment)
    )
    database = raster_info['database']
    location = raster_info['location']
    mapset = raster_info['mapset']
    mapset_path = os.path.join(database, location, mapset)
    return mapset_path
