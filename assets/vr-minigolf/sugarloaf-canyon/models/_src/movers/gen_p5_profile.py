"""Pure-python H14 skid profile (shared by gen_pass5 in Blender and fitcheck_pass5 outside it)."""
SKID_END_RAISE=.03
def skid_profile(foot):
    """Underside vertices (x,y) at every strip boundary: interior boundary = the HIGHER of the two adjacent strip
    bottoms, ends = outer strip bottom + .03. Every skid point therefore lies inside a strip column at or above
    that strip's bottom, i.e. the skid is never lower than the collider at any swing angle."""
    fs=sorted(foot,key=lambda b:b['center'][0])
    bot=[b['center'][1]-b['size'][1]/2 for b in fs];xs=[b['center'][0]-b['size'][0]/2 for b in fs]+[fs[-1]['center'][0]+fs[-1]['size'][0]/2]
    ys=[bot[0]+SKID_END_RAISE]+[max(bot[i],bot[i+1]) for i in range(len(fs)-1)]+[bot[-1]+SKID_END_RAISE]
    return list(zip(xs,ys))
def underside(prof,x):
    for (x0,y0),(x1,y1) in zip(prof,prof[1:]):
        if x0<=x<=x1:return y0+(y1-y0)*(x-x0)/(x1-x0)
    raise ValueError(x)
