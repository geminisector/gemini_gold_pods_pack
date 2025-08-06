import VS
import Director
import fg_util
import vsrandom
import faction_ships
import universe
import dynamic_universe
import dynamic_news
import debug
import generate_dyn_universe
import PickleTools
import dynamic_battle


global dnewsman_
dnewsman_ = dynamic_news.NewsManager()
baseship=None
plr=0
basefac='neutral'

mission_script_template = '''
import mission_lib
import %(module)s
temp=%(module)s.%(constructor)s%(args)r
mission_lib.AddMissionHooks(temp)
temp=0
'''

# PODXX per-system counters to track each generated mission type
perSystemMissions = {}

def resetPerSystemMissionsCounters():
  global perSystemMissions
  perSystemMissions = {}

def increaseMissionsCounter(missionKey):
  global perSystemMissions
  try:
    cnt = perSystemMissions[missionKey]
    perSystemMissions[missionKey] = cnt+1
  except:
    perSystemMissions[missionKey] = 1

def getMissionsCounter(missionKey):
  global perSystemMissions
  try:
    return perSystemMissions[missionKey]
  except:
    return 0

def isExcessiveMission(missionKey, cap):
    mcnt = getMissionsCounter( missionKey )
    if mcnt >= cap:
#      print "PODXXX excessive mission[" + missionKey + "] count[" + str(mcnt) + "]"
      return True
    else:
      return False

# load the company names & briefing text from files only once
company_names = []
cargo_briefs  = []
attack_briefs = []
patrol_briefs = []
defend_briefs = []
escort_briefs = []
rescue_briefs = []
bounty_briefs = []
scout_briefs  = []

def formatShip(ship):
    where=ship.find(".blank")
    if (where!=-1):
        ship=ship[0:where]
    return ship.capitalize()

def formatCargoCategory(ship):
    where=ship.rfind("/")
    if (where!=-1):
        ship=ship[where+1:]
    return ship.capitalize()

#Credit to Peter Trethewey, master of python and all things nefarious
def getSystemsKAwayNoFaction( start, k ):
    set = [start]#set of systems that have been visited
    pathset = [[start]]#parallel data structure to set, but with paths
    pathtor = [[start]]#parallel data structure to raw return systems with path
    r = [start] #raw data structure containing systems n away where n<=k
    for n in range(0,k):
        set.extend(r)
        pathset.extend(pathtor)
        r=[]
        pathtor=[]
        for iind in range(len(set)):
            i = set[iind]
            l = universe.getAdjacentSystemList(i)
            for jind in range(len(l)):
                j=l[jind]
                if not (j in set or j in r):
                    r.append(j)
                    pathtor.append(pathset[iind]+[j])
    return pathtor

def getSystemsNAway (start,k,preferredfaction):
    l = getSystemsKAwayNoFaction(start,k)
    if (preferredfaction==None):
        return l
    lbak=l
    if (preferredfaction==''):
        preferredfaction=VS.GetGalaxyFaction(start)
    i=0
    while i <len(l):
        if (VS.GetRelation(preferredfaction,VS.GetGalaxyFaction(l[i][-1]))<0):
            del l[i]
            i-=1
        i+=1
    if (len(l)):
        return l
    return lbak

syscreds=750

def LoadList(filename):
	bnl = []
	print 'Importing list from: ' + filename
	try:
		f = open (filename,'r')
		bnl = f.readlines()
		f.close()
	except:
		return []
	# strip newlines
	for i in range(len(bnl)):
		bnl[i]=bnl[i].rstrip()
	return bnl

def GetRandomFromList(list):
	import vsrandom
	idx = vsrandom.randint(0,len(list)-1)
	return list[idx]

def GetRandomCompanyName():
	#print 'reading company names '
	global company_names
	if (len(company_names) == 0):
		filename = 'universe/companies.txt'
		company_names = LoadList(filename)
	return GetRandomFromList(company_names)

def GetRandomCargoBrief():
	#print 'generating cargo briefing'
	global cargo_briefs
	if (len(cargo_briefs) == 0):
		filename = 'universe/cargo_brief.txt'
		cargo_briefs = LoadList(filename)
	return GetRandomFromList(cargo_briefs)

def GetRandomAttackBrief():
	#print 'generating attack briefing'
	global attack_briefs
	if (len(attack_briefs) == 0):
		filename = 'universe/attack_brief.txt'
		attack_briefs = LoadList(filename)
	return GetRandomFromList(attack_briefs)

def numPatrolPoints(sysname,cleansweep=0):
    npp = 0;
    try:
        import faction_ships
        mmax=faction_ships.numPatrolPoints[sysname]
        if mmax == 1:
          return 1
        
        if cleansweep:
          if mmax > 3:
            mmax = 3
          npp = vsrandom.randrange(1,mmax+1)
        
        else:
          if mmax <= 4:
            npp = mmax
          else:
            if mmax > 6:
              mmax = 6
            npp = vsrandom.randrange(4,mmax+1)
    except:
        npp = 1
    #print "PODXXX numPatrolPoints for system [" + sysname + "] is [" + str(npp) + "]"
    return npp

def GetRandomPatrolBrief():
	#print 'generating patrol briefing'
	global patrol_briefs
	if (len(patrol_briefs) == 0):
		filename = 'universe/patrol_brief.txt'
		patrol_briefs = LoadList(filename)
	return GetRandomFromList(patrol_briefs)

def GetRandomScoutBrief():
	#print 'generating scout briefing'
	global scout_briefs
	if (len(scout_briefs) == 0):
		filename = 'universe/scout_brief.txt'
		scout_briefs = LoadList(filename)
	return GetRandomFromList(scout_briefs)

def GetRandomDefendBrief():
	#print 'generating defend briefing'
	global defend_briefs
	if (len(defend_briefs) == 0):
		filename = 'universe/defend_brief.txt'
		defend_briefs = LoadList(filename)
	return GetRandomFromList(defend_briefs)

def GetRandomEscortBrief():
	#print 'generating escort briefing'
	global escort_briefs
	if (len(escort_briefs) == 0):
		filename = 'universe/escort_brief.txt'
		escort_briefs = LoadList(filename)
	return GetRandomFromList(escort_briefs)

def GetRandomRescueBrief():
	#print 'generating rescue briefing'
	global rescue_briefs
	if (len(rescue_briefs) == 0):
		filename = 'universe/rescue_brief.txt'
		rescue_briefs = LoadList(filename)
	return GetRandomFromList(rescue_briefs)

def GetRandomBountyBrief():
	#print 'generating bounty briefing'
	global bounty_briefs
	if (len(bounty_briefs) == 0):
		filename = 'universe/bounty_brief.txt'
		bounty_briefs = LoadList(filename)
	return GetRandomFromList(bounty_briefs)

def getCargoName(category):
    l=category.split('/')
    if len(l)>1:
        cargo = l[len(l)-1]+' '+l[0]
    else:
        cargo = category
    cargo = cargo.replace('_',' ')
    return cargo

def getMissionDifficulty ():
    import difficulty
    tmp=difficulty.getPlayerUnboundDifficulty(VS.getCurrentPlayer())
    if (tmp>1.5):
        tmp=1.5
    return tmp

def getPriceModifier(isUncapped):
    return 1.0    #PODXX
#    return 1.15
    import difficulty
    if (not difficulty.usingDifficulty()):
        return 1.0
    if (isUncapped):
        return getMissionDifficulty()/.5+.9
    return VS.GetDifficulty()/.5+.9

