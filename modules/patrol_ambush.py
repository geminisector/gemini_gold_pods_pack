from go_to_adjacent_systems import *
import vsrandom
import launch
import faction_ships
import VS
import Briefing
import universe
import unit
import quest
import Director
import ambush
class patrol_ambush (ambush.ambush):
	def __init__ (self, num_significants_to_patrol, distance_from_base, creds, savevar,systems,delay,faction,numenemies,dyntype='',dynfg='',greetingText=["Hello there, smuggler. Prepare to die!", "The price on your head is big enough that I missed my lunch"],directions=[],destination='',destObjective='',excludeNavpoints = []):
		ambush.ambush.__init__(self,savevar,systems,delay,faction,numenemies,dyntype,dynfg,greetingText,directions,destination,False,destObjective)
		self.jnum=0
		self.cred=creds
		self.patrolpoints = []
		self.objectives = []
		self.distance = distance_from_base
		self.you = VS.getPlayer()
		self.quantity=num_significants_to_patrol
		name = self.you.getName ()
		self.mplay=universe.getMessagePlayer(self.you)
		self.AdjustFaction=False
		self.excludeNavpoints = excludeNavpoints

	def terminate(self):
		if (quest.checkSaveValue(self.cp,self.var,0) or quest.checkSaveValue(self.cp,self.var,-1)):
			ambush.ambush.terminate(self)
	def SuccessMission (self):	
		if (quest.checkSaveValue(self.cp,self.var,0) or quest.checkSaveValue(self.cp,self.var,-1) or quest.checkSaveValue(self.cp,self.var,1)):
			VS.getPlayerX(self.cp).addCredits (self.cred)
			VS.terminateMission(0)

	def GeneratePatrolList (self):
		VS.IOmessage (0,"patrol",self.mplay,"You must get within %f klicks of" % self.distance)
#		count=self.quantity*2
#		str=""
                all_pp=universe.significantUnits()
                tpp = []
                for isig in range(len(all_pp)):
                  signame = all_pp[isig].getName()
                  #print "PODXX patrolAmbush next signame: " + signame
                  if (signame != "") and (signame.find("Asteroid") < 0) and (signame not in self.excludeNavpoints):
                    #print "PODXX PAmbush: " + signame
                    tpp.append(all_pp[isig])
                all_pp = tpp

		while (self.quantity>0):
		        i = vsrandom.randrange(0,len(all_pp))
			sig = all_pp[i]
			del all_pp[i]
			if (not sig.isNull()):
				nam =sig.getName ()
#				print "PODXX pambush [" + nam + "]"
				if (not (sig in self.patrolpoints)) and (nam != "") and (nam.find("Asteroid") < 0):
					self.patrolpoints += [sig]
					self.quantity=self.quantity-1
					fac =sig.getFactionName()
					if (fac!="neutral"):
						obj=VS.addObjective ("Scan: %s"% nam)
						VS.IOmessage (0,"patrol",self.mplay,"%s owned %s " % (fac,nam))
					else:
						if (sig.isPlanet()):
							if (sig.isJumppoint()):
								obj=VS.addObjective ("Scan: %s" % nam)
							else:
								obj=VS.addObjective ("Scan: %s" % nam)
						else:
							obj=VS.addObjective ("Scan %s" % nam)
						VS.IOmessage (0,"patrol",self.mplay,"The object %s " % nam)
					VS.setOwner(int(obj),VS.getPlayerX(self.cp))
					VS.setCompleteness(int(obj),-1.0)
					self.objectives+=[int(obj)]

		self.quantity=0

	def DeletePatrolPoint (self,num,nam):
		VS.IOmessage (0,"patrol",self.mplay,"[Computer] %s scanned, data saved..."%nam)
		VS.setCompleteness(self.objectives[self.jnum],1.0)
		self.you.commAnimation("scan_complete.ani")
		del self.objectives[self.jnum]
		del self.patrolpoints[self.jnum]
	def FinishedPatrol (self,playa):
		if (self.jnum<len(self.patrolpoints)):
			jpoint =self.patrolpoints[self.jnum]
			VS.setOwner(self.objectives[self.jnum],playa)
			if (jpoint.isNull()):
				self.DeletePatrolPoint(self.jnum,"Debris")
			else:
				if (playa.getSignificantDistance (jpoint)<self.distance):
					self.DeletePatrolPoint(self.jnum,jpoint.getName())
				else:
					self.jnum+=1
		else:
			self.jnum=0
		return (len(self.patrolpoints)==0)
	def Execute (self):
		ambush.ambush.Execute(self)
	        #print "PODXX pambush inesc[" + str(self.inescapable) + "] launched[" + str(self.havelaunched) + "]"
                playa=VS.getPlayerX(self.cp)
		if (playa.isNull()):
			return
		if (self.inescapable):
			if (self.quantity>0):
				self.GeneratePatrolList ()
			else:
				if (self.FinishedPatrol(playa)):
					self.SuccessMission()
				if (self.havelaunched):
					if (not self.enemy.isNull()):
						if (self.enemy.getUnitSystemFile()==playa.getUnitSystemFile()):
        						self.enemy.SetTarget(playa)
