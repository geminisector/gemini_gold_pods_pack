from go_to_adjacent_systems import *
from go_somewhere_significant import *
import vsrandom
import launch
import faction_ships
import VS
import Briefing
import universe
import unit
import Director
import quest

class go_none:
    def Execute(self):
        return 1
    def HaveArrived(self):
        return 1
    def SignificantUnit(self):
        return VS.getUnit(0);
    def __init__(self):
        pass

class cargo_mission (Director.Mission):
    def initbriefing(self):
        VS.IOmessage (0,"cargo mission","briefing","Your mission for today will be to run some %s cargo" % self.cargoname)
        self.briefgametime = 0
        self.adjsys.initbriefing()

    def getBasenameDockedAt(self):
        dockedAt = universe.getDockedBase()
        baseName = dockedAt.getFullname()
	if baseName == '' or dockedAt.isPlanet():
	    baseName = dockedAt.getName()
        return baseName
    
    def loopbriefing(self):
        brief_you=self.adjsys.loopbriefing()
        if (brief_you != -1):
            VS.IOmessage(0,"cargo mission","briefing","Once there, you must drop the cargo off at a specified unit")
            if (self.briefgametime==0):
                self.briefgametime = VS.GetGameTime()
            elif ((VS.GetGameTime()-self.briefgametime)>5):
                Briefing.terminate()
    def endbriefing(self):
        self.adjsys.endbriefing()
        del self.briefgametime
    def SetVar (self,val):
        if (self.var_to_set!=''):
            quest.removeQuest (self.you.isPlayerStarship(),self.var_to_set,val)
    def __init__ (self,factionname, numsystemsaway, cargoquantity, missiondifficulty, creds, launchoncapship, time_to_complete, category,jumps=(),var_to_set='', destBaseName='', isExpress = 0):
        Director.Mission.__init__(self);
        self.you=VS.Unit()
        self.base=VS.Unit()
        self.role="ESCORTCAP"
        self.arrived=0
        self.var_to_set=var_to_set
        self.mplay="all"
#         self.mission_time=VS.GetGameTime()+time_to_complete*100*float(1+numsystemsaway)
        self.capship= launchoncapship
        self.faction=factionname
        self.cred=creds
        self.difficulty=missiondifficulty
        
        self.isExpress = isExpress
        self.isMisland = False
        self.departBasename = self.getBasenameDockedAt()
	    
        self.ambushInSystem = ''
        if vsrandom.random() < missiondifficulty:
            self.ambushInSystem = jumps[0]
            if len(jumps) > 1:
                self.ambushInSystem = jumps[ vsrandom.randrange(1, len(jumps)) ]
        print "Cargo mission, self.ambushInSystem[" + self.ambushInSystem + "] self.departBasename[" + self.departBasename + "]"
        
        self.prevVisitedSystem = ''
        self.you=VS.getPlayer()
        self.adjsys=go_to_adjacent_systems(self.you,numsystemsaway,jumps)
        self.quantity=cargoquantity
        self.mplay=universe.getMessagePlayer(self.you)
        self.greetTime = 10000000
        self.talkingEnemy = VS.Unit()
        self.speech = []
        if (self.quantity<1):
            self.quantity=1
        self.destBaseName = destBaseName

        self.cargoname = category
        self.category = 'Contraband/' + category
        if not self.cargoname in ['Brilliance','Tobacco','Slaves','Ultimate']:
            #PODXX to distinguish mission cargo; can't do it to contraband b/c cops won't detect it
            self.cargoname = self.category = "*" + category
	carg = VS.Cargo(self.cargoname, self.category, 1, self.quantity , 0.01, 1.0)
        carg.SetMissionFlag(1)

#        carg=VS.getRandCargo(self.quantity,category)
#        if (carg.GetQuantity()==0 or category==''):
#            carg = VS.getRandCargo(self.quantity,"") #oh no... could be starships...
#            i=0
#            while i<50 and carg.GetCategory()[:10]=="Contraband":
#                print "contraband==bad"
#                carg = VS.getRandCargo(self.quantity,"")
#                i+=1
        tempquantity=self.quantity       #PODXX seems this is a non-working legacy of something...
#        self.cargoname=carg.GetContent()

        name = self.you.getName ()
        if (not self.you.isNull()):
            tmpcarg=self.you.GetCargo(self.cargoname)
            DoAddCargo=True
            try:
                if VS.loading_active_missions:
                    DoAddCargo=False
            except:
                pass
            if False and tmpcarg.GetMissionFlag() and tmpcarg.GetQuantity()>2:
                quantum=int(tmpcarg.GetQuantity()/3)
                quantum=self.you.removeCargo(carg.GetContent(),quantum,True)#use it if player has it
                carg.SetQuantity(1+quantum)
                self.quantity=self.you.addCargo(carg)
            elif DoAddCargo:
                self.quantity = self.you.addCargo(carg)  #I add some cargo
        else:
            VS.IOmessage (2,"cargo mission",self.mplay,"#ff0000Unable to establish communications. Mission failed.")
            VS.terminateMission (0)
            return
