import vsrandom
import faction_ships
import launch_recycle
import launch
import VS
import unit
import sys
import adventure
import news
import universe
import fg_util
import dynamic_battle
import debug
import generate_dyn_universe
import quest


class random_encounters:
    class playerdata:
        def GeneratePhaseAndAmplitude(self):
            self.prob_phase=20*vsrandom.random()
            self.prob_amplitude = .5+.5*vsrandom.random()
            self.prob_period = 20*vsrandom.random()+1
        def UpdatePhaseAndAmplitude(self):
            self.prob_phase+=1;
            return self.prob_amplitude*(.6+.4*VS.cos ((self.prob_phase*3.1415926536*2)/self.prob_period))
        def __init__(self,sig_distance,det_distance):
            debug.debug("init playerdata")
            try:
                faction_ships.Precache()
            except:
                import sys
                debug.debug(str(sys.exc_info()[0])+str(sys.exc_info()[1]))
            self.quests=[]
            self.curquest=0
            self.last_ship=0
            self.curmode=0
            self.lastmode=0
            self.lastsys=""
            self.sig_container=VS.Unit()
            self.significant_distance=sig_distance
            self.detection_distance=det_distance
            self.GeneratePhaseAndAmplitude()
            debug.debug("done playerdat")
    def __init__(self, sigdis, detectiondis, gendis,  minnships, gennships, unitprob, enemyprob, capprob, capdist):
        unitprob=1
        debug.debug("init random enc")
        
        self.capship_gen_distance=capdist
        #    player_num=player
        self.enprob = enemyprob
        self.fighterprob = unitprob

        self.det_distance = detectiondis
        self.sig_distance = sigdis
        self.players=[]
        self.generation_distance=gendis
        self.min_num_ships=minnships
        self.gen_num_ships=gennships
        self.capship_prob=capprob
        self.cur_player=0
        self.sig_distance_table = {"enigma_sector/heavens_gate":(2000,4000,.4)}
        self.greetTime = 10000000
        self.talkingUnit = VS.Unit()
        debug.debug("end random enc")
    def AddPlayer (self):
#    print "begin add player"
        self.players+=[random_encounters.playerdata(self.sig_distance,self.det_distance)]
