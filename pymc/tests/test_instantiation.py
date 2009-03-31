###
# Test that decorators return the appropriate object.
# David Huard
# June 21, 2007
###

###
# TODO
# ----
# Add test for deterministic
# Check discrete and binary stochastics
# Test the distribution instantiators.
###

from numpy.testing import *
import pymc
from pymc import Sampler, data, stochastic, deterministic, \
    Stochastic,Deterministic
from numpy import array, log, sum, ones, concatenate, inf
from pymc import uniform_like, exponential_like, poisson_like
import warnings

D_array =   array([ 4, 5, 4, 0, 1, 4, 3, 4, 0, 6, 3, 3, 4, 0, 2, 6,
                    3, 3, 5, 4, 5, 3, 1, 4, 4, 1, 5, 5, 3, 4, 2, 5,
                    2, 2, 3, 4, 2, 1, 3, 2, 2, 1, 1, 1, 1, 3, 0, 0,
                    1, 0, 1, 1, 0, 0, 3, 1, 0, 3, 2, 2, 0, 1, 1, 1,
                    0, 1, 0, 1, 0, 0, 0, 2, 1, 0, 0, 0, 1, 1, 0, 2,
                    3, 3, 1, 1, 2, 1, 1, 1, 1, 2, 4, 2, 0, 0, 1, 4,
                    0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1])

# Define data and stochastics

@stochastic(dtype=int)
def s(value=50, length=110):
    """Change time for rate stochastic."""
    return uniform_like(value, 0, length)

@stochastic
def e(value=1., rate=1.):
    """Rate stochastic of poisson distribution."""
    return exponential_like(value, rate)

@stochastic
def l(value=.1, rate = 1.):
    """Rate stochastic of poisson distribution."""
    return exponential_like(value, rate)

@data(dtype=int)
def D(  value = D_array,
        s = s,
        e = e,
        l = l):
    """Annual occurences of coal mining disasters."""
    return poisson_like(value[:s],e) + poisson_like(value[s:],l)

E = data(e)

@data
def F(value = D_array*.5,
        s = s,
        e = e,
        l = l):
    """Annual occurences of coal mining disasters."""
    return poisson_like(value[:s],e) + poisson_like(value[s:],l)

@data
@stochastic
def G(value = D_array*.5,
        s = s,
        e = e,
        l = l):
    """Annual occurences of coal mining disasters."""
    return poisson_like(value[:s],e) + poisson_like(value[s:],l)

class test_instantiation(TestCase):
    def test_data(self):
        assert(isinstance(D, Stochastic))
        assert(D.observed)
        assert(isinstance(E, Stochastic))
        assert(E.observed)
        assert(isinstance(F, Stochastic))
        assert(F.observed)
        assert(isinstance(G, Stochastic))
        assert(G.observed)
    
    def test_stochastic(self):
        assert(isinstance(l, Stochastic))
        assert(not l.observed)
    
    def test_invalid_keyword(self): # Ticket 239
        # Normal is given values instead of value and should raise an error
        try:
            pymc.Normal(name='alpha', values=D_array, mu=1, tau=1)
        except TypeError:
            pass
        else:
            raise AssertionError, 'Instantiation should fail.'


class test_out_of_bound_initialization(TestCase):
    
    def test_simple(self):
        # There is a very slim chance that the lower bound will have a 
        # valid value at the instantiation time of data. 
        # This checks the mechanism in PyMCObjects that redraws values for parents in an attempt
        # to avoid failure so early. 
        warnings.simplefilter('ignore',  UserWarning)
        lower = pymc.Uniform('lower', .9, 2., value=None, rseed=True,  verbose=0)
        data = pymc.Uniform('data', lower=lower, upper=5, value=[1, 2, 3, 4],  observed=True,  verbose=0)
        warnings.simplefilter('default',  UserWarning)
        
        
if __name__ == '__main__':
    import unittest
    unittest.main()
