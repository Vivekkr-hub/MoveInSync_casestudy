You are labeling Google Play reviews of MoveInSync, an employee office-commute app (India mainly, also Philippines, South Africa and others). Employees book cabs or shuttles for their shift in the app, track the cab live, board with OTP or QR check-in (sometimes a seatbelt confirmation), and get dropped. In this domain "login" and "logout" often mean the shift pickup trip and the drop trip (e.g. "logout cab", "login time"), not signing into the app. "Nodal point" = a shared pickup spot. "Clubbing" = pooling employees into one cab. "Roster" = schedule.

For EACH review line (format: `rXXXX [N star] text`), assign one or more theme codes and a short issue phrase.

Theme codes (use the code exactly):
- login_otp: can't sign in to the app, OTP for app login not received, forced re-login / logged out of the app, identity validation, registration, SSO problems
- stability: app crashes, won't open, slow, hangs, blank screens, error messages, bugs, broke after an update, "app not installed from Play Store" errors
- tracking_tripinfo: live cab tracking / GPS / map / ETA inaccurate, map zoom behaviour, trip details missing or wrong in the app (cab number, co-passengers, pickup time shown, sequence)
- boarding_checkin: QR scan, boarding OTP, seatbelt confirmation or check-in/check-out flow problems
- forced_prompts: mandatory or unskippable ride rating/feedback, repeated pop-ups or banners, terms shown on every launch, notification spam, Play Store review nags, rating options restricted
- booking: booking, cancelling, rescheduling, schedule/roster visibility, wrong dates booked, booking windows/cut-offs, changing address or pickup point in the app, waitlist
- ux_redesign: confusing UI, a recent redesign made things worse, extra steps, unreadable fonts, missing feature requests about the interface
- permissions: excessive permissions (mic, location, notifications), privacy, ads
- routing: bad routes, pooling/clubbing, long travel time, pickup scheduled too early, nodal/pickup point placement
- driver_cab: specific cab problems: cab late or didn't come, cab cancelled, cab not assigned, driver behaviour, rash driving, vehicle condition
- no_show: wrongly marked as no-show
- support: helpdesk / customer support unreachable or unhelpful
- safety: safety concerns, SOS, women or night safety
- generic_app: only a vague complaint about the app with no specific issue ("worst app", "waste")
- generic_service: only a vague complaint about the transport service with no specific issue ("worst service")
- positive_or_other: praise, neutral, or off-topic content with no complaint

Be strict: tag only what is actually complained about. Use generic_* only when no specific code applies.

issue: a short phrase (max 8 words) naming the single most specific problem, in plain words, e.g. "OTP not received on phone or email", "forced rating popup blocks OTP screen", "cab location not updating". Use "" for generic or positive reviews.

Output: write JSON to the output path you are given, shaped as {"r0001": {"t": ["login_otp"], "i": "OTP not received on phone or email"}, ...} with one key per review in your chunk. Label independently from the text alone; do not read any other files in /home/claude/msync. When done reply with "done N" where N is the number of keys written.
