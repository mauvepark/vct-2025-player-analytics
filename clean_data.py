"""Clean the VCT 2025 player stats export from Kaggle.

Usage: python clean_data.py players_stats.csv data/vct2025_players_clean.csv

- Drops "All Stages" rollup rows and multi-agent total rows (one row = player x agent x match)
- Converts percentage strings to decimals
- Decodes clutch records that were auto-converted to dates ("03-Jan" -> won 1, played 3)
"""
import sys, re, pandas as pd
src, out = sys.argv[1], sys.argv[2]
d = pd.read_csv(src)
n0 = len(d)
d = d[d["Stage"] != "All Stages"]
d = d[~d["Agents"].str.contains(",", na=False)].copy()

d = d.rename(columns={"Kill, Assist, Trade, Survive %": "KAST %"})
for c in ["KAST %", "Headshot %", "Clutch Success %"]:
    d[c] = pd.to_numeric(d[c].astype(str).str.rstrip("%"), errors="coerce") / 100

MON = {m: i+1 for i, m in enumerate("Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split())}
def decode(v):
    if pd.isna(v): return (None, None)
    v = str(v)
    if "/" in v:
        a, b = v.split("/"); return (int(a), int(b))
    m = re.fullmatch(r"(\d+)-([A-Za-z]{3})", v)
    return (MON[m.group(2)], int(m.group(1)))
wp = d["Clutches (won/played)"].map(decode)
pos = d.columns.get_loc("Clutches (won/played)")
d.insert(pos, "Clutches Won", pd.array([w for w, _ in wp], dtype="Int64"))
d.insert(pos+1, "Clutches Played", pd.array([p for _, p in wp], dtype="Int64"))
d = d.drop(columns="Clutches (won/played)")

# sanity: decoded clutches vs reported clutch %
chk = d.dropna(subset=["Clutch Success %"])
chk = chk[chk["Clutches Played"] > 0]
calc = (chk["Clutches Won"] / chk["Clutches Played"]).astype(float).round(2)
mism = (abs(calc - chk["Clutch Success %"]) > 0.011).sum()
assert (d["Clutches Won"].fillna(0) <= d["Clutches Played"].fillna(0)).all()
d.to_csv(out, index=False)
print(f"rows {n0} -> {len(d)}; clutch check: {len(chk)-mism}/{len(chk)} match reported %")