#    print "add player"
    def NewSystemHousekeeping(self,oldsystem,newsystem):
        fg_util.launchBases(newsystem)
        news.newNews()
        newquest = adventure.newAdventure (self.cur_player,oldsystem,newsystem)
        if (newquest):
            self.cur.quests+=[newquest]
        else:
            self.RestoreDroneMission()
        self.CalculateSignificantDistance()
    def RestoreDroneMission(self):
        qdf=adventure.persistentAdventure (self.cur_player)
        if (qdf):
            self.cur.quests+=[qdf]
    def CalculateSignificantDistance(self):
        sysfile = VS.getSystemFile()
        self.cur.GeneratePhaseAndAmplitude()
        if sysfile in self.sig_distance_table:
            self.cur.significant_distance = self.sig_distance_table[sysfile][0]
            self.cur.detection_distance = self.sig_distance_table[sysfile][1]
            self.cur.prob_amplitude = self.sig_distance_table[sysfile][2]
            return
        minsig =  unit.minimumSigDistApart()
        if (self.sig_distance>minsig*0.15):
            self.cur.significant_distance=minsig*0.15
        else:
            self.cur.significant_distance=self.sig_distance
        if (self.det_distance>minsig*0.2):
            self.cur.detection_distance=minsig*0.2
        else:
            self.cur.detection_distance=self.det_distance

        debug.debug("resetting sigdist=%f detdist=%f" % (self.cur.significant_distance,self.cur.detection_distance))

    def SetEnemyProb (self,enp):
        self.enprob = enp


    def AsteroidNear (self,uni, how):
        i = VS.getUnitList()
        dd = self.cur.detection_distance
        while i.notDone():
            un = i.current()            
            if (uni.getSignificantDistance(un)<how):
                if (unit.isAsteroid (un)):
                    debug.debug("asty near")
                    return 1
            i.advance()
        return 0
    def TrueEnProb(self,enprob):
        ret=1
        nam = VS.numActiveMissions()
        while (nam>0):
            ret*=(1-enprob)
            nam-=1
        debug.debug(1-ret)
        return 1-ret;
    def fixupFactionRelations(self):
        for fac in ["mining", "refinery","naval","commerce"]:
            reldel=VS.GetRelation("privateer",fac)
            VS.AdjustRelation("privateer",fac,-reldel,1);
            print "adjusting by "+str(reldel)
            reldel=VS.GetRelation(fac,"privateer")
            VS.AdjustRelation(fac,"privateer",-reldel,1);
            print "adjusting by "+str(reldel)
    
        
    def launchPalanBlockade(self, around):
        for i in range (2):
          L = launch.Launch()
          L.fg='Palan blockade'
          L.type = "centurion.bronte"
          L.faction = "criminal"
          L.ai = "default"
          L.num=2
          L.minradius = (self.generation_distance+500)*(vsrandom.randrange(10,99)*.01)*0.9
          L.maxradius=L.minradius
          launchAround=L.launch(around)
          launchAround.setFgDirective('A.')
          if i == 0:
            self.talkingUnit = launchAround
    
          L2 = launch.Launch()
          L2.fg='Palan blockade'
          L2.type = "demon.bronte"
          L2.faction = "criminal"
          L2.ai = "default"
          L2.num=2
          L2.minradius = (self.generation_distance+500)*(vsrandom.randrange(10,99)*.01)*0.9
          L2.maxradius = L.minradius
          launchAround=L2.launch(around)
          launchAround.setFgDirective('A.')
        
        #rel = VS.GetRelation("hunter","privateer")
        #if rel > -0.1:
        #  VS.AdjustRelation( "hunter", "privateer", -0.1-rel, 1.0)
          
        self.greetTime=VS.GetGameTime()+6
    

    def findUnit(self, name):
        i = VS.getUnitList()
        while i.notDone():
            testun=i.current()
            i.advance()
            if testun.getName().lower()==name.lower() or testun.getFullname().lower()==name.lower():
                return testun
        return ""
    
    def launch_near(self,un, forceLaunch=False):
        if (VS.GetGameTime()<10 and not forceLaunch):
            debug.debug("hola!")
            return
        #self.fixupFactionRelations();
        
        if un.getName() == "Palan" and quest.checkSaveValue(VS.getCurrentPlayer(),"access_to_library",1) and not quest.checkSaveValue(VS.getCurrentPlayer(),"blockade_weakened",1):
           if quest.checkSaveValue(VS.getCurrentPlayer(),"privateer_drone_active",1):
               return    # a convenience case for compatibility with old savegames when there was no "blockade_weakened" variable
           self.launchPalanBlockade(un)
           return

        cursys=VS.getSystemFile()
        sysShortName = cursys[7:]
        
        if sysShortName == "Gamma":
            jdp = self.findUnit("Jump_to_Delta_prime")
            jdpDistance = jdp.getDistance(un)
            #print "PODXX distance to Jump_to_Delta_prime: " + str( jdpDistance )
            if jdpDistance <= 2500.0:
              return
        
#    numsigs=universe.GetNumSignificantsForSystem(cursys)
        for factionnum in range(faction_ships.getMaxFactions()-1):
            faction=faction_ships.intToFaction(factionnum)

