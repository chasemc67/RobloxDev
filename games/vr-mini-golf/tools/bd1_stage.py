"""Stage bd1 (SC H1 cactus + H10 chevrons v2, LG H5 disc): fx1_stage commands writing to playtests/stage-bd1.
  BD1_ROLE=sugarloaf_canyon|lantern_grove  PYTHONPATH=tools python3 tools/bd1_stage.py <fx1_stage command> ...
Bases: SC v109 / LG v32 (fx1 final inventories).
"""
import os, sys
os.environ['FX1_ROLE'] = os.environ.get('BD1_ROLE', 'sugarloaf_canyon')
import fx1_stage
fx1_stage.ROLES['sugarloaf_canyon'].update(version=109, base='playtests/stage-fx1/sugarloaf_canyon-inventory-final.json')
fx1_stage.ROLES['lantern_grove'].update(version=32, base='playtests/stage-fx1/lantern_grove-inventory-final.json')
fx1_stage.OUT = fx1_stage.GAME / 'playtests/stage-bd1'

if __name__ == '__main__':
    fx1_stage.main()
