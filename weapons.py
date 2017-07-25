

game_weapons = {
               'Dagger': ['Small stabby knife', 0.5],
               'Sword': ['Sword', 3],
               'Axe': ['And my axe!', 1],
               'Trident': ['Hello Poseidon', 2],
               'Hammer': ['Not quite Thor\'s', 1.5]
               }

def get_description(weapon):
    return game_weapons.get(weapon, None)

def take_weapon(name, weapon, description, damage, player):
    import items as i
    equip = False
    if weapon in game_weapons:
        for item in player.items_inv:
            if item not in i.game_items.keys():
                if weapon in player.items_inv[item]:
                    if player.weapon_equipped == item:
                        player.weapon_equipped = None
                        equip = True
                    player.items_inv.pop(item)

        player.items_inv[name] = list()
        player.items_inv[name].append(weapon)
        player.items_inv[name].append(description)
        player.items_inv[name].append(damage)

        if equip:
            equipWeapon(name, damage, player)

        return True
    else:
        return False


def remove_weapon(weapon, player):
    if player.items_inv.get(weapon, None) == 1:
        del player.items_inv[weapon]
    else:
        player.items_inv[weapon] -= 1
    return

def equipWeapon(weapon, damage, player):
    player.addedAttack = damage
    if weapon != '':
        player.weapon_equipped = weapon
    else:
        player.weapon_equipped = None

def unequipWeapon(player):
    player.addedAttack = 0
    player.weapon_equipped = None
