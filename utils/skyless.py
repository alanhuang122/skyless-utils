# -*- coding: utf-8 -*-
import json, re, sys
from enum import Enum
from html.parser import HTMLParser
cache = {}
data = {}

assert sys.version_info > (3,7), "Yes, you need Python 3.7 to use this; no, I'm not sorry. Update your interpreter."

class AllowedOn(Enum):
    Unspecified = 0
    Character = 1
    QualityAndCharacter = 2
    Event = 3
    Branch = 4
    Persona = 5
    User = 6

class Category(Enum):
    Unspecified = 0
    Currency = 1
    Weapon = 101
    Hat = 103
    Gloves = 104
    Boots = 105
    Companion = 106
    Clothing = 107
    Curiosity = 150
    Advantage = 160
    Document = 170
    Goods = 200
    BasicAbility = 1000
    SpecificAbility = 2000
    Profession = 3000
    Story = 5000
    Intrigue = 5001
    Dreams = 5002
    Reputation = 5003
    Quirk = 5004
    Acquaintance = 5025
    Accomplishment = 5050
    Venture = 5100
    Progress = 5200
    Menace = 5500
    Contacts = 6000
    Hidden = 6661
    Randomizer = 6662
    Ambition = 7000
    Route = 8000
    Seasonal = 9000
    Ship = 10000
    ConstantCompanion = 11000
    Club = 12000
    Affiliation = 13000
    Timer = 13999
    Transportation = 14000
    HomeComfort = 15000
    Academic = 16000
    Cartography = 17000
    Contraband = 18000
    Elder = 19000
    Infernal = 20000
    Influence = 21000
    Literature = 22000
    Lodgings = 22500
    Luminosity = 23000
    Mysteries = 24000
    Nostalgia = 25000
    RagTrade = 26000
    Ratness = 27000
    Rumour = 28000
    Legal = 29000
    WildWords = 30000
    Wines = 31000
    Rubbery = 32000
    SidebarAbility = 33000
    MajorLateral = 34000
    Quest = 35000
    MinorLateral = 36000
    Circumstance = 37000
    Avatar = 39000
    Objective = 40000
    Key = 45000
    Knowledge = 50000
    Destiny = 60000
    Modfier = 70000
    GreatGame = 70001
    ZeeTreasures = 70002
    Sustenance = 70003
    Bridge = 70004
    Plating = 70005
    Auxiliary = 70006
    SmallWeapon = 70007
    LargeWeapon = 70008
    Scout = 70009

class Nature(Enum):
    Unspecified = 0
    Status = 1
    Thing = 2
    X = 3

parser = HTMLParser()

def render_html(string):
    string = re.sub(r'<.{,2}?br.{,2}?>','\n', string)
    string = re.sub(r'<.{,2}?[pP].{,2}?>','', string)
    string = re.sub('</?em>', '_', string)
    string = re.sub('</?[iI]>', '_', string)
    string = re.sub('</?strong>', '*', string)
    string = re.sub('</?b>', '*', string)
    return string

