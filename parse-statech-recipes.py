#! /usr/bin/env python3

import json

from math import floor, ceil

from pygments import highlight
from pygments.lexers import JsonLexer
from pygments.formatters import TerminalFormatter

import tarfile
import re
from collections import defaultdict
from itertools import product
from itertools import groupby
import uuid


def pp(data):
    print(highlight(json.dumps(data), JsonLexer(), TerminalFormatter()))

def sum_tuples_by_key(keys, values):
    d = defaultdict(int)
    for k, v in zip(keys, values):
        if v > 0:
            d[k] += v
    return dict(d)

with open("factorio_icons.json") as f:
    icons = json.load(f);

#=====[TAGS]=========================================================

tag_items = defaultdict(set)
pattern = re.compile(r"local/kubejs/export/tags/minecraft/item/(.*)\.json")
with tarfile.open("tags.tar.gz") as tar:
    for member in tar.getmembers():
        if member.isfile():
            tag = pattern.match(member.name).group(1).replace("/", ":", 1)
            for v in json.load(tar.extractfile(member)):
                tag_items[tag].add(v.replace('?', ''))

def walk(iterable):
    for item in iterable:
        if item[0] == '#':
            nested = tag_items.get(item[1:])
            if nested:
                yield from walk(nested)
        else:
            yield item

for tag in tag_items:
    tag_items[tag] = set(walk(tag_items[tag]))

#====================================================================

def tar_iterator(filename):
    with tarfile.open(filename) as tar:
        for recipe in tar.getmembers():
            if recipe.isfile():
                yield json.load(tar.extractfile(recipe))

def icon_data(key):
    return {
        "id": key,
        "position": "0px 0px"
    }

recipe_data_in = [
    {
        "type": "modern_industrialization:test",
        "eu": 1,
        "duration": 10,
        "item_inputs": [{"item": "modern_industrialization:a", "amount": 1}],
        "item_outputs": [{"item": "modern_industrialization:b", "amount": 1}]
    },
    {
        "type": "modern_industrialization:test",
        "eu": 1,
        "duration": 10,
        "item_inputs": [{"item": "modern_industrialization:b", "amount": 1}],
        "item_outputs": [{"item": "modern_industrialization:a", "amount": 2}]
    },
]
recipe_data_in = tar_iterator("recipes.tar.gz")

recipe_data_out = {
    'version'       : {"StatechIndustry":"1.13.0"},
    'categories'    : [],
    'icons'         : [],
    'items'         : [],
    'recipes'       : [],
    'limitations'   : {},
    'defaults'      : {"excludedRecipes": []},
}

ignore = {
    "modern_industrialization:forge_hammer",
    "modern_industrialization:large_steam_macerator",
    "modern_industrialization:large_steam_furnace",
}

auto_overclock = (
    "modern_industrialization__fusion_reactor",
    "modern_industrialization__singularity_forge"
)

