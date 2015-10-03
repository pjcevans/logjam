from dateutil.relativedelta import *
from datetime import datetime
from datetime import timedelta

TIMEOUT = 15 # sets how long after a mob is attacked until it is considered out of combat


class Fight(object):
  def __init__ (self, pull, index):
    self.pull = pull
    self.pet_logs = []
    self.fight_number = index
    self.players = []
    self.enemies = []
    self.pet_units = list(find_units(pull, "0xF14")) #pets enumerated but not linked to a player
    #print self.pet_units
    self.player_units = list(find_units(pull, "0x0"))
    self.enemy_units = list(find_units(pull, "0xF")) # duplication of these class assignments, would be best to move these to one function.
    #print self.enemy_units
    self.duration = find_fight_duration(pull)
    for unit in self.player_units:
      self.player_log = find_unit_events(pull, unit) #Finds limited combat logs for each player
      self.unit_pets = find_hunter_pets(self.player_log, unit)
      self.unit_pets = self.unit_pets[0]
      
      if self.unit_pets: # add logs if pet found
        self.pet_logs = find_unit_events(pull, self.unit_pets)
      self.players.append(Player(self.player_log, unit, self.pet_logs)) #Creates Player object for each friendly player
    for unit in self.enemy_units:
      self.pet_logs = []
      self.enemy_log = find_unit_events(pull, unit)      #Finds limited combat logs for each enemy unit
      #print self.enemy_log
      self.unit_pets = find_hunter_pets(self.enemy_log, unit)
      if self.unit_pets: # add logs if pet found
        for pet in self.unit_pets:
          self.pet_logs = find_unit_events(pull, self.unit_pets)
      self.enemies.append(Enemy(self.enemy_log, unit, self.pet_logs))   #Creates an Enemy object for each enemy unit

def find_hunter_pets(player_log, unit):
  for line in player_log:
    if len(line) > 10: # handles short combat log lines
      #print line[10]
      #print '"Health Link"'
      #print [line[3],line[4]]
      #print unit 
      #print line[6][0:5]
      #print "0xF14"
      if line[10] == '"Health Link"' and [line[3],line[4]] == unit and line[6][0:5] == "0xF14":
        #print [[line[6], line[7]], unit] 
        return [[line[6], line[7]], unit]

class Unit(object):
  def __init__(self, pull, unit, pet_logs):
    self.unit = unit # full <id> <name> array
    self.identifier = unit[0] # Just <id> string
    self.name = unit[1] # Just character name
    self.pull = pull #log restricted to unit's events
    self.damage_targets = list(find_units(pull, unit))
    #print self.name, " targetted ", self.damage_targets
    self.direct_healing = find_specific_events(pull, unit, "direct healing")#direct healing over the whole fight
    self.direct_spell_damage = find_specific_events(pull, unit, "direct spell damage")
    self.direct_swing_damage = find_specific_events(pull, unit, "direct swing damage")
    #self.pet_units = list(find_units(pull, "0xF14")) #pets enumerated but not linked to a player
    self.pet_intermediary = find_hunter_pets(pet_logs, self.unit)
    if self.pet_intermediary != None:
      self.pet = self.pet_intermediary
      self.pet_damage_targets = list(find_units(pet_logs, self.pet[0]))
      self.pet_direct_healing = find_specific_events(pet_logs, self.pet[0], "direct healing")#direct healing over the whole fight
      self.pet_direct_spell_damage = find_specific_events(pet_logs, self.pet[0], "direct spell damage")
      self.pet_direct_swing_damage = find_specific_events(pet_logs, self.pet[0], "direct swing damage")
      #print self.pet_direct_swing_damage

      #print self.pet[0]
    #print self.unit
    #print pet_logs
    #print self.pet
  def test_player(self):
    print "Unit " + self.name + " object initiated OK"
    return

class Player(Unit):
  def __init__(self, pull, unit, pet_logs):
    Unit.__init__(self, pull, unit, pet_logs)
    

class Enemy(Unit):
  def __init__(self, pull, unit, pet_logs):
    Unit.__init__(self, pull, unit, pet_logs)
    


