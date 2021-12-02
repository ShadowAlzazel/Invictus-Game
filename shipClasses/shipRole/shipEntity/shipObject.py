#Basic Ship Object
#"""-------------------------------SHIP-OBJECT-------------------------------------"""

class Ship:
    spaceEntity = 'shipObject'
    ammount = 0
    shiptype = 'CIV'
    shipStats = {
        "FP": 10, "ACC": 10, "EVA": 50, "SPD": 5,
        "RDR": 3, "LCK": 10, "STH": 1
    }

    def __init__(self, hullnumber, name):
        Ship.ammount += 1
        self.operational = True
        self.command = 'ASCS'
        self.fleetName = 'FleetNull'
        self.name = name
        self.hullnumber = hullnumber
        self.vesselID = ''.join([self.shiptype, '-', str(self.hullnumber)])
        self.placeHex = []  #starSpace object
        self.orientation = 'R'
        self.radar = []  #radar object
        self.armaments = {'primaryBattery': [], 'secondaryBattery': [], 'broadsideBattery': []}
        self.defenses = {'shieldType': [], 'armorType': []}
        self.detected = True 
        self.revealed = False

        print("New Ship Launched", end=': ')
        print(self.command, '-', name, sep='', end=', ') 


    #damage function that takes in a value 
    def takeDamage(self, damageNum, wPEN=0, wDIS=1):
        if self.shields > damageNum and wDIS > 0:
            damageS = self.defenses['shieldType'][0].shieldDamage(damageNum, wDIS)
            self.shields -= damageS
            return damageS
        elif self.hull > damageNum:
            damageH = self.defenses['armorType'][0].armorDamage(damageNum, wPEN) - self.shields
            self.shields = 0
            self.hull -= damageH
            return damageH
        else: 
            self.hull = 0
            print(self.vesselID, self.command, self.name, "has been destryed!")
            self._destroyShip()


    #destroy ship
    def _destroyShip(self):
        self.operational = False


    #full self repair
    def shipReset(self):
        self.hull = self.__class__.hull
        self.shields = self.__class__.shields
        print(self.name, "Reset!")


    #ping nearby hex to see if controlled
    def pingNearby(self, aHex):
        p = self.radar.radarPing(self.placeHex, aHex)
        return p


    #find targets with radar
    def detectTargets(self):
        targetsHexes = self.radar.radarDetection(self.shipStats['RDR'], self.placeHex)
        return targetsHexes


    #find tracked targets within ready gun range 
    def trackTargets(self):
        targetRanges = [0]
        gunsReadyInRange = self.gunsReady()
        if not gunsReadyInRange:
            return False

        for w in gunsReadyInRange:
            targetRanges.append(w.gunStats['RNG'])    
        targetsHexes = self.radar.radarTracking(max(targetRanges), self.placeHex)
        return targetsHexes


    #find ranges 
    def findRange(self, targetShip):
        r = self.radar.radarAcquisition(self.shipStats['RDR'], self.placeHex, targetShip.placeHex)
        return r


    #chech all guns ready to fire
    def gunsReady(self):
        gunsPrimed = []
        for b in self.armaments.values():
            for g in b:
                if g.gunLoadTime == g.gunStats['RLD']:
                    gunsPrimed.append(g)
        return gunsPrimed


    #reload all guns
    def reloadGuns(self):
        for b in self.armaments.values():
            for g in b:
                g.reloadGun()


    #recharge shields and repair armor
    def rechargeDef(self):
        s = (self.__class__.shields * (self.defenses['shieldType'][0].rechargeRate / 100))
        if self.__class__.shields > self.shields + s:
            self.shields += s

        if self.defenses['armorType'][0].armorIntegrity < 100 - self.defenses['armorType'][0].armorRegen:
            self.defenses['armorType'][0].armorIntegrity += self.defenses['armorType'][0].armorRegen


    #inspection function to look at stats
    def fullInspect(self):
        print("--<->---------------------------------------------------------------------<->--")
        print("Name: ", end='')
        print(self.command,'-' , self.name, sep='')
        print("Vessel Identifier: ", end='')
        print(self.vesselID)
        print("Ship Stats:")
        print(self.shipStats)
        print("Primary Armament:")
        for x in self.armaments['primaryBattery']:
            print(x.gunName, "in Turret", x.batteryID)
        print("Ship Defenses:")
        print(self.defenses['armorType'][0].armorName)
        print(self.defenses['shieldType'][0].shieldName)
        print("Shield Capcity at", "%.2f%%" % ((self.shields / self.__class__.shields) * 100.0), end=', ')
        print("with", self.shields // 1, "out of", self.__class__.shields, "remaining")
        print("Hull Integrity at", "%.2f%%" % ((self.hull / self.__class__.hull) * 100.0), end=', ')
        print("with", self.hull // 1, "out of", self.__class__.hull, "remaining")
        print("--<->---------------------------------------------------------------------<->--")