class Quality:
    def __init__(self, jdata):
        self.allowed_on = AllowedOn(jdata.get('AllowedOn'))
        self.available_at = jdata.get('AvailableAt')
        self.cap = jdata.get('Cap')
        self.category = Category(jdata.get('Category', 0))
        try:
            self.changedesc = convert_keys(json.loads(jdata.get('ChangeDescriptionText')))
        except:
            self.changedesc = None
        self.css = jdata.get('CssClasses')
        self.desc = jdata.get('Description', '(no description)')
        self.difficulty = jdata.get('DifficultyScaler')
        self.enhanceable = jdata.get('IsEnhanceable', False)
        self.enhancements = []
        for x in jdata['Enhancements']:
            self.enhancements.append(Effect(x))
        self.equippable = jdata.get('IsEquippable', False)
        self.event = jdata.get('UseEvent', {}).get('Id')
        self.id = jdata.get('Id')
        self.image = jdata.get('Image')
        self.is_slot = jdata.get('IsSlot', False)
        try:
            self.leveldesc = convert_keys(json.loads(jdata.get('LevelDescriptionText')))
        except:
            self.leveldesc = None
        self.name = jdata.get('Name', '(no name)')
        self.nature = Nature(jdata.get('Nature', 0))
        self.notes = jdata.get('Notes')
        # OwnQualitiesCount == len(QualitiesPossessedList)
        self.owner_name = jdata.get('OwnerName')
        try:
            self.parent = Quality.get(jdata.get('ParentQuality')['Id'])
        except TypeError:
            self.parent = None
        self.persistent = 'Persistent' in jdata
        self.plural = jdata.get('PluralName')
        self.pyramid = 'UsePyramidNumbers' in jdata
        self.qep = jdata.get('QEffectPriority')
        self.qualities = []
        for x in jdata['QualitiesPossessedList']:
            self.qualities.append(Effect(x))
        self.raw = jdata
        try:
            self.slot = Quality.get(jdata['AssignToSlot']['Id'])
        except:
            self.slot = None
        self.tag = jdata.get('Tag')
        self.test_type = 'Narrow' if 'DifficultyTestType' in jdata else 'Broad'
        try:
            self.variables = json.loads(jdata.get('VariableDescriptionText'))
            self.variables = {k: convert_keys(v) for k,v in sorted(self.variables.items())}
        except:
            self.variables = None
        self.visible = jdata.get('Visible')

    def __repr__(self):
        return f'Quality: {self.name}'

    def __str__(self):
        string = f'{self.nature.name}: {self.name}'
        string += f'\nDescription: {self.desc}'
        string += f'\nCategory: {self.category.name}'
        if self.enhancements:
            string += f'\nEnhancements: {self.enhancements}'
        if self.qualities:
            string += f'\nQualities Possessed: {self.qualities}'
        return string

    @classmethod
    def get(self, id):
        key = f'qualities:{id}'
        if key in cache:
            return cache[key]
        else:
            cache[key] = Quality(data[key])
            if cache[key].event:
                cache[key].event = Storylet.get(cache[key].event)
            return cache[key]

    def get_changedesc(self, level):
        if self.changedesc and isinstance(level, int):
            descs = sorted(list(self.changedesc.items()), reverse=True)
            for x in descs:
                if x[0] <= level:
                    desc = x
                    break
                desc = (-1, 'no description')
            return desc
        return None

    def get_leveldesc(self, level):
        if self.leveldesc and isinstance(level, int):
            descs = sorted(list(self.leveldesc.items()), reverse=True)
            for x in descs:
                if x[0] <= level:
                    desc = x
                    break
                desc = (-1, 'no description')
            return desc
        return None

def sub_qualities(string):
    for x in re.findall(r'\[qb?:(\d+)\]', string):
        string = string.replace(x, Quality.get(int(x)).name)
    return string

def convert_keys(dict):
    return {int(k): v for k,v in sorted(dict.items())}

class Requirement:  #done
    def __init__(self, jdata):
        self.raw = jdata
        self.quality = Quality.get(jdata['AssociatedQuality']['Id'])
        try:
            self.upper_bound = jdata['MaxLevel']
        except:
            try:
                self.upper_bound = sub_qualities(jdata['MaxAdvanced'])
            except KeyError:
                pass
        try:
            self.lower_bound = jdata['MinLevel']
        except:
            try:
                self.lower_bound = sub_qualities(jdata['MinAdvanced'])
            except KeyError:
                pass
        try:
            self.difficulty = jdata['DifficultyLevel']
        except:
            try:
                self.difficulty = sub_qualities(jdata['DifficultyAdvanced'])
            except KeyError:
                pass
        if hasattr(self, 'difficulty'):
            self.type = 'Challenge'
            self.test_type = self.quality.test_type
        else:
            self.type = 'Requirement'
        assert jdata.get('BranchVisibleWhenRequirementFailed') == jdata.get('VisibleWhenRequirementFailed')
        self.visibility = jdata.get('BranchVisibleWhenRequirementFailed', False)

    def __repr__(self):
        string = ''
        if not self.visibility:
            string += '[Branch hidden if failed] '
        if self.type == 'Challenge':
            if self.quality.id == 432:
                string += f'Luck: {50 - self.difficulty * 10}% chance'
            else:
                string += f'{self.test_type} {self.type}: {self.quality.name} {self.difficulty}'
        else:
            string += self.quality.name
            try:
                if self.lower_bound == self.upper_bound:
                    desc = self.quality.get_changedesc(self.lower_bound)
                    if desc:
                        desc = f' ({desc[1]})'
                    string += f' exactly {self.lower_bound}{desc if desc else ""}'
                else:
                    lower = self.quality.get_changedesc(self.lower_bound)
                    if lower:
                        lower = f' ({lower[1]})'
                    upper = self.quality.get_changedesc(self.upper_bound)
                    if upper:
                        upper = f' ({upper[1]})'
                    string += f' [{self.lower_bound}{lower if lower else ""}-{self.upper_bound}{upper if upper else ""}]'
            except:
                try:
                    desc = self.quality.get_changedesc(self.lower_bound)
                    if desc:
                        desc = f' ({desc[1]})'
                    string += f' at least {self.lower_bound}{desc if desc else ""}'
                except:
                    desc = self.quality.get_changedesc(self.upper_bound)
                    if desc:
                        desc = f' ({desc[1]})'
                    string += f' no more than {self.upper_bound}{desc if desc else ""}'
        return string

