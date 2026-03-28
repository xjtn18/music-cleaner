# VOCABULARY:

- artist -> the artist's name
- song -> the song's name
- remix tag -> one of "segue", "mash", "blend", "remix", "mashup", "segway", "vs"
- edit tag -> some phrase containing "Clean" or "Dirty", such as, "Intro - Dirty" (we dont have an exhaustive list, hopefully you can infer it from the test cases)
- KBPM -> the camelot wheel code and the BPM


# GENERAL FILE NAMING OVERVIEW:

Every file, before cleaning, should roughly be the following format (curly braces are for placeholders):

    {artist} - {song} ({remix tag}) ({edit tag}) {KBPM}

Note that, in some cases, the remix tag and the edit are together in the same set of parentheses -> we prefer them to always be split in the cleaned version.

Note that the remix tag, edit tag, and KBPM segments are optional, so they may or may not exist in the original filename.
Essentially, in the end, every cleaned filename should be artist name, a dash, then song, then remix tag, then edit tag. The tag segments may or may not exist depending if their counterpart exists or not in the original filename. You will see below a rule that states that KBPM should always be removed.

Note that any of the segments that come after the song name may or may not be wrapped in parens, so this should be accounted for. In the cleaned filename, there should always be parens around these segments.

Note that, in edit tags, any rules that apply to "Clean" should apply just the same to "Dirty".

When doing regex matches, we should always normalize to lowercase.

Note that there may be some rules you need to infer from the existing test cases, because we may not have outlined it in this file. If you can infer any based on the test cases, please add them to the end of this file, with a prefix "[Inferred]"

Please do not alter any of the existing test cases, and do not add any new test cases on your own.

Please ignore the names of the test cases -> they may or may not correctly indicate what the test is actually showcasing.


# FILE NAMING RULES:

Implement the following rules into `bin/clean`, unless they say "[Implemented]" before them. Once you have implemented them, please prefix them with "[Implemented]"

- [Implemented] if it has the KBPM, remove it

- [Implemented] capital CK as a word on its own, as well as the space after it, should be removed.

- [Implemented] any instances of "Club Killers" should be removed.

- [Implemented] Anything that says "intro dirty" or "intro clean" should be formatted to say (Intro - Dirty)" or "(Intro - Clean)" respectively. Note that the match string could already have a " - " in between the 2 words, and it could already have parens around the 2 words. Any combination could exist and should be accounted for. Capitalization should not matter, so that should be normalized as well.

- [Implemented] Anything that says "Dirty Extended" or "Clean Extended", with or without parens around it, should be formatted to say (Intro - Dirty)" or "(Intro - Clean)" respectively, following the same rules above.

- [Implemented] any "feat" on its own, disregarding capitalization, should be formatted to just "ft". If it had a period directly after, the period should be removed.

- [Implemented] any "vs" on its own (after being normalized to lowercase), and removing any period it may have after, should be formatted to just "vs"

- [Implemented] Anything spelled "segway" should be spelled "Segue". If the original word didn't have parens around it, then add them around the new spelling. If it did, leave them.

- [Implemented] Anything spelled "blend" or "mashup" needs to be spelled "mash". If the original word didn't have parens around it, then add them around the new spelling. If it did, leave them.

- [Implemented] Anything that has "vs" in it, if they do not already have a remix tag in them, you should add "(Segue)" to the name. Otherwise if it does already contain a remix tag, you should replace it with "(Segue)"

- [Implemented] "party starter" should be "Clapapella". If the original word didn't have parens around it, then add them around the new spelling. If it did, leave them.

- [Implemented] "slam in" or "slam intro" should be "Slam Edit". If the original word didn't have parens around it, then add them around the new spelling. If it did, leave them. If it said Intro in the original filename, that should be removed.

- [Implemented] "clap intro" should be "Clapapella". If the original word didn't have parens around it, then add them around the new spelling. If it did, leave them.

- [Implemented] "trans" or "transition" followed by "\d+-\d" should have that second portion come first.

- anything that says "transition" followed by some numbers should be 

- [Implemented] Any dashes between 2 number should always have a space before and after the dash if there is not already spaces there.

- [Implemented] Anything that says "acapella intro" or "acap intro" should say "Acapella In"

- [Implemented] Anything that says "acapella outro" or "acap outro" should say "Acapella Out"

- [Implemented] Anything that says "acap" without the  should say "Acapella"

- [Implemented] Anything that says "acapella intro and outro", where "and" can be "and" or "&", and where "intro" can be "in", and where "outro" can be "out", should be "acapella in & out". If the original word didn't have parens around it, then add them around the new spelling. If it did, leave them.

- [Implemented] if it says "acapella in" or "acapella out", remove the word "intro" from the edit tag

- [Implemented] Edit tags always go at the end of the filename (after all other tags)

- Other intro types (Hype Intro, Epic Intro, Break Intro, Clap Intro, etc.) should be preserved but wrapped in parens

- Other edit types (Quick Hit, Short Edit, Radio Edit, Club Edit, etc.) should be preserved but wrapped in parens

Explicit hard-coded formatting rules:

- AAP Rocky, ASAP Rocky -> A$AP Rocky
- Ty Dolla Sign -> Ty Dolla $ign
- Too Short -> Too $hort
- Schoolboy Q -> ScHoolboy Q
- JayZ -> Jay-Z
- Biggie, Biggie Smalls -> The Notorious B.I.G.
- Dr Dre -> Dr. Dre

- [Implemented] there should be no instances of nested parens, and no open parens without a closer and vice-versa

- [Inferred] commas and ampersands in the artist segment should normalize to ` x `, while existing `ft` should be preserved.

- [Inferred] `Extended Mix` should normalize to `(Ext)`.

- [Inferred] `Inst` should normalize to `(Instrumental)`.

- [Inferred] `Jump Off` should normalize to `(Jump Off Edit)`.

- [Inferred] `Clap In` should normalize to `(Clapapella)`.

- [Inferred] `Word Play Edit` should normalize to a transition tag, and standalone `Word Play` / `Wordplay` tokens after the song segment should be removed.

- [Inferred] If a filename contains `vs`, any pre-existing remix tags should be removed from custom tags and replaced by `(Segue)`.

- [Inferred] If a cleaned filename contains `Remix`, `Segue`, or `Mash`, the edit tag should prefer `Intro - Clean/Dirty` unless another tag like `Transition`, `Acapella In`, `Acapella Out`, `Slam Edit`, `Ext`, or `Clapapella` makes `Intro` redundant.

- [Inferred] Final cleanup should remove dangling dashes inside tag parens, such as `(- Dirty)` or `(JD Live -)`.

- [Inferred] Files with a trailing duplicate marker like `(1)` should be treated as duplicates and deleted during rename runs; dry runs should show them as deletions.
