"""Stage gg3 (LG goose bonus hole renumbered 19 -> 10): fx1_stage commands for Lantern Grove, writing to playtests/stage-gg3.
  PYTHONPATH=tools python3 tools/gg3_stage.py <fx1_stage command> ...
Base: LG v36 (bd1 final inventory) for the 9 round holes; gg2's v51 final inventory for the goose (tools/gg3_rename_diff.py).
"""
import os
os.environ['FX1_ROLE'] = 'lantern_grove'
import fx1_stage
fx1_stage.ROLES['lantern_grove'].update(version=36, base='playtests/stage-bd1/lantern_grove-inventory-final.json')
fx1_stage.OUT = fx1_stage.GAME / 'playtests/stage-gg3'

if __name__ == '__main__':
    fx1_stage.main()