class RecipeList:
    def __init__(self):
        self.recipes = []
        self.fluids = set()

    def add(self, recipe_type, inputs, outputs, energy=0, time=None, exclude=False):
        proper_id = lambda x: x.replace('_', '-')
        item_ids = lambda d: {proper_id(k): v for k, v in d.items()}
        recipe_type = recipe_type.replace(':', '__')

        icon = {
            "modern_industrialization__nuclear_reactor": "nuclear-power",
            "modern_industrialization__fusion_reactor": "rocket-part",
        }.get(recipe_type, "automation-2")
        icon_text = "R"

        inputs = {k.replace(':', '__'): v for k, v in inputs.items()}
        outputs = {k.replace(':', '__'): v for k, v in outputs.items()}
        names = lambda d: '+'.join(x.split('__')[-1] for x in d.keys())
        recipe_id = f"R-{len(self.recipes)}"
        recipe_name = f"({recipe_type.split('__')[-1]}) {names(outputs)}_from_{names(inputs)}"
        if time == None:
            time = 1
            #time = 1 if (recipe_type in auto_overclock) else max(ceil(energy / (128*64+32)), 1)
            multiplier = ceil(energy / (128*64+32))
            if (recipe_type not in auto_overclock) and multiplier > 1:
                icon = "automation-3"
                icon_text = str(multiplier)

        cost = {
            "modern_industrialization__packer": 0.05,
        }.get(recipe_type)
        extra_cost = {"cost": cost} if cost else {}

        self.recipes.append({
            "category"  : proper_id(recipe_type),
            "id"        : recipe_id,
            "name"      : recipe_name,
            "time"      : time,
            "row"       : 0,
            "producers" : [proper_id(recipe_type)],
            "in"        : item_ids(inputs),
            "out"       : item_ids(outputs),
            "icon"      : icon,
            "iconText"  : icon_text,
            "usage"     : floor(energy / time),
        } | extra_cost)

        if exclude:
            recipe_data_out["defaults"]["excludedRecipes"].append(recipe_id)

    def register_fluid(self, fluid):
        self.fluids.add(fluid.replace(':', '__').replace('_', '-'))

    def _items(self, k):
        return set(x for recipe in self.recipes for x in recipe[k].keys())

    def _is_fluid(self, item):
        return item in self.fluids

    def write(self):
        inputs = self._items('in')
        outputs = self._items('out')
        categories = set(recipe['category'] for recipe in self.recipes)

        recipe_data_out['recipes'] = self.recipes

        name = lambda x: x.split('--')[-1].replace('-', '_')

        def icon(item_id):
            item = name(item_id)

            if self._is_fluid(item_id):
                return "advanced-oil-processing"
            if item.endswith("_ore"):
                return "stone"
            if item.startswith("raw_"):
                return "coal"
            if item.endswith("_dust"):
                return "iron-ore"
            if item.endswith("_plate"):
                return "steel-processing"
            if item.endswith("_ingot"):
                return "copper-plate"
            if item.endswith("_battery"):
                return "battery"
            if item.endswith("_drill"):
                return "electric-mining-drill"
            if item.endswith("_gear"):
                return "iron-gear-wheel"
            if item.endswith("_wire"):
                return "copper-cable"
            if item.endswith("_cable"):
                return "green-wire"
            if "circuit" in item:
                return "electronics"
            if "_fuel_rod_depleted" in item:
                return "used-up-uranium-fuel-cell"
            if "_fuel_rod" in item:
                return "uranium-fuel-cell"
            if "_rod" in item:
                return "iron-stick"
            return "solid-fuel"

        recipe_data_out['items'] = list(({
            item : {
                "id": item,
                "name": name(item),
                "category": "processed",
                "stack": 64,
                "row": 0,
                "icon": icon(item),
            } for item in (inputs | outputs)
        } | {
            machine : {
                "id": machine,
                "name": name(machine),
                "category": "machines",
                "stack": 64,
                "row": 0,
                "icon": "assembling-machine-2",
                "iconText": "M",
                "machine": {"type":"electric", "modules":0, "speed":1},
            } for machine in categories
        }).values())

        recipe_data_out['categories'] = [
            {
                "id": category,
                "name": name(category),
                "icon": "assembling-machine-1",
                "iconText": "C",
            } for category in set(["processed"]) | categories
        ]

        recipe_data_out['icons'] = icons

        with open('src/data/mcsi/data.json', 'w') as f:
            json.dump(recipe_data_out, f)

    def simplify(self):
        while True:
            outputs = self._items('out')

            invalid = set()
            for recipe in self.recipes:
                if (set(recipe['in'].keys()) - outputs):
                    #dbg("REMOVED", recipe['out'], set(recipe['in'].keys()) - outputs)
                    invalid.add(recipe['id'])

            if not invalid:
                break

            self.recipes = [recipe for recipe in self.recipes if recipe['id'] not in invalid]

recipe_list = RecipeList()

#=====[HARDCODED]====================================================

recipe_list.add(recipe_type="raw", inputs={}, outputs={"ae2__certus_quartz_crystal":1})

deuterium_production = 163.9
deuterium_production_ticks = ceil(1 / (1.711 / 20 / 60))
deuterium_hp_water_in = 20.48
deuterium_hp_steam_out = 25450

tritium_production = 56.45
tritium_production_ticks = ceil(1 / (1.953 / 20 / 60))
tritium_hph_water_in = 7.055
tritium_hph_steam_out = 25450

plutonium_production_ticks = ceil(4 / (6.822 / 20 / 60))

recipe_list.add(
    recipe_type="modern_industrialization__nuclear_reactor",
    inputs={
        "modern_industrialization__high_pressure_water": ceil(deuterium_hp_water_in * deuterium_production_ticks),
        "modern_industrialization__le_mox_fuel_rod": 1,
        "minecraft__water": deuterium_hp_steam_out * deuterium_production_ticks,
    },
    outputs={
        "modern_industrialization__deuterium": floor(deuterium_production * deuterium_production_ticks),
        "modern_industrialization__le_mox_fuel_rod_depleted": 1,
        "modern_industrialization__steam": 8 * deuterium_hp_steam_out * deuterium_production_ticks,
    },
    time=deuterium_production_ticks
)
recipe_list.add(
    recipe_type="modern_industrialization__nuclear_reactor",
    inputs={
        "modern_industrialization__high_pressure_heavy_water": ceil(tritium_hph_water_in * tritium_production_ticks),
        "modern_industrialization__le_mox_fuel_rod": 1,
        "minecraft__water": tritium_hph_steam_out * tritium_production_ticks,
    },
    outputs={
        "modern_industrialization__tritium": floor(tritium_production * tritium_production_ticks),
        "modern_industrialization__le_mox_fuel_rod_depleted": 1,
        "modern_industrialization__steam": 8 * tritium_hph_steam_out * tritium_production_ticks,
    },
    time=tritium_production_ticks
)
recipe_list.add(
    recipe_type="modern_industrialization__nuclear_reactor",
    inputs={"modern_industrialization__uranium_fuel_rod_quad": 1},
    outputs={"modern_industrialization__uranium_fuel_rod_depleted": 4},
    time=plutonium_production_ticks
)

