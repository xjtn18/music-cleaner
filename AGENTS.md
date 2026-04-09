# VOCABULARY:

- artist -> the artist's name
- song -> the song's name
- remix tag -> one of "segue", "mash", "blend", "remix", "mashup", "segway", "vs"
- edit tag -> some phrase containing "Clean" or "Dirty", such as, "Intro - Dirty" (we dont have an exhaustive list, hopefully you can infer it from the test cases)
- KBPM -> the camelot wheel code and the BPM. This can appear as `{camelot} {bpm}`, `{bpm} {camelot}`, or with the camelot code written as just `A` / `B` beside the BPM


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

- [Implemented] capital CK as a word on its own, as well as the space after it, should be removed. Instances of "CK Cut" should also be removed, but this indiciates that this needs to be a "Quick Hit" variant for the edit tag.

- [Implemented] If you find an extra second dash (with whitespace around it) in the original filename BEFORE any tag matter, this needs to be removed before you apply any other processing steps.

- [Implemented] any instances of "Club Killers" should be removed.

- [Implemented] Anything that says "intro dirty" or "intro clean" should be formatted to say (Intro - Dirty)" or "(Intro - Clean)" respectively. Note that the match string could already have a " - " in between the 2 words, and it could already have parens around the 2 words. Any combination could exist and should be accounted for. Capitalization should not matter, so that should be normalized as well.

- [Implemented] Anything that says "Dirty Extended" or "Clean Extended", with or without parens around it, should be formatted to say (Intro - Dirty)" or "(Intro - Clean)" respectively, following the same rules above.

- [Implemented] any "feat" on its own, disregarding capitalization, should be formatted to just "ft". If it had a period directly after, the period should be removed.

- [Implemented] any "vs" on its own (after being normalized to lowercase), and removing any period it may have after, should be formatted to just "vs"

- [Implemented] Anything spelled "segway" should be spelled "Segue".

- [Implemented] Anything spelled "blend" or "mashup" needs to be spelled "mash".

- [Implemented] Anything that has "vs" in it, if they do not already have a remix tag in them, you should add "(Segue)" to the name. Otherwise if it does already contain a remix tag, you should replace it with "(Segue)"

- [Implemented] "party starter" should be "Clapapella".

- [Implemented] "slam in" or "slam intro" should be "Slam Edit". If it said Intro in the original filename, that should be removed.

- [Implemented] "clap intro" should be "Clapapella".

- [Implemented] "trans" or "transition" followed by "\d+-\d" should have that second portion come first.

- [Implemented] in the tag segments of the filename, anytime you find a 2 number separated by a dash (with or without spaces between the numbers as the dash), that means the song is a transition, and `Transition` should be added after the numeric range if it is not already there

- [Implemented] Any dashes between 2 number should always have a space before and after the dash if there is not already spaces there.

- [Implemented] -> If it contains explicitly "Acapella Intro" in the uncleaned filename, you should treat the file as if doesn't say "Acapella" when applying all other rules.

- [Implemented] Anything that says "acapella outro" or "acap outro" should say "Acapella Out"

- [Implemented] Anything that says "acap" alone should say "Acapella"

- [Implemented] Anything that says "acapella intro and outro", where "and" can be "&", and where "intro" can be "in", and where "outro" can be "out", should be "acapella in & out".

- [Implemented] if it says "acapella in" or "acapella out", remove the word "intro" from the edit tag

- [Implemented] Edit tags always go at the end of the filename (after all other tags)

- [Implemented] Other intro types (Acapella Intro, Hype Intro, Hype In, Epic Intro, Epic In, Break Intro, Break In  etc.) should be preserved but wrapped in parens
- [Implemented] Other intro types (Acapella Intro, Hype Intro, Hype In, Epic Intro, Epic In, Break Intro, Break In ) should add a redundant Intro to the edit tag at the end if it does not already have one there.

- Other edit types (Quick Hit, Short Edit, Club Edit, etc.) should be preserved but wrapped in parens. `Radio Edit` is excluded from this set and should follow the House-only rule below.

- [Implemented] If the filename contains `Club Edit`, the cleaned filename should include `Intro` in the final edit tag.

Explicit hard-coded formatting rules:

