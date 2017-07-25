from random import randint, sample, randrange
from collections import defaultdict
import math
import time


game_items = {'Apple': ['Cures some health', 'a'],
              'Chicken Leg': ['Cures more health', 'c'],
              'Healing Potion': ['Restores some health', 'p'],
              'Stamina Potion': ['Restores some stamina', 'p'],
              'Espresso': ['Restores some stamina', 'e'],
              'Amulet Of Knowledge': ['Increases maximum intelligence while wearing', '*'],
              'Amulet of Health': ['Increases maximum health while wearing', '*'],
              'Amulet of Stamina': ['Increases maximum stamina while wearing', '*'],
              'Armor Repair Kit': ['Fully repairs armor', 'r'],
              'Cetus Amulet': ['Vibrates with mysterious power', '&']}

def get_description(item):
    return game_items[item][0]

def take_item(item, player):
    if item in game_items:
        if item in player.items_inv:
            player.items_inv[item] += 1
        else:
            player.items_inv[item] = 1
        return True
    else:
        return False

def remove_item(item, player):
    if player.items_inv.get(item, None) == 1:
        del player.items_inv[item]
    else:
        player.items_inv[item] -= 1

def use_item(item, player):
    if item == 'Apple':
        use_apple(player)
    elif item == 'Chicken Leg':
        use_chicken_leg(player)
    elif item == 'Healing Potion':
        use_healing_potion(player)
    elif item == 'Stamina Potion':
        use_stamina_potion(player)
    elif item == 'Espresso':
        use_espresso(player)
    elif item == 'Chicken Soup':
        use_chicken_soup(player)
    elif 'Amulet' in item:
        equip_amulet(item, player)
    elif item == 'Armor Repair Kit':
        use_armor_repair_kit(player)

def use_apple(player):
    missingHealth = player.totalHealth() - player.curHealth
    player.curHealth += min(2 + player.dungeonLevel, missingHealth)
    remove_item('Apple', player)

def use_chicken_leg(player):
    missingHealth = player.totalHealth() - player.curHealth
    player.curHealth += min(6 + player.dungeonLevel, missingHealth)
    remove_item('Chicken Leg', player)

def use_healing_potion(player):
    intelligence = player.totalIntelligence()
    missingHealth = player.totalHealth() - player.curHealth
    frac = player.totalHealth()/5
    chance = randint(1,100) + intelligence

    if chance <= 30:
        player.curHealth += min(frac, missingHealth)
    elif chance <= 60:
        player.curHealth += min(frac*2, missingHealth)
    elif chance <= 85:
        player.curHealth += min(frac*3, missingHealth)
    elif chance <= 95:
        player.curHealth += min(frac*4, missingHealth)
    else:
        player.curHealth = player.totalHealth()

    remove_item('Healing Potion', player)

def use_stamina_potion(player):
    intelligence = player.totalIntelligence()
    missingStamina = player.totalStamina() - player.curStamina
    frac = player.totalStamina()/5
    chance = randint(1,100) + intelligence

    if chance <= 30:
        player.curStamina += min(frac, missingStamina)
    elif chance <= 60:
        player.curStamina += min(frac*2, missingStamina)
    elif chance <= 85:
        player.curStamina += min(frac*3, missingStamina)
    elif chance <= 95:
        player.curStamina += min(frac*4, missingStamina)
    else:
        player.curStamina = player.totalStamina()

    remove_item('Stamina Potion', player)


def use_espresso(player):
    missingStamina = player.totalStamina() - player.curStamina
    player.curStamina += min(3 + player.dungeonLevel, missingStamina)
    remove_item('Espresso', player)


def equip_amulet(item, player):

    unequip_item(player)

    if "Knowledge" in item:
        player.addedInt = 2 + player.level
    elif "Health" in item:
        player.addedHealth = 3 + player.level
    elif "Stamina" in item:
        player.addedStamina = 2 + player.level

    player.wearing_item = item


def use_armor_repair_kit(player):
    player.armor = player.startingArm
    remove_item('Armor Repair Kit', player)

