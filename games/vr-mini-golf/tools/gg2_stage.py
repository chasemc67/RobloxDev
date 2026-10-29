"""Stage gg2 (LG hidden goose hole 19): fx1_stage commands for Lantern Grove, writing to playtests/stage-gg2.
  PYTHONPATH=tools python3 tools/gg2_stage.py <fx1_stage command> ...
Base: LG v36 (bd1 final inventory).
"""
import os
os.environ['FX1_ROLE'] = 'lantern_grove'
import fx1_stage
fx1_stage.ROLES['lantern_grove'].update(version=36, base='playtests/stage-bd1/lantern_grove-inventory-final.json')
fx1_stage.OUT = fx1_stage.GAME / 'playtests/stage-gg2'

if __name__ == '__main__':
    fx1_stage.main()