def getSystemDifficulty(system):
    shortname = system[7:]
    if shortname in ["Perry","New_Constantinople","New_Detroit"]:
      return .25
    if shortname in ["Troy","Oxford","Shangri_La","Manchester","ND-57","Raxis","Varnus","Junction","XXN-1927","Newcastle"]:
      return .5
    if shortname in ["Metsor","Penders_Star","Saxtogue","44-p-im","119ce","Pentonville"]:
      return 1.0
    if shortname in ["Nexus","Pyrenees","Regallis","Padre","Auriga","Midgard","Castor","Aldebran","Hinds_Variable_N"]:
      return 1.5
    if shortname in ["Rikel","Tingerhoff","Palan"]:
      return 2.0
    if shortname in ["Freyja","J900","Crab-12","Sherwood","New_Caledonia","Prasepe","Pollux","DN-N1912","CM-N1054"]:
      return 3.0
    if shortname in ["Rygannon","Xytani","Ragnarok","Nitir","Surtur","CMF-A"]:
      return 4.0
    if shortname in ["Capella","KM-252","Telar","17-ar","Death","Pestilence","War","Famine","Valhalla","Eden"]:
      return 4.0
    if shortname in ["Blockade_Point_Alpha","Blockade_Point_Charlie","Hyades","Blockade_Point_Tango","Lisacc","41-gs"]:
      return 5.0
    if shortname in ["Sumn_Kpta","Mah_Rahn","Tr_Pakh"]:
      return 8.0
      
    return 0.1   # just in case

def calcPathDifficulty(path,includeDest=1):
    diff = 0
    for p in path:
      if p == path[-1] and not includeDest:
        break
      diff += getSystemDifficulty(p)
    return diff

def calcPathLengthBonus(path):
    pl = len(path)
    if pl <= 3:
      return 0
    return (pl-3)*vsrandom.randrange(1000,1500)

def isDeadEndSystem(system):
    shortname = system[7:]
    return shortname in ["Rygannon","Shangri_La","Padre","Auriga","Hinds_Variable_N","Xytani","Prasepe","Pollux","DN-N1912","Hyades","CM-N1054","Lisacc","41-gs","Valhalla"]

def calcDeadEndBonus(curSystem, destSystem):
    bonus = 0
    if (curSystem != destSystem) and isDeadEndSystem(destSystem):
        bonus = vsrandom.randrange(800,1200)
    #print "PODXX calcDeadEndBonus curSystem[" + curSystem + "] destSystem[" + destSystem + "] bonus[" + str(bonus) + "]"
    return bonus

def howMuchHarder(makeharder):
    import difficulty
    if  (makeharder==0):
        return 0
    udiff = getMissionDifficulty()
    if (udiff<=1):
        return 0
    return int(udiff*2)-1

def processSystem(sys):
    k= sys.split('/')
    if (len(k)>1):
        k=k[1]
    else:
        k=k[0]
    return k

def isFixerString(s):
    k=str(s)
    if (len(k)<2):
        return 0
    if (k[1]=='F'):
        return 1
    if (k[1]=='G'):
        return 2
    return 0
    
def writemissionname(name,path,isfixer):
    if (isfixer==0):
        if path[-1]==VS.getSystemFile():
            name="In_System_"+name
    Director.pushSaveString(plr, "mission_names", name)

    
def writedescription(name):
    Director.pushSaveString(plr, "mission_descriptions", name.replace("_"," "))
def writemissionsavegame (name):
    Director.pushSaveString(plr, "mission_scripts", name)
def writemissionvars (vars):
    Director.pushSaveString(plr, "mission_vars", PickleTools.encodeMap(vars))
def eraseExtras():
	Director.clearSaveString(plr, "mission_scripts")
	Director.clearSaveString(plr, "mission_names")
	Director.clearSaveString(plr, "mission_descriptions")
	Director.clearSaveString(plr, "mission_vars")

def eraseExtrasOld():
    import sys
    len=Director.getSaveStringLength(plr, "mission_scripts")
    if (   len!=Director.getSaveStringLength(plr, "mission_names") \
        or len!=Director.getSaveStringLength(plr, "mission_descriptions") \
        or len!=Director.getSaveStringLength(plr, "mission_vars")   ):
        sys.stdout.write("Warning: Number of mission descs., names, scripts and vars are unequal.\n")
    if len>0:
        for i in range(len-1,-1,-1):
            Director.eraseSaveString(plr, "mission_scripts", i)
            Director.eraseSaveString(plr, "mission_names", i)
            Director.eraseSaveString(plr, "mission_descriptions", i)
            Director.eraseSaveString(plr, "mission_vars", i)

use_missioncomputer=1
fixer_has_rescue=0
fixer_has_wingman=0

fixerpct=0.0
guildpct=0.4

def randomCredModifier():
    return vsrandom.randrange(0,700) - 200
    
def getEnemyShipValue(enemy):
    if enemy == "retro":
      return 400
    elif enemy == "pirates":
      return 700
    elif enemy == "kilrathi":
      return 2000
    return 1500;

def generateCleansweepMission(path,numplanets,enemy):
    if enemy in ["merchant"]:
      return

    missionKey = "attack " + enemy + str(path[-1])
    if isExcessiveMission(missionKey, 1):
      return
    increaseMissionsCounter(missionKey)

    shipvalue = getEnemyShipValue(enemy)
    forceattack=1

    fighterprob=.8;
    if numplanets == 1:
      fighterprob = 1
    if numplanets == 2:
      fighterprob=.9
    
    minships=vsrandom.randrange(2,4)
    maxships=vsrandom.randrange(2,4)
    if minships > maxships:
      tmp = minships
      minships = maxships
      maxships = tmp
    
    if (numplanets == 1) and enemy in ["pirates","retro"]:
      minships = 3
      maxships = 4

    additionalinstructions=""
    capshipprob=0.0
    if (enemy=="kilrathi" and vsrandom.random()<.06125):
        capshipprob=vsrandom.random()*.25;
    if (capshipprob):
        additionalinstructions+="Capital ships possibly in the area."
    
    creds = int( randomCredModifier() + capshipprob*10000*numplanets + ( numplanets * shipvalue * ((maxships+minships) / 2.0) * (1+0.2*forceattack) ) + 800*calcPathDifficulty(path,0) + 800*numplanets*getSystemDifficulty(path[-1]) + calcDeadEndBonus(path[0],path[-1]) + calcPathLengthBonus(path) )

    creds*=getPriceModifier(False)
    bcreds = creds
    addstr=""
    isFixer=vsrandom.random()
    if isFixer<guildpct:
        if (creds*1.4) <= 20000:
          creds*=1.4
        elif creds <= 30000:
          creds*=1.25
        addstr+="#G#Attack#\n"
    elif use_missioncomputer:
        addstr+="#C#Attack#\n"

    print "PODXXX " + addstr + " num [" + str(numplanets) + "] enemy [" + str(enemy) + "] minmaxships [" + str(minships) + "-" + str(maxships) + "] creds [" + str(bcreds) + "/" + str(creds) + "] prob [" + str(fighterprob) + "-" + str(capshipprob) + "] path " + str(path)

    dist=1500
    patrolorclean="Clean_Sweep"
    missiontype="cleansweep"

    randCompany = GetRandomCompanyName()
    attackb = GetRandomAttackBrief()
    composedBrief = attackb.replace('$CL',randCompany)
    composedBrief = composedBrief.replace('$MT',enemy.capitalize())
    composedBrief = composedBrief.replace('$NP',str(int(numplanets)))
    composedBrief = composedBrief.replace('$DS',processSystem(path[-1]))
    composedBrief = composedBrief.replace('$PY',str(int(creds)))
    composedBrief = composedBrief.replace('$IN',additionalinstructions)
    
    ispoint="s"
    if numplanets==1:
        ispoint=""
        composedBrief = composedBrief.replace('points','point')
    if len(path)==1:
        mistype = 'IN-SYSTEM ATTACK'
    else:
        mistype = 'ATTACK'
        
    writedescription(composedBrief)
    writemissionsavegame (addstr+mission_script_template % dict(
        module=missiontype,
        constructor=missiontype,
        args=(0,numplanets,dist,creds,path,'',minships,maxships,fighterprob,capshipprob,enemy,forceattack,1,[],"randomize") ))

