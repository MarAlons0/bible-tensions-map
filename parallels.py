"""
Curated parallel passages: places where the Bible tells the same thing twice
(or more) and the versions disagree. Each entry poses the discrepancy as a
question and says, in one line per passage, what that version claims.

Passage references use full book names (as bible-api.com expects); several
ranges in one passage are separated by "; ". After editing, run
fetch_bible_texts.py to refresh seed_data_bible_texts.json.
"""

GROUPS = [
    'Torah',
    'Joshua–Kings and Chronicles',
    'Exile and return',
    'Gospels',
    'Acts and letters',
]

PARALLELS = [
    # --- Torah ---------------------------------------------------------------
    {
        'id': 'creation-order', 'group': 'Torah',
        'question': 'In what order were plants, animals and humans created?',
        'passages': [
            ('Genesis 1:11-31', 'Plants (day 3), then animals (days 5–6), then man and woman together, last (1:27).'),
            ('Genesis 2:4-23', 'The man first (2:7), then the garden\'s plants (2:8–9), then the animals (2:19), then the woman (2:22).'),
        ],
        'note': 'Two creation accounts from different sources (Priestly and non-Priestly) placed side by side.',
    },
    {
        'id': 'ark-animals', 'group': 'Torah',
        'question': 'How many of each animal went into the ark?',
        'passages': [
            ('Genesis 6:19-20', 'Two of every kind, male and female.'),
            ('Genesis 7:2-3', 'Seven pairs of every clean animal and bird, one pair of the unclean.'),
        ],
        'note': 'The extra clean animals are needed for Noah\'s sacrifice (8:20) — a detail of one source, not the other.',
    },
    {
        'id': 'wife-sister', 'group': 'Torah',
        'question': 'Who passed his wife off as his sister, and to whom?',
        'passages': [
            ('Genesis 12:10-20', 'Abram, with Sarai, to Pharaoh in Egypt.'),
            ('Genesis 20:1-18', 'Abraham, with Sarah, to Abimelech king of Gerar.'),
            ('Genesis 26:1-11', 'Isaac, with Rebekah, to the same Abimelech of Gerar.'),
        ],
        'note': 'One folk motif told three times; in ch. 20 Sarah is about 90 (17:17) yet taken for her beauty.',
    },
    {
        'id': 'hagar', 'group': 'Torah',
        'question': 'How did Hagar and Ishmael leave Abraham\'s household?',
        'passages': [
            ('Genesis 16:1-16', 'Pregnant Hagar runs away from Sarai; an angel sends her back.'),
            ('Genesis 21:8-21', 'Abraham expels her with Ishmael, who is treated as a small child she lays under a bush (21:15) — though by 17:25 and 21:5–8 he would be about sixteen.'),
        ],
        'note': 'A doublet whose second telling ignores the ages set by the first.',
    },
    {
        'id': 'israel-named', 'group': 'Torah',
        'question': 'Where and how was Jacob renamed Israel?',
        'passages': [
            ('Genesis 32:22-32', 'At Peniel, after wrestling through the night with a "man".'),
            ('Genesis 35:9-15', 'At Bethel, by God speaking, as if for the first time.'),
        ],
        'note': 'Two traditions explaining the same name, tied to two different sanctuaries.',
    },
    {
        'id': 'father-in-law', 'group': 'Torah',
        'question': 'What was the name of Moses\' father-in-law?',
        'passages': [
            ('Exodus 2:16-21', 'Reuel.'),
            ('Exodus 3:1', 'Jethro.'),
            ('Numbers 10:29; Judges 4:11', 'Hobab — son of Reuel in Numbers, Moses\' father-in-law in Judges.'),
        ],
        'note': 'Different sources preserved different names for the Midianite priest.',
    },
    {
        'id': 'sabbath', 'group': 'Torah',
        'question': 'Why keep the Sabbath?',
        'passages': [
            ('Exodus 20:8-11', 'Because God rested on the seventh day of creation.'),
            ('Deuteronomy 5:12-15', 'Because you were slaves in Egypt and God brought you out.'),
        ],
        'note': 'The same commandment with two different rationales — creation versus redemption.',
    },
    {
        'id': 'rock-water', 'group': 'Torah',
        'question': 'Was striking the rock for water obedience — or the sin that barred Moses from the land?',
        'passages': [
            ('Exodus 17:1-7', 'At Horeb, God tells Moses to strike the rock; he does, and water flows. Named Massah and Meribah.'),
            ('Numbers 20:1-13', 'At Kadesh, God tells him to speak to the rock; he strikes it twice and is condemned to die outside the land. Also named Meribah.'),
        ],
        'note': 'Numbers retells the Meribah story to explain why Moses never entered Canaan.',
    },
    {
        'id': 'aaron-death', 'group': 'Torah',
        'question': 'Where did Aaron die?',
        'passages': [
            ('Numbers 20:22-29; Numbers 33:38', 'On Mount Hor.'),
            ('Deuteronomy 10:6', 'At Moserah.'),
        ],
        'note': 'Numbers 33:30–31 places Moserah several stages before Mount Hor.',
    },

    # --- Joshua–Kings and Chronicles -------------------------------------------
    {
        'id': 'achsah', 'group': 'Joshua–Kings and Chronicles',
        'question': 'When was Hebron taken and Achsah given to Othniel — and by whom?',
        'passages': [
            ('Joshua 15:13-19', 'During Joshua\'s lifetime; Caleb drives out the three sons of Anak.'),
            ('Judges 1:10-15', 'After Joshua\'s death (1:1); "Judah" defeats them — then the same story, nearly word for word.'),
        ],
        'note': 'Judges 1 reuses Joshua\'s material while presenting the conquest as unfinished.',
    },
    {
        'id': 'david-meets-saul', 'group': 'Joshua–Kings and Chronicles',
        'question': 'How did Saul come to know David?',
        'passages': [
            ('1 Samuel 16:14-23', 'David is brought to court as a musician; Saul loves him and makes him his armor-bearer.'),
            ('1 Samuel 17:55-58', 'After Goliath, Saul asks "whose son is this young man?" — as if he had never met him.'),
        ],
        'note': 'Two independent stories of David\'s rise combined without reconciling them.',
    },
    {
        'id': 'goliath', 'group': 'Joshua–Kings and Chronicles',
        'question': 'Who killed Goliath?',
        'passages': [
            ('1 Samuel 17:48-51', 'David, with a sling stone and Goliath\'s own sword.'),
            ('2 Samuel 21:19', 'Elhanan of Bethlehem killed "Goliath the Gittite".'),
            ('1 Chronicles 20:5', 'Elhanan killed Lahmi, the brother of Goliath.'),
        ],
        'note': 'Chronicles appears to harmonize: the giant Elhanan killed becomes Goliath\'s brother.',
    },
    {
        'id': 'saul-death', 'group': 'Joshua–Kings and Chronicles',
        'question': 'How did Saul die, and why?',
        'passages': [
            ('1 Samuel 31:1-6', 'He falls on his own sword after his armor-bearer refuses to kill him.'),
            ('2 Samuel 1:1-16', 'An Amalekite says he killed Saul at Saul\'s request; David has him executed.'),
            ('1 Chronicles 10:1-14', 'Suicide as in Samuel — then: "the LORD put him to death" for unfaithfulness and consulting a medium.'),
        ],
        'note': 'Chronicles adds the theological verdict; the Amalekite\'s claim contradicts 1 Samuel 31 outright.',
    },
    {
        'id': 'absalom-sons', 'group': 'Joshua–Kings and Chronicles',
        'question': 'Did Absalom have sons?',
        'passages': [
            ('2 Samuel 14:27', 'Three sons and a daughter.'),
            ('2 Samuel 18:18', '"I have no son to keep my name in remembrance."'),
        ],
        'note': 'Within the same book; harmonizers assume the sons died young.',
    },
    {
        'id': 'census', 'group': 'Joshua–Kings and Chronicles',
        'question': 'Who incited David\'s census — and what did the census and the altar site come to?',
        'passages': [
            ('2 Samuel 24:1-25', 'The LORD, angry with Israel. 800,000 + 500,000 fighting men; the threshing floor costs 50 shekels of silver.'),
            ('1 Chronicles 21:1-30', 'Satan. 1,100,000 + 470,000; the site costs 600 shekels of gold.'),
        ],
        'note': 'The Chronicler replaces God with an adversary and enlarges the price for the future Temple site.',
    },
    {
        'id': 'solomon-stalls', 'group': 'Joshua–Kings and Chronicles',
        'question': 'How many stalls for horses did Solomon have?',
        'passages': [
            ('1 Kings 4:26', '40,000.'),
            ('2 Chronicles 9:25', '4,000.'),
        ],
        'note': 'Probably a copying error in one tradition (2 Chr 1:14 and 1 Kgs 10:26 give 1,400 chariots).',
    },
    {
        'id': 'solomon-end', 'group': 'Joshua–Kings and Chronicles',
        'question': 'How did Solomon\'s reign end?',
        'passages': [
            ('1 Kings 11:1-13; 1 Kings 11:41-43', 'His foreign wives turn his heart to other gods, and God tears the kingdom from his son.'),
            ('2 Chronicles 9:29-31', 'He reigns forty years and dies. No wives, no apostasy.'),
        ],
        'note': 'Chronicles idealizes David and Solomon by omission.',
    },
    {
        'id': 'ahaziah-age', 'group': 'Joshua–Kings and Chronicles',
        'question': 'How old was Ahaziah when he began to reign?',
        'passages': [
            ('2 Kings 8:26', 'Twenty-two.'),
            ('2 Chronicles 22:2', 'Forty-two — which would make him older than his father, who died at forty (21:20).'),
        ],
        'note': 'A textual error, corrected in some ancient versions.',
    },
    {
        'id': 'hezekiah-tribute', 'group': 'Joshua–Kings and Chronicles',
        'question': 'Did Hezekiah buy off Sennacherib?',
        'passages': [
            ('2 Kings 18:13-16', 'Yes: he pays 300 talents of silver and 30 of gold, stripping the Temple doors.'),
            ('Isaiah 36:1-3', 'The siege begins with no payment mentioned.'),
            ('2 Chronicles 32:1-8', 'No payment; Hezekiah fortifies the city and trusts God.'),
        ],
        'note': 'The humiliating tribute, also recorded in Sennacherib\'s own annals, survives only in Kings.',
    },
    {
        'id': 'manasseh', 'group': 'Joshua–Kings and Chronicles',
        'question': 'Did Manasseh, the worst king of Judah, repent?',
        'passages': [
            ('2 Kings 21:1-18', 'No. His sins are the reason Judah will be destroyed (see also 23:26; 24:3).'),
            ('2 Chronicles 33:1-20', 'Yes. Taken to Babylon in chains, he repents and is restored, then reforms worship.'),
            ('Prayer of Manasseh 1:1-15', 'Supplies the repentance prayer that Chronicles only mentions.'),
        ],
        'note': 'Chronicles needs a repentance to explain his 55-year reign under its strict reward theology.',
    },
    {
        'id': 'josiah-death', 'group': 'Joshua–Kings and Chronicles',
        'question': 'How did Josiah die?',
        'passages': [
            ('2 Kings 23:28-30', 'Pharaoh Neco kills him at Megiddo when they meet.'),
            ('2 Chronicles 35:20-24', 'Neco warns him that God sent him; Josiah disguises himself, is shot by archers, and dies in Jerusalem.'),
        ],
        'note': 'Kings\' ideal reformer dies for nothing; Chronicles makes his death his own disobedience.',
    },
    {
        'id': 'jehoiachin-age', 'group': 'Joshua–Kings and Chronicles',
        'question': 'How old was Jehoiachin when he began to reign?',
        'passages': [
            ('2 Kings 24:8', 'Eighteen; he reigned three months.'),
            ('2 Chronicles 36:9', 'Eight; he reigned three months and ten days.'),
        ],
        'note': 'A dropped digit in one tradition.',
    },

    # --- Exile and return ------------------------------------------------------
    {
        'id': 'returnees', 'group': 'Exile and return',
        'question': 'How many returned from exile?',
        'passages': [
            ('Ezra 2:64-67', 'The listed families add up to 29,818 — yet the total given is 42,360.'),
            ('Nehemiah 7:66-69', 'The same list, with many different family counts adding up to 31,089 — and the same total of 42,360.'),
        ],
        'note': 'The same register copied twice, diverging in the details but not the total.',
    },
    {
        'id': 'plowshares', 'group': 'Exile and return',
        'question': 'Swords into plowshares — or plowshares into swords?',
        'passages': [
            ('Isaiah 2:2-4', 'Nations will beat their swords into plowshares.'),
            ('Micah 4:1-4', 'The same oracle, almost word for word.'),
            ('Joel 3:9-10', '"Beat your plowshares into swords" — the image reversed into a call to war.'),
        ],
        'note': 'One oracle shared by two prophets and inverted by a third.',
    },

    # --- Gospels ---------------------------------------------------------------
    {
        'id': 'genealogy', 'group': 'Gospels',
        'question': 'Who was Joseph\'s father, and through which son of David does Jesus descend?',
        'passages': [
            ('Matthew 1:1-17', 'Jacob; through Solomon. 42 generations from Abraham.'),
            ('Luke 3:23-38', 'Heli; through Nathan. Traced back to Adam.'),
        ],
        'note': 'Both run through Joseph — whom both Gospels also say was not Jesus\'s father.',
    },
    {
        'id': 'nativity', 'group': 'Gospels',
        'question': 'Where did Jesus\'s parents live, and where did they go after his birth?',
        'passages': [
            ('Matthew 2:1-23', 'They live in Bethlehem, flee to Egypt from Herod, and only later settle in Nazareth.'),
            ('Luke 2:1-7; Luke 2:39', 'They live in Nazareth, travel to Bethlehem for a census, and return to Nazareth after forty days.'),
        ],
        'note': 'Two ways to get a Nazarene born in David\'s city; no flight to Egypt in Luke, no census in Matthew.',
    },
    {
        'id': 'beatitudes', 'group': 'Gospels',
        'question': 'Who is blessed — and where was it said?',
        'passages': [
            ('Matthew 5:1-12', '"The poor in spirit"; on a mountain.'),
            ('Luke 6:17-26', '"You who are poor"; on a level place — followed by woes to the rich.'),
        ],
        'note': 'Matthew spiritualizes; Luke keeps the economic sense and adds the reversal.',
    },
    {
        'id': 'lords-prayer', 'group': 'Gospels',
        'question': 'What did the Lord\'s Prayer say?',
        'passages': [
            ('Matthew 6:9-13', 'The long form: "Our Father in heaven... your will be done... deliver us from the evil one."'),
            ('Luke 11:1-4', 'A shorter form: "Father..." with no "your will be done" or "deliver us".'),
        ],
        'note': 'The familiar doxology ("for yours is the kingdom...") is absent from the earliest manuscripts of Matthew — a later liturgical addition.',
    },
    {
        'id': 'family', 'group': 'Gospels',
        'question': 'Did Jesus\'s family think he had lost his mind?',
        'passages': [
            ('Mark 3:20-35', 'Yes: they come to restrain him, saying "he has gone out of his mind".'),
            ('Matthew 12:46-50', 'The scene of his mother and brothers outside is kept; the "out of his mind" is gone.'),
        ],
        'note': 'Matthew and Luke both drop Mark\'s embarrassing detail.',
    },
    {
        'id': 'legion', 'group': 'Gospels',
        'question': 'How many demoniacs were healed, and where?',
        'passages': [
            ('Mark 5:1-20', 'One man, in the country of the Gerasenes.'),
            ('Matthew 8:28-34', 'Two men, in the country of the Gadarenes.'),
            ('Luke 8:26-39', 'One man, Gerasenes.'),
        ],
        'note': 'Matthew often doubles figures (two blind men, two animals at the entry to Jerusalem).',
    },
    {
        'id': 'jairus', 'group': 'Gospels',
        'question': 'Was Jairus\'s daughter dying or already dead when he came to Jesus?',
        'passages': [
            ('Mark 5:21-24; Mark 5:35-43', 'Dying; news of her death arrives on the way.'),
            ('Matthew 9:18-26', 'Already dead when he asks.'),
        ],
        'note': 'Matthew compresses the story and heightens the miracle.',
    },
    {
        'id': 'foods-clean', 'group': 'Gospels',
        'question': 'Did Jesus declare all foods clean?',
        'passages': [
            ('Mark 7:14-23', 'Yes — "Thus he declared all foods clean" (7:19), Mark\'s editorial comment.'),
            ('Matthew 15:10-20', 'No such line; the point is only that eating with unwashed hands does not defile.'),
        ],
        'note': 'Matthew, writing for a Torah-observant community, removes the abolition of food laws.',
    },
    {
        'id': 'canaanite-woman', 'group': 'Gospels',
        'question': 'Who was the foreign woman, and was Jesus sent only to Israel?',
        'passages': [
            ('Mark 7:24-30', 'A Syrophoenician Greek woman, in a house in Tyre.'),
            ('Matthew 15:21-28', 'A Canaanite, crying out in the open; Jesus adds "I was sent only to the lost sheep of the house of Israel."'),
        ],
        'note': 'Matthew makes the story more pointedly about Israel\'s priority.',
    },
    {
        'id': 'divorce', 'group': 'Gospels',
        'question': 'Is divorce and remarriage ever allowed?',
        'passages': [
            ('Mark 10:2-12', 'No exceptions; it applies to wives divorcing husbands too.'),
            ('Matthew 19:3-12', 'Except for unchastity (porneia).'),
            ('1 Corinthians 7:10-11', 'Paul, citing the Lord: a wife should not separate — but if she does, let her remain unmarried.'),
        ],
        'note': 'The earliest form (Paul, Mark) is absolute; Matthew introduces the exception.',
    },
    {
        'id': 'feedings', 'group': 'Gospels',
        'question': 'Why are the disciples baffled at feeding a crowd — again?',
        'passages': [
            ('Mark 6:30-44', '5,000 men, five loaves, twelve baskets left over.'),
            ('Mark 8:1-10', '4,000, seven loaves, seven baskets — and the disciples ask "how can one feed these people?" as if it had never happened.'),
        ],
        'note': 'Probably one tradition told twice.',
    },
    {
        'id': 'anointing', 'group': 'Gospels',
        'question': 'Who anointed Jesus, where, and when?',
        'passages': [
            ('Mark 14:3-9', 'An unnamed woman in Bethany, on his head, two days before Passover.'),
            ('Luke 7:36-50', 'A "sinner" in a Pharisee\'s house in Galilee, on his feet, early in his ministry.'),
            ('John 12:1-8', 'Mary of Bethany, on his feet, six days before Passover.'),
        ],
        'note': 'One anointing tradition taken in three directions — prophetic, penitential, devotional.',
    },
    {
        'id': 'temple-cleansing', 'group': 'Gospels',
        'question': 'When did Jesus drive the traders out of the Temple?',
        'passages': [
            ('Mark 11:15-19', 'In his final week; it triggers the plot to kill him.'),
            ('John 2:13-22', 'At the very start of his ministry.'),
        ],
        'note': 'In John, the raising of Lazarus takes over the role of the final provocation.',
    },
    {
        'id': 'cockcrow', 'group': 'Gospels',
        'question': 'How many times would the cock crow before Peter\'s third denial?',
        'passages': [
            ('Mark 14:30; Mark 14:66-72', 'Twice.'),
            ('Matthew 26:34; Matthew 26:69-75', 'Once ("before the cock crows").'),
        ],
        'note': 'A small detail that harmonizers famously solved by having Peter deny Jesus six times.',
    },
    {
        'id': 'crucifixion-day', 'group': 'Gospels',
        'question': 'On what day and at what hour was Jesus crucified?',
        'passages': [
            ('Mark 14:12-16; Mark 15:25', 'The day after the Passover meal, at nine in the morning ("the third hour").'),
            ('John 19:14-16', 'The Day of Preparation for the Passover — the day before the meal — still at noon ("the sixth hour") before Pilate.'),
        ],
        'note': 'John\'s Jesus dies as the Passover lambs are slaughtered: "the Lamb of God" (1:29).',
    },
    {
        'id': 'thieves', 'group': 'Gospels',
        'question': 'Did both criminals crucified with Jesus mock him?',
        'passages': [
            ('Mark 15:27-32', 'Yes, both taunt him.'),
            ('Luke 23:39-43', 'One mocks; the other defends him and is promised paradise "today".'),
        ],
        'note': 'Luke\'s Jesus is calm and forgiving on the cross.',
    },
    {
        'id': 'last-words', 'group': 'Gospels',
        'question': 'What were Jesus\'s last words?',
        'passages': [
            ('Mark 15:33-39', '"My God, my God, why have you forsaken me?" Then a loud cry.'),
            ('Luke 23:44-48', '"Father, into your hands I commend my spirit."'),
            ('John 19:28-30', '"It is finished."'),
        ],
        'note': 'Abandonment, trust or completion — each Gospel\'s theology of the cross in one line.',
    },
    {
        'id': 'centurion', 'group': 'Gospels',
        'question': 'What did the centurion say at the cross?',
        'passages': [
            ('Mark 15:39', '"Truly this man was God\'s Son!"'),
            ('Luke 23:47', '"Certainly this man was innocent."'),
        ],
        'note': 'Luke stresses Jesus\'s innocence before Roman authority throughout.',
    },
    {
        'id': 'empty-tomb', 'group': 'Gospels',
        'question': 'Who went to the tomb, whom did they find, and did they tell anyone?',
        'passages': [
            ('Mark 16:1-8', 'Three women; one young man inside; they flee and tell no one.'),
            ('Matthew 28:1-10', 'Two women; an angel descends and rolls back the stone; they run to tell the disciples and meet Jesus.'),
            ('Luke 24:1-12', 'Several women; two men in dazzling clothes; they tell the apostles, who do not believe them.'),
            ('John 20:1-18', 'Mary Magdalene alone; she finds the stone moved and runs to Peter; later sees two angels and Jesus.'),
        ],
        'note': 'Ehrman\'s classic case for reading the Gospels "horizontally".',
    },
    {
        'id': 'appearances', 'group': 'Gospels',
        'question': 'Where did the risen Jesus meet the disciples, and when did he ascend?',
        'passages': [
            ('Matthew 28:7; Matthew 28:16-20', 'In Galilee, on a mountain. No ascension narrated.'),
            ('Luke 24:33-53', 'In Jerusalem — they are told to stay in the city — and he ascends from Bethany that same day.'),
            ('Acts 1:3-12', 'In Jerusalem over forty days; he ascends from the Mount of Olives.'),
        ],
        'note': 'Luke and Acts have the same author, yet place the ascension forty days apart.',
    },
    {
        'id': 'mark-ending', 'group': 'Gospels',
        'question': 'How does Mark end?',
        'passages': [
            ('Mark 16:1-8', 'With frightened women fleeing the empty tomb: "they said nothing to anyone, for they were afraid."'),
            ('Mark 16:9-20', 'With appearances, a commission, snake-handling and an ascension — verses absent from the earliest manuscripts.'),
        ],
        'note': 'A later scribal addition, as Misquoting Jesus details.',
    },

    # --- Acts and letters ------------------------------------------------------
    {
        'id': 'judas', 'group': 'Acts and letters',
        'question': 'How did Judas die, and who bought the field?',
        'passages': [
            ('Matthew 27:3-10', 'He returns the silver and hangs himself; the priests buy a potter\'s field with it.'),
            ('Acts 1:15-20', 'He buys a field himself, falls headlong and bursts open.'),
        ],
        'note': 'Both explain the name "Field of Blood", in different ways.',
    },
    {
        'id': 'forgive-them', 'group': 'Acts and letters',
        'question': 'Who prayed "forgive them" while being killed?',
        'passages': [
            ('Luke 23:32-34', 'Jesus — "Father, forgive them" (23:34), a line missing from several early manuscripts.'),
            ('Acts 7:54-60', 'Stephen, as he is stoned: "Lord, do not hold this sin against them."'),
        ],
        'note': 'The Luke line may have been added later, modelled on Stephen\'s death in Luke\'s second volume.',
    },
    {
        'id': 'damascus', 'group': 'Acts and letters',
        'question': 'What did Paul\'s companions perceive, and where did he go after his conversion?',
        'passages': [
            ('Acts 9:1-27', 'They hear the voice but see no one; Paul soon goes to Jerusalem and is brought to the apostles.'),
            ('Acts 22:6-16', 'They see the light but do not hear the voice.'),
            ('Galatians 1:11-20', 'Paul consults no one, goes to Arabia, and reaches Jerusalem only three years later, seeing just Peter and James.'),
        ],
        'note': 'Paul swears "I do not lie" (1:20) — insisting on his independence from Jerusalem.',
    },
    {
        'id': 'jerusalem-council', 'group': 'Acts and letters',
        'question': 'What did the Jerusalem leaders require of Gentile converts?',
        'passages': [
            ('Acts 15:1-29', 'A public council issues a decree: abstain from idol food, blood, strangled animals and porneia.'),
            ('Galatians 2:1-10', 'A private meeting: they "added nothing" — only asked him to remember the poor.'),
        ],
        'note': 'Paul never mentions the decree, even when discussing idol food (1 Corinthians 8–10).',
    },
    {
        'id': 'jude-2peter', 'group': 'Acts and letters',
        'question': 'What happens when 2 Peter copies Jude?',
        'passages': [
            ('Jude 1:5-16', 'Cites Michael\'s dispute over Moses\'s body (v. 9) and quotes 1 Enoch as prophecy (vv. 14–15).'),
            ('2 Peter 2:1-18', 'Reuses Jude\'s argument and images but removes both non-canonical references.'),
        ],
        'note': 'A later author sanitizing a source that quoted books that did not make the canon.',
    },
]

PARALLELS_BY_ID = {p['id']: p for p in PARALLELS}