def fortune(input, output, m = 1 / (10 + 2) + (10 + 1) / 2):
    recipe_list.add(
        recipe_type="fortune",
        inputs={input: 1},
        outputs={k:v*m for k,v in output.items()},
        time=5,
        exclude=True
    )

fortune("minecraft__coal_ore",                        {"minecraft__coal":1})
fortune("minecraft__iron_ore",                        {"minecraft__raw_iron":1})
fortune("minecraft__copper_ore",                      {"minecraft__raw_copper":3.5})
fortune("minecraft__gold_ore",                        {"minecraft__raw_gold":1})
fortune("minecraft__redstone_ore",                    {"minecraft__redstone":9.5}, m=1)
fortune("modern_industrialization__lignite_coal_ore", {"modern_industrialization__lignite_coal":1})
fortune("modern_industrialization__tin_ore",          {"modern_industrialization__raw_tin":1})
fortune("modern_industrialization__lead_ore",         {"modern_industrialization__raw_lead":1})
fortune("techreborn__silver_ore",                     {"modern_industrialization__raw_silver":1})

fortune("minecraft__diamond_ore",                 {"minecraft__diamond":1})
fortune("minecraft__lapis_ore",                   {"minecraft__lapis_lazuli":6.5})
fortune("minecraft__emerald_ore",                 {"minecraft__emerald":1})
fortune("modern_industrialization__antimony_ore", {"modern_industrialization__raw_antimony":1})
fortune("modern_industrialization__fluorite_ore", {"modern_industrialization__raw_fluorite":1})
fortune("modern_industrialization__nickel_ore",   {"modern_industrialization__raw_nickel":1})
fortune("modern_industrialization__bauxite_ore",  {"modern_industrialization__bauxite_dust":1})
fortune("modern_industrialization__salt_ore",     {"modern_industrialization__salt_dust":1})
fortune("modern_industrialization__quartz_ore",   {"minecraft__nether_quartz":1})

fortune("modern_industrialization__titanium_ore", {"modern_industrialization__raw_titanium":1})
fortune("modern_industrialization__tungsten_ore", {"modern_industrialization__raw_tungsten":1})
fortune("modern_industrialization__platinum_ore", {"modern_industrialization__raw_platinum":1})
fortune("modern_industrialization__mozanite_ore", {"modern_industrialization__mozanite_dust":1})

fortune("modern_industrialization__uranium_ore", {"modern_industrialization__raw_uranium":1})
fortune("modern_industrialization__iridium_ore", {"modern_industrialization__raw_iridium":1})

fortune("techreborn__ruby_ore",     {"techreborn__ruby":1.5, "techreborn__red_garnet":0.5})
fortune("techreborn__sapphire_ore", {"techreborn__sapphire":1.5, "techreborn__peridot":0.5})
fortune("techreborn__peridot_ore",  {"techreborn__peridot":1.5})
#fortune("techreborn__sodalite_ore", {"techreborn__sodalite_dust":1, "techreborn__aluminum_dust":0.5})

#=====[AUTOMATIC]====================================================

for recipe in recipe_data_in:
    if recipe['type'] in ignore:
        continue

    def _get(k):
        v = recipe.get(k, [])
        return [v] if type(v) == dict else v

    if recipe['type'] == "minecraft:smelting":
        ingredients = _get("ingredient")
        result = recipe.get("result")
        for ingredient in ingredients:
            for item in (tag_items.get(ingredient.get("tag")) or {ingredient.get("item")}):
                energy = 2 * recipe.get('cookingtime', 200)
                recipe_list.add(recipe_type="modern_industrialization__electric_furnace", inputs={item:1}, outputs={result:1}, energy=energy)

    elif recipe['type'].split(':')[0] == "modern_industrialization":
        machine = recipe['type']

        item_inputs = _get('item_inputs')
        item_outputs = _get('item_outputs')
        fluid_inputs = _get('fluid_inputs')
        fluid_outputs = _get('fluid_outputs')

        for x in fluid_inputs + fluid_outputs:
            recipe_list.register_fluid(x.get("fluid"))

        amount_in = [x.get('amount', 0) * x.get('probability', 1) for x in item_inputs + fluid_inputs]
        amount_out = [x.get('amount', 0) * x.get('probability', 1) for x in item_outputs + fluid_outputs]

        outputs = sum_tuples_by_key(
            [x.get("item") for x in item_outputs] + [x.get("fluid") for x in fluid_outputs],
            amount_out
        )

        energy = recipe['duration'] * recipe['eu']

        for inputs in product(*[tag_items.get(x.get("tag")) or {x.get("item") or x.get("fluid")} for x in item_inputs + fluid_inputs]):
            recipe_list.add(recipe_type=machine, inputs=sum_tuples_by_key(inputs, amount_in), outputs=outputs, energy=energy)

#====================================================================

before = len(recipe_list.recipes)
print("parsed  ", before)
recipe_list.simplify()
print("removed ", before - len(recipe_list.recipes))
recipe_list.write()

'''
for recipe in recipe_data_out['recipes']:
    pp(recipe)
'''