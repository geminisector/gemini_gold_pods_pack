import cleansweep
import VS
import universe
import faction_ships
import launch
class tripatrol(cleansweep.cleansweep):
	def __init__(self,numsystemsaway, num_points,distance,creds,jumps,donevar,minships,maxships,encounterprob,capshipprob,faction, forceattack,canrunaway,atckType,pirategreeting):	
		cleansweep.cleansweep.__init__(self,numsystemsaway, num_points,distance,creds,jumps,donevar,minships,maxships,encounterprob,capshipprob,faction, forceattack,canrunaway,atckType)
		self.pirategreeting=pirategreeting
		self.tricounter=16
		self.launchedpirate=False
		self.cp=VS.getCurrentPlayer()
	def Track(self,shiptype):
	        pass
	def RealSuccessMission(self):
		cleansweep.cleansweep.RealSuccessMission(self)
		print "TRIPATROL: REAL SUCCESS"
		if (not self.launchedpirate):
			jumpToWar = universe.findJumppoint("Jump_To_War")
			jumpToDeath = universe.findJumppoint("Jump_To_Death")
			jp = jumpToWar
			
			print "tripatrol: LAUNCHING PIRATE"
			
		        # in case sometimes the pirate becomes hostile for unknown reason
		        rel = VS.GetRelation("drake_pirate","privateer")
                        while rel < 0:
                          VS.AdjustRelation( "drake_pirate", "privateer", 1-rel, 1.0)
                          rel = VS.GetRelation("drake_pirate","privateer")


			self.launchedpirate=True
			L= launch.Launch()
			L.faction="drake_pirate"
			L.fg="Drake"
			L.dynfg="" 
			L.minradius=500.0
			L.maxradius=500.0
			L.ai="default"
			L.num=1
			L.type=faction_ships.getRandomFighter("pirates")
			
			if self.you.getDistance(jumpToWar) <= 2500.0:
			    pirate=L.launch(jumpToWar)
			elif self.you.getDistance(jumpToDeath) <= 2500.0:
			    pirate=L.launch(jumpToDeath)
			    jp = jumpToDeath
			else:
			    pirate=L.launch(self.you)
			    
			pirate.upgrade("jump_drive",0,0,0,1)
			pirate.SetTarget(jp)
			pirate.ActivateJumpDrive(0)
			
			universe.greet(self.pirategreeting,pirate,self.you)
			#pirate.SetVelocity((0,0,1000))
	def Execute(self):
		if (VS.getPlayer()==self.you and self.tricounter>=0):
			self.tricounter-=1
			if (self.tricounter==8):
				VS.LoadMission("patroldeath.mission")
			if (self.tricounter==0):
				VS.LoadMission("patrolwar.mission");
		cleansweep.cleansweep.Execute(self)