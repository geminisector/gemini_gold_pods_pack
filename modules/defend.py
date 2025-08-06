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
running_defend_missions={}
class defend (Director.Mission):
        
    def __init__ (self,factionname,numsystemsaway, enemyquantity, distance_from_base, escape_distance, creds, defendthis, defend_base,protectivefactionname='',jumps=(),var_to_set='',dynamic_flightgroup='',dynamic_type='', dynamic_defend_fg='',waves=0, greetingText=['We will defeat your assets in this battle, privateer...','Have no doubt!'], defendDestination = '', defendObjectiveText = ''):
        Director.Mission.__init__(self)
        self.dedicatedattack=1   #PODXX vsrandom.randrange(0,2)
        self.arrived=0
        self.waves=waves;
        self.greetingText=greetingText
        self.greetTime = 10000000
        self.protectivefaction = protectivefactionname
        self.var_to_set=var_to_set
        self.quantity=0
        self.mplay="all"
        self.dynatkfg = dynamic_flightgroup     
        self.dynatktype = dynamic_type
        self.dyndeffg = dynamic_defend_fg
        self.attackers = []
        self.objective= 0
        self.targetiter = 0
        self.ship_check_count=0
        self.defend = defendthis
        self.defend_base = defend_base
        self.faction = factionname
        self.escdist = escape_distance
        minsigdist=unit.minimumSigDistApart()
        if (minsigdist*.5<self.escdist):
            self.escdist = minsigdist
        self.cred=creds
        self.respawn=0
        self.quantity=enemyquantity
        self.savedquantity=enemyquantity
        self.distance_from_base=distance_from_base
        self.defendee=VS.Unit()
        self.difficulty=1
        self.you=VS.getPlayer()
        self.younum=VS.getCurrentPlayer()
        self.assistProb = vsrandom.randrange(30,45)*.01
        name = self.you.getName ()
        self.mplay=universe.getMessagePlayer(self.you)
        self.adjsys = go_to_adjacent_systems(self.you,numsystemsaway,jumps)  
        self.adjsys.Print("You are in the %s system,","Proceed swiftly to %s.","Your arrival point is %s.","defend",1)
        VS.IOmessage (2,"defend",self.mplay,"And there eliminate any %s starships."  % self.faction)
        self.key=str(VS.getCurrentPlayer())+str(factionname)+str(numsystemsaway)+str(enemyquantity)+str(distance_from_base)+str(escape_distance)+str(creds)+str(defendthis)+str(defend_base)+str(protectivefactionname)+str(jumps)+str(var_to_set)+str(dynamic_flightgroup)+str(dynamic_type)+str(dynamic_defend_fg)+str(waves)+str(greetingText);
        global running_defend_missions
        running_defend_missions[self.key]=0
        self.run_def_mis=0
        self.defendDestination = defendDestination
        self.defendObjectiveText = defendObjectiveText

    def SetVarValue (self,value):
        if (self.var_to_set!=''):
            quest.removeQuest (self.you.isPlayerStarship(),self.var_to_set,value)
    def SuccessMission (self):
        self.you.addCredits (self.cred)
        VS.AdjustRelation(self.you.getFactionName(),self.faction,.03,1)
        self.SetVarValue(1)
        VS.IOmessage(0,"defend",self.mplay,"[Computer] Defend mission accomplished")
        if (self.cred>0):
            VS.IOmessage(0,"defend",self.mplay,"[Computer] Bank account has been credited as agreed.")
        VS.terminateMission(1)
    def FailMission (self):
        self.you.addCredits (-self.cred)
        VS.AdjustRelation(self.you.getFactionName(),self.faction,-.02,1)                
        self.SetVarValue(-1)
        VS.IOmessage (0,"defend",self.mplay,"[Computer] Detected failure to protect mission asset.")
        VS.IOmessage (0,"defend",self.mplay,"[Computer] Mission failed!")
        VS.IOmessage (1,"defend",self.mplay,"[Computer] Bank has been informed of failure to assist asset. They have removed a number of your credits as a penalty to help pay target insurance.")
        VS.terminateMission(0)
    def NoEnemiesInArea (self,jp):
        if (self.adjsys.DestinationSystem()!=VS.getSystemFile()):
            return 0
        if (self.ship_check_count>=len(self.attackers)):
            VS.setCompleteness(self.objective,1.0)
            return 1

        un= self.attackers[self.ship_check_count]
        VS.adjustFGRelationModifier(self.younum,un.getFlightgroupName(),-.01);
        self.ship_check_count+=1
        if (un.isNull() or (un.GetHullPercent()<.7 and self.defendee.getDistance(un)>7000)):
            return 0
        else:
