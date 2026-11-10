"""examples/data/fetch.py — the public records the metocean examples (5 to 8) are drawn from, fetched at their pins.

Nothing here is committed to the repository: each file is downloaded once into examples/data/cache/ (ignored by git) and
refused unless its sha256 is the one pinned below.

  A.txt            dataset A of the environmental-contour benchmark (Haselsteiner et al., Ocean Engineering 236, 2021,
                   doi:10.1016/j.oceaneng.2021.109504): hourly Hs and Tz from an NDBC buoy, 1996–2005, at the benchmark
                   repository's commit a1561fe7. The repository carries no licence file; the hourly values are NDBC's
                   (US National Data Buoy Center, public domain), so they are fetched, never redistributed.
  44007h2015.txt.gz   NDBC buoy 44007, standard meteorological data for 2015 (wind and mean wave direction, Hs, periods),
                   from NDBC's historical archive. Public domain.

    python examples/data/fetch.py     fetch and verify both (the examples call fetch() themselves)
"""
import hashlib
import os
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, 'cache')
PINS = {
    'A.txt': ('https://raw.githubusercontent.com/ec-benchmark-organizers/ec-benchmark/a1561fe739b1b74e1c7da76e8fcf555e3316c8a2/datasets/A.txt',
              'c99b0191da514d94b3ca7df6bd4545463726238746945718a4baf80e28e97ccc'),
    '44007h2015.txt.gz': ('https://www.ndbc.noaa.gov/data/historical/stdmet/44007h2015.txt.gz',
                          '92a4982ada313fd9fefcc0a99e43b9c1391b47c267afeeeec5a29a8e2ae19b31'),
}


def fetch(name):
    """The local path of a pinned file, downloaded once and verified by sha256."""
    url, digest = PINS[name]
    path = os.path.join(CACHE, name)
    if not os.path.isfile(path):
        os.makedirs(CACHE, exist_ok=True)
        req = urllib.request.Request(url, headers={'User-Agent': 'leadline-examples/0.1'})
        with urllib.request.urlopen(req, timeout=120) as r:
            data = r.read()
        with open(path + '.part', 'wb') as f:
            f.write(data)
        os.replace(path + '.part', path)
    got = hashlib.sha256(open(path, 'rb').read()).hexdigest()
    if got != digest:
        raise RuntimeError('%s is not the pinned file (sha256 %s, pinned %s): delete it and fetch again' % (name, got[:16], digest[:16]))
    return path


def dataset_a():
    """Dataset A as three lists: times (YYYY-MM-DD-HH strings), Hs (m) and Tz (s), in file order."""
    t, hs, tz = [], [], []
    with open(fetch('A.txt'), encoding='utf-8') as fh:
        next(fh)
        for line in fh:
            a, b, c = (x.strip() for x in line.split(';'))
            t.append(a)
            hs.append(float(b))
            tz.append(float(c))
    return t, hs, tz


def ndbc_44007_2015():
    """NDBC 44007 in 2015: rows of (YYYY, MM, DD, hh, mm, WDIR, WSPD, WVHT, DPD, MWD); NDBC's missing values (99, 999)
    kept as they are, so the caller decides what a missing value is."""
    import gzip
    rows = []
    with gzip.open(fetch('44007h2015.txt.gz'), 'rt', encoding='ascii') as fh:
        for line in fh:
            if line.startswith('#'):
                continue
            v = line.split()
            rows.append((int(v[0]), int(v[1]), int(v[2]), int(v[3]), int(v[4]), int(v[5]), float(v[6]), float(v[8]), float(v[9]), int(v[11])))
    return rows


if __name__ == '__main__':
    for n in PINS:
        print('%-20s %s' % (n, fetch(n)))
