from multiprocessing import Pool

import main

lower_bounds = list(range(0, 10000000, 625000))
upper_bounds = list(range(625000, 10000001, 625000))
bounds = list(zip(lower_bounds, upper_bounds))

if __name__ == '__main__':
    p = Pool(16)
    p.map(main.download_data(), bounds)
