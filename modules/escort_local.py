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
class escort_local (Director.Mission):
	def __init__ (self,factionname,numsystemsaway, enemyquantity,  waves, distance_from_base, creds, incoming, protectivefactionname='',jumps=(),var_to_set='',dynamic_flightgroup='',dynamic_type='', dynamic_defend_fg='',dynamic_defend_type='',greetingText=[],lockOnYouProb=0,attackProb=1,escorteeGreet="",enemyLaunchDelay=0,predefinedSignificantName = ''):
		Director.Mission.__init__(self)
		self.greetingText=greetingText
		self.escorteeGreet = escorteeGreet
		if not len(self.escorteeGreet):
		    self.escorteeGreet = universe.getRandomGreeting("common")
		self.isEnemyTalk = False
		self.greetTime = 10000000
		self.escorteeTalkBeganAt = 10000000
		self.enemyLaunchDelay = enemyLaunchDelay
		self.dedicatedattack=1
		self.lockOnYouProb=lockOnYouProb
		self.arrived=0
		self.todock=VS.Unit()
		self.launchedfriend=0
		self.protectivefaction = protectivefactionname
		self.var_to_set=var_to_set
		self.quantity=0
		self.mplay="all"
		self.gametime=VS.GetGameTime()
		self.waves=waves
		self.incoming=incoming
		self.dynatkfg = dynamic_flightgroup	 
		self.dynatktype = dynamic_type
		self.dyndeffg = dynamic_defend_fg
		self.dyndeftype = dynamic_defend_type
		self.attackedByEnemies = vsrandom.random()<attackProb
		self.attackers = []
		self.objective= 0
		self.targetiter = 0
		self.lockedOnYou = []
		self.ship_check_count=0
		self.faction = factionname
		self.jp=VS.Unit()
		self.cred=creds
		self.quantity=enemyquantity
		self.savedquantity=enemyquantity
		self.distance_from_base=distance_from_base
		self.defendee=VS.Unit()
		self.difficulty=1
		self.younum=VS.getCurrentPlayer()
		self.you=VS.getPlayer()
		self.respawn=0
		name = self.you.getName ()
		self.successdelay=0
		self.objectivezero=0
		self.adjustedAfterAutopilot = incoming
		self.predefinedSignificantName = predefinedSignificantName
		self.mplay=universe.getMessagePlayer(self.you)
		self.adjsys = go_to_adjacent_systems(self.you,numsystemsaway,jumps)
		VS.IOmessage (0,"escort mission",self.mplay,"Your mission is as follows:")
		self.adjsys.Print("You are in the %s system,","Proceed swiftly to %s.","Your arrival point is %s.","escort mission",1)
		self.shipName = ''
		self.docking = False

	def SetVarValue (self,value):
		if (self.var_to_set!=''):
			quest.removeQuest (self.you.isPlayerStarship(),self.var_to_set,value)
	def SuccessMission (self):
		if (self.incoming):
			un=unit.getSignificant(vsrandom.randrange(0,20),1,0)
			if (un.getName()==self.defendee.getName()):
				un=unit.getSignificant(vsrandom.randrange(0,30),1,0)
			if (un.getName()==self.defendee.getName()):
				un=unit.getSignificant(vsrandom.randrange(0,40),1,0)
			if (un.getName()==self.defendee.getName()):
				un=unit.getSignificant(vsrandom.randrange(0,30),1,0)
			if (un.getName()==self.defendee.getName()):
				un=unit.getSignificant(vsrandom.randrange(0,40),1,0)
			if (un.getName()!=self.defendee.getName()):
				self.todock=un
				#print "docking with "+un.getName()
				VS.setObjective (self.objectivezero,"Escort To %s" % unit.getUnitFullName(un))
				VS.addObjective("Protect " + self.shipName + " till docking.")
				self.successdelay=1000000
				self.defendee.SetTarget(self.you)
			        self.defendee.setFlightgroupLeader(self.you)
				self.defendee.setFgDirective('f') 
			else:
			        self.you.SetTarget(self.defendee)
			        self.successdelay=VS.GetGameTime()+30
			
		else:
			self.defendee.setFgDirective('b') 
			self.defendee.setFlightgroupLeader(self.defendee)
			self.defendee.ActivateJumpDrive(0)			
			self.defendee.SetTarget(self.adjsys.SignificantUnit())
			VS.addObjective("Protect " + self.shipName + " till jumping.")
			self.you.SetTarget(self.defendee)
			self.successdelay=VS.GetGameTime()+120

	def PayMission(self):
		VS.AdjustRelation(self.you.getFactionName(),self.protectivefaction,.03,1)
		self.SetVarValue(1)
		if (self.cred>0):
			self.you.addCredits (self.cred)
			VS.IOmessage(0,"escort mission",self.mplay,"Excellent work pilot! Your effort has thwarted the foe!")
			VS.IOmessage(0,"escort mission",self.mplay,"You have been rewarded for your effort as agreed.")
		VS.terminateMission(1)
	def FailMission (self):
		self.you.addCredits (-self.cred)
		VS.AdjustRelation(self.you.getFactionName(),self.protectivefaction,-.02,1)				
		self.SetVarValue(-1)
		VS.IOmessage (0,"escort mission",self.mplay,"You Allowed the base you were to protect to be destroyed.")
		VS.IOmessage (0,"escort mission",self.mplay,"You are a failure to your race!")
		VS.IOmessage (1,"escort mission",self.mplay,"We have contacted your bank and informed them of your failure to deliver on credit. They have removed a number of your credits for this inconvenience. Let this serve as a lesson.")
		VS.terminateMission(0)
	def NoEnemiesInArea (self,jp):
		if (self.adjsys.DestinationSystem()!=VS.getSystemFile()):
			return 0
		if (self.ship_check_count>=len(self.attackers)):
			VS.setCompleteness(self.objective,1.0)
			return 1
		un= self.attackers[self.ship_check_count]
		self.ship_check_count+=1
		if (un.isNull() or (un.GetHullPercent()<.7 and self.defendee.getDistance(un)>7000)):
			return 0
		else:
