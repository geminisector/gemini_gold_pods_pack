**Pod's Privateer Gemini Gold tweak pack\
v 2.86**

Overview

This pack accomplishes two goals:

-   fixes a ton of bugs, making the game much more playable and closer
    to the original Privateer. IMO, there is no point in playing PGG
    without this pack at all!

-   makes slight enhancements that improve the gameplay but it still
    stays like good old Privateer (rebalanced guns and trading,
    introduced new mission subtypes and many more)

Installation

**Just extract archive contents into your Privateer folder, overwrite
original PGG files.** You can also extract the files over a PGG with an
earlier tweak pack version installed, there will be no problems. Old
saves will work, but your ship will stay unchanged by the pack, unless
you sell it and buy a new one.

Unlike in early versions, if you want to pick just a part of the pack
you probably won't be able to.

Additional recommendations

1.  I strongly advice making the following changes to your
    vegastrike.config (it is in your game installation folder).\
    a) The following parameter affects gun [damage at long
    distance]{.underline}. Increase it slightly to make battles more
    challenging and fun:\
    \<var name=\"weapon_damage_efficiency\" value=\".7\"/\>\
    \
    b) Make [tractoring]{.underline} work much closer to original game:\
    \<var name=\"percent_to_tractor\" value=\"1\"/\>\
    \<var name=\"tractor.scoop_angle\" value=\"10.\"/\>\
    \
    c) Turn on the Shelton Slide, see PGG manual for details. You can
    use this slide effect in a few different ways. It is not available
    in original Privateer, but IMO improves gaming experience quite a
    lot. Also, you will have tough time fighting quick enemies w/o the
    slide, they will constantly hang on your back and shoot with
    impunity.\
    The following binds the slide to the "space" key. Ensure no other
    binding for "space" exists, and that original Shelton key binding
    removed or replaced:\
    \<bind key=\"space\" modifier=\"none\" command=\"SheltonKey\"/\>

2.  Rely on Dumbfire missiles at the beginning. Few hits from even the
    weakest of the guns accompanied by a direct missile hit will blow up
    Pirates and Retro ships in a second. Proton torpedoes are great as
    well, though in PGG it's really tricky to install a torpedo launcher
    instead of a missile launcher.

