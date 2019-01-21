# -*- coding: utf-8 -*-
import json, re, sys
from enum import Enum
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

def render_text(string):
    return sub_qualities(render_html(string))

def sub_qualities(expression):
    if not isinstance(expression, str):
        return expression
    for x in re.findall(r'\[qb?:(\d+)\]', expression):
        expression = expression.replace(x, Quality.get(int(x)).name)
    for x in re.findall(r'(\[qvd:(\d+)\(([^\)]+)\)\])', expression):
        quality = Quality.get(int(x[1]))
        if quality.variables == None:
            continue
        text = ''
        variable = quality.variables.get(x[2])
        if variable is not None:
            text = '\n'.join([f'{key}: {variable[key]}' for key in variable])
        else:
            text = 'None'
        expression = expression.replace(x[0], f'{x[0]}\n{text}\n')
        expression = expression.replace(x[1], quality.name, 1)
    return expression

def render_html(string):
    string = re.sub(r'(?i)<.{,2}?br.{,2}?>','\n', string)
    string = re.sub(r'(?i)<.{,2}?[pP].{,2}?>','', string)
    string = re.sub(r'(?i)</?(em|i)>', '_', string)
    string = re.sub(r'(?i)</?(strong|b)>', '*', string)
    return string

class Quality:
    def __init__(self, jdata):
        self.allowed_on = AllowedOn(jdata.get('AllowedOn'))
        self.available_at = jdata.get('AvailableAt')
        self.cap = jdata.get('Cap')
        self.category = Category(jdata.get('Category', 0))
        try:
            self.changedesc = Quality.convert_keys(json.loads(jdata.get('ChangeDescriptionText')))
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
            self.leveldesc = Quality.convert_keys(json.loads(jdata.get('LevelDescriptionText')))
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
            self.variables = {k: Quality.convert_keys(v) for k,v in sorted(self.variables.items())}
        except:
            self.variables = None
        self.visible = jdata.get('Visible')

    def __hash__(self):
        attrs = []
        for attr in ['allowed_on', 'available_at', 'cap', 'category', 'css', 'desc', 'difficulty', 'enhanceable', 'equippable', 'id' , 'image', 'is_slot', 'name', 'nature', 'notes', 'owner_name', 'persistent', 'plural', 'pyramid', 'qep', 'tag', 'test_type', 'visible']:
            try:
                attrs.append((attr, getattr(self, attr)))
            except AttributeError:
                continue
        # TODO hash QLDs
        attrs.append(('enhancements', tuple(self.enhancements)))
        attrs.append(('qualities', tuple(self.qualities)))
        try:
            attrs.append(('event', self.event.id))
        except AttributeError:
            pass
        try:
            attrs.append(('slot', self.slot.id))
        except AttributeError:
            pass
        return hash(tuple(attrs))

    def __eq__(self, other):
        for attr in ['allowed_on', 'available_at', 'cap', 'category', 'css', 'desc', 'difficulty', 'enhanceable', 'equippable', 'id' , 'image', 'is_slot', 'name', 'nature', 'notes', 'owner_name', 'persistent', 'plural', 'pyramid', 'qep', 'tag', 'test_type', 'visible']:
            if hasattr(self, attr) != hasattr(other, attr):
                return False
            try:
                if getattr(self, attr) != getattr(other, attr):
                    return False
            except AttributeError:
                continue
        try:
            if self.slot.id != other.slot.id:
                return False
        except AttributeError:
            pass
        try:
            if self.event.id != other.event.id:
                return False
        except AttributeError:
            pass
        return self.changedesc == other.changedesc and self.leveldesc == other.leveldesc and self.variables == other.variables and set(self.enhancements) == set(other.enhancements) and set(self.qualities) == set(other.qualities)

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
    def convert_keys(self, input):
        return dict(sorted([(int(k), v) for k,v in input.items()]))

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

