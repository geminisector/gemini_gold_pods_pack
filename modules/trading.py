import vsrandom
import VS

from XGUIDebug import trace
_trace_level = 3
import debug

production={}
def getImports(name,faction):
    try:
        prodlist=[]
        s = VS.LookupUnitStat(name,faction,"Cargo_Import")
        while (len(s)):
            where=s.find("{")
            if (where==-1):
                s=""
                break;
            else:
                s=s[where+1:]
            #debug.debug("beg: "+s)
            where = s.find("}")
            if (where==-1):
                s=""
                break;
            else:
                tmp=s[:where]
                prodlist.append(tmp.split(";"))
                s=s[where+1:]
                if (len(prodlist[-1])>4):
                    try:
                        prodlist[-1][1]=float(prodlist[-1][1])
                    except:
                        prodlist[-1][1]=0.0
                    try:
                        prodlist[-1][2]=float(prodlist[-1][2])
                    except:
                        prodlist[-1][2]=0.0
                    try:
                        prodlist[-1][3]=float(prodlist[-1][3])
                    except:
                        prodlist[-1][3]=0.0
                    try:
                        prodlist[-1][4]=float(prodlist[-1][4])
                    except:
                        prodlist[-1][4]=0.0
                #print "rest "+s
        trace(_trace_level, "trading.getImports(%s,%s)" %(name,faction))
        trace(_trace_level, "prodlist =")
        trace(_trace_level, prodlist)
        
        #print "PODXX base[" + name + "] faction[" + faction + "] prodlist: " + str(prodlist)

        return prodlist
    except:
        import sys
        debug.error("GetImportFailure\n"+str(sys.exc_info()[0])+str(sys.exc_info()[1]))
    return []
def getExports(name,faction, twice=1000000):
	prodlist=getImports(name,faction)
	for i in range(len(prodlist)-1,-1,-1):
		if prodlist[i][3]==0 and prodlist[i][4]<=3:
			del prodlist[i]
		elif prodlist[i][3]>twice:
			prodlist.append(prodlist[i])
	trace(_trace_level, "trading.getExports(%s,%s,%s)" %(name,faction,twice))
	trace(_trace_level, "prodlist =")
	trace(_trace_level, prodlist)

	return prodlist
def getNoStarshipExports(name,faction,twice=10000):
	prodlist=getExports(name,faction,twice)
	for i in range(len(prodlist)-1,-1,-1):
		if prodlist[i][0].find('upgrades')==0:
			del prodlist[i]
		elif prodlist[i][0].find('starships')==0:
			del prodlist[i]
	trace(_trace_level, "trading.getNoStarshipExports(%s,%s,%s)" %(name,faction,twice))
	trace(_trace_level, "prodlist =")
	trace(_trace_level, prodlist)

	return prodlist

def findCargo(produceList, cargoName):
        for i in produceList:
          if (i[0] == cargoName) or (i[0][11:] == cargoName):
            return i
        return []
        
def getDefaultExports(produceList):
        de = []
        for i in produceList:
          category = i[0]
          if not isCommodity(category, category): continue
          if i[3] > 0:
            de.append(i)
        return de

defaultCargoPrices = {}

def getDefaultCargoPrice( cargoName ):
        global defaultCargoPrices
        if not len(defaultCargoPrices):
            masterList = VS.GetMasterPartList()
            for i in range(masterList.numCargo()):
                cargo = masterList.GetCargoIndex(i)
                category = cargo.GetCategory()
                if not isCommodity(category, category): continue
                
                defaultCargoPrices[category] = cargo.GetPrice()
                #print "PODXX category: " + category + ", added default price: " + str(cargo.GetPrice())
        return defaultCargoPrices[cargoName]