def find_specific_events(pull, unit, event):
    #return an array for each direct heal event.|timestamp|target id|target name|spell|amount|overheal|
    if event == "direct healing":
      direct_healing = []
      for line in pull:
        if [line[3],line[4]] == unit and line[2] =="SPELL_HEAL":
          direct_healing.append(line)
  	    #continue#direct_healing.append(line)
      #print direct_healing
      return direct_healing

    elif event == "direct spell damage":
      direct_spell_damage = []
      for line in pull:
        if [line[3],line[4]] == unit and line[2] == "SPELL_DAMAGE":
	        direct_spell_damage.append(line)
	      #continue
      return direct_spell_damage

    elif event == "direct swing damage":
      direct_swing_damage = []
      for line in pull:
        #print "3 - 4: ", [line[3],line[4]]
        #print "unit: ",  unit
        if [line[3],line[4]] == unit and line[2] == "SWING_DAMAGE":
	        direct_swing_damage.append(line)
	      #continue
      return direct_swing_damage








#class HealingTarget(object):
#  def __init__(self, pull, unit):
#    self.unit = unit
#    self.identifier = unit[0]
#    self.name = unit[1]
#    self.pull = pull #log restricted to unit's events
#    return
#
#class DamageTarget(object):
#  def __init__(self, pull, unit):
#    self.unit = unit
#    self.identifier = unit[0]
#    self.name = unit[1]
#    self.pull = pull #log restricted to unit's events
#    return
#
#class BuffTarget(object):
#  def __init__(self, pull, unit):
#    self.unit = unit
#    self.identifier = unit[0]
#    self.name = unit[1]
#    self.pull = pull #log restricted to unit's events
#    return
#
#class DebuffTarget(object):
#  def __init__(self, pull, unit):
#    self.unit = unit
#    self.identifier = unit[0]
#    self.name = unit[1]
#    self.pull = pull #log restricted to unit's events
#    return

def read_log():
  f = open('log.txt', 'r')
  x = f.readlines()
  f.close()
  return x

def split_log(combat_log_lines):
  combat_log_array = []
  for line in combat_log_lines:
    line = line[:4] + "," + line[5:] #changes date/time split to comma
    line = line[:17] + "," + line[19:] #changes time/log split to comma
    line = line.split(",") #splits by comma
    combat_log_array.append(line) #constructs array of arrays
  return combat_log_array

def remove_quotes(text):
  text = text[1:]
  text = text[:-1]
  return text


def find_unit_events(log, player):
  player_log = []
  for line in log:
    if [line[3], line[4]] == player or [line[6], line[7]] == player:
      player_log.append(line)
  return player_log
    


#def find_healers(combat_log):
#  healers = []
#  for line in combat_log:
#    if line[2] == "SPELL_HEAL":
#      healers.append(line[4])
#  healers = set(healers)
#  return healers
  
#def find_players(combat_log):
#for a given log find any friendly players who cast heals or did damage (restricted to spell_damage / swing_damage)
#  players = []
#  for line in combat_log:
#    if line[3][0:3] == "0x0" and line[2] == "SPELL_DAMAGE" or line[3][0:3] == "0x0" and line[2] == "SWING_DAMAGE":
#      players.append([line[3],line[4]])
#    if line[3][0:3] == "0x0" and line[2] =="SPELL_HEAL":
#      players.append([line[3],line[4]])
#  players = [list(i) for i in set(tuple(i) for i in players)] # taken from stackoverflow as list of lists uniqueness problem
  # players = set(players)
#  return players