class Requirement:  #done
    def __init__(self, jdata):
        self.raw = jdata
        self.id = jdata['Id']
        self.quality = Quality.get(jdata['AssociatedQuality']['Id'])
        try:
            self.upper_bound = jdata['MaxLevel']
        except:
            try:
                self.upper_bound = jdata['MaxAdvanced']
            except KeyError:
                pass
        try:
            self.lower_bound = jdata['MinLevel']
        except:
            try:
                self.lower_bound = jdata['MinAdvanced']
            except KeyError:
                pass
        try:
            self.difficulty = jdata['DifficultyLevel']
        except:
            try:
                self.difficulty = jdata['DifficultyAdvanced']
            except KeyError:
                pass
        if hasattr(self, 'difficulty'):
            self.type = 'Challenge'
            self.test_type = self.quality.test_type
        else:
            self.type = 'Requirement'
        assert jdata.get('BranchVisibleWhenRequirementFailed') == jdata.get('VisibleWhenRequirementFailed')
        self.visibility = jdata.get('BranchVisibleWhenRequirementFailed', False)

    def __hash__(self):
        attrs = []
        for attr in ['id', 'upper_bound', 'lower_bound', 'difficulty', 'type', 'test_type', 'visibility']:
            try:
                attrs.append((attr, getattr(self, attr)))
            except AttributeError:
                continue
        attrs.append(('quality', self.quality.id))
        return hash(tuple(attrs))

    def __eq__(self, other):
        for attr in ['id', 'upper_bound', 'lower_bound', 'difficulty', 'type', 'test_type', 'visibility']:
            if hasattr(self, attr) != hasattr(other, attr):
                return False
            try:
                if getattr(self, attr) != getattr(other, attr):
                    return False
            except AttributeError:
                continue
        return self.quality.id == other.quality.id

    def __repr__(self):
        try:
            upper_bound = sub_qualities(self.upper_bound)
        except:
            pass
        try:
            lower_bound = sub_qualities(self.lower_bound)
        except:
            pass
        try:
            difficulty = sub_qualities(self.difficulty)
        except:
            pass

        string = ''
        if not self.visibility:
            string += '[Branch hidden if failed] '
        if self.type == 'Challenge':
            if self.quality.id == 138163:
                string += f'Fortune: {50 - difficulty * 10}% chance'
            else:
                string += f'{self.test_type} {self.type}: {self.quality.name} {difficulty}'
        else:
            string += self.quality.name
            try:
                if lower_bound == upper_bound:
                    desc = self.quality.get_leveldesc(lower_bound) or self.quality.get_changedesc(lower_bound)
                    if desc:
                        desc = f' ({desc[1]})'
                    string += f' exactly {lower_bound}{desc if desc else ""}'
                else:
                    lower = self.quality.get_leveldesc(lower_bound) or self.quality.get_changedesc(lower_bound)
                    if lower:
                        lower = f' ({lower[1]})'
                    upper = self.quality.get_leveldesc(upper_bound) or self.quality.get_changedesc(upper_bound)
                    if upper:
                        upper = f' ({upper[1]})'
                    string += f' [{lower_bound}{lower if lower else ""}-{upper_bound}{upper if upper else ""}]'
            except:
                try:
                    desc = self.quality.get_leveldesc(lower_bound) or self.quality.get_changedesc(lower_bound)
                    if desc:
                        desc = f' ({desc[1]})'
                    string += f' at least {lower_bound}{desc if desc else ""}'
                except:
                    desc = self.quality.get_leveldesc(upper_bound) or self.quality.get_changedesc(upper_bound)
                    if desc:
                        desc = f' ({desc[1]})'
                    string += f' no more than {upper_bound}{desc if desc else ""}'
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
        self.title = jdata.get('Name', '(no name)')
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

    def __hash__(self):
        attrs = []
        for attr in ['title', 'desc', 'id']:
            try:
                attrs.append((attr, getattr(self, attr)))
            except AttributeError:
                continue
        attrs.append(('setting', self.setting.id))
        attrs.append(('area', self.area.id))
        attrs.append(('requirements', tuple(self.requirements)))
        attrs.append(('branches', tuple(self.branches)))
        return hash(tuple(attrs))

    def __eq__(self, other):
        for attr in ['title', 'desc', 'id']:
            if hasattr(self, attr) != hasattr(other, attr):
                return False
            try:
                if getattr(self, attr) != getattr(other, attr):
                    return False
            except AttributeError:
                continue
        return getattr(self.setting, 'id', None) == getattr(other.setting, 'id', None) and getattr(self.area, 'id', None) == getattr(other.area, 'id', None) and set(self.requirements) == set(other.requirements) and set(self.branches) == set(other.branches)

    def __repr__(self):
        return f'Storylet: "{self.title}"'

    def __str__(self):
        #_,c = os.popen('stty size', u'r').read().split()
        string = f'Storylet Title: "{render_text(self.title)}"\n'
        restrictions = []
        try:
            restrictions.append(f'Appears in {self.setting.title}')
        except AttributeError:
            pass
        try:
            restrictions.append(f'Limited to area: {self.area.name}')
        except AttributeError:
            pass
        string += ' '.join(restrictions)
        string += f'\nDescription: {render_text(self.desc)}'
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
        self.title = jdata.get('Name', '(no title)')
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

    def __hash__(self):
        attrs = []
        for attr in ['title', 'desc', 'cost', 'button']:
            try:
                attrs.append((attr, getattr(self, attr)))
            except AttributeError:
                continue
        attrs.append(('requirements', tuple(self.requirements)))
        attrs.append(('events', tuple(self.events.items())))
        return hash(tuple(attrs))

    def __eq__(self, other):
        for attr in ['title', 'desc', 'cost', 'button']:
            if hasattr(self, attr) != hasattr(other, attr):
                return False
            try:
                if getattr(self, attr) != getattr(other, attr):
                    return False
            except AttributeError:
                continue
        return set(self.requirements) == set(other.requirements) and set(self.events.items()) == set(self.events.items())
    
    def __repr__(self):
        return f'"{self.title}"'
    
    def __str__(self):
        string = f'Branch Title: "{render_text(self.title)}"'
        if self.desc:
            string += f'\nDescription: {render_text(self.desc)}'
        string += f'\nRequirements: {render_requirements(self.requirements)}'
        if self.cost != 1:
            string += f'\nAction cost: {self.cost}'
        string += f'\n{self.render_events()}'
        return string
    
    def render_events(self):
        event_dict = self.events
        strings = []
        for type in ['SuccessEvent', 'RareSuccessEvent', 'DefaultEvent', 'RareDefaultEvent']:
            if type in event_dict:
                event = event_dict[type]
                title = render_text(event.title)
                if type == 'SuccessEvent':
                    string = f'Success: "{title}"'
                elif type == 'RareSuccessEvent':
                    string = f'Rare Success: "{title}" ({event_dict["RareSuccessEventChance"]}% chance)'
                elif type == 'DefaultEvent':
                    string = f'{"Failure" if "SuccessEvent" in event_dict else "Event"}: "{title}"'
                else:
                    string = f'Rare {"Failure" if "SuccessEvent" in event_dict else "Success"}: "{title}" ({event_dict["RareDefaultEventChance"]}% chance)'
                string += f'\n{render_text(event.desc)}\nEffects: {event.list_effects()}'
                if event.branches:
                    string += '\nSub-branches:\n{}'.format(f"\n\n{'*' * 20}\n\n".join([str(b) for b in event.branches]))
                strings.append(string)
        return f'\n\n{"-" * 20}\n\n'.join(strings)

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
        self.title = jdata.get('Name', '(no title)')
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

    def __hash__(self):
        attrs = []
        for attr in ['id', 'title', 'desc', 'category', 'exotic_effect', 'img', 'newsetting', 'newarea']:
            try:
                attrs.append((attr, getattr(self, attr)))
            except AttributeError:
                pass
        attrs.append(tuple(self.effects))
        try:
            attrs.append(('linkedevent', self.linkedevent.id))
        except AttributeError:
            pass
        attrs.append(tuple(self.branches))
        return hash(tuple(attrs))

    def __eq__(self, other):
        for attr in ['id', 'title', 'desc', 'category', 'exotic_effect', 'img', 'newsetting', 'newarea']:
            if hasattr(self, attr) != hasattr(other, attr):
                return False
            try:
                if getattr(self, attr) != getattr(other, attr):
                    return False
            except AttributeError:
                pass
        try:
            if hasattr(self, 'linkedevent') != hasattr(other, 'linkedevent'):
                return False
            if self.linkedevent.id != other.linkedevent.id:
                return False
        except:
            pass
        return set(self.effects) == set(other.effects) and set(self.branches) == set(other.branches)


    def __repr__(self):
        return f'Event: {render_text(self.title)}'
    
    def __str__(self):
        return f'Title: "{render_text(self.title)}"\nDescription: {render_text(self.desc)}\nEffects: {self.list_effects()}\n'
    
    def list_effects(self):
        effects = []
        if self.effects:
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

