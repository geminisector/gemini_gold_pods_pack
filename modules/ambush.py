import VS
import Director
import directions_mission
import universe

class ambush(directions_mission.directions_mission):
	def privateSetupPlayer(self):
		self.timer=0
		self.inescapable=0
		self.havelaunched=0
		self.terminated=0

	def __init__(self,savevar,systems,delay,faction,numenemies,dyntype='',dynfg='',greetingText=["Hello there, smuggler. Prepare to die!", "The price on your head is big enough that I missed my lunch"], directions=[], destination='',AdjustFaction=True,destObjective=''):
		directions_mission.directions_mission.__init__ (self,savevar,directions,destination,destObjective)
		print 'Ambush: Starting'
		self.faction=faction
		self.systems=systems
		if type(systems)!=tuple and type(systems)!=list :
			self.systems=(systems,)
		self.numenemies=numenemies
		self.dyntype=dyntype
		self.dynfg=''     #dynfg
		self.greetingText=greetingText
		self.greetTime = 10000000
		self.talkingUnit = VS.Unit()
		self.cp=VS.getCurrentPlayer()
		self.delay=delay
		self.privateSetupPlayer()
		self.AdjustFaction=AdjustFaction
		self.systemWhereAmbushWillBeLaunched = ''
		
	def setupPlayer(self,cp):
		print "ambush setting player up"
		directions_mission.directions_mission.setupPlayer(self,cp)
		self.privateSetupPlayer()

	def Launch(self,you):
		if (self.havelaunched==0):
			if (type(self.numenemies)==type(1)):
				self.numenemies=(self.numenemies,)
				self.faction=(self.faction,)
				self.dyntype=(self.dyntype,)
				self.dynfg=(self.dynfg,)
			if (type(self.AdjustFaction)!=type( () ) and type (self.AdjustFaction)!=type([])):
				self.AdjustFaction=(self.AdjustFaction,)
			for i in range (len(self.faction)):
				numenemies=self.numenemies[i]
				faction=self.faction[i]
				for z in range(numenemies):
					AdjustFaction=self.AdjustFaction[-1]
					if (i<len(self.AdjustFaction)):
						AdjustFaction=self.AdjustFaction[i]
					dynfg=""
					if (len(self.dynfg)>i):
						dynfg=self.dynfg[i]
					dyntype=""
					if (len(self.dyntype)>i):
						dyntype=self.dyntype[i]
					print 'Ambush: Launch ships!'
					self.havelaunched=1
					import launch
					L=launch.Launch()
					L.fg="Shadow"
					if (dyntype==""):
						import faction_ships
						dyntype=faction_ships.getRandomFighter(faction)
					L.dynfg=dynfg
					L.type=dyntype
					L.num=1
					L.fgappend="X"
					L.minradius=800
					L.maxradius=1400
					L.faction=faction
					import universe		
					enemy=L.launch(you)

#					if (i==len(self.faction)-1 and z==0):
					if (i==0 and z==0):
					        #print "PODXX ambush setting a speaker: " + faction + ", name: " + enemy.getName()
					        self.greetTime=VS.GetGameTime()+6
					        self.talkingUnit = enemy

					lead=enemy.getFlightgroupLeader()
					enemy.SetTarget(you)
					if (lead):
						lead.SetTarget(you)
					else:
						enemy.setFlightgroupLeader(enemy)
					enemy.setFgDirective("A.")
					self.enemy=lead			
					rel=VS.GetRelation(faction,"privateer")
					if (AdjustFaction and rel>=0):
						VS.AdjustRelation(faction,"privateer",-.02-rel,1.0)
						rel=VS.GetRelation("privateer",faction)
						VS.AdjustRelation("privateer",faction,-.02-rel,1.0)
					#print "launchin"
					print 'Ambush: Ships have been launched. Exiting...'
	def terminate(self):
		self.terminated=1#VS.terminateMission(0)
	def Execute(self):
		directions_mission.directions_mission.Execute(self)
		
		you=VS.getPlayerX(self.cp)
		if you.isNull():
			return

		if (self.terminated == 1 and self.greetTime <> 10000000) or (VS.GetGameTime() >= self.greetTime):
		        universe.greet(self.greetingText,self.talkingUnit,you)
		        self.greetTime = 10000000

		if (self.terminated==1):
			return
		
		sys=you.getUnitSystemFile()
		if(not self.inescapable):
			for i in self.systems:
				where=sys.find(i)
				if (where>0):
					if (sys[where-1]=='/'):
						where=0
				if (where==0):
					self.inescapable=1
					self.timer=VS.GetGameTime()
					self.systemWhereAmbushWillBeLaunched = sys
#					print 'Ambush: wait before launching ship... system: ' + str(sys)
#                if self.inescapable:
#	          print "PODXX ambush launched[" + str(self.havelaunched) + "] delay[" + str(self.delay) + "] passd[" + str(VS.GetGameTime()-self.timer) + "]"
		if (self.inescapable and ((self.delay==0) or (VS.GetGameTime()-self.timer>=self.delay))):
			if self.systemWhereAmbushWillBeLaunched == sys:
			    self.Launch(you)
			    self.terminate()
#					print "it's unavoidable, my young apprentice... in "+str(self.delay)+" seconds from "+str(self.timer)
			
