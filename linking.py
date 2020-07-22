import os
import shlex
import subprocess
import pathlib
from grass.pygrass.modules.shortcuts import general as g


def link_to_target(target, link, dry_run=True, softlinking=''):
    """
    """
    g.message(
            f'Linking \'{target}\' to \'{link}\'',
            flags='v',
    )
    if not dry_run:
        if softlinking:
            flag = '-s'
        else:
            flag = ''
        command = f'ln {flag} {target} {link}'
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
            g.message(f'The {element} \'{link}\' is the only hardlink for the inode \'{target_inode}\'. Will NOT unlink!', flags='i')
            g.message('\n', flags='i')

        elif os.path.islink(link) or target_inode_hardlinks > 1:
            if not dry_run:
                elements_to_unlink.append(link)
    else:
        g.message(f'There is no raster map file \'{link}\' to remove', flags='v')


def unlink_directory(directory, elements_to_unlink, dry_run=True, force=False):
    """
    """
    if (
        pathlib.PurePosixPath(directory).joinpath('r.InternalLink')
        in pathlib.Path(directory).glob('**/r.InternalLink')
    ):
        if not os.path.islink(directory):
            if not force:
                g.message(f'Directory \'{directory}\' appears to be an r.internal product. Adding it to list of elements to unlink! Please Review!', flags='w')
                g.message('\n')
            elements_to_unlink.append(directory)