#			VS.setObjective(self.objective,"Destroy the %s"%unit.getUnitFullName(un))
#PODXX shorter task fits display better
			VS.setObjective(self.objective,"Repel %s attack"%self.faction)
			self.ship_check_count=0
		return 0
		
	def GenerateEnemies (self,defendee,you):
		count=0
		self.lockedOnYouCount = 0
#PODXX shorter task fits display better
#		self.objectivezero=VS.addObjective ("Protect %s from %s" % (unit.getUnitFullName(defendee),self.faction))
#		self.objectivezero=VS.addObjective ("Protect %s from %s" % (self.dyndeftype,self.faction))
		self.objective = VS.addObjective ("Destroy All %s Hostiles" % self.faction)
		VS.setCompleteness(self.objective,0.0)
		#print "quantity "+str(self.quantity)
		while (count<self.quantity):
			L = launch.Launch()
			L.fg="Shadow";L.dynfg=self.dynatkfg;
			if (self.dynatktype==''):
				L.type=faction_ships.getRandomFighter(self.faction)
			else:
				L.type=self.dynatktype
			L.ai="default";L.num=1;L.minradius=1200.0;L.maxradius=1800.0
			L.faction=self.faction
			launched=L.launch(defendee)
			if (count==0):
				self.you.SetTarget(launched)			

			if (vsrandom.random()>=self.lockOnYouProb):
				launched.SetTarget (defendee)
			else:
				launched.SetTarget (you)
				self.lockedOnYou += [ launched ]
			launched.setFgDirective('A.')
			self.attackers += [ launched ]
			count+=1
			VS.adjustFGRelationModifier(self.younum,launched.getFlightgroupName(),-2);
		#print "PODXX self.self.lockedOnYou[" + str(len(self.lockedOnYou)) + "]"
		defendee.setFgDirective('b')
		if (self.respawn==0 and len(self.attackers)>0):
			self.respawn=1
			self.greetTime=VS.GetGameTime()+6
			self.isEnemyTalk = True
		else:
			VS.IOmessage (0,"escort mission",self.mplay,"Eliminate all %s ships here" % self.faction)
			VS.IOmessage (0,"escort mission",self.mplay,"You must protect %s." % unit.getUnitFullName(defendee))

		self.quantity=0
	def GenerateDefendee(self):
		L=launch.Launch()
		L.fg ="Escort"
		L.faction=self.protectivefaction
		if (self.dyndeffg=='' and self.dyndeftype==''):
			L.type = faction_ships.getRandomFighter(self.protectivefaction)
		else:
			L.type = self.dyndeftype
		L.dynfg = self.dyndeffg
		import escort_mission
		escort_mission.escort_num+=1
		L.fgappend = str(escort_mission.escort_num)
		L.ai = "default"
		L.num=1
		L.minradius = 150
		L.maxradius = 300
		L.forcetype=True
		nearing = self.you
		if self.incoming and self.jp:
		    nearing = self.jp
		escortee=L.launch(nearing)
		if self.incoming:
		    moveUnitTo(escortee,self.you,650)