- AAP Rocky, ASAP Rocky -> A$AP Rocky
- ASAP Ferg -> A$AP Ferg
- Ty Dolla Sign -> Ty Dolla $ign
- Too Short -> Too $hort
- Schoolboy Q -> ScHoolboy Q
- JayZ -> Jay-Z
- Biggie, Biggie Smalls -> The Notorious B.I.G.
- Dr Dre -> Dr. Dre

- [Implemented] there should be no instances of nested parens, and no open parens without a closer and vice-versa

- [Inferred] commas and ampersands in the artist segment should normalize to ` x `, while existing `ft` should be preserved.

- [Inferred] In tag matter after the song segment, commas and ampersands should normalize to ` x `, while existing `ft` should be preserved, even if the vendor/remix artist does not get cleanly split away from the rest of the tag phrase.

- [Inferred] `Extended Mix` should normalize to `(Ext)`.

- [Inferred] `Inst` should normalize to `(Instrumental)`.

- [Inferred] If a cleaned filename contains `(Instrumental)`, it should never also contain a final clean/dirty edit tag.

- [Inferred] `Jump Off` should normalize to `(Jump Off Edit)`.

- [Inferred] `Clap In` should normalize to `(Clapapella)`.

- [Inferred] `Word Play Edit` should normalize to a transition tag, and standalone `Word Play` / `Wordplay` tokens after the song segment should be removed.

- [Inferred] If a filename contains `vs`, any pre-existing remix tags should be removed from custom tags and replaced by `(Segue)`.

- [Inferred] If a cleaned filename contains `Intro`, `Remix`, `Segue`, or `Mash`, the edit tag should alteast contain "Intro", unless another tag containing `Transition`, `Acapella In`, `Acapella Out`, `Slam`, `Clap`, `Ext`, or `Clapapella` makes `Intro` redundant.

- [Inferred] If tag matter contains an artist/vendor name, that implicitly means the file is a remix even if no explicit remix term appears, so the final edit tag should contain `Intro` unless a negation rule applies or the file is being cleaned under `House`.

- [Implemented] `Intro` negation rules supercede `Intro` addition rules.

- [Inferred] Final cleanup should remove dangling dashes inside tag parens, such as `(- Dirty)` or `(JD Live -)`.

- [Inferred] Files with a trailing duplicate marker like `(1)` should be treated as duplicates and deleted during rename runs; dry runs should show them as deletions.

- [Inferred] When a tag group contains a vendor/remix artist plus recognized tag matter like `Slam Edit`, `Acapella`, or a transition range, the vendor should be split into its own paren group.

- [Inferred] If an acapella token is followed by an additional phrase in the same tag group, that trailing phrase should be retained with the acapella tag unless another rule explicitly removes it, such as `Rob Rivera Acapella Break -> (Rob Rivera) (Acapella Break)`.

- [Inferred] In transition tag groups, trailing helper phrases around the range such as `Hip Hop To House`, `VIP Flip`, `Flip`, or `Edit` should be removed once the numeric range has been normalized into a `Transition` tag.

- [Inferred] House-only cleaning rules: `Clean Extended` / `Dirty Extended` should become `(Ext)` plus the final clean/dirty edit tag, `Radio Edit` should normalize to `(Original Mix)`, and House filenames should never retain `Intro` in the final edit tag.


# SORT MODE RULES:

- [Implemented] `bin/clean` supports a `--sort` mode that sorts files into subfolders instead of renaming them in place.

- [Implemented] Sort mode should only sort by the tag categories represented in `file_structure.txt`.

- [Implemented] Sort mode should ignore any music inside a folder named `EDM`, at any depth.

- [Implemented] Sort dry runs should show the original file path, the implicitly cleaned filename, and the destination path the file would be moved to.

- [Implemented] Sort dry runs should perform an implicit clean first, and the destination path should use that cleaned filename.

- [Implemented] In `Hip Hop`, if a filename matches one of the tool categories from the `Hip Hop Tools` section of `file_structure.txt`, the file should be moved out of `Hip Hop` and into `Hip Hop Tools` in the corresponding subfolder based on its edit tag.

- [Implemented] Hip Hop tool sorting should recognize these categories from cleaned tags: `Acapella`, `Acapella In`, `Acapella In & Out`, `Acapella Out`, `Clapapella`, `Instrumental`, `Jump Off Edit`, `Mash`, `Segue`, `Slam Edit`, and `Transition`.

- [Implemented] Files that do not match a `Hip Hop Tools` category should remain under their genre root and move only into the appropriate leaf edit-tag folder.