def render_requirements(rl):
    reqs = []
    challenges = []
    for r in rl:
        if r.type == 'Requirement':
            reqs.append(str(r))
        else:
            challenges.append(str(r))
    if not reqs and not challenges:
        return 'None'
    return ', '.join(reqs) + '\n' + '\n'.join(challenges)

class Storylet: #done?
    def __init__(self, jdata, shallow=False):
        self.raw = jdata
        self.title = parser.unescape(jdata.get('Name', '(no name)'))
        self.desc = jdata.get('Description', '(no description)')
        self.id = jdata['Id']
        try:
            self.setting = Setting.get(jdata['Setting']['Id'])
        except KeyError:
            self.setting = None
        try:
            self.area = Area.get(jdata['LimitedToArea']['Id'])
        except KeyError:
            self.area = None
        self.type = 'Storylet' if jdata['Deck']['Name'] == 'Always' else 'Card' if jdata['Deck']['Name'] == 'Sometimes' else 'Unknown type'
        if self.type == 'Card':
            self.frequency = jdata['Distribution']
        self.requirements = []
        for r in jdata['QualitiesRequired']:
            self.requirements.append(Requirement(r))
        
        self.branches = []
        if not shallow:
            for b in jdata['ChildBranches']:
                branch=Branch.get(b, self)
                self.branches.append(branch)
                for e in list(branch.events.items()):
                    if e[0].endswith('Event'):
                        e[1].parent = branch

    def __repr__(self):
        return f'{self.type}: "{self.title}"'

    def __str__(self):
        #_,c = os.popen('stty size', u'r').read().split()
        string = f'{self.type} Title: "{self.title}"\n'
        restrictions = []
        try:
            restrictions.append(f'Appears in {self.setting.title}')
        except AttributeError:
            pass
        try:
            restrictions.append(f' Limited to area: {self.area.name}')
        except AttributeError:
            pass
        string += ' '.join(restrictions)
        string += f'\nDescription: {render_html(self.desc)}'
        string += f'\nRequirements: {render_requirements(self.requirements)}'
        string += '\nBranches:\n{}'.format(f"\n\n{'~' * 20}\n\n".join(self.render_branches()))
        return string
    
    def render_branches(self):
        return [str(b) for b in self.branches]
    
    @classmethod
    def get(self, id):
        key = f'storylets:{id}'
        if key in cache:
            return cache[key]
        else:
            cache[key] = Storylet(data[f'events:{id}'], True)
            cache[key] = Storylet(data[f'events:{id}'], False)
            return cache[key]

class Branch:   #done
    def __init__(self, jdata, parent):
        self.raw = jdata
        self.title = parser.unescape(jdata.get('Name', '(no title)'))
        self.id = jdata['Id']
        self.parent = parent
        self.desc = jdata.get('Description', '(no description)')
        self.cost = jdata.get('ActionCost', 1)
        self.button = jdata.get('ButtonText', 'Go')
        self.requirements = []
        for r in jdata['QualitiesRequired']:
            self.requirements.append(Requirement(r))
        self.events = {}
        for key in list(jdata.keys()):
            if key in ['DefaultEvent', 'SuccessEvent', 'RareSuccessEvent', 'RareSuccessEventChance', 'RareDefaultEvent', 'RareDefaultEventChance']:
                if key.endswith('Chance'):
                    self.events[key] = jdata[key]
                else:
                    self.events[key] = Event.get(jdata[key])
        if 'RareSuccessEvent' in self.events and 'RareSuccessEventChance' not in self.events:
            self.events['RareSuccessEventChance'] = 0
        if 'RareDefaultEvent' in self.events and 'RareDefaultEventChance' not in self.events:
            self.events['RareDefaultEventChance'] = 0
    
    def __repr__(self):
        return f'"{self.title}"'
    
    def __str__(self):
        string = f'Branch Title: "{self.title}"'
        if self.desc:
            string += f'\nDescription: {render_html(self.desc)}'
        string += f'\nRequirements: {render_requirements(self.requirements)}'
        if self.cost != 1:
            string += f'\nAction cost: {self.cost}'
        string += f'\n{render_events(self.events)}'
        return string
    
    @classmethod
    def get(self, jdata, parent=None):
        key = f'branches:{jdata["Id"]}'
        if key in cache:
            return cache[key]
        else:
            cache[key] = Branch(jdata, parent)
            return cache[key]

