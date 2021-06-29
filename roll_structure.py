from dataclasses import dataclass
from roller import get_number_of_wounds

@dataclass(frozen=True)
class scenario:
    quality: int
    defence: int
    piercing: int
    regenerator: bool
    explode: bool

    def __get_probability_n_or_more(self, n) -> float:
        return (6-n)/6 + 1/6

    def get_number_of_wounds(self, shots):
        return get_number_of_wounds(self.quality, self.defence, shots, self.piercing, self.regenerator, self.explode)

    def get_column_data(self, shots):
        return [self.quality, self.defence, self.piercing, self.regenerator, self.explode, shots, self.get_number_of_wounds(shots)]