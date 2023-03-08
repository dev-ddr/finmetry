# Plot1

importing the requirements


```python
import matplotlib.pyplot as plt
import numpy as np
```

Plotting example plot


```python
x = np.linspace(0,5,100)
y = 2*x**2 + 3*x + 10

img_name = 'plot1'
fig = plt.figure(num=img_name)
ax = fig.add_subplot(111)

ax.scatter(x,y)
ax.set_xlabel('x')
ax.set_ylabel('$2x^2 + 3x + 10$')
ax.set_ylim([0,100])
ax.grid()

plt.tight_layout()
plt.show()
```


    
![png](https://github.com/ddrathod121294/finmetry/blob/base/Projects/Project1/README_files/output_3_0.png?raw=true)
    


---
---
---