class Effect:   #done: Priority goes 3/2/1/0
    def __init__(self, jdata):
        self.raw = jdata
        self.id = jdata['Id']
        self.quality = Quality.get(jdata['AssociatedQuality']['Id'])
        self.equip = 'ForceEquip' in jdata
        try:
            self.amount = jdata['Level']
        except:
            try:
                self.amount = jdata['ChangeByAdvanced']
            except KeyError:
                pass
        try:
            self.setTo = jdata['SetToExactly']
        except:
            try:
                self.setTo = jdata['SetToExactlyAdvanced']
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

    def __hash__(self):
        attrs = []
        for attr in ['id', 'amount', 'setTo', 'ceil', 'floor', 'priority']:
            try:
                attrs.append((attr, getattr(self, attr)))
            except AttributeError:
                continue
        attrs.append(('quality', self.quality.id))
        return hash(tuple(attrs))


    def __eq__(self, other):
        for attr in ['id' 'amount', 'setTo', 'ceil', 'floor', 'priority']:
            if hasattr(self, attr) != hasattr(other, attr):
                return False
            try:
                if getattr(self, attr) != getattr(other, attr):
                    return False
            except AttributeError:
                continue
        return self.quality.id == other.quality.id

    def __repr__(self):
        return str(self)

    def __str__(self):
        try:
            amount = sub_qualities(self.amount)
        except:
            pass
        try:
            setTo = sub_qualities(self.setTo)
        except:
            pass

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
            if self.quality.changedesc and isinstance(setTo, int):
                desc = self.quality.get_changedesc(setTo)
                try:
                    return f'{self.quality.name} (set to {setTo} ({desc[1]}){limits})'
                except TypeError:
                    pass
            return f'{self.quality.name} (set to {setTo}{limits})'
        except:
            if self.quality.nature == 2 or not self.quality.pyramid:
                try:
                    return f'{amount:+} x {self.quality.name}{limits}'
                except:
                    return f'{"" if amount.startswith("-") else "+"}{amount} {self.quality.name}{limits}'
            else:
                try:
                    return f'{self.quality.name} ({amount:+} cp{limits})'
                except:
                    return f'{self.quality.name} ({"" if amount.startswith("-") else ""}{amount} cp{limits})'