#    writemissionname("%s/%s_%d_navpoint%s_from_%s_in_%s_system._Autopay_%i_credits."%(patrolorclean,patrolorclean,numplanets,ispoint,enemy, processSystem(path[-1]),creds),path,isFixerString(addstr))
    writemissionname("%s/%s %d navpoint%s from %s in %s system. Autopayment %i credits."%(patrolorclean,patrolorclean,numplanets,ispoint,enemy.capitalize(), processSystem(path[-1]),creds),path,isFixerString(addstr))
    writemissionvars( { 'MISSION_TYPE' : mistype } )

def generatePatrolMission (path,numplanets,enemy):
    if enemy in ["merchant","confed","militia"]:
      return

    missionKey = "patrol " + str(path[-1])
    if isExcessiveMission(missionKey, 2):
      return
    increaseMissionsCounter(missionKey)

    shipvalue = getEnemyShipValue(enemy)

    dist=400
    fighterprob=vsrandom.randrange(15,25)*.01
    forceattack=vsrandom.randrange(0,2)
    minships=0
    maxships=vsrandom.randrange(1,4)
    creds = int( randomCredModifier() + ( fighterprob * numplanets * shipvalue * maxships * (1+0.2*forceattack) ) + 800*calcPathDifficulty(path,0) + numplanets*1200*getSystemDifficulty(path[-1]) + calcDeadEndBonus(path[0],path[-1]) + calcPathLengthBonus(path) )

    #PODXX no capships, it's a routine patrol...
    capshipprob=0

    additional=()
    additionalinstructions=""
    creds*=getPriceModifier(False)
    bcreds = creds
    addstr=""
    isFixer=vsrandom.random()
    if isFixer<guildpct:
        if (creds*1.3) <= 15000:
          creds*=1.3
        elif creds <= 25000:
          creds*=1.2
        addstr+="#G#Patrol#\n"
    elif use_missioncomputer:
        addstr+="#C#Patrol#\n"

    print "PODXXX " + addstr + " [" + str(numplanets) + "] enemy [" + str(enemy) + "] maxships [" + str(maxships) + "] fa [" + str(forceattack) + "] creds [" + str(bcreds) + "/" + str(creds) + "] prob [" + str(fighterprob) + "] path " + str(path)

    randCompany = GetRandomCompanyName()
    patrolb = GetRandomPatrolBrief()
    composedBrief = patrolb.replace('$CL',randCompany)
    composedBrief = composedBrief.replace('$NP',str(int(numplanets)))
    composedBrief = composedBrief.replace('$DS',processSystem(path[-1]))
    composedBrief = composedBrief.replace('$PY',str(int(creds)))
    composedBrief = composedBrief.replace('$EN',(str(enemy)).capitalize())
    ispoint="s"
    if numplanets==1:
        ispoint=""
    if len(path)==1:
        mistype = 'IN-SYSTEM PATROL'
    else:
        mistype = 'PATROL'
    writedescription(composedBrief)
    writemissionsavegame (addstr+mission_script_template % dict(
        module='patrol_enemies',
        constructor='patrol_enemies',
        args=(0, numplanets, dist, creds, path, '', minships, maxships, fighterprob, capshipprob, enemy, forceattack, [],"randomize") ))
#    writemissionname("Patrol/Patrol_%d_navpoint%s_in_%s_for_%s_presence._Autopay_%i_credits."%(numplanets,ispoint, processSystem(path[-1]),enemy,creds),path,isFixerString(addstr))
    writemissionname("Patrol/Patrol %d navpoint%s in %s for %s presence. Autopayment %i credits."%(numplanets,ispoint, processSystem(path[-1]),enemy.capitalize(),creds),path,isFixerString(addstr))
    writemissionvars( { 'MISSION_TYPE' : mistype } )
 
def generateScoutLocalMission(path,enemy):
    if len(path) > 1:
      return
    missionKey = "scout " + enemy + str(path[0])
    if isExcessiveMission(missionKey, 2):
      return
    increaseMissionsCounter(missionKey)

    shipvalue = 800   #getEnemyShipValue(enemy)
    forceattack=vsrandom.random()>.5

    fighterprob=vsrandom.randrange(40,70)*0.01;
    
    sysdiff = getSystemDifficulty(path[-1])
    
    if enemy in ["retro","pirates"]:
      minships=vsrandom.randrange(2,4)
      maxships=vsrandom.randrange(minships,4)
      q = 2
      if sysdiff < 1:
        q = 1.5
        minships -= 1
        maxships -= 1
    else:
      minships = maxships = 1
      q = 1.5
      if sysdiff >= 2:
        q = 2.5
        maxships = 2

    sysName = processSystem(path[0])
    navpoints = universe.getNonBaseSignificants()
    scoutSigName = (navpoints[ vsrandom.randrange(0,len(navpoints)) ]).getName()
    
    creds = int( randomCredModifier() + shipvalue * q * (1+0.2*forceattack) + 500*2*sysdiff )

    creds*=getPriceModifier(False)
    bcreds = creds
    addstr=""
    isFixer=vsrandom.random()
    if isFixer<guildpct:
        if (creds*1.3) <= 10000:
          creds*=1.3
        else:
          creds*=1.2
        addstr+="#G#Scout#\n"
    elif use_missioncomputer:
        addstr+="#C#Scout#\n"

    print "PODXXX " + addstr + " scoutSigName[" + scoutSigName + "] enemy [" + str(enemy) + "] minmaxships [" + str(minships) + "-" + str(maxships) + "] creds [" + str(bcreds) + "/" + str(creds) + "] prob [" + str(fighterprob) + "] fa[" + str(forceattack) + "] path " + str(path)

    dist=1500
    missiontype="scout"

    composedBrief = GetRandomScoutBrief().replace('$CL',GetRandomCompanyName())
    composedBrief = composedBrief.replace('$NP',scoutSigName)
    composedBrief = composedBrief.replace('$DS',sysName)
    composedBrief = composedBrief.replace('$PY',str(int(creds)))
    
    path=[path[0]]
    mistype = 'IN-SYSTEM SCOUT'
        
    writedescription(composedBrief)
    writemissionsavegame (addstr+mission_script_template % dict(
        module='patrol_enemies',
        constructor='patrol_enemies',
        args=(0,1,dist,creds,path,'',minships,maxships,fighterprob,0,enemy,forceattack,[],"randomize",[scoutSigName]) ))
    writemissionname("Scout/Scout %s in %s system for enemy presence. Autopayment %i credits."%(scoutSigName,sysName,creds),path,isFixerString(addstr))
    writemissionvars( { 'MISSION_TYPE' : mistype } )

def isNotWorthy(fac):
    return VS.GetRelation(fac,VS.getPlayer().getFactionName()) <= -0.06
    
