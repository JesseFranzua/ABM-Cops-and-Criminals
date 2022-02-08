import numpy as np
from scipy import stats
import matplotlib.pyplot as plt


def zipf(height):
    """
    Returns y values following zipf's law given a starting height and x values between 0 and 6.
    """
    x = np.linspace(1, 7, 1000)
    y = height / x
    y = np.flip(y)
    x = np.linspace(0, 6, 1000)
    return x, y

# average crimes eyeballed from default run
avg_per_district =[1.8, 2.4, 2.5, 3, 3.8, 4.5, 6.1]
x_avg = np.linspace(0, 1, len(avg_per_district))

# values follwoing zipf law with same max
zipf_list = zipf(max(avg_per_district))[1]
x_zipf = np.linspace(0, 1, len(zipf_list))

# visual comparison of cdf's
plt.plot(x_avg, np.cumsum(avg_per_district) / sum(avg_per_district), label='districts')
plt.plot(x_zipf, np.cumsum(zipf_list) / sum(zipf_list), label='zipf')
plt.legend()
plt.show()

# statistical test
test = stats.kstest(avg_per_district, zipf_list) 
print(test)
# if p-value is low, reject null-hypothesis that they are identical
#test