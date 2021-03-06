import os
import shlex
import subprocess
import pathlib
from grass.pygrass.modules.shortcuts import general as g
from messages import MESSAGE_LINKING
from messages import MESSAGE_SOFT_LINKING
from messages import MESSAGE_RELATIVE_LINKING
from messages import MESSAGE_WILL_NOT_UNLINK
from messages import MESSAGE_REVIEW_UNLINKING_DIRECTORY
from messages import MESSAGE_NO_RASTER_MAP

def link_to_target(
        target,
        link,
        dry_run=True,
        softlinking='',
        relative=False
    ):
    """
    This function creates the requested 'link' to the 'target' file.
    This function does not return anything.

    Parameters
    ----------
    target :
        The target file to link to

    link :
        The link file to create

    dry_run :
        A boolean flag on whether to actually perform the linking or not

    softlinking :
        An empty string or the '-s' string passed to the actual command's
        'flags' option to define whether linking softly or not.

    relative :
        A boolean flag to define whether to create relative links
    """
    linking_message = MESSAGE_LINKING
    if softlinking:
        linking_message = MESSAGE_SOFT_LINKING
        if relative:
            linking_message = MESSAGE_RELATIVE_LINKING
    g.message(
            linking_message.format(target=target, link=link),
            flags='v',
    )
    if not dry_run:
        flags=''
        if softlinking:
            flags += '-s'
            if relative:
                flags += 'r'
        command = f'ln {flags} {target} {link}'
        command = shlex.split(command)
        try:
            subprocess.run(command)
        except subprocess.CalledProcessError as e:
            grass.fatal(e.output)

def unlink_for_target(target, link, elements_to_unlink, dry_run=True):
    """
    """
    target_inode = os.stat(target).st_ino
    target_inode_hardlinks = os.stat(target).st_nlink
    if os.path.isfile(link):  # exclude directories
        if not os.path.islink(link) and target_inode_hardlinks == 1:
            if 'cell_misc' in str(link):
                element = 'meta-element/file'
            else:
                element = 'element/map'
            will_not_unlink = MESSAGE_WILL_NOT_UNLINK.format(
                                element=element,
                                link=link,
                                target_inode=target_inode,
                              )
            g.message(will_not_unlink, flags='i')
            g.message('\n', flags='i')

        elif os.path.islink(link) or target_inode_hardlinks > 1:
            if not dry_run:
                elements_to_unlink.append(link)
    else:
        no_raster_map = MESSAGE_NO_RASTER_MAP.format(link=link)
        g.message(no_raster_map, flags='v')


def unlink_directory(directory, elements_to_unlink, dry_run=True, force=False):
    """
    """
    if (
        pathlib.PurePosixPath(directory).joinpath('r.InternalLink')
        in pathlib.Path(directory).glob('**/r.InternalLink')
    ):
        if not os.path.islink(directory):
            if not force:
                review_unlinking_directory = MESSAGE_REVIEW_UNLINKING_DIRECTORY.format(
                                                directory=directory
                                             )
                g.message(review_unlinking_directory, flags='w')
                g.message('\n')
            elements_to_unlink.append(directory)
