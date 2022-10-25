from actions import*
from attributes import Element, Reactions

RaiFish = {"list": [Skill(0, 0),
                    Swap(2, 0.62),
                    Skill(2, 0.85, infusion=Element.ELECTRO),
                    Reaction(2, 1.1, Reactions.ELECTROSWIRL),
                    Reaction(2, 1.9, Reactions.ELECTROSWIRL),
                    Swap(1, 1.9),
                    Skill(1, 2.13),
                    Reaction(1, 2.42, Reactions.OVERLOAD),
                    Burst(1, 2.85),
                    Swap(3, 3.72),
                    Normal(3, 3.95, 2),
                    Charged(3, 4.5),
                    Reaction(0, 4.47, Reactions.OVERLOAD),
                    Burst(3, 4.58),
                    Reaction(3, 4.73, Reactions.OVERLOAD),
                    Swap(2, 5),
                    Burst(2, 5.23, infusion=Element.PYRO),
                    Reaction(2, 6.62, Reactions.ELECTROSWIRL),
                    Swap(0, 6.83),
                    Burst(0, 7.07),
                    Reaction(2, 7.7, Reactions.ELECTROSWIRL),
                    Reaction(2, 7.7, Reactions.OVERLOAD),
                    Normal(0, 8.93, 3),
                    Reaction(2, 9.65, Reactions.ELECTROSWIRL),
                    Reaction(2, 9.65, Reactions.OVERLOAD),
                    Normal(0, 11.08, 3),
                    Reaction(2, 11.6, Reactions.ELECTROSWIRL),
                    Reaction(2, 11.6, Reactions.OVERLOAD),
                    Normal(0, 13.23, 3),
                    Reaction(2, 13.55, Reactions.ELECTROSWIRL),
                    Reaction(2, 13.55, Reactions.OVERLOAD),
                    Swap(3, 15.37),
                    Reaction(2, 15.5, Reactions.ELECTROSWIRL),
                    Reaction(2, 15.5, Reactions.OVERLOAD),
                    Charged(3, 15.5),
                    Normal(3, 15.4, 1),
                    Skill(3, 15.6),
                    Swap(2, 16.6),
                    Skill(2, 16.83, infusion=Element.PYRO),
                    Reaction(2, 17.08, Reactions.ELECTROSWIRL),
                    Reaction(2, 17.87, Reactions.ELECTROSWIRL),
                    Reaction(2, 17.87, Reactions.OVERLOAD),
                    Normal(3, 18, 3),
                    Swap(0, 18.95),
                    Skill(0, 19.18),
                    Normal(0, 20.05, 1),
                    Swap(1, 20.07),
                    Skill(1, 20.3),
                    Reaction(1, 20.58, Reactions.OVERLOAD),
                    Burst(1, 21.02),
                    Reaction(1, 21.65, Reactions.OVERLOAD),
                    Swap(3, 21.88),
                    Normal(3, 22.38, 2),
                    Burst(3, 22.75),
                    Swap(2, 23.15),
                    Skill(2, 23.4, infusion=Element.PYRO),
                    Reaction(2, 23.65, reaction=Reactions.ELECTROSWIRL),
                    Reaction(2, 24.43, reaction=Reactions.ELECTROSWIRL),
                    Reaction(2, 24.435, reaction=Reactions.OVERLOAD),
                    Burst(2, 24.45, infusion=Element.PYRO),
                    Reaction(2, 25.82, reaction=Reactions.ELECTROSWIRL),
                    Swap(0, 26.05),
                    Burst(0, 26.28),
                    Reaction(2, 26.92, reaction=Reactions.OVERLOAD),
                    Reaction(2, 26.92, reaction=Reactions.ELECTROSWIRL),
                    Normal(0, 28.15, 3),
                    Reaction(2, 28.87, reaction=Reactions.OVERLOAD),
                    Reaction(2, 28.87, reaction=Reactions.ELECTROSWIRL),
                    Normal(0, 30.3, 3),
                    Reaction(2, 30.82, reaction=Reactions.OVERLOAD),
                    Reaction(2, 30.82, reaction=Reactions.ELECTROSWIRL),
                    Normal(0, 32.45, 3),
                    Reaction(2, 32.77, reaction=Reactions.OVERLOAD),
                    Reaction(2, 32.77, reaction=Reactions.ELECTROSWIRL),
                    Swap(2, 34.15),
                    Reaction(2, 34.72, reaction=Reactions.OVERLOAD),
                    Reaction(2, 34.72, reaction=Reactions.ELECTROSWIRL),
                    Skill(2, 34.82, infusion=Element.PYRO),
                    Reaction(2, 35.87, reaction=Reactions.PYROSWIRL),
                    Swap(0, 35.87)],
           "length": 36}