def generateEscortLocal(path,lowerCasedShipType,fac,enfac=''):
    if (isNotWorthy(fac)):
        return
        
    shipType = lowerCasedShipType.capitalize()
    defendeeFragility = 0
    if shipType in ["Tarsus"]:
      defendeeFragility = 700
    elif shipType in ["Galaxy","Drayman"]:
      defendeeFragility = 600
    elif shipType in ["Orion"]:
      defendeeFragility = 500
    elif shipType in ["Broadsword"]:
      defendeeFragility = 500
    else:
      return
        
    if not len(enfac):
        enfac = faction_ships.get_enemy_of(fac)
    attackStrength = 300 + getEnemyShipValue(enfac)
    
    waves=1      #PODXX we count total number of waves here, not just "additional waves"
    diff=1
    if enfac in ["kilrathi"]:
      waves=vsrandom.randrange(1,3)
      diff=vsrandom.randrange(1,3)
    elif enfac in ["retro"]:
      waves=vsrandom.randrange(1,4)
      if waves == 1:
        diff=vsrandom.randrange(3,5)
      elif waves == 2:
        diff=vsrandom.randrange(2,4)
      else:
        diff=2
    else:
      waves=vsrandom.randrange(1,4)
      if waves == 1:
        diff=vsrandom.randrange(2,4)
      elif waves == 2:
        diff=2
      else:
        diff=vsrandom.randrange(1,3)
      
    if shipType in ["Tarsus"]:
      if enfac in ["kilrathi"]:
        diff = 1
        waves = 1
      elif enfac in ["retro"]:
        waves = vsrandom.randrange(1,3)
        diff=2
      else:
        waves = vsrandom.randrange(1,3)
        if waves == 2:
          diff = 1
        else:
          diff = 2

    waveStrength = 1 - .15*(diff == 1)

    missionKey = "escort " + shipType + enfac
    if isExcessiveMission(missionKey, 1):
      return
    increaseMissionsCounter(missionKey)

    attackProb = vsrandom.randrange(50,60)*0.01;

#    creds = int( randomCredModifier() + 500 + attackProb*(attackStrength + defendeeFragility)*1.5*2*waveStrength + 600*2*getSystemDifficulty(path[0]) )
    creds = int( randomCredModifier() + (attackStrength + defendeeFragility)*1.5*2*waveStrength + 600*2*getSystemDifficulty(path[0]) )

    incoming=vsrandom.randrange(0,2)
    isFixer=vsrandom.random()
    creds*=getPriceModifier(False)
    bcreds = creds
    addstr=""
    if isFixer<guildpct and (fac in ["merchant"]):         #PODXX merchant guild will protect merchants only
        creds*=1.3
        addstr+="#G#Escort#\n"
    elif use_missioncomputer:
        addstr+="#C#Escort#\n"
        
    print "PODXXX " + addstr + " [" + fac + " " + str(shipType) + "] enemy [" + enfac + "] quantity-waves [" + str(diff) + "-" + str(waves) + "] creds [" + str(bcreds) + "/" + str(creds) + "] " + str(path[0])
    
    additionalinfo="TO the jump point"
    if (incoming):
        additionalinfo="FROM the jump point to a base"

    randCompany = GetRandomCompanyName()
    escortb = GetRandomEscortBrief()
    composedBrief = escortb.replace('$CL',randCompany)
    composedBrief = composedBrief.replace('$MT',enfac.capitalize())
#    composedBrief = composedBrief.replace('$DS',processSystem(path[-1]))
    composedBrief = composedBrief.replace('$PY',str(int(creds)))
    composedBrief = composedBrief.replace('$AI',additionalinfo)
    composedBrief = composedBrief.replace('$ET',shipType)
    mistype = 'IN-SYSTEM ESCORT'
    writedescription(composedBrief)
    writemissionsavegame(addstr+mission_script_template % dict(
        module='escort_local',
        constructor='escort_local',
        args=(enfac,0,diff,max(0,waves-1),1500,creds,incoming,fac,(),'','','','',lowerCasedShipType,universe.getRandomGreeting(enfac),.3,attackProb)))
#        args=(enfac,0,diff,max(0,waves-1),1500,creds,incoming,fac,(),'','','','',lowerCasedShipType,['...','...'],.3,attackProb)))
#    writemissionname("Escort/Escort_%s_%s,_expect_%s_attack._Autopay_%i_credits."%(fac,shipType,enfac,creds),[path[-1]],isFixerString(addstr))
    writemissionname("Escort/Escort %s %s %s, expect %s attack. Autopayment %i credits."%(fac.capitalize(),shipType,additionalinfo,enfac.capitalize(),creds),[path[-1]],isFixerString(addstr))
    writemissionvars( { 'MISSION_TYPE' : mistype } )


def generateEscortMission (path,fg,fac):
    if (isNotWorthy(fac)):
        return
    typ = fg_util.RandomShipIn(fg,fac)
    if typ in faction_ships.unescortable:
        typ = faction_ships.unescortable[typ]
    diff=vsrandom.randrange(0,6)
    creds=250*diff+1.2*syscreds*len(path)
    creds*=getPriceModifier(False)
    addstr=""
    isFixer=vsrandom.random()
    if isFixer<fixerpct:
        creds*=2
        addstr+="#F#bases/fixers/merchant.spr#Talk to the Merchant#Thank you. I entrust that you will safely guide my collegue until you reach the destination.#\n"
    elif isFixer<guildpct:
        creds*=1.4
        addstr+="#G#Escort#\n"
    elif use_missioncomputer:
        addstr+="#C#Escort#\n"
    if len(path)==1:
        mistype = 'IN-SYSTEM ESCORT'
    else:
        mistype = 'ESCORT'
    writemissionsavegame (addstr+mission_script_template % dict(
        module='escort_mission',
        constructor='escort_mission',
        args=(fac,diff,float(creds),0,0,path,'',fg,typ)))
    writedescription("The %s %s in the %s flightgroup requres an escort to %s. The reward for a successful escort is %d credits."%(fac,formatShip(typ),fg, processSystem(path[-1]),creds))
    writemissionname("Escort/Escort_%s_%s_to_%s"%(fac,fg,processSystem(path[-1])),path,isFixerString(addstr))
    writemissionvars( { 'MISSION_TYPE' : mistype } )

def changecat(category):
    l=category.split('/')
    if len(l)>1:
        return l[-1]+'_'+l[0]
    else:
        return category

def pathWarning(path,isFixer):
    global dnewsman_
    message = str()
    factions = list()
    if isFixer:
        message+="\nPrecautions taken to ensure the success of this mission should be taken at your expense."
    else:
        for system in path:
            sysfac = VS.GetGalaxyFaction(system)
            if sysfac not in factions:
                factions.append(sysfac)
        message+="\n\nYou are responsible for the success of this mission.  Precautions taken to ensure this outcome will be taken at your expense.  With that in mind, I will advise you that you will be travalling through systems dominated by the "
        if len(factions) == 1:
            message+=dnewsman_.data.getFactionData(factions[0],'full')[0]+"."
        else:
            message+="following factions: "
            jj=0
            for fac in factions:
                jj+=1               
                message+=dnewsman_.data.getFactionData(fac,'full')[0]
                if jj<len(factions)-1:
                    message+=", "
                elif jj<len(factions):
                    message+=" and "
    return message
def adjustQuantityDifficulty(max):
   return 3+int((max-3)*VS.GetDifficulty())
def isHabitable (system):
    planetlist=VS.GetGalaxyProperty(system,"planets")
    if (len(planetlist)==0):
        return False
    planets=planetlist.split(' ')
    for planet in planets:
        if planet=="i" or planet=="a" or planet=="am" or planet=="u" or planet=="com" or planet=="bd" or planet=="s" or planet=="o" or planet=="at" or planet=="bs" or planet=="bdm" or planet=="bsm" or planet=="f" or planet=="fm" or planet=="t":
            return True
    debug.debug(str(planets)+ " Not in Habitable List")
    return False
    