#		    if not self.attackedByEnemies:
#		        self.greetTime=VS.GetGameTime()+6
#		else:
#		    self.greetTime=VS.GetGameTime()+6

 	        #print "PODXX setting greettime: " + str(VS.GetGameTime())
 	        self.greetTime=VS.GetGameTime()+6
		
		escortee.upgrade("jump_drive",0,0,0,1)
		escortee.setFlightgroupLeader(self.you)
		escortee.setFgDirective('f')
		escortee.setMissionRelevant()

		self.shipName = self.dyndeftype.capitalize()
		dotIn = self.shipName.find(".")
                if (dotIn!=-1):
                  self.shipName = self.shipName[0:dotIn]

		return escortee

	def Execute (self):
		if VS.GetGameTime() >= self.greetTime:
		    self.greetTime = 10000000
		    if self.isEnemyTalk:
		        universe.greet(self.greetingText,self.attackers[0],self.you);
		    else:
        	        self.escorteeTalkBeganAt = VS.GetGameTime()
		        universe.greet(self.escorteeGreet,self.defendee,self.you)
			        
		if (self.successdelay):
			if ( (not self.incoming and self.defendee.getUnitSystemFile()!=self.you.getUnitSystemFile()) or VS.GetGameTime()>self.successdelay or (self.incoming and self.todock.isNull()==False)):
				if (not self.defendee):
				    self.FailMission()
				if not self.incoming:
				    self.PayMission()
				else:
				    if VS.GetGameTime()>self.successdelay:
				        self.PayMission()    
				    elif not self.docking and self.you.getDistance(self.todock)<1200:
				        #print "PODXX docking, distance: " + str(self.defendee.getDistance(self.todock))
				        self.defendee.setFgDirective('b') 
				        self.defendee.setFlightgroupLeader(self.defendee)
				        self.you.SetTarget(self.defendee)
				        self.defendee.performDockingOperations(self.todock,0)
				        self.successdelay = VS.GetGameTime() + 20
				        self.docking = True
			return #nothing more happens inside this control
			
		if (self.you.isNull() or (self.launchedfriend and self.defendee.isNull())):
			VS.IOmessage (0,"escort mission",self.mplay,"#ff0000You were unable to arrive in time to help. Mission failed.")
			self.SetVarValue(-1)
			VS.terminateMission(0)
			return
		if (not self.adjsys.Execute()):
			return
		if (not self.arrived):
			self.arrived=1
			if (self.launchedfriend==0 and not self.incoming):
				 self.defendee=self.GenerateDefendee()
				 self.launchedfriend=1
			self.adjsys=go_somewhere_significant (self.you,0,self.distance_from_base,0,"","",1,0,self.predefinedSignificantName)
			self.adjsys.Print ("You must visit the %s","escort mission","docked around the %s", 0)
			self.jp=self.adjsys.SignificantUnit()
		else:
			if (self.launchedfriend==0):
				 self.defendee=self.GenerateDefendee()
				 self.launchedfriend=1
			if (self.defendee.isNull ()):
				self.FailMission(you)
				return
			else:
				self.defendee.setFlightgroupLeader(self.you)
				if (self.quantity>0 and self.attackedByEnemies):
				    if not self.adjustedAfterAutopilot:
				        self.adjustedAfterAutopilot = True
				        moveUnitTo(self.defendee,self.you,150)      
				    if self.greetTime < 10000000 and not self.isEnemyTalk:
				        # letting an escortee to begin talking
				        return
				    if VS.GetGameTime() - self.escorteeTalkBeganAt < self.enemyLaunchDelay:
				        #this was done mostly for a Hunter Toth mission to work properly, he talks long so we have to wait...
				        return
				    self.GenerateEnemies (self.defendee,self.you)
				if (self.ship_check_count==0 and len(self.attackers)):
					if (self.targetiter>=len(self.attackers)):
					    self.targetiter=0
					un =  self.attackers[self.targetiter]
					if (not un.isNull()):
					  if (un in self.lockedOnYou):
					    un.SetTarget (self.you)
					  else:
					    un.SetTarget (self.defendee)
					un.setFgDirective('A.')
					self.targetiter += 1
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