class Setting:
    def __init__(self, jdata):
        self.raw = jdata
        self.id = jdata.get('Id')
        self.title = jdata.get('Name')
        self.persona = jdata.get('Personae')

        self.exchange = jdata.get('Exchange', {}).get('Id')
        if self.exchange:
            self.exchange = Exchange.get(self.exchange)

    def __hash__(self):
        return hash((self.id, self.title, self.exchange.id))

    def __eq__(self, other):
        return self.id == other.id and self.title == other.title and getattr(self.exchange, "id", None) == getattr(other.exchange, "id", None)

    def __repr__(self):
        return self.title

    def __str__(self):
        string = f'Setting name: {self.title} (Id {self.id})'
        if self.exchange:
            string += f'\n{repr(self.exchange)}'
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
        self.name = jdata.get('Name')
        self.desc = jdata.get('Description')
        self.image = jdata.get('ImageName')
        self.message = jdata.get('MoveMessage')

    def __hash__(self):
        return hash((self.id, self.name, self.desc, self.image, self.message))

    def __eq__(self, other):
        for attr in ['id', 'name', 'desc', 'image', 'message']:
            if getattr(self, attr) != getattr(other, attr):
                return False
        return True

    def __repr__(self):
        if self.name:
            return f'Area: {self.name} (Id {self.id})'
        return f'Area {self.id}'

    def __str__(self):
        if self.name:
            parts = [f'Area: {self.name} (Id {self.id})']
        else:
            parts = [f'Area {self.id}']
        if self.desc:
            parts.append(f'Description: {self.desc}')
        if self.message:
            parts.append(f'Move message: {self.message}')
        if self.image:
            parts.append(f'Image: {self.image}')
        return '\n'.join(parts)

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
        self.name = jdata.get('Name')
        self.title = jdata.get('Title')
        self.desc = jdata.get('Description')
        self.settings = jdata.get('SettingIds', [])
        self.shops = []
        for x in jdata.get('Shops', []):
            self.shops.append(Shop(x))

    def __hash__(self):
        return hash((self.id, self.name, self.title, self.desc, tuple(self.settings), tuple(self.shops)))

    def __eq__(self, other):
        for attr in ['id', 'name', 'title', 'desc']:
            if getattr(self, attr) != getattr(other, attr):
                return False
        return set(self.shops) == set(other.shops)

    def __repr__(self):
        if self.title:
            return f'Exchange title: {self.title} (ID {self.id})'
        elif self.name:
            return f'Exchange name: {self.name} (ID {self.id})'
        else:
            return f'Exchange {self.id}'

    def __str__(self):
        settings = [Setting.get(s).title for s in self.settings]
        if self.title:
            string = f'Exchange title: {self.title} (ID {self.id})\n'
        else:
            string = f'Exchange {self.id}\n'
        string += f'Found in {", ".join(settings)}\n'
        if self.name:
            string += f'Exchange name: {self.name}\n'
        if self.desc:
            string += f'Exchange description: {self.desc}\n'
        string += f'Shops:\n'
        string += '\n\n'.join([str(shop) for shop in self.shops])
        return string

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

    def __hash__(self):
        return hash((self.id, self.name, self.desc, self.image, tuple(self.requirements), tuple(self.offerings)))

    def __eq__(self, other):
        for attr in ['id', 'name', 'desc', 'image']:
            if getattr(self, attr) != getattr(other, attr):
                return False
        return set(self.requirements) == set(self.requirements) and set(self.offerings) == set(self.offerings)

    def __repr__(self):
        return self.name

    def __str__(self):
        string = f'Shop name: {self.name}\n'
        string += f'Description: {self.desc}\n'
        string += f'Requirements: {render_requirements(self.requirements)}\n'
        string += f'Items:\n'
        string += '\n\n'.join([str(o) for o in self.offerings])
        return string

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

    def __hash__(self):
        attrs = []
        for attr in ['id', 'buymessage', 'sellmessage', 'buy', 'sell']:
            try:
                attrs.append((attr, getattr(self, attr)))
            except AttributeError:
                continue
        attrs.append(('item', self.item.id))
        attrs.append(('price', self.price.id))
        return hash(tuple(attrs))

    def __eq__(self, other):
        for attr in ['id', 'buymessage', 'sellmessage', 'buy', 'sell']:
            if hasattr(self, attr) != hasattr(other, attr):
                return False
            try:
                if getattr(self, attr) != getattr(other, attr):
                    return False
            except AttributeError:
                continue
        return self.item.id == other.item.id and self.price.id == other.price.id

    def __repr__(self):
        return f'Item: {self.item.name}'

    def __str__(self):
        string = f'Item: {self.item.name}'
        try:
            string += f'\nSells for {self.buy[0]} x {self.buy[1].name}'
            if self.buymessage != '(no message)':
                string += f'\nPurchase message: {self.buymessage}'
        except AttributeError:
            if self.buymessage != '(no message)':
                string += f'\nPurchase message: {self.buymessage} (cannot be bought)'
        try:
            string += f'\nPurchases for {self.sell[0]} x {self.sell[1].name}'
            if self.sellmessage != '(no message)':
                string += f'\nSale message: {self.sellmessage}'
        except AttributeError:
            if self.sellmessage != '(no message)':
                string += f'\nSale message: {self.sellmessage} (cannot be sold)'
        return string
