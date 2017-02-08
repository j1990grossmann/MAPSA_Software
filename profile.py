import cProfile
import re
import pstats
import daq_continous_2MPA

cProfile.run('daq_continous_2MPA.start_daq(2,100)', 'restats')
p = pstats.Stats('restats')
p.strip_dirs().sort_stats("cum").print_stats()

