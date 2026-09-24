"""Pull the Allan deviations behind the DAI paper's Fig. 4c.

Source: C. Baynham et al., "A Prototype Differential Atom Interferometer for
Fundamental Physics", arXiv:2504.09158 -- data and code at
https://doi.org/10.5281/zenodo.19592552 (CC BY 4.0).

The paper's ``figures/Figure 4.ipynb`` computes the overlapping Allan
deviation of each run's differential phase, and the spread of the same over
its Monte Carlo runs at the standard quantum limit, then writes what it plots
to ``figures/Figure_4_data.xlsx``. This script copies that workbook's
``allan_deviation`` sheet, as it stands, to
``src/aionanim/data/dai_fringes/adev.csv``, which is what
``aionanim.plots.dai_fringes`` reads.

    .venv/bin/python data_scripts/process_dai_adev.py [data_analysis.zip]

With no argument the zip is downloaded from Zenodo into a temporary directory
and its checksum checked.
"""

import csv
import io
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

from process_dai_fringes import OUT_DIR, check_md5, fetch_zip

SOURCE = "data_analysis/figures/Figure_4_data.xlsx"
SHEET = "allan_deviation"

# Just enough of the xlsx format to read one sheet of numbers and inline
# strings, which is all the notebook's openpyxl writes.
NS = {
    "m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}
REL = "{%s}id" % NS["r"]


def read_sheet(workbook, name):
    """The sheet's rows, as lists of strings."""
    with zipfile.ZipFile(workbook) as book:
        sheets = ET.fromstring(book.read("xl/workbook.xml"))
        rels = ET.fromstring(book.read("xl/_rels/workbook.xml.rels"))
        rid = next(s.get(REL) for s in sheets.iter(f"{{{NS['m']}}}sheet") if s.get("name") == name)
        target = next(r.get("Target") for r in rels if r.get("Id") == rid)
        sheet = ET.fromstring(book.read("xl/" + target.lstrip("/").removeprefix("xl/")))
    rows = []
    for row in sheet.iter(f"{{{NS['m']}}}row"):
        cells = []
        for cell in row:
            if cell.get("t") == "inlineStr":
                cells.append(cell.find(".//m:t", NS).text)
            else:
                cells.append(cell.find("m:v", NS).text)
        rows.append(cells)
    return rows


def main():
    zip_path = Path(sys.argv[1]) if len(sys.argv) > 1 else fetch_zip()
    check_md5(zip_path)

    with zipfile.ZipFile(zip_path) as archive:
        rows = read_sheet(io.BytesIO(archive.read(SOURCE)), SHEET)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / "adev.csv"
    with open(out, "w", newline="") as f:
        f.write(
            "# Overlapping Allan deviation of the differential phase, low (LLN) "
            "and high (HLN) laser noise runs, against the standard quantum limit\n"
            "# From Baynham et al., arXiv:2504.09158, "
            "doi:10.5281/zenodo.19592552 (CC BY 4.0)\n"
            f"# Source file: {SOURCE}, sheet '{SHEET}', as written by "
            "'data_analysis/figures/Figure 4.ipynb'\n"
            "# Columns, all deviations in mrad:\n"
            "#   tau_s, averaging time; adev_{lln,hln}_mrad and their "
            "err_{neg,pos}, each run's Allan deviation and its error bar;\n"
            "#   mc_tau_s, averaging time of the Monte Carlo runs at the SQL; "
            "mc_{68,95}ci_{lower,upper}_mrad, the spread of their deviations;\n"
            "#   sql_scaling_mrad, the SQL per bin of shots falling as "
            "1/sqrt(tau) from the first mc_tau_s\n"
        )
        csv.writer(f).writerows(rows)
    print(f"wrote {out.relative_to(OUT_DIR.parent.parent)}: {len(rows) - 1} averaging times")


if __name__ == "__main__":
    main()
