import cProfile
import re
import pstats

cProfile.run('daq_continous_2MPA.py', 'restats')
p = pstats.Stats('restats')
p.strip_dirs().sort_stats(-1).print_stats()
