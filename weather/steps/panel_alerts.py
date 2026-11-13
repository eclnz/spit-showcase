"""Panel e: on how many days each site had each alert, on the rows of panel d.

With two alerts, the first in name order runs left and the second right; with
any other number, each site has a bar for each alert.
"""

import argparse

from plot_style import INK, alert_colours, panel, rows, save, site_order
from panel_anomaly import BOTTOM, TOP


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("table")
    parser.add_argument("-o", dest="out", required=True)
    args = parser.parse_args()

    table = rows(args.table)
    pairs = sorted({(r["region"], r["site"]) for r in table})
    regions, sites = [p[0] for p in pairs], [p[1] for p in pairs]
    order = site_order(sites, regions)
    alerts = sorted({r["alert"] for r in table})
    palette = alert_colours(alerts)
    days = {(r["site"], r["alert"]): int(r["days"]) for r in table}
    counts = {a: [days.get((sites[i], a), 0) for i in order] for a in alerts}
    y = list(range(len(order)))
    limit = max(max(c) for c in counts.values()) or 1

    fig, ax = panel("e", left=0.12, bottom=BOTTOM, top=TOP, right=0.1)
    if len(alerts) == 2:
        left, right = alerts
        ax.barh(y, [-n for n in counts[left]], color=palette[left], height=0.7)
        ax.barh(y, counts[right], color=palette[right], height=0.7)
        ax.axvline(0, color=INK, linewidth=0.6)
        ax.set_xlim(-limit * 1.1, limit * 1.1)
        for offset, name, ha in ((-4, left, "right"), (4, right, "left")):
            ax.annotate(name, (0, 1), xycoords=("data", "axes fraction"), xytext=(offset, 2),
                        textcoords="offset points", ha=ha, va="bottom", fontsize=6, color=palette[name],
                        fontweight="bold")
    else:
        height = 0.8 / len(alerts)
        for k, name in enumerate(alerts):
            ax.barh([row - 0.4 + height * (k + 0.5) for row in y], counts[name], color=palette[name],
                    height=height, label=name)
        ax.set_xlim(0, limit * 1.1)
        ax.legend(loc="lower right", fontsize=5.5, bbox_to_anchor=(1, 1), ncol=len(alerts), handlelength=1)
    ax.set_ylim(len(order) - 0.5, -0.5)
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ax.xaxis.set_major_formatter(lambda value, _: f"{abs(value):g}")
    ax.set_xlabel("alert days")
    save(fig, args.out)


if __name__ == "__main__":
    main()