def getMilitiaRisk4System(system):
    shortname = system[7:]
    if shortname in ["Perry","New_Constantinople","New_Detroit","Tingerhoff","Junction","XXN-1927"]:
      return 0.9
    if shortname in ["Troy","Manchester","ND-57","Raxis","Newcastle","Varnus","New_Caledonia","Hinds_Variable_N"]:
      return 0.65
    if shortname in ["Metsor","Oxford","Penders_Star","Saxtogue","44-p-im","119ce"]:
      return .3
    if shortname in ["Sherwood","Nexus","Rikel","Pyrenees","Regallis","Padre","Auriga","Midgard","Shangri_La","Castor","Palan","Aldebran"]:
      return .5
    if shortname in ["Rygannon","Xytani","Ragnarok","Nitir","Surtur","CMF-A"]:
      return .5
    if shortname in ["Freyja","J900","Crab-12","Prasepe","Pollux","DN-N1912"]:
      return .3
    if shortname in ["Blockade_Point_Alpha","Blockade_Point_Charlie","Hyades","Blockade_Point_Tango","Lisacc"]:
      return .65
    if shortname in ["Capella","KM-252","Telar","17-ar","Death","Pestilence","War","Famine","Valhalla","Eden"]:
      return 0.1
    if shortname in ["Sumn_Kpta","Mah_Rahn","Tr_Pakh"]:
      return 0.1
      
    return 0.1   # ,"41-gs","CM-N1054","Pentonville"

def calcMilitiaRisk(path):
    risk = 0
    for p in path:
      risk += getMilitiaRisk4System(p)
    return risk
    
systemsBaseDict = {
      'Gemini/Oxford':['Oxford'],
      'Gemini/XXN-1927':['Jolson','Joplin'],
      'Gemini/Saxtogue':['Olympus'],
      'Gemini/New_Detroit':['New_Detroit'],
      'Gemini/New_Constantinople':['New_Constantinople','Edom'],
      'Gemini/Aldebran':['Matahari'],
      'Gemini/Auriga':['Beaconsfield','Elysia'],
      'Gemini/Castor':['Romulus'],
      'Gemini/Hyades':['Charon'],
      'Gemini/Junction':['Victoria','Speke','Burton'],
      'Gemini/DN-N1912':['N1912-1'],
      'Gemini/Lisacc':['Lisacc'],
      'Gemini/Manchester':['Wickerton','Thisbury'],
      'Gemini/Midgard':['Heimdal'],
      'Gemini/ND-57':['New_Reno'],
      'Gemini/New_Caledonia':['Edinburgh','Glasgow'],
      'Gemini/Newcastle':['Liverpool'],
      'Gemini/Nexus':['Macabee'],
      'Gemini/Nitir':['Nitir'],
      'Gemini/Padre':['Magdaline'],
      'Gemini/Prasepe':['Saratov'],
      'Gemini/Pyrenees':['New_Iberia','Basque'],
      'Gemini/Palan':['Palan','Basra'],
      'Gemini/Perry':['Anapolis','Perry_Naval_Base'],
      'Gemini/Pollux':['Remus'],
      'Gemini/Regallis':['Kronecker'],
      'Gemini/Rikel':['Siva','Vishnu'],
      'Gemini/Ragnarok':['Mjolnir'],
      'Gemini/Raxis':['Gracchus','Trinsic'],
      'Gemini/Tingerhoff':['Bodensee','Munchen'],
      'Gemini/Rygannon':['Rygannon'],
      'Gemini/Surtur':['Surtur'],
      'Gemini/Troy':['Achilles','Helen','Hector'],
      'Gemini/Varnus':['Rilke','Rodin'],
      'Gemini/Valhalla':['Valkyrie'],
      'Gemini/Shangri_La':['Erewhon'],
      'Gemini/Hinds_Variable_N':['Meadow','Oresville']
    }
    
def getRandomBaseName(sysName):
    try:
      sysBases = systemsBaseDict[sysName]
      return sysBases[ vsrandom.randrange(0,len(sysBases)) ]
    except:
      return ''

refineryBases = ['Beaconsfield','Joplin','Meadow','Rilke','Munchen','Gracchus','Remus','Anapolis','Basra','Liverpool','Edinburgh','Glasgow','Wickerton','Thisbury',]
agriculturalPlanets = ['Burton','Edom','Elysia','Victoria','Oresville','Erewhon','Rodin','Helen','Surtur','Bodensee','Trinsic','Mjolnir','Siva','Palan','New_Iberia','Nitir','Heimdal',]
pleasurePlanets = ['Magdaline','New_Reno','N1912-1','Speke','Matahari','Olympus','Jolson']
miningBases = ['Valkyrie','Achilles','Hector','Rygannon','Vishnu','Kronecker','Basque','Saratov','Macabee','Lisacc','Charon','Romulus',]

def getBaseType(baseName):
    if baseName in refineryBases:
      return " (refinery)"
    if baseName in agriculturalPlanets:
      return " (agricultural)"
    if baseName in pleasurePlanets:
      return " (pleasure)"
    if baseName in miningBases:
      return " (mining)"
    return ""

def generateCargoMission (path, numcargos,category, fac):
    launchcap = 0
    if (not launchcap) and not isHabitable(path[-1]):
        return False
    if (category==''):     # sometimes it happen?
        category='Iron'

    missionKey = "cargo " + str(path[-1])
    if isExcessiveMission(missionKey, 2):
      return False
    increaseMissionsCounter(missionKey)

    destBaseName = getRandomBaseName(path[-1])
    baseType = getBaseType(destBaseName)
    
    isExpress = (len(path) > 2) and (vsrandom.random() < .33)
    
    ambushChance = vsrandom.random()
    if ambushChance < .6 or ambushChance > .8:
        ambushChance = 0
    
    pathDiff = calcPathDifficulty(path)
    creds = int( randomCredModifier() + 40*numcargos + ambushChance*4000 + pathDiff*800 + (category == "Contraband")*2000*calcMilitiaRisk(path) + calcDeadEndBonus(path[0],path[-1]) + calcPathLengthBonus(path))
    if isExpress:
        creds *= 1.2

    creds*=getPriceModifier(False)
    bcreds = creds
    addstr=""
    isFixer=vsrandom.random()
    if category != 'Contraband' and isFixer<.7:             #PODXX increased a bit, cargo runs must be less available via missioncomputer
        if creds*1.3 < 15000:
            creds*=1.3
        else:
            creds*=1.2
        addstr+="#G#Cargo#\n"
    elif use_missioncomputer:
        addstr+="#C#Cargo#\n"

    print "PODXXX " + addstr + " [" + category + "-" + str(numcargos) + "] pathDiff [" + str(pathDiff) + "] ambush[" + str(ambushChance) + "] creds [" + str(bcreds) + "/" + str(creds) + "] isExpress[" + str(isExpress) + "] path " + str(path) + " " + destBaseName

    cargoName = category
    if category == 'Contraband':
        contrabands = ['Brilliance','Tobacco','Slaves','Ultimate']
        cargoName = contrabands[vsrandom.randrange(0, len(contrabands))]

    writemissionsavegame (addstr+mission_script_template % dict(
        module='cargo_mission',
        constructor='cargo_mission',
        args=(fac,0,numcargos,ambushChance,creds,launchcap,0,cargoName,path,'',destBaseName,isExpress)))
    randCompany = GetRandomCompanyName()
    if (randCompany==''):
        strStart = "We need to deliver some "
    else:
        strStart = randCompany+" seeks delivery of "
    if len(path)==1:
        mistype = 'IN-SYSTEM CARGO'
    else:
        mistype = 'CARGO'
    brief = GetRandomCargoBrief()
    
    if isExpress:
        brief = "EXPRESS delivery! " + brief + " Payment will be HALVED for landings enroute."
    
    ambushText = ''
    if ambushChance > 0:
        ambushText = " Scouts report an AMBUSH is likely along the route."

    if (brief<>''):
        composedBrief = brief.replace('$CL',randCompany)
        composedBrief = composedBrief.replace('$CG',str(numcargos) + " " + formatCargoCategory(category))   #PODXX now quantity will appear in a brief!
        composedBrief = composedBrief.replace('$DB',destBaseName + baseType)
        composedBrief = composedBrief.replace('$DS',processSystem(path[-1]))
        composedBrief = composedBrief.replace('$PY',str(int(creds)))
        composedBrief = composedBrief.replace('$AM', ambushText)
        writedescription(composedBrief)
    else:
        writedescription(strStart+"%s cargo to the %s system. The mission is worth %d credits to us.  You will deliver it to a base owned by the %s.%s"%(formatCargoCategory(category), processSystem(path[-1]),creds,fac,pathWarning(path,isFixer<guildpct)))

    briefDest = processSystem(path[-1])
    if len(destBaseName):
        briefDest = destBaseName + baseType + " in " + briefDest

    if ambushChance > 0:
        ambushText = " Ambush is likely."

    expressText = ""
    if isExpress:
        expressText = " Express delivery."
       