Sukokomon = {"list" : [Swap(2, 0),
                       Charged(2, 0),
                       Skill(2, 0),
                       Swap(1, 0.55),
                       Skill(1, 0.65),
                       Reaction(1, 1.15, reaction=Reactions.EC),
                       Swap(3, 1.683),
                       Skill(3, 1.75),
                       Reaction(2, 2.15, reaction=Reactions.EC),
                       #Normal(2, 2.283, 1), i dont think this should be here
                       Swap(0, 2.817),
                       Normal(0, 2.917, 1),
                       Reaction(0, 3.15, Reactions.ELECTROSWIRL),
                       Reaction(0, 3.2, Reactions.EC),
                       Skill(0, 3.15),
                       Reaction(3, 3.85, Reactions.OVERLOAD),  #batchest
                       Reaction(0, 3.85, Reactions.ELECTROSWIRL),
                       Reaction(0, 3.85, Reactions.ELECTROSWIRL),
                       Reaction(0, 3.85, Reactions.HYDROSWIRL),
                       Reaction(0, 3.85, Reactions.PYROSWIRL, bs=True),
                       Reaction(0, 3.85, Reactions.OVERLOAD),
                       Reaction(1, 3.9, Reactions.EC),
                       Normal(0, 4, 2),
                       Reaction(0, 4.68, Reactions.EC), # check the timing on this
                       Reaction(0, 4.68, Reactions.ELECTROSWIRL),
                       Skill(0, 4.68),
                       Reaction(1, 5.38, Reactions.EC),
                       Reaction(0, 5.38, Reactions.ELECTROSWIRL),
                       Reaction(0, 5.38, Reactions.ELECTROSWIRL),
                       Reaction(0, 5.38, Reactions.HYDROSWIRL),
                       Reaction(0, 5.38, Reactions.PYROSWIRL, bs=True),
                       Reaction(0, 5.38, Reactions.OVERLOAD),
                       Reaction(3, 5.5, Reactions.OVERLOAD), # idk the exact timing of this
                       Normal(0, 5.72, 1),
                       Reaction(0, 6.15, Reactions.HYDROSWIRL),
                       Swap(3, 6.13,),
                       Burst(3, 6.28),
                       Reaction(3, 6.67, Reactions.OVERLOAD),
                       Reaction(0, 7.17, Reactions.EC),
                       Reaction(3, 7.43, Reactions.OVERLOAD),
                       Swap(1, 7.73),
                       Burst(1, 7.86), # the exact ordering of stuff here is confusing as hell and not quite right but
                       # it should be good enough
                       Reaction(3, 8.63, Reactions.OVERLOAD),
                       Reaction(3, 9.83, Reactions.OVERLOAD),
                       Normal(1, 9.21, 2, charged=True),
                       Reaction(1, 10.4, Reactions.EC),
                       Normal(1, 11.5, 2), # TODO: huh
                       Normal(1, 11.5, 2, charged=True),
                       Reaction(1, 10.4, Reactions.EC),
                       Reaction(3, 11.03, Reactions.OVERLOAD),
                       Reaction(3, 12.23, Reactions.OVERLOAD),
                       Reaction(3, 13.43, Reactions.OVERLOAD),
                       Reaction(3, 14.63, Reactions.OVERLOAD),
                       Swap(2, 12.85),
                       Charged(2, 12.9),
                       Burst(2, 12.95),
                       Swap(3, 13.967),
                       Skill(3, 14.067),
                       Reaction(1, 14.5, Reactions.EC),
                       Swap(0, 15.133),
                       Normal(0, 15.2, 1),
                       Reaction(0, 15.3, Reactions.ELECTROSWIRL),
                       Reaction(3, 15.83, Reactions.OVERLOAD),
                       Reaction(3, 16.2, Reactions.OVERLOAD),
                       Skill(0, 15.533),
                       Reaction(0, 16.333, Reactions.ELECTROSWIRL),
                       Reaction(0, 16.333, Reactions.ELECTROSWIRL),
                       Reaction(0, 16.333, Reactions.HYDROSWIRL),
                       Reaction(0, 16.333, Reactions.PYROSWIRL),
                       Reaction(0, 16.333, Reactions.OVERLOAD),
                       Normal(0, 16.5, 1),
                       Burst(0, 16.983, infusion=Element.HYDRO),
                       Reaction(3, 17.03, Reactions.OVERLOAD),
                       Reaction(0, 17.317, Reactions.EC),
                       Normal(0, 17.8, 3),
                       Reaction(0, 18.167, Reactions.HYDROSWIRL),
                       Reaction(1, 18.167, Reactions.EC),
                       Reaction(3, 18.23, Reactions.OVERLOAD),
                       Reaction(3, 19.5, Reactions.OVERLOAD),
                       Reaction(0, 19.2, Reactions.EC),
                       Reaction(0, 19.2, Reactions.ELECTROSWIRL),
                       Reaction(0, 19.2, Reactions.ELECTROSWIRL),
                       Reaction(0, 19.2, Reactions.HYDROSWIRL),
                       Reaction(3, 19.43, Reactions.OVERLOAD),
                       Normal(0, 20, 3),
                       Reaction(0, 20.4, Reactions.ELECTROSWIRL),
                       Reaction(0, 20.4, Reactions.HYDROSWIRL),
                       Reaction(0, 20.4, Reactions.EC),
                       Reaction(3, 21.1, Reactions.OVERLOAD),
                       Reaction(0, 21.117, Reactions.ELECTROSWIRL),
                       Reaction(0, 21.117, Reactions.ELECTROSWIRL),
                       Normal(0, 21.35, 3),
                       Reaction(0, 21.85, Reactions.HYDROSWIRL),
                       Reaction(0, 21.7, Reactions.EC),
                       Reaction(0, 23.2, Reactions.ELECTROSWIRL),
                       Reaction(0, 23.2, Reactions.ELECTROSWIRL),
                       Reaction(0, 23.2, Reactions.HYDROSWIRL),
                       Reaction(0, 23.2, Reactions.EC),
                       Normal(0, 22.7, 3),
                       Reaction(0, 23.7, Reactions.ELECTROSWIRL),
                       Reaction(0, 23.7, Reactions.EC),
                       Reaction(0, 24.2, Reactions.ELECTROSWIRL),
                       Reaction(0, 24.2, Reactions.ELECTROSWIRL),
                       Reaction(0, 24.2, Reactions.EC),
                       Normal(0, 24.05),
                       Reaction(0, 24.7, Reactions.ELECTROSWIRL),
                       Reaction(0, 24.7, Reactions.EC),
                       ],
             "length": 25}



