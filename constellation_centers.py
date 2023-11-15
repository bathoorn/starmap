from skyfield.constants import T0

_COLUMN_NAMES = (
    'RAhrs', 'DEdeg', 'dummy', 'Area', 'Rank', 'Name',
)


def load_dataframe(fobj):
    """Given an open file for `catalog.txt`, return a parsed dataframe.

    If your copy of ``catalog.txt`` has already been unzipped, pass the
    optional argument ``compression=None``.

    """
    try:
        from pandas import read_csv, set_option
    except ImportError:
        raise ImportError("NO PANDAS NO CANDO")

    fobj.seek(0)
    magic = fobj.read(2)
    compression = 'gzip' if (magic == b'\x1f\x8b') else None
    fobj.seek(0)

    df = read_csv(
        fobj, sep=' ', names=_COLUMN_NAMES, compression=compression,
        comment='#',
        usecols=['RAhrs', 'DEdeg', 'Area', 'Rank', 'Name'],
        na_values=[''],
    )
    df.columns = (
        'ra_hours', 'dec_degrees', 'area', 'rank', 'name',
    )
    df = df.assign(
        ra_degrees = df['ra_hours'] / 15.0,
        epoch_year = 2000.0,
    )
    return df.set_index('name')