# PODXXXXXXXXXXXXXXXXXXXXXXXXX BRUTAL AND MESSY HACK TO RESEMBLE ORIGINAL PRIVATEER
            if not (faction in ["pirates","confed","kilrathi","retro","merchant","hunter","militia"]):
              continue
            avg=0.0          # chance to spawn a ship
            mod="couple"     # default ships quantity modifier
            capShipType = ""
            capShipProb = 0
            launchAround = un

            # Pirate bases and hideout areas
            if (sysShortName in ["Capella","KM-252","Telar","17-ar","Death","Pestilence","War","CM-N1054","Famine"]):
              if (faction in ["pirates"]):
                avg=.6
                mod="quad"
                capShipType = "galaxy.pirpar"
                capShipProb = .15
              elif (faction in ["hunter"]):
                avg=.15
                mod="single"
              elif (faction in ["merchant"]):
                avg=0
              elif (faction in ["kilrathi"]):
                avg=.1
                mod="single"
              else:
                avg=0.06
                mod="single"

            if (sysShortName in ["Valhalla"]):
              if (faction in ["pirates","retro"]):
                avg=.5
                mod="quad"
              elif (faction in ["kilrathi"]):
                avg=.1
                mod="single"
              else:
                avg=0.06

            if (sysShortName in ["Eden"]):
              if (faction in ["retro"]):
                avg=.6
                mod="quad"
              else:
                avg=0

            # high pirate chance but smallish numbers, to ease the campaign
            if (sysShortName in ["Pentonville"]):
              if (faction in ["pirates"]):
                avg=.4
                capShipType = "galaxy.pirpar"
                capShipProb = .2
              elif (faction in ["hunter"]):
                avg=.1
                mod="single"
              else:
                avg=0
            
            # chokelines with a chance of a weak pirate ambush
            if (sysShortName in ["Metsor","Penders_Star","Saxtogue","44-p-im","119ce"]):
              if (faction in ["pirates"]):
                avg=.3
              elif (faction in ["militia","merchant"]):
                avg=.15
                mod="single"
              elif (faction in ["retro"]):
                avg=.1
                mod="single"
              elif (faction in ["kilrathi"]):
                avg=0
              else:
                avg=0.06
                mod="single"

            # Some moderately pirate-infested systems
            if (sysShortName in ["Freyja","J900","Crab-12","Sherwood","New_Caledonia","Prasepe","Pollux","DN-N1912"]):
              if (faction in ["pirates"]):
                avg=.4
                mod="triple"
              elif (faction in ["militia"]):
                avg=.2
              elif (faction in ["merchant","retro"]):
                avg=.15
              elif (faction in ["kilrathi"]):
                avg=.1
                mod="single"
              else:
                avg=0.06
                mod="single"

            if (sysShortName in ["Rygannon","Xytani","Ragnarok","Nitir","Surtur","CMF-A"]):
              if (faction in ["pirates"]):
                avg=.3
                mod="triple"
              elif (faction in ["merchant","militia","confed"]):
                avg=.2
              elif (faction in ["kilrathi"]):
                avg=.18
              else:
                avg=0.1

            # Special case for the "Jump_to_Delta" navpoint
            if sysShortName == "Rygannon":
              jd = self.findUnit("Jump_to_Delta")
              jdDistance = jd.getDistance(un)
              print "PODXX distance to Jump_to_Delta: " + str( jdDistance )
              if jdDistance <= 2500.0:
                if (faction in ["pirates"]):
                  avg=.3
                  mod = "couple"
                elif (faction in ["kilrathi"]):
                  avg=.15
                  mod="single"
                else:
                  avg = 0
            
            # Quite safe systems
            if (sysShortName in ["Troy","Manchester","ND-57","Raxis","Varnus","Newcastle"]):
              if (faction in ["pirates","retro"]):
                avg=.13
              elif (faction in ["merchant","militia"]):
                avg=.2
              elif (faction in ["kilrathi"]):
                avg=0
              else:
                avg=0.06
                mod="single"
            
            # Not that safe but big trouble should be rare
            if (sysShortName in ["Nexus","Rikel","Pyrenees","Regallis","Padre","Auriga","Midgard","Castor","Aldebran","Hinds_Variable_N"]):
              if (faction in ["pirates","retro"]):
                avg=.18
                mod="triple"
              elif (faction in ["militia"]):
                avg=.2
              elif (faction in ["merchant"]):
                avg=.15
                mod="single"
              elif (faction in ["kilrathi"]):
                avg=.0
              else:
                avg=0.06
                mod="single"

            # Major hubs
            if (sysShortName in ["Junction","XXN-1927"]):
              if (faction in ["merchant","militia"]):
                avg=.25
                mod="triple"
              elif (faction in ["pirates","retro"]):
                avg=.18
              elif (faction in ["kilrathi"]):
                avg=0
              else:
                avg=0.1

            if (sysShortName in ["New_Constantinople","New_Detroit"]):
              if (faction in ["merchant","militia","confed","hunter"]):
                avg=.25
                mod="triple"
              else:
                avg=0.06
                mod="single"

            if (sysShortName in ["Shangri_La","Oxford"]):
              if (faction in ["retro"]):
                avg=.25
              elif (faction in ["kilrathi"]):
                avg=0
              else:
                avg=0.1
                mod="single"

            if (sysShortName in ["Palan","Tingerhoff"]):
              if (faction in ["hunter"]):
                avg=.3
              elif (faction in ["militia","merchant","confed"]):
                avg=.2
              else:
                avg=0.18

            if (sysShortName in ["Perry"]):
              if (faction in ["confed"]):
                avg=.6
                mod="quad"
                capShipType = "paradigm"
                capShipProb = .1
              elif (faction in ["merchant","militia","hunter"]):
                avg=.15
              else:
                avg=0.06
                mod="single"

            # Confed's blockposts and border systems
            if (sysShortName in ["Blockade_Point_Alpha","Blockade_Point_Charlie","Hyades","41-gs","Blockade_Point_Tango","Lisacc"]):
              if (faction in ["kilrathi"]):
                avg=.4
                mod="triple"
                capShipType = "kamekh"
                capShipProb = .05
              elif (faction in ["confed"]):
                avg=.7
                mod="triple"
                capShipType = "paradigm"
                capShipProb = .1
              else:
                avg=0

            if (sysShortName in ["Sumn_Kpta","Mah_Rahn","Tr_Pakh"]):
              if (faction in ["kilrathi"]):
                avg=.85
                mod="quad"
                capShipType = "kamekh"
                capShipProb = .3
              elif (faction in ["confed"]):
                avg=.15
              else:
                avg=0.0

            if (sysShortName in ["Delta"]):
              if (faction in ["kilrathi"]):
                avg=.15
              elif (faction in ["pirates"]):
                avg=.45
                mod="quad"
                capShipType = "galaxy.pirpar"
                capShipProb = .15
              else:
                avg=0.0

            if (sysShortName in ["Beta"]):
              if (faction in ["kilrathi"]):
                avg=.2
              elif (faction in ["pirates"]):
                avg=.35
                mod="triple"
                capShipType = "galaxy.pirpar"
                capShipProb = .15
              else:
                avg=0.0

            if (sysShortName in ["Gamma"]):
              if (faction in ["kilrathi"]):
                avg=.5
                mod="triple"
              else:
                avg=0.0

            if (sysShortName in ["Delta_Prime"]):
                avg=0.0

            if (faction == "retro") and quest.checkSaveValue(VS.getCurrentPlayer(),"removed_BoostedSteltek",1):
                avg = min(.66, avg*1.25)
                if mod == 'triple': mod = 'quad'
                if mod == 'couple': mod = 'triple'
                if mod == 'single': mod = 'couple'
                #print "PODXXX Righteous Fire, stronger retro chance[" + str(avg) + "] mod[" + mod + "]"

            rndnum=vsrandom.random()
            print "[" + sysShortName + "] mod[" + str(mod) + '] Chance for %s ships: %g; will generate ships: %d'%(faction, avg, rndnum<avg)
            if rndnum>=avg:
              continue
              
            
            typenumbers=fg_util.chooseRandomShips( faction, fg_util.DefaultNumShips(mod) )
            flightgroup = sysShortName + "_" + faction + str( vsrandom.randrange(10,100))
            radius = (self.generation_distance+500)*(vsrandom.randrange(10,99)*.01)*0.9
            
            if vsrandom.random() < capShipProb:
                L = launch.Launch()
                L.fg=flightgroup
                L.dynfg=''
                L.type = capShipType
                L.faction = faction
                L.ai = "default"
                L.num=1
                L.minradius=radius
                L.maxradius = radius
                launchAround=L.launch(un)
                launchAround.setFgDirective('A.')
                radius = 100.0

            print 'GenDist[' + str(self.generation_distance) + '] radius[' + str(radius) + '] mod[' + mod + '] around[' + launchAround.getName() + '] FG Name: "%s", ShipTypes: %s'%(flightgroup,str(typenumbers))
            launch_recycle.launch_types_around(flightgroup,faction,typenumbers,'default',radius,launchAround,self.generation_distance*vsrandom.random()*2,'')