class Event:    #done
    def __init__(self, jdata):
        self.raw = jdata
        self.id = jdata['Id']
        self.parent = None        
        self.title = parser.unescape(jdata.get('Name', '(no title)'))
        self.desc = jdata.get('Description', '(no description)')
        self.category = jdata.get('Category')
        self.effects = []
        for e in jdata['QualitiesAffected']:
            self.effects.append(Effect(e))
        try:
            if jdata['ExoticEffects'] != '':
                self.exotic_effect = jdata['ExoticEffects']
            else:
                self.exotic_effect = None
        except KeyError:
            self.exotic_effect = None
        self.img = jdata.get('Image')
        if jdata.get('SwitchToSettingId') and jdata.get('SwitchToSetting', {}).get('Id'):
            assert jdata.get('SwitchToSettingId') == jdata.get('SwitchToSetting', {}).get('Id')
        try:
            self.newsetting = Setting.get(jdata.get('SwitchToSetting', {}).get('Id'))
        except:
            self.newsetting = None
        try:
            self.newarea = Area.get(jdata.get('MoveToArea', {}).get('Id'))
        except:
            self.newarea = None
        try:
            self.linkedevent = Storylet.get(jdata['LinkToEvent']['Id'])
        except KeyError:
            self.linkedevent = None
        self.branches = []
        for b in jdata.get('ChildBranches'):
            branch = Branch.get(b, self)
            self.branches.append(branch)
            for e in list(branch.events.items()):
                if e[0].endswith('Event'):
                    e[1].parent = branch
    
    def __repr__(self):
        return f'Event: {self.title}'
    
    def __str__(self):
        return f'Title: "{self.title}"\nDescription: {render_html(self.desc)}\nEffects: {self.list_effects()}\n'
    
    def list_effects(self):
        effects = []
        if self.effects != []:
            effects.append(f'[{", ".join([str(e) for e in self.effects])}]')
        if self.exotic_effect:
            effects.append(f'Exotic effect: {self.exotic_effect}')
        if self.newsetting:
            effects.append(f'Move to new setting: {self.newsetting}')
        if self.newarea:
            effects.append(f'Move to new area: {self.newarea}')
        if self.linkedevent:
            effects.append(f'Linked event: "{self.linkedevent.title}" (Id {self.linkedevent.id})')
        return '\n'.join(effects)
        
    @classmethod
    def get(self, jdata):
        key = f'events:{jdata["Id"]}'
        if key in cache:
            return cache[key]
        else:
            cache[key] = Event(jdata)
            return cache[key]

def render_events(event_dict):
    strings = []
    for type in ['SuccessEvent', 'RareSuccessEvent', 'DefaultEvent', 'RareDefaultEvent']:
        if type in event_dict:
            event = event_dict[type]
            if type == 'SuccessEvent':
                string = f'Success: "{event.title}"'
            elif type == 'RareSuccessEvent':
                string = f'Rare Success: "{event.title}" ({event_dict["RareSuccessEventChance"]}% chance)'
            elif type == 'DefaultEvent':
                string = f'{"Failure" if "SuccessEvent" in event_dict else "Event"}: "{event.title}"'
            else:
                string = f'Rare {"Failure" if "SuccessEvent" in event_dict else "Success"}: "{event.title}" ({event_dict["RareDefaultEventChance"]}% chance)'
            string += f'\n{render_html(event.desc)}\nEffects: {event.list_effects()}'
            if event.branches:
                string += '\nSub-branches:\n{}'.format(f"\n\n{'*' * 20}\n\n".join([str(b) for b in event.branches]))
            strings.append(string)
    return f'\n\n{"-" * 20}\n\n'.join(strings)

