"""Choose a planting date by weighing dry spell risk against the cost of waiting.

loss(date) = risk(date) + wait_cost * (weeks after the first date)

risk is the share of years (0 to 1) with a dry spell of the chosen length in the
30 days after planting. wait_cost is what one extra week of waiting costs, as a
fraction of what a failed planting costs. It is a simple model, not a crop model.
The risk curve is smoothed over 7 days so that one odd year cannot pick the date.
"""

SMOOTH_HALF = 3     # average over the date and 3 dates either side


def smooth(values, half=SMOOTH_HALF):
    out = []
    for i in range(len(values)):
        lo, hi = max(0, i - half), min(len(values), i + half + 1)
        out.append(sum(values[lo:hi]) / (hi - lo))
    return out


def best_index(risk_share, wait_cost):
    """risk_share: list of risks (0 to 1), one per planting date, earliest first.
    Returns the index of the date with the lowest loss (earliest date wins a tie)."""
    s = smooth(risk_share)
    loss = [s[i] + wait_cost * i / 7 for i in range(len(s))]
    return min(range(len(loss)), key=lambda i: (round(loss[i], 12), i))


def robust_index(curves, wait_cost):
    """Choose one date that works reasonably well under every scenario (minimax regret).

    curves: a list of risk curves (each a list of risks 0 to 1, earliest date first), one per
    scenario, for example one per rainfall source and period.
    For each scenario, the regret of a date is how much more loss it gives than that scenario's own
    best date. The robust date has the smallest worst-case regret across scenarios.
    Returns (robust index, its worst-case regret, the own-best index of each scenario).
    """
    losses = []
    for risk in curves:
        s = smooth(risk)
        losses.append([s[i] + wait_cost * i / 7 for i in range(len(s))])
    n = len(losses[0])
    floor = [min(l) for l in losses]
    regret = [max(l[i] - f for l, f in zip(losses, floor)) for i in range(n)]
    idx = min(range(n), key=lambda i: (round(regret[i], 12), i))
    own = [min(range(n), key=lambda i: (round(l[i], 12), i)) for l in losses]
    return idx, regret[idx], own
