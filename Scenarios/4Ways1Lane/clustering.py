from sklearn import manifold
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# performs some explorative analysis + plots starting from a plot of the events' corrdinates
# the clustering has been performed via t-sne 2-3d and K means post 2d PCA. 


df = pd.read_csv('data.csv')
print(df)

# COORDINATES SCATTERPLOT ###############################################################

plt.figure()
plt.title('Coordinates (meters), coded by closest')
plt.grid()
plt.scatter(df['x'], df['y'], c=df['closest'])
plt.colorbar()

plt.figure()
plt.title('Coordinates (meters), coded by speed')
plt.grid()
plt.scatter(df['x'], df['y'], c=df['speed'])
plt.colorbar()
plt.show()

# SPEED DISTRIBUTION ####################################################################

fig, (ax1, ax2) = plt.subplots(1,2)
fig.suptitle('Distributions')
ax1.hist(df['speed'])
ax1.set_title('speed distribution at breaking time')
ax2.hist(df['closest'])
ax2.set_title('distribution of closest vehicles')
ax1.grid()
ax2.grid()
fig.show()

# T-SNE DECOMPOSITION ###################################################################

scaler = StandardScaler()
X = scaler.fit_transform(df.drop(columns=['time', 'lane']).values)

tsne = manifold.TSNE(n_components=2, random_state=0)
transformed_data_2D = tsne.fit_transform(X)

tsne3D = manifold.TSNE(n_components=3, random_state=0)
transformed_data_3D = tsne3D.fit_transform(X)


fig = plt.figure()
ax = fig.add_subplot(projection='3d')
plt.title('T-SNE 3D projected Manifold, closest colorcoded')
plt.grid()
p = ax.scatter3D(transformed_data_3D[:,0], transformed_data_3D[:,1], transformed_data_3D[:,2], c=df['closest'])
fig.colorbar(p)
plt.show()

plt.figure()
plt.title('T-SNE 2D projected Manifold, speed colorcoded')
plt.grid()
plt.scatter(transformed_data_2D[:,0], transformed_data_2D[:,1], c=df['speed'])
plt.colorbar()
plt.show()

#  TRYING PCA + KMEANS #################################################################
reduced_data = PCA(n_components=2).fit_transform(X)
kmeans = KMeans(init="k-means++", n_clusters=4, n_init=4)
kmeans.fit(reduced_data)

# Step size of the mesh. Decrease to increase the quality of the VQ.
h = 0.2  # point in the mesh [x_min, x_max]x[y_min, y_max].

# Plot the decision boundary. For that, we will assign a color to each
x_min, x_max = reduced_data[:, 0].min() - 1, reduced_data[:, 0].max() + 1
y_min, y_max = reduced_data[:, 1].min() - 1, reduced_data[:, 1].max() + 1
xx, yy = np.meshgrid(np.arange(x_min, x_max, h), np.arange(y_min, y_max, h))

# Obtain labels for each point in mesh. Use last trained model.
Z = kmeans.predict(np.c_[xx.ravel(), yy.ravel()])

# Put the result into a color plot
Z = Z.reshape(xx.shape)
plt.figure(1)
plt.clf()
plt.imshow(
    Z,
    interpolation="nearest",
    extent=(xx.min(), xx.max(), yy.min(), yy.max()),
    cmap=plt.cm.Paired,
    aspect="auto",
    origin="lower",
)

plt.plot(reduced_data[:, 0], reduced_data[:, 1], "k.", markersize=2)
# Plot the centroids as a white X
centroids = kmeans.cluster_centers_
plt.scatter(
    centroids[:, 0],
    centroids[:, 1],
    marker="x",
    s=169,
    linewidths=3,
    color="w",
    zorder=10,
)
plt.title(
    "K-means clustering on the dataset (PCA-reduced data)\n"
    "Centroids are marked with white cross"
)
plt.xlim(x_min, x_max)
plt.ylim(y_min, y_max)
plt.xticks(())
plt.yticks(())
plt.show()