def getExportsModificators(defaultExports):
        outOfStockCount = 0
        doubleQuantity = False
        reducedPrice = False
        numberOfExports = len(defaultExports)
        rnd = vsrandom.random()
        if numberOfExports == 1:
            if rnd < 0.2:
                outOfStockCount = 1
            else:
                doubleQuantity = vsrandom.random() < 0.25
                reducedPrice = vsrandom.random() < 0.3
        elif numberOfExports <= 3:
            doubleQuantity = rnd < 0.3
            reducedPrice = vsrandom.random() < 0.35
            if vsrandom.random() < 0.2:
                outOfStockCount = 1
        elif numberOfExports <= 5:
            doubleQuantity = rnd < 0.35
            reducedPrice = vsrandom.random() < 0.4
            outOfStockCount = vsrandom.randrange(1,3)
        elif numberOfExports <= 8:
            doubleQuantity = rnd < 0.35
            reducedPrice = vsrandom.random() < 0.45
            outOfStockCount = vsrandom.randrange(2,4)
        elif numberOfExports <= 10:
            doubleQuantity = rnd < 0.4
            reducedPrice = vsrandom.random() < 0.5
            outOfStockCount = vsrandom.randrange(3,5)
        else:
            doubleQuantity = rnd < 0.5
            reducedPrice = vsrandom.random() < 0.6
            outOfStockCount = vsrandom.randrange(4,6)
            
        vsrandom.shuffle(defaultExports)
        outOfStock = []
        for i in range(outOfStockCount):
            outOfStock.append(defaultExports[i][0])
        doublingCargoName = 'none'
        reducedPriceCargoName = 'none'
        if doubleQuantity:
            dblIdx = vsrandom.randrange(outOfStockCount, len(defaultExports))
            doublingCargoName = defaultExports[dblIdx][0]
        if reducedPrice:
            rdpIdx = vsrandom.randrange(outOfStockCount, len(defaultExports))
            reducedPriceCargoName = defaultExports[rdpIdx][0]
        
        return (outOfStock, doublingCargoName, reducedPriceCargoName)

def pumpExportCargo(base, defaultExports):
        for nextExportCargo in defaultExports:
            cargoName = nextExportCargo[0]
            if cargoName[:11] == "Contraband/":
                cargoName = cargoName[11:]
            print "PODXXX pumping cargoName: " + cargoName + ", category: " + nextExportCargo[0]
            cargo = VS.Cargo(cargoName,nextExportCargo[0], 1, 1, 0.01, 1.0)
            cargo.SetMaxFunctionality(1.0)  #not sure what this thing means, copy-pasted from commodity_lib
            cargo.SetFunctionality(1.0)
            cargo.SetCategory(nextExportCargo[0])    # probably not necessary
            base.addCargo( cargo )

def getUniqueBaseNameAndFaction(base):
        if base.isPlanet():
            return (base.getName(), "planets")
        baseName = base.getFullname()
        if baseName == '':
            baseName = base.getName()
        return (baseName, base.getFactionName())
            
def getBaseType(base):
        if base.isPlanet():
            return base.getFullname()
        baseName = base.getName()
        if baseName == '':
            baseName = base.getFullname()
        return baseName
        
def isCommodity(cargoName, cargoCategory):
        if cargoName == '': return False
        if cargoCategory[:8] == 'upgrades': return False
        if cargoCategory[:9] == 'starships': return False
        return True
        
def calcPriceReduction(defPrice):
#        if defPrice < 20:
#            return defPrice/2
#        if defPrice < 36:
#            return defPrice-10
#        if defPrice < 71:
#            return defPrice-13
#        if defPrice < 135:
#            return defPrice-16
#        if defPrice < 340:
#            return defPrice-20
#        if defPrice < 500:
#            return defPrice-25
#        if defPrice < 1000:
#            return defPrice-35
        if defPrice < 20:
            return defPrice/2
        if defPrice < 36:
            return defPrice-20
        if defPrice < 71:
            return defPrice-30
        if defPrice < 135:
            return defPrice-40
        if defPrice < 340:
            return defPrice-50
        if defPrice < 500:
            return defPrice-60
        if defPrice < 1000:
            return defPrice-70

