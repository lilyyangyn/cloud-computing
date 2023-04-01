import numpy as np
import matplotlib.pyplot as plt

x = np.linspace(-5, 5)
y = x

fig = plt.figure(figsize=(5, 10))  # Set the figure size to 5 inches by 10/2 inches
ax = fig.add_subplot(111)

ax.plot(x, y)
ax.set_xlabel('x')
ax.set_ylabel('y')
ax.set_title('y = x')

plt.subplots_adjust(left=0.2, bottom=0.2, right=0.8, top=0.8)  # Adjust the margins of the plot

plt.show()