aggravateFish = {"list": [
    Skill(0, 0),
    Swap(1, 0.7),
    Burst(1, 0.97),
    SetAura(1, 2.5, aura=Aura.QUICKEN),
    Swap(2, 2.02),
    Burst(2, 2.32, infusion=Element.ELECTRO),
    Swap(3, 3.9),
    Charged(3, 3.95),
    Burst(3, 4.18),
    Swap(0, 5),
    Burst(0, 5.4),
    Normal(0, 7.28, 3),
    Normal(0, 9.43, 3),
    Normal(0, 11.58, 3),
    Normal(0, 13.73, 1),
    Swap(2, 15.8),
    Skill(2, 16.2, infusion=Element.ELECTRO),
    Swap(3, 17.8),
    Charged(3, 18),
    Skill(3, 18.3),
    Swap(0, 19),
    Skill(0, 19.27),
    Swap(1, 19.97),
    Burst(1, 20.24),
    Swap(2, 21.3),
    Burst(2, 21.6, infusion=Element.ELECTRO),
    Swap(3, 23),
    Charged(3, 23.43),
    Burst(3, 23.45),
    Swap(0, 24.27),
    Burst(0, 24.67),
    Normal(0, 26.55, 3),
    Normal(0, 28.7, 3),
    Normal(0, 30.85, 3),
    Normal(0, 33, 1),
    Swap(2, 35.07),
    Skill(2, 35.47, infusion=Element.ELECTRO),
], "length": 36}