# XXXXXXXXXXXXXXXXXXXXXXXXX END


    def atLeastNInsignificantUnitsNear (self,uni, n):
        num_ships=0
        leadah = uni.getFlightgroupLeader ()
        i = VS.getUnitList()
        dd = self.cur.detection_distance
        while i.notDone():
            un = i.current()
            if (uni.getSignificantDistance(un)<dd*1.6):
                if ((not un.isSignificant()) and (not un.isSun())):
                    unleadah = un.getFlightgroupLeader ()
                    if (leadah!=unleadah):
                        num_ships+=1
            i.advance()
        return num_ships>=n

    def SetModeZero(self):
        self.cur.last_ship=0
        self.cur.curmode=0
        self.cur.sig_container.setNull()
        for q in self.cur.quests:
            q.NoSignificantsNear()

    def SetModeOne (self,significant):
        self.cur.last_ship=0
        self.cur.curmode=1
        self.cur.sig_container=significant
        if VS.getPlayer().isNull():
            return
        cursys = VS.getSystemFile()
        oldsys = self.cur.lastsys==cursys
        if (not oldsys):
            self.NewSystemHousekeeping(self.cur.lastsys,cursys)
            self.cur.lastsys=cursys
        for q in self.cur.quests:
            q.SignificantsNear(self.cur.sig_container)