#    writemissionname("Cargo/Deliver_%i_%s_to_%s_system.%s_Autopay_%i_credits.%s"%(numcargos,changecat(category),briefDest,ambushText,creds,expressText),path,isFixerString(addstr))
    writemissionname("Cargo/Deliver %i %s to %s system.%s Autopayment %i credits.%s"%(numcargos,changecat(category),briefDest,ambushText,creds,expressText),path,isFixerString(addstr))
    writemissionvars( { 'MISSION_TYPE' : mistype, 'NUMCARGOS' : numcargos } )   #PODXX added variable cargo quantity support
    return True


def generateRescueMission(path,rescuelist):
    rescueFac = rescuelist[0]
    enemyFac = rescuelist[2]

    if (isNotWorthy(rescueFac)):
        return
        
    missionKey = "rescue " + str(path[-1])
    if isExcessiveMission(missionKey, 1):
      return
    increaseMissionsCounter(missionKey)

    attackStrength = 1000
    if enemyFac in ["merchant"]:
      attackStrength = 500
    
    numships = vsrandom.randrange(1,3)
    
    creds = int( randomCredModifier() + attackStrength*numships + numships*1500*(enemyFac=="kilrathi") + 2000 + 800*calcPathDifficulty(path) + calcDeadEndBonus(path[0],path[-1]) )
    
    creds*=getPriceModifier(False)
    bcreds = creds
    addstr = ""
    isFixer=vsrandom.random()
    if (rescueFac == "merchant"):
        creds*=1.5
        addstr+="#G#Rescue#\n"
    elif use_missioncomputer:
        addstr+="#C#Rescue#\n"
        
    print "PODXXX " + addstr + " [" + rescueFac + "] from [" + enemyFac + "] numships [" + str(numships) + "] creds [" + str(bcreds) + "/" + str(creds) + "] path " + str(path)

    if len(path)==1:
        mistype = 'IN-SYSTEM RESCUE'
    else:
        mistype = 'RESCUE'
        
    randCompany = GetRandomCompanyName()
    rescueb = GetRandomRescueBrief()
    composedBrief = rescueb.replace('$CL',randCompany)
    composedBrief = composedBrief.replace('$MT',rescueFac.capitalize())
    composedBrief = composedBrief.replace('$AT',str(int(numships)))
    composedBrief = composedBrief.replace('$AN',enemyFac.capitalize())
    composedBrief = composedBrief.replace('$DS',processSystem(path[-1]))
    composedBrief = composedBrief.replace('$PY',str(int(creds)))
    
    writedescription(composedBrief)
    writemissionsavegame (addstr+mission_script_template % dict(
        module='rescue',
        constructor='rescue',
        args=(creds,0,rescueFac,numships,enemyFac,'',path)))
        #args=(creds,0,rescueFac,numships,enemyFac,rescuelist[1],path)))
    writemissionname("Rescue/Rescue %s pilot from %s in %s. Autopayment %i credits."%(rescueFac.capitalize(),enemyFac.capitalize(),processSystem(path[-1]),creds),path,0)
    writemissionvars( { 'MISSION_TYPE' : mistype } )


fighters = {
    "retro" :    [  ("talon",400),("talon.retro2",500),("talon.retro2",500)  ],
    "pirates" :  [  ("talon",700),("talon.pirion",800),("talon.pirmeson",600)  ],
    "kilrathi" : [  ("dralthi",2000),("dralthi.tachyon",2500),("dralthi.ion",2500),("dralthi.ion",2500),
                    ("gothri",4000),("gothri.particle",4000),("gothri.tachyon",4000),("gothri.plasma",5000)  ],
    "criminal" : [  ("demon",1500),("demon.laser",1500),("demon.tachyon",2000),("demon.tachyon",2000),("demon.ion",2000),
                    ("orion.hunter",3000),("orion.ionturret",4000),("orion.plasma",3500),
                    ("centurion",4000),("centurion.tachpar",4500),("centurion.ion",4500),("centurion.plasma",5000)  ]
}

lightFighters = {
    "retro" :    [  ("talon",400),("talon",400),("talon.retro2",500)  ],
    "pirates" :  [  ("talon",700),("talon.pirlaser",600),("talon.pirmeson",600)  ],
    "kilrathi" : [  ("dralthi",2000)  ],
    "criminal" : [  ("demon",1500),("demon.laser",1500)  ]
}

def getRandomFighter(faction, shipMatrix):
    ships = shipMatrix.get(faction, [])
    ship = ships[ vsrandom.randrange(0, len(ships)) ]
    #print "PODXX getRandomFighter [" + faction + "]: " + str(ship) + " from: " + str(ships)
    return ship
    
def generateBountyMission (path,fg,fac):
    if fac in ["merchant", "confed", "militia"]:
      return
    
    missionKey = "bounty " + str(path[-1])
    if isExcessiveMission(missionKey, 1):
      return
    increaseMissionsCounter(missionKey)

    numNavPoints = faction_ships.numPatrolPoints[path[-1]]; 
     
    outlawMission = False
    if (fac == "retro" and vsrandom.random() < .3) or (fac in ["pirates","kilrathi"] and vsrandom.random() < .15):
      outlawMission = True
      fac = "criminal"

    rf = getRandomFighter(fac, fighters)
    shipType = rf[0]
    shipValue = rf[1]
    shipTypeFormatted = str(formatShip(shipType))
    commaInd = shipTypeFormatted.find(".")
    if (commaInd != -1):
        shipTypeFormatted = shipTypeFormatted[0:commaInd]
        
    escortType = ''
    escortValue = 0
    if vsrandom.random() > .5:
      et = getRandomFighter(fac, lightFighters)
      escortType = et[0]
      escortValue = et[1]
    
    greeting = universe.getRandomGreeting(fac)
    
    creds = int( randomCredModifier() + shipValue + escortValue + 800*calcPathDifficulty(path,0) + numNavPoints*600*getSystemDifficulty(path[-1]) + calcDeadEndBonus(path[0],path[-1]) + calcPathLengthBonus(path) )

    creds*=getPriceModifier(False)
    bcreds = creds
    addstr=""
    isFixer=vsrandom.random()
    if isFixer<guildpct:
        if (creds*1.4) <= 15000:
          creds*=1.4
        elif (creds*1.3) <= 20000:
          creds*=1.3
        else:
          creds*=1.2
        addstr+="#G#Bounty#\n"
    elif use_missioncomputer:
        addstr+="#C#Bounty#\n"

    print "PODXXX " + addstr + " [" + fac + "-" + shipType + "] escort [" + escortType + "] creds [" + str(bcreds) + "/" + str(creds) + "] path " + str(path)

    addInfo = ""
    if escortType <> '':
        shipType = [shipType, escortType]
        addInfo += "The ship in question is thought to have an escort."