#            VS.setObjective(self.objective,"Destroy the %s"%unit.getUnitFullName(un))
            VS.setObjective(self.objective,"Destroy %s ships"% (self.faction.capitalize()))
            self.ship_check_count=0
        return 0
        
    def generateAssistance( self, defendee, you ):
        assFactions = ["militia", "militia", "confed", "hunter"]
        faction = assFactions[ vsrandom.randrange( 0, len(assFactions) ) ]
        L = launch.Launch()
        L.fg="Assist"; L.dynfg='';
        L.type=faction_ships.getRandomFighter(faction)
        L.ai="default";L.num=1;L.minradius=1200.0;L.maxradius=1500.0
        L.faction=faction
        launched=L.launch(self.defendee)

        
    def GenerateEnemies (self,jp,you):
        VS.IOmessage (0,"escort mission",self.mplay,"You must protect %s." % unit.getUnitFullName(jp,True))
        count=0
        jp.setMissionRelevant()
        if self.defendObjectiveText <> '':
            if self.defendObjectiveText <> 'none':
                VS.addObjective (self.defendObjectiveText)
        else:
            VS.addObjective ("Protect %s from the %s" % (unit.getUnitFullName(jp),self.faction.capitalize().replace("_"," ")))
        self.objective = VS.addObjective ("Destroy %s ships"% (self.faction.capitalize()))
        VS.setCompleteness(self.objective,0.0)
#        print "defend.GenerateEnemies quantity "+str(self.quantity)
        while (count<self.quantity):
            L = launch.Launch()
            L.fg="Shadow";L.dynfg=self.dynatkfg;
            if (self.dynatktype==''):
                L.type=faction_ships.getRandomFighter(self.faction)
            else:
                L.type=self.dynatktype
            L.ai="default";L.num=1;L.minradius=900.0;L.maxradius=1200.0
            L.faction=self.faction
            launched=L.launch(self.defendee)
            if (count==0):              
                self.you.SetTarget(launched)            

            if (self.defend):
                launched.SetTarget (jp)
            else:
                 launched.SetTarget (self.you)
            if (self.dedicatedattack):
                launched.setFgDirective('A.')
            self.attackers += [ launched ]
            count+=1
        if (self.respawn==0 and len(self.attackers)>0):
            self.respawn=1
            self.greetTime=VS.GetGameTime()+6
#            universe.greet(self.greetingText,self.attackers[0],you);
        else:
            VS.IOmessage (0,"escort mission",self.mplay,"Eliminate all %s ships here" % self.faction)

        self.quantity=0
    def Execute (self):
        if (self.you.isNull() or (self.arrived and self.defendee.isNull())):
            VS.IOmessage (0,"defend",self.mplay,"#ff0000You were unable to arrive in time to help. Mission failed.")
            self.SetVarValue(-1)
            VS.terminateMission(0)
            return   

        global running_defend_missions
        if running_defend_missions[self.key]!=self.run_def_mis:
            print "ABORTING DEFEND MISSION WITH PARAMS "+self.key+" because another is running "
            VS.terminateMission(1)
            return
        running_defend_missions[self.key]+=1
        self.run_def_mis+=1
        if (not self.adjsys.Execute()):
            return
        if (not self.arrived):
            self.arrived=1
            tempfaction=''
            if (self.defend_base):
                tempfaction=self.protectivefaction
                if (tempfaction==''):
                    tempfaction = faction_ships.get_enemy_of(self.faction)
#            self.adjsys=go_somewhere_significant (self.you,self.defend_base or self.defend,self.distance_from_base,self.defend,tempfaction,self.dyndeffg,1,not self.defend_base)
# 1,0,0 to defend a planet; 0,1,1 to defend a ship
            self.adjsys=go_somewhere_significant (self.you,self.defend_base,self.distance_from_base,not self.defend_base,tempfaction,self.dyndeffg,1,not self.defend_base, self.defendDestination)
            self.adjsys.Print ("You must visit the %s","defend","near the %s", 0)
            self.defendee=self.adjsys.SignificantUnit()
        else:
            if (self.defendee.isNull ()):
                if (self.defend):
                    self.FailMission(you)
                else:
                    self.SuccessMission()
                    return
            else:
                if VS.GetGameTime() >= self.greetTime:
                    if self.defend_base and len(self.attackers):
                        universe.greet(self.greetingText,self.attackers[0],self.you)
                    else:
                        universe.greet(self.greetingText,self.defendee,self.you)
                    self.greetTime = 10000000
        
                if (self.quantity>0):
                    if vsrandom.random() < self.assistProb:
                      self.generateAssistance(self.defendee,self.you)
                      self.quantity += 1
                    self.GenerateEnemies (self.defendee,self.you)
                if (self.ship_check_count==0 and self.dedicatedattack):
                    if (self.targetiter>=len(self.attackers)):
                        self.targetiter=0
                    else:
                        un =  self.attackers[self.targetiter]
                        if (not un.isNull()):
                            un.setFgDirective('A.')
                            if (self.defend):
                                un.SetTarget (self.defendee)
                            else:
                                un.SetTarget (self.you)
                        self.targetiter=self.targetiter+1
                if (self.NoEnemiesInArea (self.defendee)):
                    if (self.waves>0):
                        self.quantity=self.savedquantity
                        self.waves-=1
                    else:
                        self.SuccessMission()
    def initbriefing(self):
        print "ending briefing"                
    def loopbriefing(self):
        print "loop briefing"
        Briefing.terminate();
    def endbriefing(self):
        print "ending briefing"        
                
def initrandom(factionname,numsysaway,minenquant,maxenquant,credperen,defendit,defend_base,p_faction='',jumps=(),var_to_set=''):
    enq=minenquant
    enq=vsrandom.uniform(minenquant,maxenquant) 
    return defend(factionname,numsysaway,enq,8000.0,100000.0,enq*credperen,defendit,defend_base,p_faction,jumps,var_to_set)