def unequip_item(player):
    player.addedHealth = 0
    player.addedStamina = 0
    player.addedIntelligence = 0
    player.wearing_item = None

def add_key(pad):

    import pad2 as p

    kr = randint(1, p.max_y)
    kc = randint(1, p.max_x)
    tile = pad.instr(kr, kc, 1)

    while tile != '.':
        kr = randint(1, p.max_y)
        kc = randint(1, p.max_x)
        tile = pad.instr(kr, kc, 1)

    pad.addstr(kr, kc, '~')
    return (kr, kc)

def add_items(pad, level, cetus_amulet_level):
    import pad2 as p
    import weapons as w

    global cetus_pos
    cetus_pos = None
    map_items = defaultdict(list)
    food = ['Apple', 'Chicken Leg', 'Espresso']

    #add food items and potions
    count = randint(15, 20)
    for i in range(count):
        index = randrange(0, len(food))
        item = food[index]
        tile = ','
        while tile != '.':
            row = randint(1, p.max_y)
            col = randint(1, p.max_x)
            tile = pad.instr(row, col, 1)
        map_items[(row, col)].append(item)
        map_items[(row, col)].append(game_items[item][0])
        map_items[(row, col)].append(game_items[item][1])
        pad.addstr(row, col, game_items[item][1])

    potions = ['Healing Potion','Stamina Potion']
    count = randint(1, 5)
    for i in range(count):
        index = randrange(0, len(potions))
        item = potions[index]
        tile = ','
        while tile != '.':
            row = randint(1, p.max_y)
            col = randint(1, p.max_x)
            tile = pad.instr(row, col, 1)
        map_items[(row, col)].append(item)
        map_items[(row, col)].append(game_items[item][0])
        map_items[(row, col)].append(game_items[item][1])
        pad.addstr(row, col, game_items[item][1])

    if cetus_amulet_level != level:
        amulets = ['Amulet Of Knowledge', 'Amulet of Health', 'Amulet of Stamina']
        #40% chance of amulet
        if randint(0, 10) < 4:
            index = randrange(0,len(amulets))
            tile = ','
            while tile != '.':
                row = randint(1, p.max_y)
                col = randint(1, p.max_x)
                tile = pad.instr(row, col, 1)
            item = amulets[index]
            map_items[(row, col)].append(item)
            map_items[(row, col)].append(game_items[item][0])
            map_items[(row, col)].append(game_items[item][1])
            pad.addstr(row, col, game_items[item][1])
    else:
        tile = ','
        while tile != '.':
            row = randint(1, p.max_y)
            col = randint(1, p.max_x)
            tile = pad.instr(row, col, 1)
        item = 'Cetus Amulet'
        map_items[(row, col)].append(item)
        map_items[(row, col)].append(game_items[item][0])
        map_items[(row, col)].append(game_items[item][1])
        pad.addstr(row, col, game_items[item][1])
        cetus_pos = (row, col)


    weapons = w.game_weapons.keys()
    #40% chance of weapon
    if randint(0, 10) < 4:
        index = randrange(0,len(weapons))
        tile = ','
        while tile != '.':
            row = randint(1, p.max_y)
            col = randint(1, p.max_x)
            tile = pad.instr(row, col, 1)
        item = weapons[index]
        map_items[(row, col)].append('L' + str(level) + ' ' + item)
        map_items[(row, col)].append(w.game_weapons[item][0])
        map_items[(row, col)].append('/')
        map_items[(row, col)].append(item)
        map_items[(row, col)].append(level * w.game_weapons[item][1] )
        pad.addstr(row, col, '/')

    num = randint(1,2)
    for i in range(num):
        tile = ','
        while tile != '.':
            row = randint(1, p.max_y)
            col = randint(1, p.max_x)
            tile = pad.instr(row, col, 1)
        item = 'Armor Repair Kit'
        map_items[(row, col)].append(item)
        map_items[(row, col)].append(game_items[item][0])
        map_items[(row, col)].append(game_items[item][1])
        pad.addstr(row, col, game_items[item][1])



    return map_items




