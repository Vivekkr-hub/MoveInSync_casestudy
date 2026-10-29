"""Theme taxonomy for MoveInSync Play Store reviews (rule-based, for the weekly tracker).

The one-off analysis labelled every 1-3 star review from the last 12 months with an
LLM against the same codes; these rules are tuned to agree with those labels so the
weekly numbers stay comparable without needing an LLM. Agreement per theme is in
validation/regex_vs_llm.csv. A review can match several themes.
"""
import re

APP, OPS = "App", "Ops"

THEMES = {
    # ---------- App: product and engineering can fix ----------
    "stability": dict(
        label="Crashes, won't open, slow, breaks after update", owner=APP,
        pat=r"crash|not open|n'?t open|won'?t (open|launch|load)|unable to open|not opening|closes (immediately|on open|automatically)|"
            r"\bhang(s|ing)?\b|freez|\bstuck\b|\bslow|\blag(s|gy|ging)?\b|keeps? loading|not loading|n'?t load|blank|white screen|"
            r"stopped working|not responding|after (the |an |auto-?)?(latest |new |recent )?update|reinstall|re-install|"
            r"not (been )?(downloaded|installed) (from|through|via) (the )?play ?store|"
            r"no internet|check your (internet|connection)|server|request failed|something went wrong|\berrors?\b|"
            r"\bbug(s|gy)?\b|glitch|(app|it) (is )?not working|doesn'?t work|does not work|never works|not work(ing)? properly|"
            r"(app|it) (often |sometimes |always )?(goes |is )?down\b"),
    "tracking_tripinfo": dict(
        label="Live tracking, ETA and trip details", owner=APP,
        pat=r"track|gps|live location|(cab|driver'?s?|vehicle|bus|shuttle) location|\bmap\b|\bmaps\b|\beta\b|arrival time|zoom|"
            r"location (is |was )?(not )?(updat|accura|refresh|correct|wrong)|(wrong|incorrect|inaccurate) location|real ?-?time|"
            r"co-?passenger|co-?employee|co-?traveller|cab ?mates|fellow|(cab|vehicle|car) (no\b|number|details)|who all|"
            r"(pick ?up|drop|cab|shuttle) tim(e|ing)s? (is |are )?(shown |showing )?(not|wrong|incorrect|inaccurate|differ|chang)|"
            r"inaccurate timing|trip (details|info)|sequence"),
    "login_otp": dict(
        label="Login, OTP and forced re-login", owner=APP,
        # "login/logout" alone is shift vocabulary (pickup/drop trips), so it only counts with app context
        pat=r"(not|n'?t|no|never|didn'?t|unable to (get|receive)).{0,25}\botps?\b|\botps?\b.{0,30}(not |receiv|generat|com(e|ing)|sent|send|deliver|mail|sms|whatsapp|log ?in|sign)|"
            r"(log ?in|sign ?in).{0,40}\botp|(unable|not able|can'?t|cannot|could ?n'?t|failed) to (log ?in|sign ?in|sign ?up|register)|"
            r"(log ?in|sign ?in) (issue|problem|page|screen|again|every|fail|error)|"
            r"(every ?time|each time|repeatedly|again and again).{0,30}(log ?in|sign ?in)|"
            r"logs? (me |us |you )?out (automatically|every|frequently|after|on its own|randomly)|"
            r"(logged|logging|logs) (me |us )?out (after|every|automatically|frequently)|keeps? logging (me )?out|auto ?-?logout|"
            r"re-?login|sign ?up|validate (my )?identity|identity validation|verif(y|ication) code|not registered|session expir|"
            r"password|authenticat|\bsso\b"),
    "booking": dict(
        label="Booking, cancelling and schedule visibility", owner=APP,
        pat=r"\bbook(ing|ed|s)?\b(?! ?(app|application))|schedul|roster|\bcancel|reschedul|ad-?hoc|same[- ]day|waitlist|"
            r"\bdates?\b|calendar|month(ly)? view|week(ly)? view|next week|in advance|cut-?off|"
            r"amend|\bedit\b|modify|change (my |the )?(pickup|drop|address|location|shift|timing|destination)|(update|new) (my )?(address|location)"),
    "ux_redesign": dict(
        label="Confusing UI and disruptive redesigns", owner=APP,
        pat=r"new (ui|ux|update|version|design|features?|interface|app)|recent (update|enhancement|changes?)|"
            r"update (made|has made|makes) it|since (the )?(last|latest|new|recent) update|before the (update|upgrade)|"
            r"previous (version|ui)|old (version|ui|app)|confus|unintuitive|not user ?-?friendly|user ?interface|"
            r"\bui\b|\bux\b|font|2 step|two step|extra (step|click)|complicated|difficult to (use|navigate|find)|"
            r"hard to (use|find|navigate)|outdated|dark mode|no (option|way) to (call|chat|message|contact)"),
    "forced_prompts": dict(
        label="Forced ratings, repeated pop-ups, notification spam", owner=APP,
        pat=r"(rat(e|ing)|feedback|review|star).{0,60}(force|mandator|compuls|skip|every (ride|trip|time)|"
            r"each (ride|trip)|twice|can'?t (close|cancel|dismiss)|cannot (close|cancel|dismiss)|decline|defer|popup|pop-up|pop up|until)|"
            r"(force|mandator|compuls|skip|popup|pop-up|pop up).{0,40}(rat(e|ing)|feedback|review)|"
            r"pop ?-?ups?|banner|(terms|policy|polic(ies)|agreement|disclaimer).{0,50}(every|each|again|repeat)|i agree|"
            r"too (many|much) notification|notification(s)? (spam|every|all day)|excessive(ly)? notif|play ?store review|"
            r"(4|four) or (5|five) star|turn on notification|asking for feedback|feedback of the last ride|"
            r"rate (my |the )?(previous|last) (ride|trip)"),
    "boarding_checkin": dict(
        label="Boarding check-in (QR, OTP, seatbelt prompt)", owner=APP,
        pat=r"\bqr\b|scan|seat ?-?belt|seat buckle|check-?in|check ?-?out|boarding (otp|pin)|view otp"),
    "permissions": dict(
        label="Permissions, privacy and ads", owner=APP,
        pat=r"permission|microphone|\bmic\b|privacy|background location|location all the time|always allow|"
            r"camera access|contacts access|\bads\b|advertis"),
    # ---------- Ops: transport service, vendors, client policy ----------
    "support": dict(
        label="Helpdesk unreachable or unhelpful", owner=OPS,
        pat=r"support|help ?desk|help ?line|customer (care|service)|call (center|centre)|\bivr\b|"
            r"complain|no (one|body) (responds|answers|picks)|not (respond|reachable|picking)|escalat|"
            r"sahayta|sahaeta|saheta|toll ?free|grievance"),
    "driver_cab": dict(
        label="Late or missing cabs, driver behaviour", owner=OPS,
        pat=r"\bdrivers?\b(?! location)|\blate\b|delay|didn'?t (come|arrive|turn up|show)|did not (come|arrive)|"
            r"not (come|coming|arrived?)|never (came|come|arrive)|no cab|cab (didn|did not|never|not|is not)|not assign|"
            r"waiting for|waited|wait(ed)? for (\d+|an?|over|more)|\brash\b|over ?speed|rude|misbehav|behaviou?r|vehicle (condition|quality)|dirty|"
            r"cab (cancel|got cancel)|cancelled by|vendor|cabbies"),
    "routing": dict(
        label="Routing, pooling and pickup times", owner=OPS,
        pat=r"rout(e|ing)|club(bing|bed)?|\bpool(ing|ed)?\b|pick ?-?up (time|is) (too |very )?early|too early|very early|"
            r"early pick|long (route|way|time|travel)|longest|detour|nodal|pick ?-?up point|drop point|"
            r"travel time|hours? (in|inside) (the )?(cab|bus)|\d+(\.\d+)? ?h(ou)?rs? (daily|to reach|before)"),
    "no_show": dict(
        label="Unfair no-show marking", owner=OPS,
        pat=r"no ?-?show|noshow|marked absent|mark(ed)? me (as )?absent"),
    "safety": dict(
        label="Safety (SOS, women and night travel)", owner=OPS,
        pat=r"\bsafe(ty)?\b|unsafe|\bsos\b|emergency|women|female|\blady\b|ladies|late night|harass|danger"),
}

_COMPILED = {k: re.compile(v["pat"], re.I) for k, v in THEMES.items()}


def tag(text):
    """Return the list of theme keys matched by a review text."""
    if not isinstance(text, str):
        return []
    return [k for k, rx in _COMPILED.items() if rx.search(text)]