#         creds_deducted = (carg.GetPrice()*float(self.quantity)*vsrandom.random()+1)
#         self.cred += creds_deducted
        if (tempquantity>0):
            self.cred*=float(self.quantity)/float(tempquantity)
        else:
            VS.IOmessage (2,"cargo mission",self.mplay,"#ff0000You do not have space to add our %s cargo to your ship. Mission failed."%self.cargoname)
            self.aborted=True
            VS.terminateMission(0)
            return

        if (self.quantity==0):
            VS.IOmessage (2,"cargo mission",self.mplay,"#ff0000You do not have space to add our cargo to the mission. Mission failed.")
            self.aborted=True
            VS.terminateMission(0)
            return

        VS.IOmessage (0,"cargo mission",self.mplay,"Your mission is as follows:" )
        self.adjsys.Print("You should start in the system named %s","Then jump to %s","Finally, jump to %s, your final destination","cargo mission",1)
        VS.IOmessage (2,"cargo mission",self.mplay,"Give the cargo to a %s unit or planet." % (self.faction))
        VS.IOmessage (3,"cargo mission",self.mplay,"You will receive %d of the %s cargo" % (self.quantity,self.cargoname))
#         VS.IOmessage (4,"cargo mission",self.mplay,"We will deduct %.2f credits from your account for the cargo needed." % (creds_deducted))
        VS.IOmessage (4,"cargo mission",self.mplay,"You will earn %.2f credits when you deliver our cargo." % (creds))
        VS.IOmessage (4,"cargo mission",self.mplay,"#00ff00Good luck!")
#         self.you.addCredits (-creds_deducted)

    def takeCargoAndTerminate (self,you, remove):
        removenum=0 #if you terminate without remove, you are SKREWED
        self.base.setCombatRole(self.role)
        if (remove):
            removenum=you.removeCargo(self.cargoname,self.quantity,1)
            mpart=VS.GetMasterPartList()
            newcarg=mpart.GetCargo(self.cargoname)
            newcarg.SetQuantity(removenum)
            #self.base.addCargo(newcarg)
            has=self.you.hasCargo(self.cargoname)
            print "Cargo mission, removed " + str(removenum) + " of " + self.cargoname + ", has: " + str(has)
            if (has):
                has=self.you.removeCargo(self.cargoname,has,1)
                print "...removed again %d"%has
                newcarg.SetMissionFlag(0)
                newcarg.SetQuantity(has)
                self.you.addCargo(newcarg) #It seems that removing and then adding it again is the only way...
        if ((removenum>=self.quantity) or (self.quantity==0) or removenum>=1):
            VS.IOmessage (0,"cargo mission",self.mplay,"#00ff00Excellent work pilot.")
            VS.IOmessage (0,"cargo mission",self.mplay,"#00ff00You have been rewarded for your effort as agreed.")
            VS.IOmessage (0,"cargo mission",self.mplay,"#00ff00Your excellent work will be remembered.")
            
            # halved profit if mislanded during a rush mission
            if self.isExpress and self.isMisland:
                self.cred = self.cred / 2
                print 'Express delivery conditions are not met, halved credits: ' + str(self.cred)
            
            you.addCredits(self.cred)
            VS.AdjustRelation(you.getFactionName(),self.faction,.01*self.difficulty,1)
            self.SetVar(1)
            VS.terminateMission(1)
            return
        else:
            VS.IOmessage (0,"cargo mission",self.mplay,"#ff0000You did not follow through on your end of the deal.")
            if (self.difficulty<1):
                VS.IOmessage (0,"cargo mission",self.mplay,"#ff0000Your pay will be reduced")
                VS.IOmessage (0,"cargo mission",self.mplay,"#ff0000And we will consider if we will accept you on future missions.")
                addcred=(float(removenum)/(float(self.quantity*(1+self.difficulty))))*self.cred
                you.addCredits(addcred)
            else:
                VS.IOmessage (0,"cargo mission",self.mplay,"#ff0000You will not be paid!")
                universe.punish(self.you,self.faction,self.difficulty)
            self.SetVar(-1)
            VS.terminateMission(0)
            return

    def knownBases(self):
        if self.base.getName().find("mining_base")!=-1:
            return True
        if (self.base.isPlanet()):
            return True
        if self.base.getName().find("new_constantinople")!=-1:
            return True
        if self.base.getName().find("perry")!=-1:
            return True
        if self.base.getName().find("refinery")!=-1:
            return True
        return False

    def findUnit(self, name):
        i = VS.getUnitList()
        while i.notDone():
            testun=i.current()
            i.advance()
            if testun.getName().lower()==name.lower() or testun.getFullname().lower()==name.lower():
                return testun
        i = VS.getUnitList()
        while i.notDone():
            testun=i.current()
            i.advance()
            if testun.isDockableUnit():
                return testun
        return VS.getUnit(0)
        
    def isTechnological(self, category):
        if category[0] == '*':
          category = category[1:]
        return category in ['Plutonium','Uranium','Construction','Advanced_Fuels','Communications','Computers','Factory_Equipment',
                            'Holographics','Spaceship_Parts','Robot_Servants','Robot_Workers','Medical_Equipment','Mining_Equipment']
    
    def launchAmbush(self):
        numEnemies = 3
        if vsrandom.random() < .3:
            numEnemies = 4
            
        faction = "pirates"
        if self.isTechnological( self.cargoname ) and (vsrandom.random()<0.5):
            faction = "retro"
        self.speech = universe.getRandomGreeting(faction)
            
        for n in range(numEnemies):
            L = launch.Launch()
            L.fg = "Shadow"
            L.faction = faction
            L.dynfg = ''
            L.type = faction_ships.getRandomFighter(faction)
            L.num = 1
            L.ai = "default"
            L.minradius = 700
            L.maxradius = 1100
            enemy = L.launch(self.you)
            enemy.SetTarget(self.you)
            enemy.setFgDirective("A.")
            if n < 1:
                self.talkingEnemy = enemy
                self.greetTime=VS.GetGameTime()+6
                
    
    def Execute (self):