3.  ITTS radars are glitchy, so don't hurry to invest money.\
    In the "Righteous Fire" part, the Shield Regenerator upgrade does
    not work at all. Probably Thrust Enhancer does not give anything as
    well (or it's hardly noticeable), I'm not sure.

4.  The PGG project is unfinished, so there are a number of other known
    glitches; you can read about most of them in a Bug tracking topic at
    PGG forum.

List of changes (spoilers)

Below is the list of changes introduced by the tweak pack. Some smallish
changes omitted. Sorry for the mess.

1.  **Modified enemy/friendly ships you encounter:**\
    - Tarsus now has lasers instead of MassDrivers, improved cargo
    variety\
    - Galaxy has better guns, reduced shields from level 3 to 2,
    improved cargo variety\
    - hunters' Orion has better guns and missiles, but shields lvl4
    instead of 5. Drops cargo sometimes; merchants' Orion is different
    and is weaker all around\
    - all Centurions have better guns and missiles, but shields now
    level 2 instead of 3 (non-random Centurions might have custom
    equipment). Gun mounts moved closer to the center of the ship.\
    - Riordian, Seelig and Kroiz now fly unique and stronger ships, and
    may drop expensive cargo when killed\
    - Draymans have improved cargo variety; mounted guns were not
    working for some reason, so I placed a turret with two Meson
    Blasters\
    - Stiletto has better guns, but shields now lvl1 instead of lvl2\
    - Gladius has weaker shields (lvl 1 instead of 2), but better guns\
    - Demons now have better guns; fixed gun mounts positions\
    - slightly different guns for some Talons (e.g. weaker for Retro,
    stronger for Pirates)\
    - improved cargo variety for Retro and Pirates\
    - Broadswords now have shield 4 instead of 5, a bit better guns and
    drop cargo sometimes\
    - Gothri has a bit better guns, sometimes drops slaves or weaponry
    cargo; now shield2/gen4 instead of 3/4\
    - ejected and tractored pilots are legal to carry at any time! They
    can be "sold" at any base, the price is lowered however. Think of it
    like you rescue them for reward.\
    - reduced armor for Paradigm and Kamekh, was way too thick IMO

2.  **Reworked trading really hard:**\
    - altered a lot of prices, the overview of produce/demand is in
    *commodities.jpg* (can be considered as a spoiler)\
    - turned off in-flight random "trading", it was changing cargo
    quantities at bases in a minor way\
    - instead, the whole cargo list of the base is re-created
    approximately after a minute spent in open space, or if you visit
    another base\
    - while sitting at the base, cargo re-creation timer is stopped, you
    can't wait for changes this way\
    - save-reloading *does not* result in cargo replenish! I believe
    it's the best way to implement trading in Privateer\
    - trading contraband is super-profitable now. Notice that pirate
    bases in Pentonville, Capella and KM-252 usually have slightly less
    commodities for trade than Sherwood/Telar bases. To replenish
    commodities stock you have to either fly to another base or spend
    like 10 minutes in open space\
    - some cargos might randomly be "out of stock", you see this when
    quantity is 1-to-5\
    - one cargo quantity can be doubled; one cargo price can be reduced
    (can apply to the same cargo)\
    - prices are not static, but the variation is minor, mostly to add a
    realistic feeling

3.  **Adjusted prices for quite a lot of equipment,** biggest changes
    for radars. Also, radars now have varying detection range (higher
    price --- longer range)

4.  **Ship prices changed:** Orion 120000, Galaxy 80000, Centurion
    300000

5.  **Pirate bases now function as they should,** also fixed \"Unknown\"
    base names in Quine; cargo delivery mission to a pirate base now
    show VDU task name \"Deliver cargo to pirate base.\" instead of
    \"Deliver cargo to .\"

6.  **Incorporated some things from \"weapon and armor fix\"** (link
    below):\
    - armor is tougher, but isometal is not that hard, just as it should
    be: 2x of tungsten; accordingly lowered armor for some enemy ships
    that were affected by this improvement\
    - sound of Steltek weapons changed\
    - missiles made almost as damaging, but other parameters slightly
    differ (see missiles comparison picture). Dumbfires now very useful
    b/c they hit more often.\
    Fwiw, \"weapon and armor fix\" [is
    here](http://privateer.sourceforge.net/comlink/viewtopic.php?f=1&t=1007&p=5765&hilit=armor+fix&sid=d214dcfeb017ad42f9efcaac5a759a17#p5765)

7.  **All guns reworked,** but price changed only for plasma.\
    Tractor beam range increased, see advices above to improve
    tractoring success rate.\
    Proton torpedoes fly faster; it seemed PGG version was slower than
    it should...\
    The main aim was to make every gun useable, with effectiveness
    strictly correlating to the price. So there won't be things like
    worse/same gun for bigger money. See relative guns comparison
    picture.

8.  **Reworked the algorithm of random encounters,** IMO now it really
    resembles the feel of original game, and even better in terms of
    fun/logic/playability. As a side effect, eliminated "crowdness" at
    later stages, when anywhere you come you see a big clash of all
    kinds of ships. Note that every system has a chance of spawning an
    enemy ship, i.e. there are no totally safe locations.\
    In the Righteous Fire campaign, random retro groups are stronger and
    encountered with higher frequency.\
    A quick guide is below, the "safest" systems are:\
    - New Constantinople, New Detroit, Perry: very slim chance of enemy
    encounter, only single enemy units spawned, best friendly protection
    from militia etc. Theoretically, you can be "lucky" to encounter 1
    Gothri, 1 pirate Talon and 1 retro at the same spot, and no friendly
    ships, but I haven't seen such a thing yet.\
    - next come Troy, ND-57, Raxis, Manchester, Newcastle, Varnus:
    mostly free of enemies, but small pirate/retro groups (1 or 2 ships)
    might be seen sometimes\
    - Oxford and Shangri La, mostly as previous, with higher retro
    chance\
    - Junction, XXN-1927: good protection here, but pairs of pirates or
    retro are a normal encounter\
    - Pender\'s Star, Saxtogue, Metsor, 119ce, 44-p-im: choke systems
    with higher chance of small pirate ambushes, and less protected by
    militia etc\
    - other systems are tougher and should be avoided early on, or
    visited with higher caution. Many systems are not necessary awful,
    just you can run into a group of 3 pirates or smth similar... be
    prepared. Top left quadrant is pirate-infested, top-right gradually
    increases Kilrathi presence\
    - you can encounter a "pirates galaxy" in some systems like Telar,
    Capella etc. They always have an escort and counted as pirates
    "mobile bases"/freighters\
    - you can be lucky to encounter a Kilrathi Kamekh in border systems
    like Lisacc or blockade points. If you fly to Mah'Rahn and two other
    Kilrathi systems you will see random Kamekhs for sure.

9.  **CARGO missions**\
    - now cargo quantity varies from 10 to 40, shown in mission brief
    and affects payment\
    - route difficulty and length affects payment\
    - average payment is lowered, cargo run is effectively the easiest
    mission\...\
    - militia/confed per-route-system-search-risk increases payment in
    contraband runs\
    - mission cargo name now begins with an **\*** symbol (but
    Contraband still w/o it), and cannot be sold\
    - no "to-the-ship" deliveries, only regular bases like in original
    Privateer\
    - destination base *name* *and type* is shown in the mission brief!\
    - *new mission subtype:* cargo run with a likely ambush. These
    missions appear infrequently, and marked by a special note in a
    brief ("ambush is likely"); a system where an ambush will be
    triggered is randomly chosen from the path (not always but \>50%);
    you can run into retro ambush if mission cargo is "technological".
    Payed significantly better.\
    - *new mission subtype:* "express cargo run" which gives you 20%
    payment bonus on average. You are not allowed to land in the middle
    of such a mission. If you do, the payment will be halved.

10. **PATROL missions**\
    - encounter probability is 15-25% per navpoint\
    - no capships: it's a routine patrol, not a clean-sweep mission
    where we do know the enemy is strong and will be there\
    - minimum number of navpoints is 4, maximum is 6. For smaller
    systems all navpoints must be patrolled\
    - expected enemy type now visible in brief. Of course you will
    encounter random ships as a bonus\
    - reward based on enemy toughness, number of navpoints, travel route
    difficulty and overall toughness of a patrolled system\
    - dynamic task names made shorter to fit the VDU screen better

11. **ATTACK missions**\
    - added some missing \"enemy type\" and \"additional instructions\"
    hooks into attack_brief.txt\
    - encounter probability is 80% per navpoint or even higher\
    - number of navpoints can be 1, 2 or 3\
    - reward based on enemy toughness, number of navpoints, likelihood
    of (kilrathi) capships, travel route difficulty and toughness of a
    patrolled system\
    - separated from \"bounty\" mission type\
    - maximum is 1 capship per mission

12. **BOUNTY missions**\
    - reward based on enemy toughness, presence of escort, number of
    navpoints to look through, travel route difficulty and destination
    system toughness\
    - computer does not show at which navpoint your prey can be found\
    - increased initial appearance range of the prey. Sometimes it takes
    time to find it, unless you have good long range radar.\
    - prey does not always attack you (now 50% chance)\
    - *new mission subtype:* bounty on a \"notorious criminal\", who can
    fly Demon, Orion or Centurion and treated as a pirate. Nice way to
    combat hunter-type ships w/o any penalty to relations, plus a
    reward\
    - big variety of ship outfits and prey/escort combinations

13. **DEFEND missions**\
    - reward based on attackers power and travel route difficulty, plus
    a fixed bonus\
    - defendee will appear mostly at navpoints to reduce annoying
    accidential landings during the battle. Sometimes it will be near
    planets but the distance is increased for the same reason.\
    - there is a random chance (40% on average) for a militia, confed or
    hunter ship assistance. Additional enemy ship is spawned as well.

14. **RESCUE missions**\
    - reward based on attackers agility/strength and travel route
    difficulty, plus a fixed bonus\
    - there is a 30% chance for the enemies to lock on you instead of
    chasing the ejected pilot\
    - will appear in merchant guild if the pilot is a merchant\
    - more stable mission generation, i.e. you will see these kind more
    often. Systems with more enemies will have a higher chance for a
    rescue mission.

15. **ESCORT missions**\
    - 30% chance for each attacker to lock on you\
    - slight corrections in a briefing\
    - reward based on attack deadliness and escortees fragility\
    - escorts are only for Draymans, Galaxies, Tarsuses, Orions and
    Broadswords. Easier enemies when escorting a Tarsus\
    - Merchant Guild organizes escorts for merchant ships only\
    - dynamic task names made shorter to fit the VDU better\
    - there is a 40-50% chance to finish mission w/o being attacked\
    - have to escort ship to a planet when docking is required (fly
    close to 12000)\
    - more durable Tarsus in Escort missions

16. **SCOUT missions**\
    - implemented this sort of missions from scratch, similar to
    original Priv\
    - 40-to-70% chance of enemy encounter\
    - mission brief does not mention what type of enemy you will be
    facing\
    - predefined navpoint to scout, shown in mission brief\
    - available in Mission Computer and Mercenary Guild

17. **Fixed a number of bugs in different parts of the game,** like
    these and many more:\
    - fixed paired names for navpoints with asteroids. Now asteroids
    have blank name.\
    - patrol/attack missions: asteroids no longer count as navpoints\
    - all non-planet bases now of a \"neutral\" faction, so they won\'t
    suddenly become hostile\
    - fixed out-of-the-jump collisions that happened sometimes. Rarely I
    still bump into something invisible, which depletes front shields...
    have no clue what could it be\
    - Salthi and Drone ships now have explosion animations\
    - fixed a bug when missions carried over from a previously visited
    base\
    - fixed a solid bug: when you jump out into asteroid field you are
    no longer randomly teleported far away from that jump point (like
    when you travel to Rikel system). There are a few spots in game that
    affected by it, primarily campaign missions.\
    - fixed a very annoying bug: if you take a cargo mission, or finish
    one, PGG trading engine was not aware of this. As a result, either
    you were losing a portion of purchased cargo, or was not able to
    load full ship. Completely fixed this, at least I cannot reproduce
    the bug anymore\
    - fixed a bug: when you complete a mission, your Quine mission list
    is not cleared now\
    - fixed a bug that forced the game to generate missions that won't
    result travelling to systems that are hostile to your current system
    owning faction. Like, sitting in Nexus you never saw a mission to
    fly to a neighbor Capella, I consider it was a bug. Also, I made
    pirate bases in KM-252, Telar, Pentonville, Capella and Sherwood
    hidden so you won't see a cargo mission to fly there. All these
    things reside in a "universe\\wcuniverse.xml" file.\
    - Tarsus cargo expansion that is given when you start a new game is
    not bugged anymore

18. **Main campaign fixes and adjustments:**\
    - some slight ambush timings changes in Tayla missions; Riordian in
    4^th^ Tayla mission now has an animation on VDU bound to his speech;
    pirates now made friendly at the beginning of each Tayla mission;
    Riordian now flies along with "criminals" so when you kill them
    pirates remain friendly\
    - Lynch: when you speak to him after 2^nd^ mission (Kroiz), your
    record vs hunters is cleared. Same vs confeds after the 3^rd^
    mission. Ambush timing in 3^rd^ mission slightly changed. Miggs
    flies a dedicated Talon with a plasma gun mounted. Seelig, Kroiz and
    Miggs now have animations on VDU bound to their speech\
    - Masterson: fixed Toth speech, and he is significantly harder to
    defend now; 3^rd^ mission some Hunters will likely lock on you;
    4^th^ transport is a bit harder to defend. Also, relations vs
    hunters will be reset to slightly negative at the beginning of the
    4^th^ mission\
    - 1^st^ and 3^rd^ Murphy missions made tougher (increased the number
    of Demons you face); 2^nd^ mission is easier (3+3 Centurions).
    Demons and Centurions have better armor. After 1^st^ and 2^nd^
    missions relations vs random hunters are set to slightly negative,
    but they won't attack you yet. Final talk to Lynn sets relations vs
    hunters to moderately negative. 1^st^ and 2^nd^ mission enemies now
    fly near Nav 1 like in original Privateer. The blockade around Palan
    now functions similar to original Privateer.\
    - Monkhouse flight to Basra: ambush by 3gothris+3dralthis, with zero
    initial delay\
    - Taryn Cross missions have delay before ambush is triggered;
    asteroids now do not count as patrol points (was same glitch as in
    normal patrol missions); all 4 missions now show travel instructions
    and a \"Scanning..." procedure on VDU\
    - Garrovick has a moderately tough unique ship... previously it was
    randomly equipped, and now armor is about the same as in default PGG
    (was a bug)\
    - Kilrathi ambush in Gamma: instead of 10 Dralthis, now you are
    ambushed by 1 Kamekh, 3 Gothri and 5 Dralthi. This is closer to the
    original game, and more fun. It is possible to reconstruct the
    battle even closer, but IMO it's fine enough.\
    - Goodin mission: stronger Retro ambush in Perry\
    - mission briefs correctly displayed in Quine

19. **RF campaign -- similar changes** **and bugfixes** across the
    majority of the missions.

20. **Altered all spawning distances in random and campaign missions.**
    It is noticeable, and should make more sense/fun than default PGG.

21. **Random encounters: all ships now launched around visited
    navpoint,** not around you.

22. **Improved all mission briefs** shown in Quine.

23. **Retro now have two different ships outfits, pirates have three.**
    It was always strange to see every pirate fly exactly the same kind
    of Talon, like they were cloned somewhere. Campaign/computer
    missions are affected by this as well.

24. **Save/reloading does not change available missions list, and does
    not replenish commodities.** You have to fly to another base or
    spend some time in space now.

25. **Orions now have 3 gun mounts, better maneuverability and top
    cruise speed is 400.** It's a decent fighter now; try to finish both
    campaigns flying it!

26. **Galaxies top cruise speed increased**, now it is 350

27. Some **asteroids made bigger and harder** to blow up. Asteroid field
    combat becomes tougher; in this sense the gameplay becomes closer to
    Privateer.

28. **Scripted enemies talk to you** right when they are spawned during
    a mission

**If you want higher reward in computer missions:**

1\. Edit \"\\modules\\dynamic_mission.py\", find this spot:

def getPriceModifier(isUncapped):

return 1.0 #PODXX

2\. Put in a higher number, like 1.5 will make *every* mission 1.5x more
profitable

Feel free to send suggestions at any time to **podbelski@gmail.com**, or
leave a comment in a PGG forum.

**Enjoy!**