class Effect:   #done: Priority goes 3/2/1/0
    def __init__(self, jdata):
        self.raw = jdata
        self.quality = Quality.get(jdata['AssociatedQuality']['Id'])
        self.equip = 'ForceEquip' in jdata
        try:
            self.amount = jdata['Level']
        except:
            try:
                self.amount = sub_qualities(jdata['ChangeByAdvanced'])
            except KeyError:
                pass
        try:
            self.setTo = jdata['SetToExactly']
        except:
            try:
                self.setTo = sub_qualities(jdata['SetToExactlyAdvanced'])
            except KeyError:
                pass
        try:
            self.ceil = jdata['OnlyIfNoMoreThan']
        except KeyError:
            pass
        try:
            self.floor = jdata['OnlyIfAtLeast']
        except KeyError:
            pass
        try:
            self.priority = jdata['Priority']
        except KeyError:
            self.priority = 0

    def __repr__(self):
        if not hasattr(self, 'setTo') and not hasattr(self, 'amount'):
            return f'{self.quality.name} - no effect'
        try:
            limits = f' if no more than {self.ceil} and at least {self.floor}'
        except:
            try:
                limits = f' if no more than {self.ceil}'
            except:
                try:
                    limits = f' only if at least {self.floor}'
                except:
                    limits = ''
        if self.equip:
            limits += ' (force equipped)'
                
        try:
            if self.quality.changedesc and isinstance(self.setTo, int):
                desc = self.quality.get_changedesc(self.setTo)
                try:
                    return f'{self.quality.name} (set to {self.setTo} ({desc[1]}){limits})'
                except TypeError:
                    pass
            return f'{self.quality.name} (set to {self.setTo}{limits})'
        except:
            if self.quality.nature == 2 or not self.quality.pyramid:
                try:
                    return f'{self.amount:+} x {self.quality.name}{limits}'
                except:
                    return f'{"" if self.amount.startswith("-") else "+"}{self.amount} {self.quality.name}{limits}'
            else:
                try:
                    return f'{self.quality.name} ({self.amount:+} cp{limits})'
                except:
                    return f'{self.quality.name} ({"" if self.amount.startswith("-") else ""}{self.amount} cp{limits})'
        
class Lodging:
    def __init__(self, jdata):
        self.raw = jdata
        self.id = jdata.get('Id')
        self.name = jdata.get('Name', '(no name)')
        self.desc = render_html(jdata.get('Description', '(no description)'))
        self.image = jdata.get('ImageName')
        self.hand = jdata.get('MaxHandSize')

    def __repr__(self):
        return self.name

    def __str__(self):
        string = f'Lodging: {self.name} (Id {self.id})'
        string += f'\nDescription: {self.desc}'
        if not self.hand:
            string += '\nHand size: None'
        elif self.hand == 1:
            string += '\nHand size: 1 card'
        else:
            string += f'\nHand size: {f"{self.hand} cards" if self.hand else "N/A"}'
        return string

    @classmethod
    def get(self, id):
        key = f'domiciles:{id}'
        if key in cache:
            return cache[key]
        else:
            cache[key] = Lodging(data[key])
            return cache[key]

class Setting:
    def __init__(self, jdata):
        self.raw = jdata
        self.id = jdata.get('Id')
        self.title = jdata.get('Name')
        self.persona = jdata.get('Personae')
        self.maxactions = jdata.get('MaxActionsAllowed')
        self.exhaustion = jdata.get('ActionsInPeriodBeforeExhaustion')
        self.turnlength = jdata.get('TurnLengthSeconds')

        self.area = jdata.get('StartingArea', {}).get('Id')
        if self.area:
            assert jdata.get('StartingArea') == data[f'areas:{self.area}']
            self.area = Area.get(self.area)

        self.domicile = jdata.get('StartingDomicile')
        if self.domicile:
            self.domicile = Lodging(self.domicile)

#        self.exchange = jdata.get('Exchange')
#        if self.exchange:
#            self.exchange = Exchange(self.exchange)
        
        self.items = 'ItemsUsableHere' in jdata

    def __repr__(self):
        return self.title

    def __str__(self):
        string = f'Setting name: {self.title} (Id {self.id})'
        if self.area:
            string += f'\nStarting area: {self.area}'
        if self.domicile:
            string += f'\nStarting lodging: {self.domicile}'
        string += f'\nItems are {"" if self.items else "NOT "}usable here'
        return string

    @classmethod
    def get(self, id):
        key = f'settings:{id}'
        if key in cache:
            return cache[key]
        else:
            cache[key] = Setting(data[key])
            return cache[key]

