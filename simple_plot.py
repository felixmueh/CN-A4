#!/usr/bin/env python3

import matplotlib.pyplot as plt
import numpy as np

import sys

filename = sys.argv[1]

data = np.genfromtxt(filename)

plt.plot(data)
plt.show()
