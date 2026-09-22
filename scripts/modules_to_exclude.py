# This list contains the filenames of artifact scripts that take a long time to run,
# or that produce enough rows to crowd a report the examiner did not ask them for.
# These modules are deselected by default in the GUI.

modules_to_exclude = [
    'c2paProvenance',
    'imagemngCache',
    # Records recovered from the unallocated space of MMKV stores. Not slow, but the
    # table is large and most of it is only worth reading when recovery is the question:
    # a single localisation store on one tested image contributed 12,255 of that run's
    # 12,637 rows. The examiner opts in.
    'mmkvCarved',
    'walStrings'
]