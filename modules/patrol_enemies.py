import patrol
import universe
import VS
class patrol_enemies(patrol.patrol):
	def __init__(self,numsystemsaway, num_points,distance,creds,jumps,donevar,minships,maxships,encounterprob,capshipprob,faction,forceattack,atckType=[],greeting=[],patrolPointsNames=[]):
		patrol.patrol.__init__(self,numsystemsaway,num_points,distance,creds,jumps,donevar,patrolPointsNames)
		self.minships=minships
		self.maxships=maxships
		self.encounterprob=encounterprob
		self.capshipprob=capshipprob
		self.launchedCapship = []
		self.capshipFaction = faction
		self.faction=faction
		self.forceattack=forceattack
		self.atckType=atckType
		self.greeting=greeting
		self.greetTime = 10000000
		self.talkingUnit = VS.Unit()
		self.talkingUnitFaction = self.faction
	def Track(self,shiptype):
		pass
	def SuccessMission(self):
		patrol.patrol.SuccessMission(self)
#	def FinishedPatrol(self):
#	        if self.greetTime < 10000000:
#	            print "PODXX FinishedPatrol self.greetTime: " + str(self.greetTime)
#	            return False
#	        return patrol.patrol.FinishedPatrol(self)
	def DeletePatrolPoint(self,num,nam):
		import vsrandom
		#print "PODXX DPP minships[" + str(self.minships) + "] maxships[" + str(self.maxships) + "] encprob[" + str(self.encounterprob) + "] capprob[" + str(self.capshipprob) + "]"
		if (vsrandom.random()<self.encounterprob):
			import faction_ships
			fac=self.faction
			typeIndex = -1
			if (type(fac) is list or type(fac) is tuple):
				typeIndex = vsrandom.randrange(0,len(fac))
				fac = fac[typeIndex]
			dynfg=""
			import fg_util
			import VS
			for i in range(vsrandom.randrange(self.minships,self.maxships+1)):
				import launch
				L=launch.Launch()
				L.fg="Shadow"
				L.dynfg=''    #dynfg
				L.faction=fac
				if (vsrandom.random()<self.capshipprob):
					L.type=faction_ships.getRandomCapitol(fac)
					L.faction = self.capshipFaction
				else:
				        if typeIndex>=0 and len(self.atckType):
					  L.type=self.atckType[typeIndex]
					  if L.type == '':
					    L.type=faction_ships.getRandomFighter(fac)
					else:
					  L.type=faction_ships.getRandomFighter(fac)
				#print "PODXX typeIndex[" + str(typeIndex) + "] type: " + L.type + " capProb: " + str(self.capshipprob)
				L.ai="default"
				L.num=1
				L.minradius=1000.0
				L.maxradius=1250.0
				L.fgappend="_Patrol"
				if (self.patrolpoints[num]):
					#newun=L.launch(self.patrolpoints[num])
					newun=L.launch(self.you)
					if self.capshipprob > 0:
					    self.launchedCapship = [newun]
					    self.capshipprob = 0         #PODXX one capship is enough
					if (self.forceattack):
						lead=newun.getFlightgroupLeader()
						if (lead):
							lead.SetTarget(self.you)
						else:
							newun.setFlightgroupLeader(newun)
						newun.SetTarget(self.you)
						newun.setFgDirective("A.")
					if i < 1 and len(self.greeting):
					    # only first spawned unit will talk
					    # and we wait few seconds for the scan/autopilot/jump process to finish
					    self.greetTime=VS.GetGameTime()+6
					    self.talkingUnit = newun
					    self.talkingUnitFaction = L.faction
					self.Track(newun)
		patrol.patrol.DeletePatrolPoint(self,num,nam)
		
	def Execute (self):
	        if VS.GetGameTime() >= self.greetTime:
		    nextGreeting = self.greeting
		    if self.greeting == "randomize":
		        nextGreeting = universe.getRandomGreeting(self.talkingUnitFaction)
	            #print "PODXX will greet: " + str(nextGreeting)
	            if len(nextGreeting):
	                universe.greet( nextGreeting, self.talkingUnit, self.you )
	            self.greetTime = 10000000

	        patrol.patrol.Execute(self)