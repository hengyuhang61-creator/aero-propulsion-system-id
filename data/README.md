# Input provenance and acquisition

The original NASA files are **not redistributed** here. No dataset redistribution license is inferred from public download availability. Obtain files yourself from the official [Sajben Study #2 page](https://www.grc.nasa.gov/WWW/wind/valid/transdif/transdif02/transdif02.html), Table 2, pressure files:

```bash
curl -fL -o sajwpres.data https://www.grc.nasa.gov/WWW/wind/valid/transdif/transdif02/sajwpres.data
curl -fL -o sajspres.data https://www.grc.nasa.gov/WWW/wind/valid/transdif/transdif02/sajspres.data
```

These are reader instructions; the takeover audit reused frozen local files and did not download new data. Preserve bytes and line endings before hashing. On Windows, use `curl.exe` if `curl` is a shell alias. Do not bypass access restrictions if the official URLs become unavailable.

| File | SHA-256 of frozen bytes |
|---|---|
| sajwpres.data | ae2541b66d71e7ede514d3572965b00d1ca2510747ba4b8b2fd92690f4f1b167 |
| sajspres.data | 5d58b25b6d4da51ff3a79a8b38529474df5490b5b5cb54c3abef0f6947f7f217 |

`--verify-frozen` refuses changed hashes. A byte mismatch may be line-ending conversion or source revision; investigate it before making an equivalence claim. Do not change the expected hash merely to make the check pass.

Columns are bottom x/H, bottom p/p0, top x/H, top p/p0. H is throat height, p is static wall pressure, p0 is inlet total pressure. Each file has 37 active numeric rows; the repeated last bottom station is omitted once, leaving 36 bottom and 37 top stations. Commented downstream-extension rows are not data in this protocol.

NASA's main geometry page gives H=0.14435 feet (approximately 44 mm). Study #2 uses a feet grid, while other archive geometry files use inches. Study #2's condition table says inlet total pressure 19.50 psia, but the main page and retained WIND input give 19.58 psia; the input files state experimental T0=300 K whereas the WIND condition is 500 R=277.7778 K. These discrepancies are retained. R08 uses the published dimensionless measurements and nominal ratios; it does not resolve absolute-condition uncertainty. R03/R09/R10 use the frozen 19.58 psia / 500 R numerical condition.

The Study #2 prose says downstream pressure was increased for the strong case, but its numeric table changes 16.05 to 14.10 psia and its nominal ratio changes 0.82 to 0.72. Follow the numeric definitions and record this source inconsistency.

No time axis, commanded excitation history, measurement-error bars, or statistical replicates are provided by these two files. The expected-summary JSON is a derived numerical result, not a copy of the raw curves.
