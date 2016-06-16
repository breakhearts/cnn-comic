from scipy import fft
import numpy as np


def pmf2cf(pmf, k):
    '''convert probability mass point to characteristic function
    
    checked only for positive k so far
    use pmf function instead of pmf array
    
    Parameters
    ----------
    pmf : array
        probabiltiy mass function
    k : array
        support points of random variable in array pmf
        required equidistant (? for fft)
        (integer, what if not integer values, e.g. 1.5?)
    
    Returns
    -------
    cf : array
        characteristic function
    w : array
        points at which characteristic function is evaluated
    
    '''
    npoints = len(k)
    w = k * 2.*np.pi/npoints  
    cf = fft.fft(pmf).conj() #no idea why I need conj to reverse sign of imag
    return cf, w