#    if outlawMission:
#        fac = 'pirates'
    writemissionsavegame (addstr+mission_script_template % dict(
        module='bounty',
        constructor='bounty',
        args=(0,0,creds,False,0,fac,path,'','',shipType,0,greeting)))
        #args=(0,0,creds,runaway,diff,fac,path,'',fg,shipType,0)))
    
    randCompany = GetRandomCompanyName()
    targetstr = shipTypeFormatted                     #+":"+str(shipType)
    if shipTypeFormatted == "Talon":     # to distinguish between Talons
      targetstr = fac.capitalize() + " " + targetstr
      
    bountyb = GetRandomBountyBrief()
    if outlawMission:
        bountyb = "$CL puts a $PY bounty on a notorious criminal flying " + targetstr + ", recently seen in $DS system. $AI"
    composedBrief = bountyb.replace('$CL',randCompany)
    composedBrief = composedBrief.replace('$MT',targetstr)
    composedBrief = composedBrief.replace('$DS',processSystem(path[-1]))
    composedBrief = composedBrief.replace('$PY',str(int(creds)))
    composedBrief = composedBrief.replace('$AI',addInfo)
    if len(path)==1:
        mistype = 'IN-SYSTEM BOUNTY'
    else:
        mistype = 'BOUNTY'
    writedescription(composedBrief)
#    if (cap):
#        writemissionname ("Bounty/on_%s_Capital_Vessel_in_%s._Autopay_%i_credits."%(fac.capitalize(),processSystem(path[-1]),creds),path,isFixerString(addstr))
#    else:
#        writemissionname ("Bounty/on_%s_%s_in_%s._Autopay_%i_credits."%(fac,shipTypeFormatted,processSystem(path[-1]),creds),path,isFixerString(addstr))
    writemissionname ("Bounty/Find and eliminate %s %s in %s system. Autopayment %i credits."%(fac.capitalize(),shipTypeFormatted,processSystem(path[-1]),creds),path,isFixerString(addstr))
    writemissionvars( { 'MISSION_TYPE' : mistype } )

def generateDefendMission (path,defendfg,defendfac, attackfg,attackfac):
    if (isNotWorthy(defendfac)):
        return
    #defendfac = "merchant"    #PODXX decided to hardcode this b/c it kinda strange to see a non-merchant Drayman    
    
    attacktyp = fg_util.RandomShipIn(attackfg,attackfac)                    
    
    attackStrength = 0
    quantity = 0
    if str(attacktyp) in ["talon","gladius"]:
      if attackfac == "retro":
        attackStrength = 650
        quantity = vsrandom.randrange(3,5)
      else:
        attackStrength = 1000
        quantity = vsrandom.randrange(2,4)
    elif str(attacktyp) in ["dralthi","demon","stiletto"]:
      attackStrength = 2000
      quantity = vsrandom.randrange(1,4)
    elif str(attacktyp) in ["gothri","centurion","orion"]:
      attackStrength = 3000
      quantity = vsrandom.randrange(1,3)
    else:
      return

    missionKey = "defend " + str(path[-1])
    if isExcessiveMission(missionKey, 1):
      return
    increaseMissionsCounter(missionKey)

    creds = int( randomCredModifier() + 2000 + attackStrength*quantity + 800*calcPathDifficulty(path) + calcDeadEndBonus(path[0],path[-1]) )
    
    creds*=getPriceModifier(False)
    bcreds = creds
    addstr=""
    isFixer=vsrandom.random()
    if isFixer<guildpct:
        creds*=1.4
        addstr+="#G#Defend#\n"
    elif use_missioncomputer:
        addstr+="#C#Defend#\n"

    print "PODXXX " + addstr + " [" + defendfac + "] from [" + attackfac + "-" + str(attacktyp) + "] quantity [" + str(quantity) + "] creds [" + str(bcreds) + "/" + str(creds) + "] path " + str(path)

    writemissionsavegame (addstr+mission_script_template % dict(
        module='defend',
        constructor='defend',
        args=(attackfac,0,quantity,2000.0,5000.0,creds,True,False,defendfac,path,'',attackfg,attacktyp,'',0,universe.getRandomGreeting("common"))))
    iscapitol=""
    if True:
        iscapitol="capital "
    randCompany = GetRandomCompanyName()
    defendb = GetRandomDefendBrief()
    composedBrief = defendb.replace('$CL',randCompany)
    composedBrief = composedBrief.replace('$DT',iscapitol)
    composedBrief = composedBrief.replace('$DS',processSystem(path[-1]))
    composedBrief = composedBrief.replace('$PY',str(int(creds)))
    composedBrief = composedBrief.replace('$MT',attackfac.capitalize())
    if len(path)==1:
        mistype = 'IN-SYSTEM DEFEND'
    else:
        mistype = 'DEFEND'
    writedescription(composedBrief)
#    writemissionname("Defend/Defend_%s_from_%s_in_%s._Autopay_%i_credits."%(defendfac.capitalize(), attackfac.capitalize(), processSystem(path[-1]), creds),path,isFixerString(addstr))
    writemissionname("Defend/Defend %s Drayman from %s in %s. Autopayment %i credits."%(defendfac.capitalize(), attackfac.capitalize(), processSystem(path[-1]), creds),path,isFixerString(addstr))
    writemissionvars( { 'MISSION_TYPE' : mistype } )


def generateWingmanMission(fg, faction):
    numships=vsrandom.randrange(1,4)
    creds=10000+15000*numships
    writemissionsavegame ('#\n' + mission_script_template % dict(
        module='wingman',
        constructor='wingman',
        args=(creds,faction,numships,0)))
    s="A pilot"
    EorA="a"
    are="is"
    if numships > 1:
        s=str(numships)+" pilots"
        EorA="e"
        are="are"
    isFixer=vsrandom.random()
    if isFixer<fixerpct and fixer_has_wingman:
        creds*=2
        addstr+="#F#bases/fixers/merchant.spr#Talk to the Merchant#Thank you. I entrust you will make the delivery successfully.#\n"
    elif isFixer<guildpct:
        creds*=1.5
        addstr+="#G#Wingman#\n"
    elif use_missioncomputer:
        addstr+="#C#Wingman#\n"
    writedescription(s+" in the %s faction %s willing to help you out and fight with you as long as you pay %d credits."%(faction, are, creds))
    writemissionname("Wingmen/Hire_%d_%s_Wingm%sn"%(numships,faction,EorA),[VS.getSystemFile()],0)
    writemissionvars( { 'MISSION_TYPE' : 'CONTRACT WINGMAN' } )
    
    
