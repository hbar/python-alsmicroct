# functions for post processing datasets

import numexpr as ne # routines for the fast evaluation of array expressions elementwise by using a vector-based virtual machine
# =============================================================================

def convert8bit(rec,data_min,data_max):
    rec = rec.astype(np.float32,copy=False)
    df = np.float32(data_max-data_min)
    mn = np.float32(data_min)
    scl = ne.evaluate('0.5+255*(rec-mn)/df',truediv=True)
    ne.evaluate('where(scl<0,0,scl)',out=scl)
    ne.evaluate('where(scl>255,255,scl)',out=scl)
    return scl.astype(np.uint8)
