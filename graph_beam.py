import matplotlib.pyplot as plt
import numpy as np


beam_sizes = [1, 3, 4, 5, 6, 9, 11, 12, 15, 25]
blue_scores = [13.8, 15.2, 15.2, 13.3, 13.2, 12.6, 12.3, 10.3, 11.0, 8.7 ]

# create a basic plot
plt.plot(beam_sizes, blue_scores)

# give titles to each axis
plt.xlabel('beam size')
plt.ylabel('blue score')

# give a title to the plot
plt.title("IMPACT OF BEAM SIZE ON TRANSLATION QUALITY")

plt.show()
plt.savefig('foo.png', bbox_inches='tight')


# create a bar plot
plt.bar(beam_sizes, blue_scores)

plt.xticks(np.arange(0, 26))

# give titles to each axis
plt.xlabel("beam size" )
plt.ylabel('blue score')

# give a title to the plot
plt.title("IMPACT OF BEAM SIZE ON TRANSLATION QUALITY")

plt.show()
plt.savefig('beam_size_plots.png',bbox_inches='tight' )

