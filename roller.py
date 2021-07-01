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

def get_number_of_successful_shots(quality, num_shots, cover, reroll, blast) -> int:
    return (int(get_probability_n_or_more(quality) * num_shots)) * blast

def get_number_of_failed_saves(defence, piercing, num_wounds) -> int:
    modified_defence = min(6, defence + piercing)
    return num_wounds - (int(get_probability_n_or_more(modified_defence) * num_wounds))

def get_number_of_failed_regenerations(regenerator, num_wounds) -> int:
    return num_wounds - (int(get_probability_n_or_more(regenerator) * num_wounds))

def get_number_of_wounds(quality, defence, shots, piercing=0, regenerator=False, explode=False, cover=0, reroll=1, blast=1, deadly=1):
    num_shots = shots + (get_number_of_extra_shots(shots) if explode else 0)
    shots = get_number_of_successful_shots(quality, num_shots, cover, reroll, blast)
    dead = get_number_of_failed_saves(defence, piercing, shots)
    if regenerator:
        dead = get_number_of_failed_regenerations(5, dead)
    return dead

def get_number_of_wounds_randomly(quality, defence, shots, piercing=0, regenerator=False, explode=False, cover=0, reroll=1, blast=1, deadly=1):
    # First calculate the number of hits.
    num_hits = 0
    for i in range(shots):
        roll = random.randint(1, 6)
        if roll == 6:
            if explode:
                num_hits += blast
                # We roll 2 additional times for explode.
                new_roll = random.randint(1, 6)
                num_hits += blast if new_roll == 6 or (new_roll - cover) >= quality else 0
                new_roll = random.randint(1, 6)
                num_hits += blast if new_roll == 6 or (new_roll - cover) >= quality else 0
            else:
                # A 6 always succeeds.
                num_hits += blast
        elif roll == 1:
            # A 1 always fails.
            num_hits += 0
        elif roll <= reroll:
            # If the number is less than reroll, we missed, so roll again.
            new_roll = random.randint(1, 6)
            num_hits += blast if new_roll == 6 or (new_roll - cover) >= quality else 0
        elif (roll - cover) >= quality:
            # Else just handle it normally.
            num_hits += blast
    
    # We have the number of hits. Now get the number of failed rolls.
    wounds = 0
    for i in range(num_hits):
        roll = random.randint(1, 6)
        target = min(6, defence + piercing)
        if roll < target:
            # Check for the regenerator.
            if regenerator:
                regen_roll = random.randint(1, 6)
                wounds += deadly if regen_roll < 5 else 0
            else:
                wounds += deadly
    
    return wounds

def get_number_of_wounds_randomly_x_times(quality, defence, shots, piercing=0, regenerator=False, explode=False, cover=0, reroll=1, blast=1, deadly=1, repeat=5):
    total_wounds = 0
    for i in range(repeat):
        total_wounds += get_number_of_wounds_randomly(quality, defence, shots, piercing, regenerator, explode, cover, reroll, blast, deadly)
    total_wounds = total_wounds / repeat
    return int(round(total_wounds))

def get_number_of_wounds_randomly_x_times_list(quality, defence, shots, piercing=0, regenerator=False, explode=False, cover=0, reroll=1, blast=1, deadly=1, repeat=5):
    return [int(get_number_of_wounds_randomly(quality, defence, shots, piercing, regenerator, explode, cover, reroll, blast, deadly)) for i in range(repeat)]

if __name__ == "__main__":
    parser = init_argparse()
    args = parser.parse_args()
    dead = get_number_of_wounds(args.quality, args.defence, args.num_shots, args.piercing, args.regenerator, args.explode)
    print (f"Average number of wounds: {dead}")