#    import dynamic_battle
#    dynamic_battle.UpdateCombatTurn()

    def decideMode(self):
        myunit=VS.getPlayerX(self.cur_player)
        if (not myunit):
            self.SetModeZero()
            return myunit
        significant_unit = self.cur.sig_container
        
#        un=VS.getUnit(0);
#        i=0
#        while (un):
#            debug.debug(un.getName())
#            i+=1
#            un=  VS.getUnit(i)

        if (not significant_unit):
            un=VS.getUnit(self.cur.last_ship)
            if (self.DifferentSystemP()):
                debug.debug("RE: jumped to different system 2...")
                un.setNull()
            if (not un):
                self.SetModeZero()
            else:
                sd = self.cur.significant_distance
                if ((un.getSignificantDistance(myunit)<sd) and (un.isSignificant())):
                    debug.debug("RE reached sig unit: " + un.getName())
                    self.SetModeOne (un)
                    return un
                self.cur.last_ship+=1
            return VS.Unit()
        else:
            #significant_unit is something.... lets see what it is
            cursys = VS.getSystemFile()
            if (self.DifferentSystemP()):
                debug.debug("Jumped to different system 1...")
                self.SetModeZero()
                significant_unit.setNull ()
            else:
                if (myunit.getSignificantDistance (significant_unit) > self.cur.detection_distance):
                    self.SetModeZero ()
                    return VS.Unit()
