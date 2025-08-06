import patrol_enemies
import unit
import VS
class cleansweep(patrol_enemies.patrol_enemies):
	def __init__(self,numsystemsaway, num_points,distance,creds,jumps,donevar,minships,maxships,encounterprob,capshipprob,faction, forceattack,canrunaway,atckType=[],greeting=[]):
		patrol_enemies.patrol_enemies.__init__(self,numsystemsaway, num_points,distance,creds,jumps,donevar,minships,maxships,encounterprob,capshipprob,faction,forceattack,atckType,greeting)
		self.enum=0
		self.canrunaway=canrunaway
		self.activeships=[]
		self.guaranteed_success=False
	
	def Track(self,shiptype):
		import VS
                unitName = unit.getUnitFullName(shiptype,False)
                colonIn = unitName.find(":")
                if (colonIn!=-1):
                  unitName = unitName[0:colonIn].capitalize()
		obj=VS.addObjective( "Destroy enemy: " + unitName )
		VS.setOwner(obj,self.you)
		VS.setCompleteness(obj,-1.0)
		self.activeships.append((shiptype,obj))
		
	def SuccessMission(self):
		self.guaranteed_success=True
	def RealSuccessMission(self):
		patrol_enemies.patrol_enemies.SuccessMission(self)
	def DeletePatrolPoint(self,num,nam):
		patrol_enemies.patrol_enemies.DeletePatrolPoint(self,num,nam)
	def Dead(self,activeship):
		runawaydist=4000
		tmp = (self.canrunaway and activeship[0].GetHullPercent()<.7)
		if tmp:
			VS.setCompleteness(activeship[1],0.0)
		ret = ((tmp and self.you.getDistance(activeship[0])>runawaydist) or not activeship[0])
		return ret
	def Execute(self):
		if (self.enum>=len(self.activeships)):
			self.enum=0
		else:
			if (self.Dead(self.activeships[self.enum])):
				obj = self.activeships[self.enum][1]
				VS.setCompleteness(obj,1.0)
		                VS.eraseObjective(obj)
				del self.activeships[self.enum]
		                for i in range(0, len(self.activeships)):
		                   #print "PODXX clsw5 decreasing obj index for ship: " + str(i) + ", cur index: " + str(self.activeships[i][1]) + ", deleted obj index: " + str(obj)
		                   if self.activeships[i][1] > obj:
		                     self.activeships[i] = (self.activeships[i][0], self.activeships[i][1]-1)
			else:
				self.enum+=1
		if (len(self.activeships)==0 and self.guaranteed_success):
			self.RealSuccessMission()
		else:
			patrol_enemies.patrol_enemies.Execute(self)
