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
    "method": "Probability",
    "buckets": 5
}

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

def print_header():
    return put_column([
        put_markdown("## Wound Calculator"),
        put_text("A simple app that allows you to input some OPR stats, and calculates the average number of \
wounds generated for that spread and number of shots.")
    ])

def print_wounds(roll_info):
    wounds = 0
    if (roll_info['method'] == 'Probability'):
        wounds = get_number_of_wounds(roll_info['quality'], 
                                    roll_info['defence'], 
                                    roll_info['shots'], 
                                    roll_info['piercing'], 
                                    roll_info['regen'] == "Yes", 
                                    roll_info['explode'] == "Yes")
        put_markdown(f"# Number of wounds: {wounds}")
    else:
        with use_scope('graph', clear=True):
            put_row([None, put_loading(), None], size='50%')
        
        # Estimate it by running the numbers through a random generator and seeing what comes out.
        wounds = get_number_of_wounds_randomly_x_times_list(roll_info['quality'], 
                                    roll_info['defence'], 
                                    roll_info['shots'], 
                                    roll_info['piercing'], 
                                    roll_info['regen'] == "Yes", 
                                    roll_info['explode'] == "Yes",
                                    10000)
        
        with use_scope('graph', clear=True):
            # Get the median, as its less prone to outliers.
            put_markdown(f"# Average number of wounds: {statistics.median(wounds)}")
            chart = create_chart(wounds, roll_info['buckets'])
            put_html(chart.render_notebook())

def put_inputs(roll_info):
    return [
    put_row([
        pin.put_select(label="Attacker Quality: ", options=[2,3,4,5,6], name="quality", value=roll_info['quality']), None,
        pin.put_select(label="Defender Defence: ", options=[2,3,4,5,6], name="defence", value=roll_info['defence']), None,
        pin.put_input(label="Number of shots: ", type=NUMBER, name="shots", value=roll_info['shots'])
    ]),
    put_row([
        pin.put_select(label="AP: ", options=[0, 1, 2, 3, 4, 5, 6], name="piercing", value=roll_info['piercing']), None,
        pin.put_radio(label="Regenarator?", options=["No", "Yes"], name="regen", value=roll_info['regen'], inline = True), None,
        pin.put_radio(label="Explode?", options=["No", "Yes"], name="explode", value=roll_info['explode'], inline = True)
    ]),
    put_row([
        pin.put_radio(label="Calculation Method: ", name="method", options=["Probability", "Simulate"], value="Probability"), None,
        pin.put_input(label="Histogram Buckets: ", name="buckets", type=NUMBER, value=5), None,
        put_buttons(buttons=["Reload"], onclick=update_scope_new)
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
    with use_scope("wounds", clear=True):
        shots_val = pin.pin['shots']
        buckets_val = pin.pin['buckets']
        update_inputs(base_info, {'name': 'shots', 'value': shots_val})
        update_inputs(base_info, {'name': 'buckets', 'value': buckets_val})
        print_wounds(base_info)

def app():
    put_row(print_header())
    put_collapse("Inputs", put_inputs(base_info), open=True)
    #put_row([put_column(print_header()), put_column(put_inputs(base_info))])
    while True:
        new_val = pin.pin_wait_change(["quality", "defence", "piercing", "regen", "explode", "method"])
        update_scope(new_val)

if __name__ == '__main__':
    start_server(app, port=os.environ.get('PORT', 8080))