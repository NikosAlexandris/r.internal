MESSAGE_LINKING_INSIDE_TARGET_MAPSET = (
        'Linking an existing raster map '
        'inside the same Mapset '
        'without a \'suffix\' '
        'is not allowed!'
)
MESSAGE_CREATE_ELEMENT_DIRECTORY = '+ Creating element directory \'{path}\''
MESSAGE_CREATE_SUBELEMENT_DIRECTORY = '+ Creating sub-element directory \'{path}\''
MESSAGE_DRY_RUN = ' >>> Dry run: show intentions, yet do nothing!'
MESSAGE_DRY_UNLINKING = 'The following links would be removed:'
MESSAGE_MAP_NOT_FOUND = 'Can\'t find the {target} raster map'
MESSAGE_LINKING = 'Linking \'{target}\' to \'{link}\''
MESSAGE_SOFT_LINKING = 'Soft ' + MESSAGE_LINKING
MESSAGE_RELATIVE_LINKING = 'Relative ' + MESSAGE_SOFT_LINKING
MESSAGE_UNLINKING = 'Removing linked raster map file '
MESSAGE_UNLINKING_ADDITIONAL_INFORMATION = (
        'No element directories removed. '
        'Please carefully remove such elements manually.'
)
MESSAGE_UNLINKING_EMPTY_LIST = 'The list of raster map files to unlink is empty!'
MESSAGE_UNLINKING_WARNING = (
        'Nothing removed. '
        'You must use the force flag (-f) to actually unlink '
        'the specified hardlinked raster map files. '
        'Exiting.'
)
STRING_ELEMENT = 'Element'
STRING_META_ELEMENT = 'Meta-element'
STRING_SUB_ELEMENT = 'Sub-element'
MESSAGE_EXISTS = ' \'{element}\' already exists'
MESSAGE_ELEMENT_EXISTS = STRING_ELEMENT + MESSAGE_EXISTS
MESSAGE_SUB_ELEMENT_EXISTS = STRING_SUB_ELEMENT + MESSAGE_EXISTS
MESSAGE_META_ELEMENT_EXISTS = STRING_META_ELEMENT + MESSAGE_EXISTS
MESSAGE_WILL_NOT_UNLINK = (
        'The {element} \'{link}\' '
        'is the only hardlink for the inode \'{target_inode}\'.'
        'Will NOT unlink!'
)
MESSAGE_REVIEW_UNLINKING_DIRECTORY = (
        'Directory \'{directory}\''
        'appears to be an r.internal product. '
        'Adding it to list of elements to unlink! '
        'Please Review!'
)
MESSAGE_NO_RASTER_MAP = 'There is no raster map file \'{link}\' to remove'