Test = {"list": [
    Skill(0, 0),
    Swap(1, 0.7),
    SetAura(0, 0.9, aura=Aura.ELECTRO),
    Burst(2, 0.95, infusion=Element.ELECTRO),
    Swap(1, 2.13),
    Skill(1, 2.32),
    Burst(1, 3.32),
    Swap(3, 4.18),
    Normal(3, 4.5, 1),
    Burst(3, 4.83),
    Reaction(3, 5.4, reaction=Reactions.OVERLOAD),
    Swap(2, 5.467),
    Burst(2, 5.517, infusion=Element.PYRO),
    Reaction(2, 6.9, reaction=Reactions.OVERLOAD),
    Swap(0, 7),
    Burst(0, 7.167),
    Normal(0, 9.05, 3),
    Normal(0, 11.2, 3),
    Normal(0, 13.35, 3),
    Normal(0, 15.5, 1),
    Swap(3, 17.8),
    Skill(3, 17.95),
    Normal(3, 18.5, 1),
    Swap(2, 18.98),
    Skill(2, 19.1, infusion=Element.ELECTRO),
    Normal(2, 20.6, 1),
    Swap(0, 20.9),
    Skill(0, 21),
    Normal(0, 21.5, charged=False),
    Swap(1, 22),
    Skill(1, 22.23),
    Burst(1, 22.6),
    Swap(2, 23.58),
    Burst(2, 23.73, infusion=Element.PYRO),
    Reaction(2, 25.26, reaction=Reactions.OVERLOAD),
    Swap(3, 25.4),
    Normal(3, 25.5, 1),
    Burst(3, 25.8),
    Swap(0, 26.517),
    Burst(0, 26.7),
    Normal(0, 28.58, 3),
    Normal(0, 30.73, 3),
    Normal(0, 32.88, 3),
    Normal(0, 35.03, 1),
    Swap(2, 37.41),
    Skill(2, 37.5, infusion=Element.ELECTRO)

], "length": 39}
"""Swap(3, 17.8),
Charged(3, 18),
Skill(3, 18.3),
Swap(0, 19),
Skill(0, 19.27),
Burst(2, 19.5  , infusion=Element.PYRO),
Swap(1, 19.97),
Burst(1, 20.24),
Swap(2, 21.3),
Swap(3, 23),
Charged(3, 23.43),
Burst(3, 23.45),
Swap(0, 24.27),
Burst(0, 24.67),
Normal(0, 26.55, 3),
Normal(0, 28.7, 3),
Normal(0, 30.85, 3),
Normal(0, 33, 1),
Swap(2, 35.07),
Skill(2, 35.47, infusion=Element.PYRO),"""

# i know this particular rotation sucks but its good enough to get a weapon comparison which is all i want rn
# taser doesn't have a strict rot anyway :upside_down:
Taser = {"list":
             [Normal(1, 0),
              Burst(1, 0.75),
              SetAura(0, 0.8, Aura.ELECTRO),
              Swap(2, 1.5),
              Skill(2, 1.85),
              SetAura(0, 1.9, Aura.EC),
              Burst(2, 2.9),
              Normal(2, 3.5, 1),
              Swap(0, 4.3),
              Skill(0, 4.5, stacks=2),
              Normal(0, 5.4, 1),
              Burst(0, 5.7),
              Normal(0, 7.2),
              Swap(3, 7.42),
              Normal(3, 7.6,  1),
              Burst(3, 8.05, infusion=Element.HYDRO),
              Normal(3, 9.567, 2),
              Skill(3, 10.15),
              Normal(3, 11.367, 2),
              Normal(3, 12.633, 2),
              Skill(3, 13.3),
              Swap(1, 14.617),
              Normal(1, 14.983, 1),
              Skill(1, 15.417),
              Swap(0, 16.35),
              Skill(0, 16.55, stacks=2),
              Normal(0, 17.55, 2),
              Swap(3, 18.917),
              Normal(3, 19.083, 2),
              Normal(3, 20.183, 2)
              ],
         "length": 21.3}