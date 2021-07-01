from pywebio.input import *
from pywebio.output import *
from pywebio import pin
from pywebio import start_server
from roller import *
import os
import math
import statistics

from cutecharts.charts import Bar
from cutecharts.faker import Faker

base_info = {
    "quality": 4,
    "defence": 4,
    "shots": 10,
    "piercing": 0,
    "regen": "No",
    "explode": "No",
    "buckets": 5,
    "reroll": 0,
    "deadly": 1,
    "blast": 1,
    "cover": "None",
    "reload": False
}

def cover_to_number(cover_str):
    if cover_str == "None":
        return 0
    elif cover_str == "Light":
        return 1
    elif cover_str == "Heavy":
        return 2

def create_chart(values: list, buckets: int):
    # Divvy the values up into buckets.
    minval = max(min(values)-1, 0)
    maxval = max(values)+1
    width = maxval - minval
    step = width / buckets
    if step < 1:
        step = 1

    labels = []
    counts = []
    for i in range(buckets):
        # We go to less than 1 bucket because we're going to get the upper and lower bounds.
        lower_bound = math.floor(minval + (i * step))
        upper_bound = math.floor(minval + ((i + 1) * step))
        label = f"{lower_bound}-{upper_bound}"
        # Get the sum as a percentage.
        count = (sum(i >= lower_bound and i < upper_bound for i in values)/len(values)) * 100
        labels.append(label)
        counts.append(round(count, 2))

    chart = Bar("Distribution of Rolls", width="100%", height="100%")
    chart.set_options(labels=labels, x_label="Wounds (buckets)", y_label="Ocurrences %")
    chart.add_series("Count", counts)
    return chart

def print_header(button_outline=False):
    with use_scope('header', clear=True):
        put_column([put_row([put_markdown("## Wound Calculator"), None, put_buttons(buttons=["Reload"], onclick=update_scope_new, outline=button_outline).style('align-self: center; justify-self: right;')], \
    size='70% 5% 25%'), put_text("A simple app that allows you to input some OPR stats, and calculates the average number of \
wounds generated for that spread and number of attacks.")])

def print_wounds(roll_info):
    wounds = 0
    # if (roll_info['method'] == 'Probability'):
    #     wounds = get_number_of_wounds(roll_info['quality'], 
    #                                 roll_info['defence'], 
    #                                 roll_info['shots'], 
    #                                 roll_info['piercing'], 
    #                                 roll_info['regen'] == "Yes", 
    #                                 roll_info['explode'] == "Yes")
    #     put_markdown(f"# Number of wounds: {wounds}")
    # else:
    with use_scope('graph', clear=True):
        put_row([None, put_loading(), None], size='50%')
    
    # Estimate it by running the numbers through a random generator and seeing what comes out.
    wounds = get_number_of_wounds_randomly_x_times_list(roll_info['quality'], 
                                roll_info['defence'], 
                                roll_info['shots'], 
                                roll_info['piercing'], 
                                roll_info['regen'] == "Yes", 
                                roll_info['explode'] == "Yes",
                                cover_to_number(roll_info['cover']),
                                roll_info['reroll'],
                                roll_info['blast'],
                                roll_info['deadly'],
                                10000)
    
    with use_scope('graph', clear=True):
        # Get the median, as its less prone to outliers.
        put_markdown(f"# Average number of wounds: {statistics.median(wounds)}")
        chart = create_chart(wounds, roll_info['buckets'])
        put_html(chart.render_notebook())

def put_inputs(roll_info):
    return [
    put_row([
        pin.put_select(label="Attacker Quality: ", options=[2,3,4,5,6], name="quality", value=roll_info['quality'], help_text='The effective quality of the attacking units.'), None,
        pin.put_select(label="Defender Defence: ", options=[2,3,4,5,6], name="defence", value=roll_info['defence'], help_text='The unmodified defence of the defending units.'), None,
        pin.put_input(label="Number of attacks: ", type=NUMBER, name="shots", value=roll_info['shots'], help_text='The number of attacks we are rolling for.')
    ]),
    put_row([
        pin.put_select(label="AP: ", options=[0, 1, 2, 3, 4, 5, 6], name="piercing", value=roll_info['piercing'], help_text='The armour piercing value of the weapon.'), None,
        pin.put_radio(label="Regenarator?", options=["No", "Yes"], name="regen", value=roll_info['regen'], inline = True, help_text='Whether the defender ignores a wound on a 5+.'), None,
        pin.put_radio(label="Explode?", options=["No", "Yes"], name="explode", value=roll_info['explode'], inline = True, help_text='Whether to roll two addition attacks when a 6 is rolled.')
    ]),
    put_row([
        pin.put_select(label="Cover: ", options=["None", "Light", "Heavy"], name="cover", value=roll_info['cover'], help_text='Whether the defenders are in any kind of cover.'), None,
        pin.put_select(label="Blast: ", options=[1, 3, 6], name="blast", value=roll_info['blast'], help_text='The number of saves caused by each successful attack.'), None,
        pin.put_select(label="Deadly: ", options=[1, 2, 3, 4, 5, 6], name="deadly", value=roll_info['deadly'], help_text='The number of wounds caused by each failed save.'), None,
    ]),
    put_row([
        pin.put_select(label="Reroll On: ", options=[0, 1, 2, 3, 4, 5, 6], name="reroll", value=roll_info['reroll'], help_text='Rerolls the dice when at or below the number.'), None,
        pin.put_input(label="Histogram Buckets: ", name="buckets", type=NUMBER, value=5, help_text='The number of histogram buckets to display.'), None
    ])]

def update_inputs(info, input):
    if input['name'] == 'shots':
        if not input['value'] or input['value'] == None:
            input['value'] = 0
    
    if input['name'] == 'buckets':
        if not input['value'] or input['value'] == None:
            input['value'] = 1

    info[input['name']] = input['value']

def update_scope(new_val):
    with use_scope("wounds", clear=True):
        update_inputs(base_info, new_val)
        print_wounds(base_info)

def update_scope_new(button):
    print_header(True)
    base_info['reload'] = False

    with use_scope("wounds", clear=True):
        update_inputs(base_info, {'name': 'quality', 'value': pin.pin['quality']})
        update_inputs(base_info, {'name': 'defence', 'value': pin.pin['defence']})
        update_inputs(base_info, {'name': 'piercing', 'value': pin.pin['piercing']})
        update_inputs(base_info, {'name': 'regen', 'value': pin.pin['regen']})
        update_inputs(base_info, {'name': 'explode', 'value': pin.pin['explode']})
        update_inputs(base_info, {'name': 'shots', 'value': pin.pin['shots']})
        update_inputs(base_info, {'name': 'buckets', 'value': pin.pin['buckets']})
        update_inputs(base_info, {'name': 'cover', 'value': pin.pin['cover']})
        update_inputs(base_info, {'name': 'reroll', 'value': pin.pin['reroll']})
        update_inputs(base_info, {'name': 'blast', 'value': pin.pin['blast']})
        update_inputs(base_info, {'name': 'deadly', 'value': pin.pin['deadly']})
        print_wounds(base_info)

def app():
    print_header(True)
    put_collapse("Input", put_inputs(base_info), open=True)

    while True:
        new_val = pin.pin_wait_change(["quality", "defence", "piercing", "regen", "explode", "shots", "buckets", "cover", "reroll", "blast", "deadly"])
        if base_info['reload'] == False:
            print_header(False)
            base_info['reload'] = True

if __name__ == '__main__':
    start_server(app, port=os.environ.get('PORT', 8080), reconnect_timeout=600)