def find_units(combat_log, unit):
#for a given log find any enemy players who cast heals or did damage (restricted to spell_damage / swing_damage)
  players = []
  #print unit

  if unit == "0xF14":
  #enumerates pets
    for line in combat_log:
      if line[3][0:5] == "0xF14" and line[2] == "SPELL_DAMAGE" or line[3][0:5] == "0xF14" and line[2] == "SWING_DAMAGE":
        players.append([line[3],line[4]])
      if line[3][0:5] == "0xF14" and line[2] =="SPELL_HEAL":
        players.append([line[3],line[4]])
    players = [list(i) for i in set(tuple(i) for i in players)]
    return players


  if  unit == "0x0" or unit[0][0:5] == "0xF13":
  #if "0x0" in unit[0]:
    for line in combat_log:
      if line[3][0:3] == "0x0" and line[2] == "SPELL_DAMAGE" or line[3][0:3] == "0x0" and line[2] == "SWING_DAMAGE":
        players.append([line[3],line[4]])
      if line[3][0:3] == "0x0" and line[2] =="SPELL_HEAL":
        players.append([line[3],line[4]])
    players = [list(i) for i in set(tuple(i) for i in players)]
    return players

  if unit == "0xF" or unit[0][0:3] == "0x0" or unit[0][0:5] == "0xF14":
  #elif "0xF" in unit[0]
    for line in combat_log:
      if line[3][0:5] == "0xF13" and line[2] == "SPELL_DAMAGE" or line[3][0:5] == "0xF13" and line[2] == "SWING_DAMAGE":
        players.append([line[3],line[4]])
      if line[3][0:3] == "0xF" and line[2] =="SPELL_HEAL":
        players.append([line[3],line[4]])
    players = [list(i) for i in set(tuple(i) for i in players)]
    #print players
    return players
  return []

#def 

#def tally_healing(combat_log, healers):
#  all_healing = []
#  for healer in healers:
#    individual_healing = [healer]
#    healing_done = 0
#    for line in combat_log:
#      if line[2] == "SPELL_HEAL":
#        if line[4] == healer:
#          healing_done += int(line[12])
#    individual_healing.append(healing_done)
#    all_healing.append(individual_healing)
#  return all_healing
#  #print all_healing

def find_fight_duration(combat_log):
# Based on healing so obviously needs changing
  times = []
  for line in combat_log:
    #if line[2] == "SPELL_HEAL":
    times.append(line[1])
  #converts time to time object, worth stripping out to new function
  total_time = datetime.strptime(times[0-1], '%H:%M:%S.%f') - datetime.strptime(times[0], '%H:%M:%S.%f')
  #returns an int
  return total_time.total_seconds()

#def find_heals_per_second(healing_done, length_of_encounter):
##takes a list of lists, healer_name+healing_done and length_of_encounter
#  healing_and_hps = []
#  for i in healing_done:
#    hps = i[1] / length_of_encounter
#    i.append(round(hps))
#    healing_and_hps.append(i)
#  return healing_and_hps


#reads lines from log.txt
#split lines into elements	  

#for i in combat_log:
#	if i[2] == "SPELL_HEAL":
#		print i[4],i[12]
#print(combat_log[0][4])
#healers = find_healers(combat_log)
#healing_done = tally_healing(combat_log, healers)
#length_of_encounter = find_fight_duration(combat_log) #returns an int
#hps = find_heals_per_second(healing_done, length_of_encounter)



def find_pulls(combat_log):
# runs through combat log splitting unique combat periods into a list
  mobs = []
  mobs_timestamp = []
  pull = []
  combat = False
  #print combat
  for index, line in enumerate(combat_log):

# test timestamp of mobs & kill if late
# test timestamp against current time
# remove mob from mobs
# run if mobs = [] block
    if mobs != []:

      timeout = datetime.strptime(line[1], '%H:%M:%S.%f') # turns current lines time into a time object
      timeout = timeout - timedelta(0,TIMEOUT) # sets timeout based on static 
      for mobstamp in mobs_timestamp:
        
        if datetime.strptime(mobstamp[2], '%H:%M:%S.%f') < timeout: #using timeout has fixed evades brill but poss evaded targets now dont show in log? (ie their damage events do not)
          mobs_timestamp.remove(mobstamp)
          for mob in mobs: 
            if mob == mobstamp[0:2]:
              mobs.remove(mob) 

      if mobs == []:
        combat = False
        #print combat
        pull = combat_log[:index-2] #cuts current pull to end on the line last mob died
        pulls.append(pull)
        combat_log = combat_log[index-2:]
        find_pulls(combat_log) #recursively calls this function for the remainder of the combat_log (each pull removed from the start each iteration)
        break

    if line[2] == "SPELL_DAMAGE" or line[2] == "SWING_DAMAGE" or line[2] == "RANGE_DAMAGE": #add more pull-Types here
      if [line[7],line[6]] in mobs and line[6][0:5] == "0xF13":
        for mob in mobs_timestamp: # updates mob timestamp every damage received event (should up this to damage dealt)
          if mob[0:2] == [line[7], line[6]]:
            mob[2] = line[1]
            #update timestamp of appropriate record
      elif [line[7],line[6]] not in mobs and line[6][0:5] == "0xF13": #if damaged hostile target is not in mob list
	#print [line[7],line[6]]
        if mobs == []:
          combat_log = combat_log[index:] #cuts off start of combat log at combat start (ie when mobs = 0)
          combat = True
          #print combat
        mobs.append([line[7],line[6]]) #appends mob name + id to mob list 
        mobs_timestamp.append([line[7],line[6],line[1]])
	#print mobs
        #print combat				
        continue