#                else:
#                    return significant_unit
            return significant_unit
    
    def DifferentSystemP(self):
        if VS.getPlayer().isNull():
            return 0
        cursys=VS.getSystemFile()
        if (cursys==self.cur.lastsys):
            return 0
        self.NewSystemHousekeeping(self.cur.lastsys,cursys)
        
        asteroidJumps = [ ("Gemini/Rikel", "Gemini/44-p-im", "Jump_To_44-P-IM"),
                          ("Gemini/Rikel", "Gemini/New_Detroit", "Jump_To_New_Detroit"),
                          ("Gemini/Rikel", "Gemini/Midgard", "Jump_To_Midgard"),
                          ("Gemini/Gamma", "Gemini/Delta_Prime", "Jump_To_Delta_Prime"),
                          ("Gemini/Gamma", "Gemini/Beta", "Jump_To_Beta"),
                          ("Gemini/Beta", "Gemini/Gamma", "Jump_To_Gamma"),
                          ("Gemini/Rygannon", "Gemini/Delta", "Jump_To_Delta"),
                          ("Gemini/Lisacc", "Gemini/Blockade_Point_Tango", "Jump_To_Blockade_Point_Tango"),
                          ("Gemini/Mah_Rahn", "Gemini/Blockade_Point_Tango", "Jump_To_Blockade_Point_Tango"),
                          ("Gemini/Ragnarok", "Gemini/Blockade_Point_Alpha", "Jump_To_Blockade_Point_Alpha"),
                          ("Gemini/War", "Gemini/Pestilence", "Jump_To_Pestilence"),
                          ("Gemini/War", "Gemini/Troy", "Jump_To_Troy")]
        for aj in asteroidJumps:
            if aj[0] == cursys and aj[1] == self.cur.lastsys:
                debug.debug("RE relocation spot: " + str(aj))
                for sig in universe.significantUnits():
                  if sig.getName() == aj[2]:
                    VS.getPlayerX(self.cur_player).SetPosition( sig.Position() )
        self.cur.lastsys=cursys
        return 1
    
    def Execute(self):
        if VS.GetGameTime() >= self.greetTime:
            universe.greet( [("You have to go through us to get to Palan",True,"campaign/blockadem.wav")], self.talkingUnit, VS.getPlayer() );
            self.greetTime = 10000000

        generate_dyn_universe.KeepUniverseGenerated()
        dynamic_battle.UpdateCombatTurn()
        if (self.cur_player>=len(self.players)):
            self.AddPlayer()
        self.cur=self.players[self.cur_player]
        if (self.cur.curquest<len(self.cur.quests)):
            if (self.cur.quests[self.cur.curquest].Execute()):
                self.cur.curquest+=1
            else:
                del self.cur.quests[self.cur.curquest]
        else:
            self.cur.curquest=0
        un = self.decideMode ()
	if VS.getPlayerX(self.cur_player) and (self.cur.curmode!=self.cur.lastmode):
            #lastmode=curmode#processed this event don't process again if in critical zone
            self.cur.lastmode=self.cur.curmode
            print "curmodechange %d" % (self.cur.curmode)#?
            if un:
#      if ((vsrandom.random()<(self.fighterprob*self.cur.UpdatePhaseAndAmplitude())) and un):
                if (not self.atLeastNInsignificantUnitsNear (un,self.min_num_ships)):
                    #determine whether to launch more ships next to significant thing based on ships in that range
                    debug.debug("Launch near: " + un.getName())
                    if un.getName() == 'Asteroid_Field':
                        self.launch_near (VS.getPlayerX(self.cur_player))
                    else:
                        self.launch_near (un)
        self.cur_player+=1
        if (self.cur_player>=VS.getNumPlayers()):
            self.cur_player=0
	
	# This could cause some issues, don'cha think?
        #VS.setMissionOwner(self.cur_player)

debug.debug("done loading rand enc")
