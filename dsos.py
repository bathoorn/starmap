from skyfield.constants import T0

_COLUMN_NAMES = (
    'DSOID', 'RAdeg', 'DEdeg', 'Bmag', 'Vmag',
    'OType', 'MType', 'MajRarcmin', 'MinRarcmin', 'OAdegrees', 'RS', 'RSerror',
    'Plx', 'Plxerror', 'NRSdist', 'NRSdisterror', 'NGC', 'IC', 'M', 'C', 'B',
    'Sh2', 'VdB', 'RCW', 'LDN', 'LBN', 'Cr', 'Mel', 'PGC', 'UGC', 'Ced', 'Arp', 'VV', 'PK', 'PN',
    'SNR', 'ACO', 'HCG', 'ESO', 'VdBH', 'DWB', 'Tr', 'St', 'Ru', 'VdB-Ha',
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
        fobj, sep='	', names=_COLUMN_NAMES, compression=compression,
        comment='#',
        usecols=['DSOID', 'RAdeg', 'DEdeg', 'Bmag', 'Vmag', 'M'],
        na_values=[''],
    )
    df.columns = (
        'dso_id', 'ra_degrees', 'dec_degrees', 'magnitudeB', 'magnitude',
        'messier_id',
    )
    df = df.assign(
        ra_hours = df['ra_degrees'] / 15.0,
        epoch_year = 2000.0,
    )
    df.loc[df['messier_id'] != 0.0, 'label'] = 'M' + df['messier_id'].astype(str)
    df = df[~df.messier_id.eq(0.0)]
    return df.set_index('dso_id')