#add a timeout of 15 secs for each mob, to ensure each combat phase Definitely will end.
    if line[2] == "PARTY_KILL" and [line[7],line[6]] in mobs or line[2] == "UNIT_DIED" and [line[7],line[6]] in mobs: #if a mob in the list dies
      mobs.remove([line[7],line[6]])
      for mob in mobs_timestamp: #removes mob from mobs.timestamp (has to be for as only == first 2)
        if mob[0:2] == [line[7], line[6]]:
          mobs_timestamp.remove(mob)
      if mobs == []:
        combat = False
        #print combat
        pull = combat_log[:index-2] #cuts current pull to end on the line last mob died
        pulls.append(pull)
        combat_log = combat_log[index-2:]
        find_pulls(combat_log) #recursively calls this function for the remainder of the combat_log (each pull removed from the start each iteration)
        break

combat_log_lines = read_log()
combat_log = split_log(combat_log_lines)
pulls = []

find_pulls(combat_log) 
#print len(pulls) # pulls is now an array containing rows of combat log split by fights
#pulls is set by find_pulls()
fights = []
for index, pull in enumerate(pulls): #possibly can remove index
  fights.append(Fight(pull, index))  #loads fight objects for each fight


###################
# Tests
###################
for index, fight in enumerate(fights):
  print " "
  print "Fight", index+1, "duration:", fight.duration
  print " "
  for index, player in enumerate(fight.players):
    print "Player", index+1, ":" 
    player.test_player()
  for index, enemy in enumerate(fight.enemies):
    print "Enemy", index+1, ":"
    enemy.test_player()
  print " "

##################
# API functions
##################
total_direct_damage = 0
for fight in fights:
  print "Fight: ", fight.fight_number+1
  for player in fight.players:
    print player.damage_targets
    for line in player.direct_spell_damage:
      if line[6][0:5] == "0xF13":
        print line[4] + " did " + line[12] + " damage to " + line[7]
        total_direct_damage += int(line[12])

    for line in player.pet_direct_spell_damage:
      if line[6][0:5] == "0xF13":
        print line[4] + " did " + line[12] + " damage to " + line[7]
        total_direct_damage += int(line[12])

    for line in player.direct_swing_damage:
      if line[6][0:5] == "0xF13":
        print line[4] + " did " + line[9] + " damage to " + line[7]
        total_direct_damage += int(line[9])

    for line in player.pet_direct_swing_damage:
      if line[6][0:5] == "0xF13":
        print line[4] + " did " + line[9] + " damage to " + line[7]
        total_direct_damage += int(line[9])

print "total direct damage = " + str(total_direct_damage)

print " "

total_direct_damage = 0
for fight in fights:
  print "Fight: ", fight.fight_number+1
  for enemy in fight.enemies:
    print enemy.damage_targets
    for line in enemy.direct_spell_damage:
      if line[6][0:3] == "0x0":
        print line[4] + " did " + line[12] + " damage to " + line[7]
        total_direct_damage += int(line[12])
    for line in enemy.direct_swing_damage:
      if line[6][0:3] == "0x0":
        print line[4] + " did " + line[9] + " damage to " + line[7]
        total_direct_damage += int(line[9])
print "total direct damage = " + str(total_direct_damage)
#now add target specific direct_damage and find damage on each target
#can we find DPS?


###############
# Improvements to make:
###############
# - Unit events are limited to swings, spell damage, and spell healing.
# - Find_pulls is currently a recursive function, neat but bound to cause problems at some point (actually proving resilient)
# - using timeout has fixed evades brill but poss evaded targets now dont show in log? (ie their damage events do not)
#
