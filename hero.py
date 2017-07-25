import math
import items
from random import randint
from collections import OrderedDict as od
import weapons as w
CONSTANT = 0.25


"""
Formula to calculate character level:

    LEVEL = math.floor(CONSTANT * math.sqrt(self.experience))

Formula to calculate stat increase for each new level:

    stat += math.floor(math.sqrt(level*base_stat))

MAX_ARMOR should be 15
"""

class Hero(object):
       # Initialize a Hero Class instance
    def __init__(self, baseHealth, baseStamina, baseInt, baseArmor, attack, agility):
        self.curHealth = baseHealth
        self.attack = attack
        self.curStamina = baseStamina
        self.curInt = baseInt
        self.maxHealth = baseHealth
        self.maxStamina = baseStamina
        self.agility = agility
        self.maxInt = baseInt
        self.armor = baseArmor
        # Beginning stats common to all characters:
        self.has_key = False
        self.weapon_equipped = None
        self.wearing_item = None
        self.item_worn = ''
        self.addedHealth = 0
        self.addedStamina = 0
        self.addedAttack = 0
        self.addedInt = 0
        self.experience = 0
        self.level = 0
        self.cetus_amulet_level = randint(1,15)
        # Inventory dictionaries
        # keep track of inventory items and numbers of items
        self.items_inv = od()

        # Character position info:
        self.position = ()
        self.tile = ''
        self.dungeonLevel = 1

    def totalHealth(self):
        return self.maxHealth + (self.addedHealth * max(self.level, 1))

    def total_attack(self):
        #add in attak increases by weapon etc
        return self.attack + self.addedAttack

    def totalStamina(self):
        return self.maxStamina + (self.addedStamina * max(self.level, 1))


    def totalIntelligence(self):
        return self.maxInt + (self.addedInt * max(self.level, 1))

    def check_level(self):
        level_by_xp = math.floor(CONSTANT * math.sqrt(self.experience))

        if self.level < level_by_xp:
            self.level = level_by_xp
            self.maxHealth += math.floor(math.sqrt(self.level*self.baseHealth))
            self.maxStamina += math.floor(math.sqrt(self.level*self.baseStamina))
            self.maxInt += math.floor(math.sqrt(self.level*self.baseInt))
            self.attack += math.floor(math.sqrt(self.level*self.baseAttack))

            if self.wearing_item:
                items.use_item(self.wearing_item, self)

            self.curHealth = self.totalHealth()
            self.curStamina = self.totalStamina()
            self.curInt = self.totalIntelligence()


    def decrement_stamina(self):
        """
        stamina decreases by .0025 every step you take. if stamina is depleted,
        health will decrease by .0025.
        """
        if self.curStamina > 0.0025:
            self.curStamina -= 0.0025
        elif self.curStamina == 0:
            self.curHealth -= 0.0025
        else:
            dif = 0.001 - self.curStamina
            self.curStamina = 0
            self.curHealth -= dif

    def drink_coffee(self):
        if 'Espresso' in self.items_inv.keys():
            items.use_item('Espresso', self)


    def defend_attack(self, enemy_attack, msg, enemy):
        #dodged the attack
        if randint(1, 10) < self.agility:
            return
        #each blow reduces armor by 1
        if self.armor == 0:
            attack = enemy_attack
        elif self.armor <= 5:
            attack = enemy_attack * (2/3.0)
            self.armor -= 0.5
        elif self.armor <= 10:
            attack = enemy_attack * (3/5.0)
            self.armor -= 0.5
        elif self.armor <= 15:
            attack = enemy_attack * (1/2.0)
            self.armor -= 0.5

        self.curHealth -= attack

        msg.insert(0, str(round((attack), 1)) + ' damage from ' + enemy)



    def attack_enemy(self, enemy_pos, enemies, pad, msg, special_flag):
        dead = False
        for enemy in enemies:
            if enemy_pos == enemy.position:
                a = self.total_attack()
                if special_flag:
                    a = a*1.5
                dead, damage = enemy.defend_attack(a)
                if dead:
                    msg.insert(0, 'killed ' + enemy.name)
                else:
                    msg.insert(0, str(damage) + ' damage to ' + enemy.name)
                self.experience += damage
                break
        if dead:
            pad.addstr(enemy.position[0], enemy.position[1], enemy.tile)
            enemies.pop(enemies.index(enemy))
            self.check_level()

    def special_attack(self, enemies, msg, pad):
        if not self.weapon_equipped:
            msg.insert(0, 'You need a weapon')
        elif self.curStamina < self.level:
            msg.insert(0, 'Not enough stamina')
        else:
            hr, hc = self.position
            neighbors = [(1,0), (0,1), (-1,0), (0,-1)]
            for nr, nc in neighbors:
                adjacent_position = (nr + hr, nc + hc)
                self.attack_enemy(adjacent_position, enemies, pad, msg, True)
            self.curStamina -= self.level


    def pick_up_item(self, pos, pad, map_items, msg):
        '''
        pos = position as (row, col)
        '''
        item = pad.instr(pos[0], pos[1], 1)

        if item == '~':
            self.has_key = True
            msg.insert(0, 'found key')
            return True
        elif item == '/':
            array = map_items[pos]

            w.take_weapon(array[0], array[3],array[1], array[4], self)
            msg.insert(0, 'picked up ' + array[0])
            map_items.pop(pos)
            return True
        else:
            try:
                item = map_items[pos][0]
            except IndexError:
                msg.insert(0, 'This doesn\'t look like anything to me')
                return True

            #add map item to inventory
            #delete map item from map_items
            if items.take_item(item, self):
                msg.insert(0, 'picked up ' + item)
                map_items.pop(pos)
                return True

        return False

    def eat_food(self):
        missing_health = self.totalHealth() - self.curHealth

        if missing_health > 2 and 'Chicken Leg' in self.items_inv.keys():
            items.use_item('Chicken Leg', self)
        elif 'Apple' in self.items_inv.keys():
            items.use_item('Apple' ,self)

class Knight(Hero):
    hero_type = "Knight"

    def desc(self):
        return "Lots of Armor, Strongest Hits"

    def __init__(self):
        self.baseHealth = 13
        self.baseStamina = 3
        self.baseInt = 3
        self.startingArm = 15
        self.baseAttack = 5

        Hero.__init__(self, self.baseHealth, self.baseStamina,
                      self.baseInt, self.startingArm, self.baseAttack, 0)

class Assassin(Hero):
    hero_type = "Assassin"

    def desc(self):
        return "High Stamina, Medium Health and Attack Strength"

    def __init__(self):
        self.baseHealth = 15
        self.baseStamina = 5
        self.baseInt = 3
        self.startingArm = 7
        self.baseAttack = 4

        Hero.__init__(self, self.baseHealth, self.baseStamina,
                      self.baseInt, self.startingArm, self.baseAttack, 5)

class Sorcerer(Hero):
    hero_type = "Sorcerer"

    def desc(self):
        return "High Health and Intelligence, Not Very Strong"

    def __init__(self):
        self.baseHealth = 17
        self.baseStamina = 4
        self.baseInt = 5
        self.startingArm = 6
        self.baseAttack = 3

        Hero.__init__(self, self.baseHealth, self.baseStamina,
                      self.baseInt, self.startingArm, self.baseAttack, 3)


