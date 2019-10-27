
def computeHV(solutions, num_objectives=2, ref_point=None):
    from pygmo import hypervolume
    
    if ref_point is None:
        if num_objectives == 2:
            ref_point = [1.01, 1.01]

        elif num_objectives == 3:
            ref_point = [1.01, 1.01, 1.01]

        else:
            raise ValueError('Invalid number of objectives')

    if len(ref_point) != num_objectives:
        raise ValueError("Number of objectives and the dimension of the reference point do not match")
    
    # Get hypervolume with a reference point 
    return hypervolume(solutions).compute(ref_point)