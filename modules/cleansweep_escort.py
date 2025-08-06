import VS
import unit
import cleansweep
import universe
import vsrandom
import launch
import faction_ships
class cleansweep_escort(cleansweep.cleansweep):
	def __init__(self,numsystemsaway, num_points,distance,creds,jumps,donevar,minships,maxships,encounterprob,capshipprob,faction, forceattack,canrunaway, friendlyfaction,allygreetingtext=[],lastnum=3,enemygreetingtext=[]):
		cleansweep.cleansweep.__init__(self,numsystemsaway,num_points,distance,creds,jumps,donevar,minships,maxships,encounterprob,capshipprob,faction,forceattack,canrunaway)
		self.friendlyfaction=friendlyfaction
		self.allygreetingtext=allygreetingtext
		self.allyEndtext = [("Good work! We'd had been cat meal without your help.",True,"campaign/Uhler2.wav")]
		self.launchedyet=False
		self.ally=None
		self.lastnum=lastnum
		self.allyobj=0
		self.enemygreetingtext=enemygreetingtext
		self.KahlTalked = False
		self.capshipFaction = 'kahl'
		self.engreetedyet=0
		self.enemygreetingtime=0
		self.talkTime = 10000000
		self.uhlerTalked = False
		self.uhlerTalkedTwice = False
	def LaunchAlly(self):
		L = launch.Launch()
		L.faction='uhler'
		L.fg="Patrol_Wing"
		L.dynfg=""
		L.minradius=400.0
		L.maxradius=600.0
		L.num=1
		L.ai="default"
		L.type = faction_ships.getRandomCapitol(self.friendlyfaction)
		self.ally = L.launch(self.you)
		self.ally.setMissionRelevant()
		self.allyobj=VS.addObjective("Protect Commodore Uhler's Paradigm")

		L.type = faction_ships.getRandomFighter(self.friendlyfaction)
		L.num=vsrandom.randrange(3,6)
		L.faction=self.friendlyfaction
		L.launch(self.you)

		self.talkTime=VS.GetGameTime()+6
	
	def Execute(self):
		if VS.GetGameTime() >= self.talkTime:
                    self.talkTime = 10000000
                    if not self.uhlerTalked:
                        universe.greet(self.allygreetingtext,self.ally,self.you)
                        self.uhlerTalked = True
                    else:
		        universe.greet(self.enemygreetingtext,self.launchedCapship[0],self.you)
                        
		if (self.adjsys.HaveArrived()):
			if (self.you and not self.launchedyet):
				self.launchedyet=True
				self.LaunchAlly()
			else:
				if (not self.ally):
					VS.setCompleteness(self.allyobj,-1.0)
		cleansweep.cleansweep.Execute(self)
	def DeletePatrolPoint(self,num,nam):
		tmp=self.encounterprob
		if (self.engreetedyet!=1 or VS.GetGameTime()>self.enemygreetingtime+10):
			self.enemygreetingtime=VS.GetGameTime()
			self.engreetedyet+=1
		if (len(self.patrolpoints)==1 and self.launchedyet):
			if (self.ally):
				pos= self.you.Position()
				pos=(pos[0],pos[1]+2*self.ally.rSize(),pos[2]+self.you.rSize()*2+2*self.ally.rSize())
				self.ally.SetPosition(pos)#move him nearby to last nav point
				self.encounterprob=1.0
				self.minships=self.lastnum
				self.maxships=self.lastnum
				if self.capshipprob < 0:
				    self.capshipprob = 1.0
		elif (self.engreetedyet==2):
			self.encounterprob=1.0
		cleansweep.cleansweep.DeletePatrolPoint(self,num,nam)
		if len(self.launchedCapship) and not self.KahlTalked:
		    self.talkTime=VS.GetGameTime()+6
		    self.KahlTalked = True
		self.encounterprob=tmp
	def RealSuccessMission(self):
		if (self.ally or not self.launchedyet):
			cleansweep.cleansweep.RealSuccessMission(self)
			if self.KahlTalked and not self.uhlerTalkedTwice:
			    # we expect this branch happens only after all enemies killed
			    self.uhlerTalkedTwice = True
			    universe.greet(self.allyEndtext,self.ally,self.you)
			    #self.you.commAnimation("com_reismann_male_01.ani")
                            #VS.playSound("campaign/Uhler2.wav",(0.,0.,0.),(0.,0.,0.))
		else:
			self.FailMission()
			