def replenishCommodities(base):
        (unitName, faction) = getUniqueBaseNameAndFaction(base)
        baseType = getBaseType(base)
        
        global production
        defaultBaseProd = production.get((baseType,faction))
        if defaultBaseProd == None:
            defaultBaseProd = getImports(baseType,faction)
            production[(baseType,faction)] = defaultBaseProd
          
        if not len(defaultBaseProd):
            return
            
        defaultExports = getDefaultExports(defaultBaseProd)
        #print "PODXX defaultExports: " + str(defaultExports)
        
        (outOfStock,doublingCargoName,reducedPriceCargoName) = getExportsModificators(defaultExports)
        print "PODXXX double quantity: " + doublingCargoName + "; reduced price: " + reducedPriceCargoName + "; outOfStock: " + str(outOfStock)
        
        # prior to refilling ensure the base has at least 1 of every exported cargo, otherwise sometimes it's not replenished...
        pumpExportCargo(base, defaultExports)
        
        prices = {}
        exports = []
        cargoToReplenish = []
	for nextCargoIdx in range(base.numCargo()):
	    nextCargo = base.GetCargoIndex( nextCargoIdx )
            nextCargoName     = nextCargo.GetContent()
            nextCargoCategory = nextCargo.GetCategory()
            nextCargoQuantity = nextCargo.GetQuantity()
            
            if not isCommodity(nextCargoName, nextCargoCategory): continue

            print "PODXXX next base cargo: " + nextCargoName + ", category: " + nextCargoCategory + ", quantity: " + str(nextCargoQuantity) #+ ", price: " + str(nextCargo.GetPrice())
            if nextCargoQuantity < 0: continue
            if nextCargo.GetPrice() <= 0: continue
            
            if nextCargoQuantity > 0:
                base.removeCargo(nextCargoName,nextCargoQuantity,0)
                
            # sometimes these incorrect cargos appeared, after you sold contraband to a base
            # upd: already fixed the bug in commodity_lib, but will leave this check just in case
            if nextCargoCategory in ["Slaves", "Brilliance", "Tobacco", "Ultimate"]:
                print "PODXX removed incorrect cargo: " + nextCargoCategory
                base.removeCargo(nextCargoName,nextCargoQuantity,0)
                continue
            
            cargoEntry = findCargo(defaultBaseProd, nextCargoCategory)
            #print "PODXXX cargoEntry: " + str(cargoEntry)
            defQuantity = 0
            if not len(cargoEntry):
                print "PODXXX cargoEntry not found!"     #probably never triggered
            
            defQuantity = int( cargoEntry[3] )
            newQuantity = 0
            if defQuantity > 0:
                quantVar = vsrandom.randrange( 1 + int(cargoEntry[4]) )
                if vsrandom.random() < 0.5:
                  quantVar *= -1
                newQuantity = defQuantity + quantVar

                if nextCargoCategory == doublingCargoName:
                  newQuantity = defQuantity*2 + quantVar
                if VS.getSystemFile() in ["Gemini/Pentonville","Gemini/KM-252","Gemini/Capella"]:
                  newQuantity = int( newQuantity * .75)
                
                if nextCargoCategory in outOfStock:
                  newQuantity = vsrandom.randrange(1,6)

            defPrice = getDefaultCargoPrice( cargoEntry[0] )
            if nextCargoCategory == reducedPriceCargoName:
                defPrice = calcPriceReduction(defPrice)
            priceVar = vsrandom.randrange( 1 + int(cargoEntry[2]) )
            if vsrandom.random() < 0.5:
                priceVar *= -1
            newPrice = int(defPrice * ( float(cargoEntry[1]) ) + priceVar)
            
            print "PODXXX resetting to: " + nextCargoCategory + ", price: " + str(newPrice) + ", quantity: " + str(newQuantity)
            nextCargo.SetQuantity(newQuantity)
            #nextCargo.SetPrice(newPrice)       #PODXX for some reason this does not affect the price...whatever
            cargoToReplenish.append(nextCargo)  #will replenish cargo later to avoid on-the-fly collisions
            
            if (newPrice > 0):
                prices[nextCargoName] = newPrice
            if (newQuantity > 0):
                exports.append([nextCargoName, newQuantity])

        #now actually replenish cargo
        for c in cargoToReplenish:
            base.addCargo(c)
            
        return (prices,exports)
    

class trading:
    def __init__(self):
        self.last_ship=0
        self.quantity=4
        self.price_instability=0.01
        self.count=0
        self.regenTimestamps = {}
        self.lastCheck = 0
    def SetPriceInstability(self, inst):
        self.price_instability=inst
      
    def SetMaxQuantity (self,quant):
        self.quantity=quant
        
    def Execute(self):
        #PODXX this code is no longer used, instead base cargo replenished upon landing (see commodity_lib.py)
        return
    
        if self.lastCheck > 0 and (VS.GetGameTime() - self.lastCheck < 5):
            return
        self.lastCheck = VS.GetGameTime()
        print "PODXX trading next check " + str(self.lastCheck)
        
        unitIdx = 0
        while True:
            nextUnit = VS.getUnit (unitIdx)
            if nextUnit.isNull():
                return
            unitIdx += 1
            if (not nextUnit.isSignificant()) or (nextUnit.isPlayerStarship()!=-1):
                continue

            unitName = nextUnit.getName()
            if not nextUnit.isPlanet():
                unitName = nextUnit.getFullname()
            if unitName[:4] == 'Jump' or unitName == '':
                continue
            print "PODXX trading nextSig: " + unitName
            try:
                prevRegen = self.regenTimestamps[unitName]
                if VS.GetGameTime() - prevRegen > 30:
                    self.regenTimestamps[unitName] = VS.GetGameTime()
                    regenerateCommodities(nextUnit)
            except:
                self.regenTimestamps[unitName] = VS.GetGameTime()
                regenerateCommodities(nextUnit)
            