##        if (VS.getGameTime()>mission_time):
##          VS.IOmessage (0,"cargo mission",self.mplay,"You Have failed to deliver your cargo in a timely manner.")
##          VS.IOmessage (0,"cargo mission",self.mplay,"The cargo is no longer of need to us.")
##          if (you):
##            takeCargoAndTerminate(you,0)
##          return
        if (self.you.isNull() or (self.arrived and self.base.isNull())):
            VS.IOmessage (0,"cargo mission",self.mplay,"#ff0000You were unable to deliver cargo. Mission failed.")
            self.SetVar(-1)
            VS.terminateMission(0)
            return
            
        if self.ambushInSystem != '':
            curSystem = VS.getSystemFile()
            if curSystem != self.prevVisitedSystem:
                self.prevVisitedSystem = curSystem
                if curSystem == self.ambushInSystem:
                    self.ambushInSystem = ''
                    self.launchAmbush()
        
        if VS.GetGameTime() >= self.greetTime:
            universe.greet( self.speech, self.talkingEnemy, self.you )
            self.greetTime = 10000000
        
        # raise a flag if incorrectly docked during an express mission
        if self.isExpress and not self.isMisland:
            dockedAt = self.getBasenameDockedAt()
            if not self.departBasename and dockedAt:
                self.departBasename = dockedAt
                #print 'PODXX setting departBasename: ' + self.departBasename

            #print 'PODXX dockedAt[' + dockedAt + '] departBasename[' + self.departBasename + '] destBasename[' + self.destBaseName + ']'
            if dockedAt and (dockedAt != self.destBaseName) and (dockedAt != self.departBasename):
                #print 'PODXX Misland!'
                self.isMisland = True
            
        if (not self.adjsys.Execute() and not (self.arrived and self.base and self.base.isDocked(self.you))):
            return
        if (self.arrived):
            self.adjsys.Execute=self.adjsys.HaveArrived
            if (self.base.isDocked(self.you) or (self.base.getDistance(self.you)<=1 and not self.knownBases())):
                self.takeCargoAndTerminate(self.you,1)
                return
        else:
            if not len(self.destBaseName):
              self.arrived=1
              tempfac=self.faction
              if vsrandom.random()<=.3:
                tempfac=''
              self.adjsys=go_somewhere_significant(self.you,1,100,not self.capship,tempfac)
              capstr="planet"
              dockstr="land"
              if tempfac=='':
                dockstr="dock"
                capstr="ship"
              self.adjsys.Print("You must visit the %%s %s" % (capstr),"cargo mission",", docked around the %s",0)
              VS.IOmessage(0,"cargo mission",self.mplay,"Once there, %s and we will transport the cargo off of your ship." % (dockstr))
              self.base=self.adjsys.SignificantUnit()
              self.role=self.base.getCombatRole()
              self.base.setCombatRole("INERT")
            else:
              self.arrived=1
              self.adjsys=go_none()
              self.base=self.findUnit(self.destBaseName)
              self.obj=VS.addObjective("Deliver cargo to %s." % self.destBaseName);
              VS.setOwner(self.obj,self.you)
              VS.setCompleteness(self.obj,0)            

def initrandom (factionname, missiondifficulty,creds_per_jump, launchoncapship, sysmin, sysmax, time_to_complete, category,jumps=(),var_to_set=''):
    numsys=vsrandom.randrange(sysmin,sysmax)
    return cargo_mission(factionname,numsys, vsrandom.randrange(4,15), missiondifficulty,creds_per_jump*float(1+numsys),launchoncapship, 10.0, category,jumps,var_to_set)









