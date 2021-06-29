import argparse
import random

def get_probability_n_or_more(n) -> float:
    return (6-n)/6 + 1/6

def init_argparse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        usage="%(prog)s [OPTION] ...",
        description="Calculates the average number of models killed"
    )
    parser.add_argument(
        "-v", "--version", action="version",
        version = f"{parser.prog} version 1.0.0"
    )
    parser.add_argument("-q", "--quality", help="The quality of the attacking models", type=int)
    parser.add_argument("-d", "--defence", help="The defence of the defending models", type=int)
    parser.add_argument("-n", "--num_shots", help="The number of shots the attackers are making", type=int)
    parser.add_argument("-p", "--piercing", help="The armour piercing value of the attackers weapons", type=int, default=0)
    parser.add_argument("-r", "--regenerator", action="store_true", default=False, help="Whether the defender models have regenerator")
    parser.add_argument("-e", "--explode", action="store_true", default=False, help="Whether 6s explode to 3 hits.")

    return parser

def get_number_of_extra_shots(num_shots) -> int:
    return (num_shots * 1/6) * 2

def get_number_of_successful_shots(quality, num_shots) -> int:
    return (int(get_probability_n_or_more(quality) * num_shots))

def get_number_of_failed_saves(defence, piercing, num_wounds) -> int:
    modified_defence = min(6, defence + piercing)
    return num_wounds - (int(get_probability_n_or_more(modified_defence) * num_wounds))

def get_number_of_failed_regenerations(regenerator, num_wounds) -> int:
    return num_wounds - (int(get_probability_n_or_more(regenerator) * num_wounds))

def get_number_of_wounds(quality, defence, shots, piercing=0, regenerator=False, explode=False):
    num_shots = shots + (get_number_of_extra_shots(shots) if explode else 0)
    shots = get_number_of_successful_shots(quality, num_shots)
    dead = get_number_of_failed_saves(defence, piercing, shots)
    if regenerator:
        dead = get_number_of_failed_regenerations(5, dead)
    return dead

def get_number_of_wounds_randomly(quality, defence, shots, piercing=0, regenerator=False, explode=False):
    # First calculate the number of hits.
    num_hits = 0
    for i in range(shots):
        roll = random.randint(1, 6)
        if roll == 6 and explode:
            num_hits += 3
        elif roll >= quality:
            num_hits += 1
    
    # We have the number of hits. Now get the number of failed rolls.
    wounds = 0
    for i in range(num_hits):
        roll = random.randint(1, 6)
        target = min(6, defence + piercing)
        if roll < target:
            # Check for the regenerator.
            if regenerator:
                regen_roll = random.randint(1, 6)
                wounds += 1 if regen_roll < 5 else 0
            else:
                wounds += 1
    
    return wounds

def get_number_of_wounds_randomly_x_times(quality, defence, shots, piercing=0, regenerator=False, explode=False, repeat=5):
    total_wounds = 0
    for i in range(repeat):
        total_wounds += get_number_of_wounds_randomly(quality, defence, shots, piercing, regenerator, explode)
    total_wounds = total_wounds / repeat
    return int(round(total_wounds))

def get_number_of_wounds_randomly_x_times_list(quality, defence, shots, piercing=0, regenerator=False, explode=False, repeat=5):
    return [int(get_number_of_wounds_randomly(quality, defence, shots, piercing, regenerator, explode)) for i in range(repeat)]

if __name__ == "__main__":
    parser = init_argparse()
    args = parser.parse_args()
    dead = get_number_of_wounds(args.quality, args.defence, args.num_shots, args.piercing, args.regenerator, args.explode)
    print (f"Average number of wounds: {dead}")