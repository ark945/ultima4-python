# Ultima IV → Python — Roadmap

The plan I (the author agent) execute through, in order. I work top-down without asking;
each item lands with a faithful port (C function cited), a headless check, and a memory
update. The North Star: a playable game whose state & content are clean plain-text data,
driven by two runtime agents (editor = writes, tutor = reads). See the project memory.

## ⏯ Start here next session (snapshot 2026-07-04)
**✅ MOONGATES ARE AGENT-USABLE (issues #4/#5).** The moons run on a **real-time clock** (int 0x1C
~18.2 Hz), independent of moves — faithful to the original. It was frozen headless (no loop); now a
single lazy wall-clock driver (`game.catch_up_moons`) advances it from observe/act (headless) AND
every render frame (windowed), so both modes are mechanically identical. `observe()` now carries
`moons:{trammel,felucca,gate:{x,y,destination,adjacent}}`. New turn-based **time primitives** let the
agent advance the real-time clock without moving: `wait <seconds>` and `wait until moongate|moons_dark|
trammel N|felucca N` (MCP tools `wait`/`wait_until`; also in `agent-play`). Moves still never touch the
moons (`end_turn` untouched). `game.moon_wallclock=False` freezes wall-time for deterministic tests.
Plus **`travel_to(x,y)`** / `"go x y"` (issue #5 traversal half) — BFS-pathfinds across the overworld/
town in one call, stops on arrival/combat/dialog/damage/block with `travel_reason`+`steps_taken`.
Batch tools are steered in CLAUDE.md/AGENTS.md + the MCP server `instructions`. `./run test` = 87/87.

**✅ SHIPPED PUBLIC + onboarding hardened.** Live at github.com/leeroywking/ultima4-python (public).
Fresh-clone onboarding is fixed: root `README.md` (clone→play quickstart), portable `.mcp.json`
(`${CLAUDE_PROJECT_DIR:-.}`), stdio-clean MCP (no pygame banner leak). New watch/headless surfaces:
**`./run mcp --window`** (watch an external/MCP-driven agent play live in a window — via
`LiveWindow.submit`) and **`./run smoke [out.png]`** (headless one-frame render to PNG). CLAUDE.md
now makes the visible-watch mode the gated default (never silently headless-play). Testing-agent
issues #1 (onboarding) + #2 (watch MCP agent live) addressed & closed.

**✅ ORIGINALS PURGED.** All original copyrighted binaries (`.EGA/.PIC/.ULT/.DNG/.TLK/.MAP/.CON`,
the DOS executables) and the five one-shot import tools (`convert_graphics`, `extract_intro`,
`convert_maps`, `dump_dialogue`, `lzw`) plus the decompiled `u4/` source tree have been **deleted**.
The two load-bearing party binaries were text-ified: `PARTY.SAV` → `data/party_start.json`,
`PARTY.NEW` → `data/party_template.json` (byte-exact round-trip via `Party.to_json/from_json`).
The game now runs with **zero original files**. `PARTY.SAV` is now only a runtime save (gitignored).

Ships as a **free, non-commercial fan port / agent toy** — public is fine (U4 is Origin/EA
freeware; see `docs/AGENTS.md` for attribution). The purge above makes the repo self-contained:
clone → play, no original files needed.

**Build is green: `./run test` prints `N/N checks passed` (83/83 at this snapshot).** Runnable:
`./run` (title → intro → game), `./run town britain` (debug boot), `./run demo` (scripted live
playthroughs), `./run smoke` (headless one-frame PNG), `./run agent-play` / `./run agent-demo` /
`./run watch` / `./run mcp` / `./run mcp --window` (the agent-playable stack — UltimaEnv observe/act,
reference agent, live human-watch window, MCP server + windowed MCP), `./run tiles` (regenerate the
tile ref). Single source of truth
now holds for graphics (PNG), intro/tarot + menus (JSON), dialogue (JSON), the party seeds (JSON),
**and all maps — overworld/towns/dungeons (editable ascii-tilemap, `data/maps/*.txt`)**; the import
tools that produced them are gone (recover from git history ≤ `b5fa243` if ever needed).
**Runtime reads zero original binaries** (only PNG/JSON/ascii-maps + `PARTY.SAV`) — proven by booting
the game with all 27 map binaries removed. See the Phase-4 "Maps are editable ascii-tilemaps" entry +
its deletion-readiness audit for what a full `data/` purge still needs (rune `.EGA`, `.CON` arenas).

This session closed the **core gameplay-loop correctness gap** with six faithful ports, each
C-cited and headless-tested (60→71 checks):
1. **Per-turn upkeep** (`upkeep.py`, C_1C53) — food/starvation, poison damage, sleep-wake, MP regen
   (per-class Int cap), hull self-repair, and the all-dead → Lord British revive (C_0EB1).
2. **Search quest-item table** (`items.SEARCH_TABLE`, U4_SRCH.C D_2920) — Bell/Horn/Wheel/Skull,
   Book/Candle, Black/White Stones, Mystic Armour/Weapons, Mandrake/Nightshade, all 8 runes, with
   the real moon/cooldown/karma gating. **This is the key to playable progression.**
3. **Use effects** (`items.use_item`, U4_USE.C) — Bell→Book→Candle ritual at the Abyss, Horn, Wheel,
   Skull (cast vs hold-aloft), Key.
4. **Abyss entry** (`cmd_enter`, C_3FB9) — the entrance opens only after the ritual; descends Abyss.Dng.
5. **Environmental hazards** (`hazards.py`, U4_EVT.C C_9209) — swamp/poison→'P', sleep field→'S',
   lava→burn-on-foot/sink-at-sea. Closes the status loop with upkeep + the Cure/Awaken spells.
6. **Bridge trolls** (TIL_17, 1/8 → combat).
The status subsystem is now coherent end-to-end (verified by a 200-move random-walk smoke: swamp
poison → bleed-out → LB revive, no crashes).

**Best next candidates (pick up here):**
1. **Faithful in-game UI/layout** — ornamental border, party-roster panel (member/HP/status, right
   side), map-left / stats-right / prompt-bottom. C: U4_INIT.C C_213B frame. (Highest visual payoff;
   needs pygame, harder to headless-test — render frames and eyeball them.)
2. **The 8 colored Stones via dungeon altar rooms** — the `.DNG` 4096B room block is still skipped;
   parsing it unlocks the altar puzzle (3-part key) + the 6 remaining stones (Abyss-gating). Big.
3. **Remaining U4_EVT.C C_9209 branches** — dungeon field/pit/winds events and in-combat arena-tile
   hazards (our dungeon uses a different tile encoding than the overworld TIL_ values — map it first,
   don't guess). And monster special attacks (U4_AI.C): poison/sleep/fire/steal/divide.
4. **Small visual refinements:** water/field procedural shimmer (C_34EA, ANIMATED_FLOW static);
   intro music (no audio engine); the small rune/symbol .EGA images use a 2nd undecoded format.

New modules this session: `ultima4/upkeep.py`, `ultima4/hazards.py`. Heavily rewritten: `items.py`
(Search table + Use handlers + Abyss ritual gate). Wiring: `game.end_turn` + `game.cmd_enter`.

## Done
- [x] Phase 0 — state (byte-exact tParty/tChara), graphics (CGA+EGA), world map, main loop, overworld walking.
- [x] Phase 1a — .ULT town loader, enter/leave, building-mode walking, NPC display, simplified new-game.
- [x] Phase 1b — Talk: .TLK decode → `Dialogue`/`TalkData`, faithful `Conversation` keyword engine, yes/no question, give/join.
- [x] Phase 1c — town NPC movement (wander/follow), `run` launcher, `selftest`, `.TLK`→JSON export.

## Now → next (Phase 1 completion)
- [x] **JSON-backed dialogue** — game reads `data/dialogue/*.json` as the single source of truth (.TLK is import-only; fallback dropped — see Phase 4). Editor loop proven (edit text file → live in game).
- [~] **Shops** (U4_SHOPS.C) — sign-board/alphabet Talk path (`C_A686`) wired; **weapons, armor, food, reagents** ported (buy/sell, reagent haggle→karma). Remaining: tavern/pub, healer, inn, guild, stable, +seer/hawkwind — they need HP/time/item systems, so they're routed with a "coming soon" message for now.
- [x] **Lord British** (U4_LB.C) — first-meeting, resurrection, level-up (HP→level*100, stat boosts), heal-on-"health", lore keywords, context "help". Reachable via the new Klimb.
- [x] **Klimb/Descend + multi-floor castles** — LB's castle is two floors (LCB_1/LCB_2); ladders (0x1B/0x1C) connect them. `MULTI_FLOOR` table.
- [x] **Ztats** — character-sheet readout (CMD_Ztats).
- [x] **Named tile constants** — `tiles.py` now exports plain-English tile names (LORD_BRITISH, LADDER_UP, MERCHANT, …); code no longer uses raw hex. `docs/TILES.md` = visual reference of all 256 (158 await user names).
- [x] **Doors** — Open (door→walkable, auto-closes after 5 turns) and Jimmy (key unlocks a locked door). C: U4_EXPLO.C CMD_Open/CMD_Jimmy.
## v1 scope — everything below is now SCAFFOLDED

All remaining v1 work is stubbed: each system has a module with the real API surface,
docstrings, and C-source citations, raising `NotImplementedError`. Player commands dispatch
to them via `game._stub` (catches NotImplementedError → "coming in v1", never crashes). To
implement a piece, fill its module function and wire a `selftest` check. `[S]` = stubbed.

### Building-mode commands & shops
- [x] **items.py** — Get (chest gold), Search (hidden-item framework), Use (special items: wheel restores hull, others context-bound), Ready, Wear, Ignite, Hole-up (camp/heal), Locate (sextant), Peer (gem). (U4_GET/SRCH/USE/PEER)
- [x] **Shops cont.** — Guild (smuggler), Tavern (meals + rumor clues), Healer (cure/heal/resurrect/blood), Inn (rest→full heal) all DONE & tested. All 8 sign-board slots implemented. TODO later: Stable (SHP_horse — needs transport.py), Hawkwind (in shrines.py).

### Phase 2 — systems
- [x] **Combat** — `combat.py`: MOD_COMBAT 11x11 arena, party-then-monsters turn loop, move/Attack(dir,melee+ranged)/Pass, monster AI (close+strike), hit/damage/death, win→XP / loss→return. Wired: overworld encounters start it, renders in play.py. (`.CON` arena *visuals* + exact damage tables = refinement.)
- [x] **Spells + Mixing** — `mixing.py` (MixSession: pick spell, add reagents, recipe match→mixture/fizzle; recipes ported from D_277E) + `spells.py` (CastSession: spend mixture+MP from D_208C; utility effects Awaken/Cure/Heal/Resurrect/Light implemented, others acknowledged; combat-target damage = refinement). Wired to M/C keys.
- [x] **Dungeons** — `dungeon.py`: load `.DNG` (8 levels x 8x8, nibble-encoded), MOD_DUNGEON first-person (arrows advance/retreat/turn, K/D ladders, X exit), walls block, tile effects (chest→gold, fountain→heal, field→harm, room→combat), enter from overworld 0x09. Top-down render (3D raycast = refinement).
- [x] **Shrines + Hawkwind** — `shrines.py`: rune-gated entry, 8 mantras (ahm/mu/ra/beh/cah/summ/om/lum), meditate→vision/Spirituality, karma-99→partial Avatarhood (`game.elevated`); HawkwindSession counsels per-virtue from karma. Shrine entry wired from overworld 0x1E. (Hawkwind in-game reachability via an LCB NPC = small follow-up.)
- [x] **Moongates** — `moongate.py`: moons cycle on their **own animation clock** (`game.tick_moons` from the overworld redraw loop, NOT per move — C_3A80's D_1668 divider + D_1664 sub-counter → Trammel +2 / Felucca +6, phase=ctr>>5); they advance while standing still and freeze off the overworld. Open gate drawn on the (mutable) world map at the Trammel spot; stepping onto 0x43 teleports to the Felucca destination; both-full→Abyss message. C: U4_ANIM C_3A80 / U4_MAP C_2A91.
- [x] **Transport** — `transport.py`: Board/X-it/Fire; ship sails water (SAILABLE), balloon flies anywhere, horse = land w/o slow-progress. Integrated into `_move_overworld` via `can_move_onto`. World map now mutable (set_tile). (Overworld vessel *objects* placed later by monsters.py/editor.)
- [x] **World monsters** — `monsters.py`: spawn near view on suitable terrain (sea/land), close in each outdoor turn (torus-aware follow), attack when adjacent → `combat.start_encounter` (falls back to a message until combat lands). `game.monsters` list + `monster_sprites` rendered in play.py.
- [x] **Endgame** — `endgame.py`: `abyss_requirements`/`can_enter_abyss` (3-part key + party of 8 + all 8 virtues elevated), CodexSession (Word of Passage "veramocor" → "infinity" → `game.won`). Wired to descending the Abyss (dungeon 0x18) bottom. C: U4_END.C.

### Phase 3 — the actual point (data-driven + agent layer)
- [x] **GameRPC** — `agent/rpc.py`: snapshot/party/query (read) + guarded set() & primitives (max_stats, heal, grant_item, add_moongate, add_npc). The keystone both agents use.
- [x] **Editor agent** — `agent/editor.py`: rule-based NL → RPC ops ("max my stats", "give N gold", "heal", "add a moongate", "add a shopkeeper npc", "grant the bell"). Mutates the live game; verified.
- [x] **Tutor agent** — `agent/tutor.py` + `knowledge/quest_graph.py`: `next_step`/`ask` with progressive hinting (nudge→direct), per-virtue facts (shrine town, mantra, how to raise), objective chain from a live snapshot.
- [~] Editable data: dialogue (JSON) + moongate tables (now mutable lists, editor-writable). Places/start-data → JSON = future polish.
- [x] **Authentic character creation** — `character_creation.py`: the gypsy's 7 questions as a single-elimination bracket over the 8 virtues → class → starting stats/home/karma. C: TITLE_1.C.
- [x] **Live-demo framework** — `ultima4/demo.py` (`Director`) + `ultima4/demo_scenarios.py`
  (`SCENARIOS` registry) + `tools/demo.py` (`./run demo`) + the **`live-demo` skill**. The Director
  plays a real headless `Game` through the *actual* input path (`handle()` for keys/movement,
  `feed()` for Talk/shop dialogue) and records a transcript: narration + the game's own messages +
  ASCII minimaps (`@`=party) + checked outcomes. Lets the agent answer "launch the game and take me
  through <X>" by mapping to a named scenario or composing a new one against the verbs (`enter`,
  `goto`, `do`, `say`, `talk`, `setup`, `minimap`, `expect`). Seven scenarios ship and are asserted
  green by the suite: `lord_british_heal`, `talk_to_townsfolk`, `buy_a_weapon`, `heal_at_the_inn`,
  `mix_and_cast_heal`, `first_dungeon`, `win_a_fight`. Headless + deterministic (seeded) so demos
  double as smoke tests; flows derive from the verified sequences in `tools/selftest.py`.
  - **Watch-the-agent-play (visual)** — `ultima4/stage.py` `PygameStage` drives the *real game
    window* via the shared renderer (`play.draw_game`, factored out of play.main): the character
    moves tile-by-tile, Talk dialogue scrolls, blows land. `./run demo <name> --watch` plays live
    (paced to wall-clock, `--speed`/`--cga`); `./run demo <name> --gif out.gif` renders the whole
    playthrough to an animated GIF with **no display needed** (fast path skips real-time sleeping);
    `--shots DIR` = one PNG/frame. The Director gained an optional `stage` and presents each verb
    (move/say/do) as paced, animated frames; pure headless path unchanged (demo.py/scenarios never
    import pygame). selftest renders a scenario to frames headlessly (SDL dummy). Known simplification:
    scenarios set required state directly and `goto` scene-cuts positioning rather than walking every
    tile — the gameplay actions are real/animated; authentic pathfinding is a future upgrade.

- [x] **Agent-playable: expose the game to external agents** — a layered stack so any agent can
  download, run, and *play* the game while a human watches.
  - **`ultima4/env.py` `UltimaEnv`** — the stable observe/act substrate over `Game`: `reset`/
    `observe`/`act`/`legal_actions`/`play`. Serializable observation (mode, position, ASCII view +
    legend, party/inventory, visible NPCs/monsters, messages-since, interaction prompt, `won`) and a
    small action grammar (`move N|S|E|W` / `key <L>` / `say <text>` / `pass`). `legal_actions` is
    computed per state. Deterministic (seeded) — replaying an action list reproduces state.
  - **`tools/agent_play.py` (`./run agent-play`)** — stateless CLI driver: rebuilds from seed and
    replays the whole `--do` list each call, so an agent plays turn-by-turn across invocations. Used
    to dogfood the schema (Claude navigated overworld→into Jhelom through it).
  - **`ultima4/agent/mcp_server.py` (`./run mcp`)** — MCP server (FastMCP) exposing
    `new_game/observe/act/legal_actions/play` + `list_demos/run_demo`, so any MCP-capable agent
    plays it. `mcp` is an optional dep; lazy-imported so the package never hard-requires it.
  - **`ultima4/live_window.py` + `tools/watch_agent.py` (`./run watch`)** — the human-watch view:
    a free-running pygame render loop (main thread, `play.draw_game`) draining a thread-safe action
    queue, while an agent policy on a background thread reads `observe()` and enqueues actions. The
    human watches the character move/talk/fight live. `--scenario` replays a demo live; default is an
    agent wander policy.
  - **`examples/random_agent.py` (`./run agent-demo`)** — reference policy (reads `view_ascii`/
    `visible`/`standing_on` → picks from `legal_actions`); living docs of the env loop.
  - **`pyproject.toml`** (pip-installable, `[mcp]` extra) + **`docs/AGENTS.md`** (the observe/act
    contract, connection paths, and a **copyright/data-licensing** caveat: ship the engine, bring
    your own U4 data, regenerate assets via `./run maps|gfx|dump`). selftest covers env determinism,
    the MCP tools, the live window (headless), and the reference agent. Built by parallel subagents,
    integrated here. Known follow-ups: scoring/eval harness, multi-session hosting, authentic
    tile-by-tile navigation for scripted scenarios.

## Phase 4 — faithful completeness (gap log)

v1 is structurally complete & winnable-by-editing, but many systems are simplified or absent
vs the original. This is the running catalogue of what's missing, so findings aren't lost to
memory. Source-referenced. `[ ]` = not started, `[~]` = partial. Audit ongoing — keep adding.

### Intro & launch sequence (HIGH PRIORITY — user wants this dutifully faithful)
The original is a separate title executable (`u4/SRC-TITLE/`); all art assets are present in
`data/` (TITLE.EGA, ANIMATE.EGA, GYPSY.EGA, PORTAL.EGA, virtue-card scenes HONOR/SACHONOR.EGA…).
Currently only step 8's *logic* exists (`character_creation.py` bracket), with paraphrased text.
- [x] **Title screen + intro/launch sequence** — `play.run_title` + `ultima4/intro.py` (`IntroDirector` state machine; logic is headless-testable, play.py is the pygame driver). Composes a native 320x200 frame (picture backdrop + CHARSET text window at row 19 + the gypsy's two virtue cards cropped from the pair-image per C_2B6D) and scales it to the window. Flow faithful to TITLE_0.C/TITLE_1.C: title (the **TITLE** logo backdrop + Option-C menu from menus.json in its box; ANIMATE is the sprite sheet of the two title "monsters", NOT a backdrop — animating them is a refinement) → letter keys **(I)nitiate / (J)ourney / (R)eturn** (C: TITLE_0.C main switch KBD_I/J/R) → new game runs the 24 narrative scenes (each over its backdrop, keypress between; C_2883) → gypsy casting → class reveal → PORTAL transport → into Britannia. All text via the CHARSET renderer, paginated (long/edited questions page before A/B). The picture is shown 152px tall and the bottom 48px (rows 19-24) is cleared to black as the text window (C: Gra_3(40,152,..)+Gra_5) so text is always legible; cards cropped exactly 96x124 @ src x=8/216,y=12 (C_2B6D). selftest 59/59; both boot paths smoke clean headless; title/question/scene frames eyeball-verified.
  - [x] **Main menu** — Journey Onward (load PARTY.SAV, full wiring in step 6) / Initiate New Game / Return to view. C: TITLE_0.C C_0B45 + main switch.
  - [x] **Casting bracket (faithful)** — `CastingBracket` ports C_2C12 exactly: random pairings among non-eliminated virtues, reseed at q4/q6 → 8→4→2→1 in 7 questions; A keeps virtue a, B keeps b; survivor = class. Seeded via game.rng for reproducible tests.
  - [x] **Card presentation** — "the gypsy places the first/second/last two cards … they are the cards of X and Y" beats + the two virtue cards drawn, then the dilemma. C: TITLE_1.C C_2C12 (STR 0x35-0x38).
  - [x] **Animated title "monsters"** — the two creatures at the top corners (red phoenix dst (0,0) / green serpent dst (272,0)) cycle their real frames (`ultima4/title_anim.py`, tables parsed from DATA.C D_3380/D_33F8/D_344A/D_345C/D_3438; C: TITLE_0.C C_068C). **"Return to the view"** works: hides the menu over the animated title, any key restores it (C: C_05A4/C_0B45).
  - [x] **Animated "view" demo in the menu box** — the 19x5 overworld window around Lord British's castle (base map DATA.C D_3683) with the scripted demo: a moongate opens, a fighter leaves the castle, pirate ships sail, monsters roam (`ViewAnim` ports C_041A; the D_36E2 byte script + D_00C8 sprite bases parsed from DATA.C; sprites frame-cycle via anim_frame). Rendered at (8,104) per Gra_0; menu text overlays it (view-only on R). Water shimmer (C_34EA) still static.
  - [~] Refinements: exact card crop done (96x124 @ C_2B6D coords); intro music (BEEP.ASM) — no audio engine. History-of-Britannia book is framed by its narrative scenes (the actual Book text is a separate read).
- [x] **Intro/tarot editable JSON (extracted from the original)** — `tools/extract_intro.py` (`./run intro`) parses `SRC-TITLE/TITLE_1.C` `D_2EE6` + `TITLE_0.C` C_0B45 *verbatim* (C-string parser, no transcription drift) → `data/intro/{questions,cards,narrative,menus}.json`; loader `ultima4/intro_data.py` (single source of truth, no .C fallback). **questions.json** = 28 entries, one per virtue *pair* `{a_index,b_index,a_virtue,b_virtue,text}`, mapped by the original `STR(D_30CA[a]+b)` (A⇒a, B⇒b), original `\n` preserved. **cards.json** = each virtue→`{image,side}` (4 pair-images HONCOM/VALJUS/SACHONOR/SPIRHUM, even=left/odd=right; C: D_307E/C_2B6D). **narrative.json** = the 24 ordered scenes 0x1D..0x34 each w/ its backdrop (tree/portal/outside/inside/wagon/gypsy/abacus, derived from C_2883) + casting/finale fragments. **menus.json (Option C)** = title-screen lines w/ row/col + the 3 selectable options. `character_creation.py` now renders the verbatim question text via the loader (editing the JSON changes what's asked). selftest 56/56.
  - [x] Card-art↔question mapping in JSON (cards.json). Bracket+scoring stays code. **NOTE: pictures (tree/portal/wagon/gypsy/abacus + the 4 card images) still need PNG conversion — they decode via the LZW pipeline; add them to convert_graphics in step 5.**
- [x] **Class reveal** + gypsy speaks ("So be it! Thy path is chosen!", STR 0x42) → class + home towne. C: TITLE_1.C C_2C12.
- [x] **Moongate transport** — STR 0x43 over the PORTAL backdrop → drop into Britannia (build_party places the avatar at the class's start). C: TITLE_1.C C_2C12/C_2E04. (The moving moongate animation C_273E/C_27E0 is a still-backdrop refinement.)
- [ ] **Ending cinematic** — Codex revelation sequence (text in U4_END.C, no presentation yet).

### Quest progression (HIGH — game is winnable only by editing, not by playing)
- [x] **Search quest-item table** — `items.SEARCH_TABLE` ports `U4_SRCH.C` D_2920 verbatim: the
  Bell/Horn/Wheel/Skull (mItems), Book (Lycaeum), Candle (Cove), Black/White Stones, Mystic
  Armour (Empath)/Weapons (Serpent's Hold), Mandrake/Nightshade, and all 8 runes by location.
  Faithful gating ported: moon-new gate (mandrake/nightshade/skull/black-stone), 16-move reagent
  cooldown (f_1e8), one-shot bits, Mystic = all-karma-zeroed (full Avatarhood), Honor +5 & XP per
  find, "Drift Only!" while ballooning. selftest: Bell/runes/stones + Mystic gating.
- [~] **The 8 colored Stones** (`Party.mStones` bitmask) — White & Black are found by Search; the
  other 6 (used in the Abyss) come from dungeon altar rooms, still absent (`.DNG` room block).
- [x] **Use** effects ported faithfully (`items.use_item`, C: U4_USE.C D_0434): ring Bell → read
  Book → light Candle in order at the Abyss entrance (0xe9,0xe9) sets the ST_USE_* bits; Horn,
  Wheel (ship@hull-50 → 99), Skull (cast into Abyss = +10 karma all & ST_CAST_SKULL, else held
  aloft = destroy nearby monsters & -5 karma all), Key ("No place to Use them!"). **Abyss entry
  wired** (`cmd_enter`, C: U4_EXPLO.C C_3FB9): standing on the entrance enters Abyss.Dng only once
  the ritual is complete, else "Can't!". selftest: ritual order, Skull cast, Abyss gate.
- [ ] World placement of the runes (now *findable* by Search — see above), learnable mantras, the 3-part key.

### UI / presentation (vs original screen)
- [x] **Real text via the game's CHARSET font** — `play.py` now blits the original 8x8 CHARSET glyphs (`load_font_glyphs`/`blit_text`) for ALL panel text (status, messages, talk caret); SysFont removed. Glyphs sliced from `assets/charset.png` (ASCII-laid-out, verified 'A'==0x41); CGA font is 128 glyphs (loader derives count from the sheet).
  - [x] **Pagination/windowing (faithful):** `ultima4/textwin.py` (pure, tested) — `wrap_text` greedily wraps to the window width honoring embedded `\n` (original pre-wrapped prose untouched, edited text re-flowed; over-wide words hard-split), `paginate` chunks by window height (always ≥1 page), `pages_for` combines. Geometry cited from source: intro window 40 cols × 6 rows (`txt_Y=19`, TITLE_1.C), in-game 12-line pause (U4_LB.C C_E3D2). Panel messages now word-wrap to the panel width so they never overrun. Interactive fill-then-keypress page-flip wires up with the intro sequence (step 5).
- [ ] **PNG as the single source of truth for ALL graphics** (decided — no fallback, no dual sources):
  - [x] **LZW decoder ported** — `tools/lzw.py` (faithful port of `u4/forVS/lzw.c`: fixed 12-bit codes, hash-table dict, the 8086 MUL/RCL probe2). Verified: every full-screen picture .EGA → exactly 32000B (320x200 @4bpp), incl. all intro scenes (TITLE/GYPSY/ANIMATE/PORTAL/WAGON + paired card backdrops HONCOM/SACHONOR/SPIRHUM/VALJUS). **TODO: small symbol/rune images (RUNE_*, single-virtue, KEY7) use a 2nd format (not full-screen LZW) — identify the original loader before decoding (don't guess); not needed for the intro's main scenes.**
  - [x] **Converter + canonical PNGs** — `tools/convert_graphics.py` (`./run gfx`): SHAPES→`assets/shapes.png` (16x16 sheet), CHARSET→`assets/charset.png`, 13 full-screen pictures→`assets/*.png`. Picture layout confirmed empirically (linear 4bpp, 160 B/row, hi-nibble-left — vertical-transition test: linear 5055 vs even/odd 18598 vs planar noise). Spritesheet verified LOSSLESS (slice == direct decode). `.EGA` decoders + LZW live only in the tool.
  - [x] **Game loads PNG only** — play.py slices `assets/shapes.png` (+`_cga`) into 256 tiles and `assets/charset.png` for glyphs; no `.EGA`/decode_shapes at runtime (decoders live only in the tools). All boot modes (ega/cga/town) verified clean. SINGLE SOURCE OF TRUTH achieved for tiles/font; pictures ready for the intro.
  - Editing a PNG = editing the actual asset → changes in-game; viewable as PNG.
- [x] **Dialogue JSON is the single source of truth** — `dialogue.load_for_location` reads `data/dialogue/<Town>.json` ONLY (all 16 towns present); the `.TLK` binary is import-only, decoded once by `./run dump` (tools/dump_dialogue), never read at runtime. A missing JSON is a hard error (no silent .TLK fallback). Same single-source rule as .EGA→PNG. selftest verifies all 16 + that editing the JSON changes NPC lines.
- [x] **Maps are editable ascii-tilemaps — the single source of truth** (`ultima4/asciimap.py`,
  `tools/convert_maps.py` = `./run maps`, `data/maps/*.txt`). The last original binaries read at
  runtime — `WORLD.MAP` (overworld), 17 × `.ULT` (towns/castles), 8 × `.DNG` (dungeons) — now load
  from human-readable text. Format `ascii-tilemap v1`: a self-describing grid (embedded legend,
  mnemonic glyphs `~`water `.`grass `^`mtn `T`town `B`wall…) hardened against editor corruption —
  `|`…`|` row sentinels + fixed-width asserts + a `crc32` footer make a mangled file **reject loudly
  on load, never load silently-wrong** (critical: there is no binary backstop once originals are
  deleted). LOSSLESS incl. bytes the engine doesn't use yet: a town's full 256-byte NPC block
  (readable `# npcs:` hex table) and a dungeon's room-data block (4 KB / 16 KB Abyss — carried
  verbatim as hex, so the altar/stone rooms survive deletion). `world.py`/`location.py`/`dungeon.py`
  read the text; binaries are import-only. **Proven deletion-ready:** with all 27 map binaries moved
  out of `data/`, the game boots overworld→Britain→Deceit and the suite stays 75/75. selftest: every
  map round-trips byte-exact while the original exists, self-validates (crc) after it's gone, and a
  corruption-rejection test. C: U4_MAP.C / U4_EXPLO.C C_3E30 / U4_DNG.C.
  - **Deletion-readiness audit (what a full `data/` purge still needs).** Runtime is now 100% clean —
    it reads only PNG + JSON + ascii-maps + `PARTY.SAV`; **no original binary is read at runtime.**
    Safe to delete now (modern single source exists, parity-gated): `WORLD.MAP`, `*.ULT`, `*.DNG`,
    `*.TLK`, the full-screen `*.EGA` + `SHAPES`/`CHARSET`. Still BLOCK a full purge (unused at runtime,
    so deleting breaks nothing *today*, but loses art/data for unfinished features): the small
    symbol/rune `*.EGA` (`RUNE_*`, single-virtue, `KEY7`, `STONCRCL` — 2nd undecoded format, not yet
    PNG); the `*.CON` combat arenas + `CAMP.DNG` (combat generates a brick arena, never reads them —
    convert to ascii arenas before deleting); confirm `PARTY.NEW`/`AVATAR.EXE` hold nothing (templates
    live in code). Deletable cruft (nothing references): `*.EXE`/`*.COM`/`*.DRV`/`DOSBox*`, `*.PIC`
    (CGA-variant pics, redundant with the `.EGA`→PNG path). **Before deleting `.TLK`/`.EGA`**, give the
    dialogue/graphics parity selftests the same skip-if-original-absent treatment the map checks now
    use, so the suite stays green post-deletion.
- [ ] **Ornamental border** frame around the play area.
- [ ] **Party roster panel** — per-member number / name / HP / status (original = right side).
- [ ] Faithful **layout** (map-left / stats-right / prompt-bottom).
- [~] Moons — done (top-center, real glyphs; advance on the animation clock, not on movement — C_3A80). Water/field **procedural shimmer** (ANIMATED_FLOW tiles) not rendered. C: U4_ANIM.C C_34EA.

### Systems still simplified / absent
- [x] **Per-turn upkeep** (C: U4_MAIN.C C_1C53) — `ultima4/upkeep.py`: sleepers wake 1/8 per move, **poisoned members take 2/move**, `food_dec(party_size)` each move + **starvation** (all alive take 2), `MP_recover()` (per-class Int cap, +1/move clamped 99), hull self-repair (1, 1/3 of moves, <50), and the **all-dead → Lord British revive** (C_0EB1: throne room, full heal, strip gear, food=20099/gold=200). Wired into `end_turn` + the dungeon step (U4_DNG.C mirrors it). selftest: food/starvation, poison+wake, MP-by-class, revive.
- [x] **Status effects + environmental hazards** — `hazards.py` ports U4_EVT.C C_9209 (overworld
  branch): swamp/poison field poison a 'G' member (1/8), sleep field sleeps a conscious one (1/4),
  lava/fire burns the party on foot (1/2 → 10..24) or dents the hull at sea (sinking → LB revive).
  Closes the loop with upkeep.py (poison drains 2/move, sleepers wake 1/8). Bridge-troll ambush
  (TIL_17, 1/8 → combat) ported too. Wired into `end_turn` before upkeep (matching the C loop
  order). selftest: poison-then-drain, lava on-foot vs at-sea, troll ambush.
  Remaining: dungeon field/pit events, in-combat arena-tile hazards (U4_EVT.C dungeon/combat branches).
- [~] **Magic effects** — only 5/26 spell effects real; the other 21 acknowledge only; no in-combat casting. C: U4_SPELL.C.
- [~] **Combat** — generated brick arena (not real `.CON` maps); simplified hit/damage; **no monster special attacks** (U4_AI.C: Poison/Electrified/Fiery/Slept/Lava/Magical hits), no ranged/special AI, fleeing, slime-divide, gremlin-steal-food, hostile-NPC combat. C: U4_COMBA/B/C, U4_AI.
- [~] **Dungeons** — top-down (not first-person 3D, U4_3D.C); `.DNG` room block (4096B) skipped (altar rooms, the stones); no traps/typed-fountains/darkness/gremlins. C: U4_DNG.C.
- [~] **Transport** — no boardable ship/horse OBJECTS spawned in the world; Fire (cannons) does no damage; no Stable (buy horse); balloon wind, ship hull damage/sinking.
- [x] **Save/Load (minimal)** — `Game.cmd_quit` ports U4_Q_N_V.C CMD_Quit: "Quit & Save..." + move count, refuses inside a town/castle ("Not Here!", only overworld loc 0 or dungeon 0x11-0x18 may save), writes the byte-exact PARTY.SAV, sets `quit_requested` so play.py draws the save message and exits. `Game.load_saved()` (C: U4_INIT.C Load) restores the party + re-derives moon counters; "Journey Onward" on the title calls it (resumes on the overworld at the saved position). selftest: PARTY.SAV round-trips byte-exact, town-guard + resume verified (test backs up/restores the real save). MONSTERS.SAV/DNGMAP.SAV (overworld monster + dungeon map persistence) deferred.
- [ ] **Sound/music** — none.
- [ ] **Hawkwind** implemented but not placed as a reachable LCB NPC.
- [ ] Misc commands: New-order (reorder party), Volume, Yell (name/board), full multi-page Ztats, gem Peer full-map render.

## Working rules
- Faithful port first (cite the C function), verify against original behavior, then refactor to data.
- Every feature ships with a headless check wired into `tools/selftest.py` so `./run test` stays green.
- Push everything that is *data* into plain text; keep only genuine *rules* as (legible) code.
