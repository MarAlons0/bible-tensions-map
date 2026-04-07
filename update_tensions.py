"""
One-time script to update seed_data.json:
  - Rename T05
  - Replace T09 / T19 / T20 with new tensions + new OT scores
Run: python update_tensions.py
"""
import json

# ---------------------------------------------------------------------------
# New tension definitions
# ---------------------------------------------------------------------------
NEW_TENSIONS = {
    'T05': {
        'id': 'T05',
        'name': 'Ethical imperative vs. Ritual/Institutional observance',
        'pole_a': 'Ethical/prophetic priority',
        'pole_b': 'Ritual/Institutional observance',
    },
    'T09': {
        'id': 'T09',
        'name': 'Faith vs. Works',
        'pole_a': 'Faith/grace',
        'pole_b': 'Works/deeds',
    },
    'T19': {
        'id': 'T19',
        'name': 'Realized vs. Apocalyptic eschatology',
        'pole_a': 'Realized/present',
        'pole_b': 'Apocalyptic/future',
    },
    'T20': {
        'id': 'T20',
        'name': 'Suffering as redemptive vs. as punishment',
        'pole_a': 'Redemptive/meaningful',
        'pole_b': 'Divine punishment/retribution',
    },
}

# ---------------------------------------------------------------------------
# New scores for T09, T19, T20 across all 38 OT books
# ---------------------------------------------------------------------------
NEW_SCORES = {
    # T09 — Faith vs. Works  (Pole A=-5 faith/grace, Pole B=+5 works/deeds)
    'T09': {
        'GEN': (0,  "Abraham's faith counted as righteousness (15:6) but covenant requires circumcision; both poles present"),
        'EXO': (3,  "Sinai covenant is works-based; blessings contingent on obedience; Passover grace tempered by law"),
        'LEV': (5,  "Entirely prescriptive ritual requirements; holiness achieved through specific deeds"),
        'NUM': (3,  "Wilderness failures punished; success tied to following divine commands exactly"),
        'DEU': (4,  "Blessings and curses explicitly tied to obedience (28-30); covenant is fundamentally works-based"),
        'JOS': (3,  "Military success directly tied to obedience; Achan's sin causes collective defeat"),
        'JDG': (3,  "Deuteronomistic cycle: sin→punishment, repentance→deliverance; salvation conditional on behavior"),
        'RUT': (1,  "Hesed (loyal love) drives the narrative; works of loyalty matter but grace visible in Boaz"),
        '1SA': (1,  "Obedience matters (Saul's failure) but David chosen by grace despite flaws"),
        '2SA': (0,  "David's unconditional covenant (7:12-16) balanced against consequences for his sin"),
        '1KI': (3,  "Kings evaluated by obedience to Torah; outcomes determined by faithfulness"),
        '2KI': (3,  "Israel's destruction attributed to accumulated covenant violations; strongly works-based"),
        '1CH': (2,  "Proper worship arrangements matter; cult establishes works-based framework for blessing"),
        '2CH': (3,  "Explicit retributive theology: kings who seek God prosper, those who don't suffer"),
        'EZR': (4,  "Covenant renewal requires separation from foreign wives; purity through deeds essential"),
        'NEH': (4,  "Community covenant renewed through specific behavioral commitments"),
        'EST': (None, "No explicit theological framework regarding faith or works"),
        'JOB': (-3, "Directly challenges the works/reward system; Job's righteousness doesn't prevent suffering; God is not transactional"),
        'PSA': (-1, "Trust-language dominates lament psalms; Torah psalms (1, 119) emphasize works; mixed but faith-language slightly dominant"),
        'PRO': (4,  "Strong works theology: wisdom (right action) leads to flourishing; consequences follow choices"),
        'ECC': (-2, "Undermines works theology: righteous and wicked face the same fate; trust God despite meaninglessness"),
        'SNG': (None, "Not applicable; love poetry with no soteriological framework"),
        'ISA': (-2, "Prophetic critique of empty ritual; trust over political alliances; new covenant through grace (40-55)"),
        'JER': (-2, "New covenant written on hearts, not tablets; interior transformation over external compliance"),
        'LAM': (2,  "Jerusalem's suffering implicitly tied to covenant violation; works-theology assumed"),
        'EZK': (1,  "Individual responsibility for deeds (18) but promise of new heart/spirit (36) introduces grace"),
        'DAN': (-2, "Daniel and companions trust God regardless of outcome; faithfulness under persecution is not transactional"),
        'HOS': (-2, "'I desire steadfast love, not sacrifice' (6:6); relationship/trust over ritual performance"),
        'JOL': (1,  "'Return to me with all your heart' — behavioral repentance required but God's mercy is the emphasis"),
        'AMO': (0,  "Ethical demands (justice = works) but also critique of ritual without heart; balanced"),
        'OBA': (2,  "Edom judged for their deeds against Jacob; works-based retribution"),
        'JON': (-2, "God's mercy extends to Nineveh far beyond what Jonah thinks earned; grace is the point"),
        'MIC': (0,  "'Do justice, love kindness, walk humbly' (6:8) — works and trust equally emphasized"),
        'NAM': (2,  "Nineveh destroyed for accumulated wickedness; deeds determine fate"),
        'HAB': (-4, "'The righteous shall live by his faith' (2:4) — most explicit faith-over-works statement in OT"),
        'ZEP': (2,  "Judgment based on behavior; remnant defined by seeking righteousness"),
        'HAG': (3,  "Economic hardship attributed to failure to rebuild temple; obedience brings blessing"),
        'ZEC': (0,  "Apocalyptic grace (Joshua cleansed by God) alongside covenant requirements; balanced"),
    },

    # T19 — Realized vs. Apocalyptic eschatology  (Pole A=-5 realized, Pole B=+5 apocalyptic)
    'T19': {
        'GEN': (None, "No eschatological framework; primordial narrative, not eschatological"),
        'EXO': (None, "Exodus is historical liberation, not eschatological vision"),
        'LEV': (None, "Cultic manual; no eschatological content"),
        'NUM': (None, "Wilderness narrative; no significant eschatological vision"),
        'DEU': (1,   "Future blessing/curse framework; some forward-looking promises but not apocalyptic"),
        'JOS': (-2,  "Land promise being fulfilled now; the divine gift is received in the present — realized"),
        'JDG': (None, "Cyclical history; no eschatological perspective"),
        'RUT': (None, "No eschatological content"),
        '1SA': (None, "No eschatological content"),
        '2SA': (1,   "Davidic covenant points to an eternal future dynasty; mild forward orientation"),
        '1KI': (None, "No eschatological content"),
        '2KI': (None, "Exile as historical event; no eschatological framework"),
        '1CH': (None, "No significant eschatological content"),
        '2CH': (None, "No significant eschatological content"),
        'EZR': (-1,  "Return from exile as fulfillment of prophecy; restoration happening now — realized"),
        'NEH': (-1,  "Restoration in progress in the present; realized"),
        'EST': (None, "No eschatological content"),
        'JOB': (None, "Wisdom meditation on suffering; no eschatological framework"),
        'PSA': (1,   "Enthronement psalms assert God reigns now; but eschatological hope also present; mixed"),
        'PRO': (None, "Wisdom literature; no eschatological framework"),
        'ECC': (None, "Present-focused skepticism; no eschatological content"),
        'SNG': (None, "Not applicable"),
        'ISA': (3,   "New creation, new exodus, Servant Songs — all point to future transformation; strongly future-oriented"),
        'JER': (2,   "New covenant is a future promise; 'days are coming' repeated; restoration ahead"),
        'LAM': (2,   "Hope for future restoration after present devastation"),
        'EZK': (3,   "Valley of dry bones (37), future temple vision (40-48), restoration — all future-oriented"),
        'DAN': (5,   "Paradigmatic apocalyptic: four kingdoms, Son of Man, resurrection, end of ages — fully eschatological"),
        'HOS': (2,   "Future restoration promised: 'I will betroth you to me forever' (2:19)"),
        'JOL': (4,   "Day of the Lord, eschatological Spirit-outpouring, cosmic signs — strongly apocalyptic"),
        'AMO': (3,   "Day of the Lord (5:18-20), future judgment and restoration of Davidic tent"),
        'OBA': (3,   "Day of the Lord against the nations; Zion's future dominion"),
        'JON': (None, "No eschatological content; God's mercy is immediate and particular"),
        'MIC': (2,   "Future peace (swords into plowshares 4:3), messianic ruler from Bethlehem (5:2)"),
        'NAM': (2,   "Future fall of Nineveh as divine judgment; forward-looking"),
        'HAB': (3,   "'The earth will be filled with knowledge of God' (2:14); patient waiting for future vindication"),
        'ZEP': (3,   "Day of the Lord (1:14-18), future restoration of remnant and nations"),
        'HAG': (2,   "Future glory of rebuilt temple will surpass Solomon's; messianic Zerubbabel hope"),
        'ZEC': (4,   "Elaborate apocalyptic visions; future messianic king, battle of nations, living waters"),
    },

    # T20 — Suffering as redemptive vs. as punishment  (Pole A=-5 redemptive/meaningful, Pole B=+5 retributive)
    'T20': {
        'GEN': (1,   "Suffering generally tied to sin (Eden, flood); Joseph's suffering leads to redemption — partially meaningful"),
        'EXO': (2,   "Egypt's plagues = divine punishment; Israel's wilderness hardships = discipline for disobedience"),
        'LEV': (None, "Prescriptive text; no narrative suffering"),
        'NUM': (3,   "Plague, fire, snake-bites consistently follow rebellion; suffering as punishment is explicit"),
        'DEU': (4,   "Curses for disobedience catalogued in detail (28); suffering as direct divine retribution"),
        'JOS': (2,   "Achan's sin causes collective defeat; suffering traced to specific transgression"),
        'JDG': (3,   "Oppression consistently follows apostasy in the Deuteronomistic cycle"),
        'RUT': (0,   "Naomi's suffering not explained as punishment; mysterious; loyalty overcomes it"),
        '1SA': (1,   "Saul's decline = punishment; David's suffering is more complex — not simply retributive"),
        '2SA': (2,   "David's troubles after Bathsheba-Uriah = explicit divine punishment (12:11)"),
        '1KI': (2,   "Kingdom division = result of Solomon's apostasy; suffering tied to sin"),
        '2KI': (3,   "Fall of both kingdoms attributed to cumulative covenant violation"),
        '1CH': (1,   "Uzzah's death = punishment for improper approach; less suffering focus overall"),
        '2CH': (3,   "Most explicit retributive theology in Chronicles; outcomes track obedience throughout"),
        'EZR': (1,   "Exile framed as punishment; focus now on restoration through obedience"),
        'NEH': (1,   "Historical review frames exile as punishment; community moves forward through covenant renewal"),
        'EST': (0,   "Jewish suffering under Haman is political, not framed as divine punishment; deliverance is providential"),
        'JOB': (-5,  "The entire book argues against retributive theology; friends' view (suffering=sin) is explicitly rejected by God"),
        'PSA': (-1,  "Lament psalms frequently protest undeserved suffering; some psalms assume punishment framework; mixed"),
        'PRO': (3,   "Strong retributive framework: righteous prosper, wicked suffer — suffering signals foolishness or sin"),
        'ECC': (-2,  "Explicitly notes righteous suffer while wicked prosper; retribution theology is undermined throughout"),
        'SNG': (None, "Not applicable"),
        'ISA': (-3,  "Servant Songs introduce vicarious/redemptive suffering (52:13-53:12); suffering as meaningful sacrifice"),
        'JER': (-1,  "Jeremiah's suffering is vocational, not punitive; he is righteous but suffers for his prophetic call"),
        'LAM': (0,   "Both poles simultaneously: punishment (1:5,18) AND lament at God's silence (3:8); neither resolves"),
        'EZK': (2,   "Individual responsibility for deeds (18); suffering follows sin; Ezekiel's own suffering is vocational"),
        'DAN': (-3,  "Faithful companions suffer under persecution; their suffering is meaningful resistance vindicated by God"),
        'HOS': (0,   "Israel's suffering = punishment but God's response is overwhelming love; judgment serves restoration"),
        'JOL': (2,   "Locust plague as divine punishment; repentance leads to restoration"),
        'AMO': (3,   "Coming judgment as punishment for injustice and idolatry; suffering is deserved"),
        'OBA': (3,   "Edom's coming devastation = punishment for violence against Jacob"),
        'JON': (-1,  "Jonah's fish experience is corrective/transformative; Nineveh's threatened suffering averted by repentance"),
        'MIC': (1,   "Coming judgment = punishment; but God's ultimate purpose is restoration"),
        'NAM': (3,   "Nineveh's total destruction = divine punishment for cruelty; no redemption offered"),
        'HAB': (-2,  "Habakkuk protests undeserved suffering of the righteous; 'righteous live by faith' challenges retribution"),
        'ZEP': (2,   "Day of the Lord as punishment for wickedness; remnant theology"),
        'HAG': (1,   "Economic hardship = discipline for neglecting temple; corrective rather than purely punitive"),
        'ZEC': (0,   "Refinement through hardship (13:9); suffering serves purification; balanced"),
    },
}


def update():
    with open('seed_data.json') as f:
        data = json.load(f)

    # Update tension definitions
    for t in data['tensions']:
        if t['id'] in NEW_TENSIONS:
            t.update(NEW_TENSIONS[t['id']])
    print("Updated tension definitions for T05, T09, T19, T20")

    # Update book scores for T09, T19, T20
    updated_books = 0
    for book_id, book in data['books'].items():
        changed = False
        for tension_id, scores in NEW_SCORES.items():
            if book_id in scores:
                score, note = scores[book_id]
                book['tensions'][tension_id] = {'score': score, 'note': note} if score is not None else None
                changed = True
        if changed:
            updated_books += 1

    print(f"Updated T09/T19/T20 scores for {updated_books} books")

    with open('seed_data.json', 'w') as f:
        json.dump(data, f, ensure_ascii=False)
    print("seed_data.json saved")


if __name__ == '__main__':
    update()
