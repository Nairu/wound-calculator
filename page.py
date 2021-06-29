from pywebio.input import *
from pywebio.output import *
from pywebio import pin
from pywebio import start_server
from roller import *

def print_header():
    return put_column([
        put_markdown("## Wound Calculator"),
        put_text("A simple app that allows you to input some OPR stats, and calculates the average number of \
wounds generated for that spread and number of shots.")
    ])

def print_wounds(roll_info):
    wounds = get_number_of_wounds(roll_info['quality'], 
                                roll_info['defence'], 
                                roll_info['shots'], 
                                roll_info['piercing'], 
                                roll_info['regen'] == "Yes", 
                                roll_info['explode'] == "Yes")
    put_markdown(f"# Number of wounds: {wounds}")

def put_inputs(roll_info):
    put_row([
        pin.put_select(label="Attacker Quality: ", options=[2,3,4,5,6], name="quality", value=roll_info['quality']), None,
        pin.put_select(label="Defender Defence: ", options=[2,3,4,5,6], name="defence", value=roll_info['defence']), None,
        pin.put_input(label="Number of shots: ", type=NUMBER, name="shots", value=roll_info['shots'])
    ])
    put_row([
        pin.put_select(label="AP: ", options=[0, 1, 2, 3, 4, 5, 6], name="piercing", value=roll_info['piercing']), None,
        pin.put_radio(label="Regenarator?", options=["No", "Yes"], name="regen", value=roll_info['regen'], inline = True), None,
        pin.put_radio(label="Explode?", options=["No", "Yes"], name="explode", value=roll_info['explode'], inline = True)
    ])

def update_inputs(info, input):
    if input['name'] == 'shots':
        if not input['value'] or input['value'] == None:
            input['value'] = 0

    info[input['name']] = input['value']

def app():
    base_info = {
        "quality": 4,
        "defence": 4,
        "shots": 10,
        "piercing": 0,
        "regen": "No",
        "explode": "No"
    }

    put_row(print_header())
    put_inputs(base_info)
    #put_row([put_column(print_header()), put_column(put_inputs(base_info))])
    while True:
        new_val = pin.pin_wait_change(["quality", "defence", "shots", "piercing", "regen", "explode"])
        with use_scope("wounds", clear=True):
            update_inputs(base_info, new_val)
            print_wounds(base_info)

if __name__ == '__main__':
    start_server(app, debug=True, port='8080')