def GetFactionToDefend(thisfaction, fac, cursys):
    m = fg_util.FGsInSystem ("merchant",cursys)
    nummerchant=len(m)
    m+=fg_util.FGsInSystem (thisfaction,cursys)
    numthisfac=len(m)
    m+=fg_util.FGsInSystem (fac,cursys)
    return (m,nummerchant,numthisfac)

CARGOS = ['Exotic_Foods','Natural_Furs','Premium_Liquor','Pets',
          'Gems','Plutonium','Uranium','Artwork','Construction',
          'Advanced_Fuels','Communications','Computers','Factory_Equipment',
          'Holographics','Home_Appliances','Medical_Equipment','Spaceship_Parts',
          'Pre_Fabs','Plastics','Robot_Servants','Robot_Workers','Textiles',
          'Passengers','Antique_Books','Mining_Equipment','Food_Dispensers',
          'Home_Entertainment','Tungsten','Iron','Isometal','Wood']
def chooseRandomCargo():
    return CARGOS[ vsrandom.randrange(0, len(CARGOS)) ]

def setFactionRelation(faction, newrel):
    rel = VS.GetRelation(faction,"privateer")
    while (rel - newrel) > 0.01 or (rel - newrel) < -0.01:
        #print "PODXX rel: " + str(rel) + ", newrel: " + str(newrel)
        VS.AdjustRelation(faction,"privateer",newrel-rel,1.0)
        rel=VS.GetRelation(faction,"privateer")

def contractMissionsFor(baseFaction,baseship,minsysaway,maxsysaway):
    # doing this makes very hard to become friendly with Kilrathi
    #VS.AdjustRelation('kilrathi','privateer',-0.1,1.0)
    setFactionRelation('kilrathi',-2)
    
    resetPerSystemMissionsCounters()
    cursystem = VS.getSystemFile()
    cursysFaction = VS.GetGalaxyFaction (cursystem)
    merchantShips = ["tarsus","galaxy","drayman","orion"]
    
    if cursystem in ['Gemini/Hyades']:
      cursysFaction = "confed"           # strange thing, otherwise Hyades always 'belongs' to kilrathi...
    
    for i in range (minsysaway,maxsysaway+1):
        nxtSystemLayer = getSystemsKAwayNoFaction(cursystem,i)
        vsrandom.shuffle(nxtSystemLayer)
        #print "contractMissionsFor nxtSystemLayer quantity[" + str(len(nxtSystemLayer)) + "]"
        for j in nxtSystemLayer:
            nxtSystem = j[-1]
            nxtSysShort = nxtSystem[7:]
            sysDiff = getSystemDifficulty(nxtSystem)
            
            enemies = ["pirates","pirates","pirates","retro","retro","kilrathi"]
#                "New_Constantinople","Troy","Manchester","Newcastle","Nexus","Rikel","Pyrenees","Regallis","Midgard",
#                "Junction","XXN-1927","Metsor","Penders_Star","44-p-im","119ce","Pentonville","Castor",
#                "Freyja","J900","Crab-12","Sherwood","New_Caledonia","Prasepe","Pollux","CM-N1054",
#                "Capella","KM-252","Telar","17-ar","Death","Pestilence","War","Famine","Valhalla",

            if nxtSysShort in ["Hinds_Variable_N","Padre","Auriga","Shangri_La","Aldebran","DN-N1912","Saxtogue","ND-57","Raxis","Varnus","Oxford","New_Detroit",]:
                enemies = ["pirates","pirates","retro","retro","retro","kilrathi"]

            if nxtSysShort in ["Perry","Palan","Tingerhoff","Rygannon","Xytani","Ragnarok","Nitir","Surtur","CMF-A",
                           "Blockade_Point_Alpha","Blockade_Point_Charlie","Hyades","Blockade_Point_Tango","Lisacc","41-gs",]:
                enemies = ["pirates","retro","kilrathi","kilrathi"]

            #print "PODXX " + nxtSysShort + " " + str(enemies)
            (FGs2defend,numMerchantFac,numCursysFac) = GetFactionToDefend(cursysFaction, baseFaction, nxtSystem)

            for kk in range (4):
                for iesc in range (12):
                    if i>0:
                        continue
                    escortedFac = "confed"
                    shipType = "broadsword"
                    if vsrandom.random() > .3:
                        escortedFac = "merchant"
                        shipType = merchantShips[ vsrandom.randrange(0, len(merchantShips)) ]
                    generateEscortLocal(j,shipType,escortedFac,enemies[vsrandom.randrange(0,len(enemies))])
                    generateScoutLocalMission(j,enemies[vsrandom.randrange(0,len(enemies))])
                
                nxtEnemyFac = enemies[vsrandom.randrange(0,len(enemies))]

                if (i<2) and (vsrandom.random() < 0.5*sysDiff):
                    rescFacs = ["merchant","merchant","confed","militia"]
                    generateRescueMission(j,[rescFacs[vsrandom.randrange(0,len(rescFacs))],'',nxtEnemyFac])
                
                nxtEnemyFG = fg_util.RandomFlightgroup(nxtEnemyFac)

                bountyRnd = .24
                # this is to balance the number of bounty missions between near and far systems
                if i == 1:
                    bountyRnd = .17
                if i == 2:
                    bountyRnd = .13
                if i == 3:
                    bountyRnd = .09
                if i == 4:
                    bountyRnd = .06
                if vsrandom.random() < bountyRnd:
                    generateBountyMission(j,nxtEnemyFG,nxtEnemyFac)

                if len(FGs2defend) and i<3 and (vsrandom.random() < sysDiff):
                    rnd=vsrandom.randrange(0,len(FGs2defend))
                    def_fg=FGs2defend[rnd]
                    def_fac = "merchant"
                    if rnd>=numMerchantFac:
                        def_fac = cursysFaction
                    if rnd>=numCursysFac:
                        def_fac = baseFaction
                    generateDefendMission(j,def_fg,def_fac,nxtEnemyFG,nxtEnemyFac)


            # a bit messy cycle, could be refactored but meh... works fine
            for kk in range(6):
                nxtEnemyFac = enemies[vsrandom.randrange(0,len(enemies))]
                if i<4 and vsrandom.random()<.2:
                    if (vsrandom.random()>.6 or nxtSystem in faction_ships.fortress_systems):
                        generatePatrolMission(j,numPatrolPoints(nxtSystem,0),nxtEnemyFac)
                    else:
                        generateCleansweepMission(j,numPatrolPoints(nxtSystem,1),nxtEnemyFac)
                
                cargRnd = 1
                if i == 1:
                    cargRnd = .70
                if i == 2:
                    cargRnd = .80
                if i == 3:
                    cargRnd = .87
                if i == 4:
                    cargRnd = .92
                if vsrandom.random()>cargRnd:
                    category=chooseRandomCargo()
                    if (vsrandom.random()>.85):
                        category = 'Contraband'
                    generateCargoMission(j,vsrandom.randrange(10,40),category,baseFaction)
                        

def CreateMissions(minsys=0,maxsys=4):
    generate_dyn_universe.KeepUniverseGenerated()
    if VS.networked():
        # No generating stuff while networked.
        return
    i=0
    global plr,basefac,baseship
    plrun=VS.getPlayer()
    plr=plrun.isPlayerStarship()
    eraseExtras()
    i = VS.getUnitList()
    while(i.notDone() and not i.current().isDocked(plrun)):
        i.advance()
    if (i.notDone()):
        basefac=i.current().getFactionName()
    if (basefac=='neutral'):
        basefac=VS.GetGalaxyFaction(VS.getSystemFile())
    contractMissionsFor(basefac,baseship,minsys,maxsys)
#    import news
#    news.processNews(plr)
#    print "GOOG OGOO"