class Area:
    def __init__(self, jdata):
        self.raw = jdata
        self.id = jdata.get('Id')
        self.name = jdata.get('Name', '(no name)')
        self.desc = jdata.get('Description', '(no description)')
        self.image = jdata.get('ImageName', '(no image)')
        self.message = jdata.get('MoveMessage', '(no move message)')

    def __repr__(self):
        return f'{self.name} (Id {self.id})'

    def __str__(self):
        string = f'{self.name} (Id {self.id})'
        string += f'\nDescription: {self.desc}'
        string += f'\n{self.message}'
        return string

    @classmethod
    def get(self, id):
        key = f'areas:{id}'
        if key in cache:
            return cache[key]
        else:
            cache[key] = Area(data[key])
            return cache[key]
    
class Exchange:
    def __init__(self, jdata):
        self.raw = jdata
        self.id = jdata.get('Id')
        self.name = jdata.get('Name', '(no name)')
        self.title = jdata.get('Title', '(no title)')
        self.desc = jdata.get('Description', '(no description)')
        self.shops = []
        for x in jdata.get('Shops', []):
            self.shops.append(Shop(x))
    
    def __repr__(self):
        return f'Exchange Title: {self.title} (ID {self.id})'
    
    def __str__(self):
        return f'Exchange Title: {self.title} (ID {self.id})\nExchange Name: {self.name}\nExchange Description: {self.desc}\nShops:\n{self.shops}'

    def __getitem__(self, key):
        return next(s for s in self.shops if s.name == key)

    @classmethod
    def get(self, id):
        key = f'exchanges:{id}'
        if key in cache:
            return cache[key]
        else:
            cache[key] = Exchange(data[key])
            return cache[key]

class Shop:
    def __init__(self, jdata):
        self.raw = jdata
        self.id = jdata.get('Id')
        self.name = jdata.get('Name', '(no name)')
        self.desc = jdata.get('Description', '(no description)')
        self.image = jdata.get('Image')
        self.requirements = []
        for r in jdata.get('QualitiesRequired', []):
            self.requirements.append(Requirement(r))
        self.offerings = []
        for item in jdata.get('Availabilities'):
            self.offerings.append(Offering(item))

    def __repr__(self):
        return self.name

    def __str__(self):
        return f'Shop Name: {self.name}\nDescription: {self.desc}\nItems: [{", ".join([o.item.name for o in self.offerings])}]'

    def __getitem__(self, key):
        return next(o for o in self.offerings if o.item.name == key)

class Offering:
    def __init__(self, jdata):
        self.raw = jdata
        self.id = jdata.get('Id')
        self.item = Quality.get(jdata.get('Quality', {}).get('Id'))
        self.price = Quality.get(jdata.get('PurchaseQuality', {}).get('Id'))
        self.buymessage = jdata.get('BuyMessage', '(no message)')
        if not self.buymessage.replace('"',''):
            self.buymessage = '(no message)'
        self.sellmessage = jdata.get('SellMessage', '(no message)')
        if not self.sellmessage.replace('"',''):
            self.sellmessage = '(no message)'
        if 'Cost' in jdata:
            self.buy = (jdata.get('Cost'), self.price)
        if 'SellPrice' in jdata:
            self.sell = (jdata.get('SellPrice'), self.price)

    def __repr__(self):
        return f'Item: {self.item.name}'

    def __str__(self):
        string = f'Item: {self.item.name}'
        try:
            string += f'\nSells for {self.buy[0]} x {self.buy[1].name}'
            if self.buymessage != '(no message)':
                string += f'\nPurchase Message: {self.buymessage}'
        except AttributeError:
            if self.buymessage != '(no message)':
                string += f'\nPurchase Message: {self.buymessage} (cannot be bought)'
        try:
            string += f'\nPurchases for {self.sell[0]} x {self.sell[1].name}'
            if self.sellmessage != '(no message)':
                string += f'\nSale Message: {self.sellmessage}'
        except AttributeError:
            if self.sellmessage != '(no message)':
                string += f'\nSale Message: {self.sellmessage} (cannot be sold)'
        return string
