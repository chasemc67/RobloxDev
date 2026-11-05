import fitcheck_pass2 as F
F.CUTS[('h06_sluice_gate','rock18')]=F.CUTS[('h06_sluice_gate','rail5')]
for n in ('rail5','rail7','felt_approach'):
 F.CUTS[('h11_lock_gate',n)]=F.CUTS[('h11_lock_gate','rail4')]
for n in ('rail4','rail5','rail7','rail8','felt_approach'):
 F.CUTS[('h11_lock_lift',n)]=F.CUTS[('h11_lock_lift','felt_lock')]
if __name__=='__main__':F.main(proposed=True)
