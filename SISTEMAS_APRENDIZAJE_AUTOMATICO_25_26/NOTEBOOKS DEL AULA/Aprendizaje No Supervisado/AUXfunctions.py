from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from yellowbrick.cluster import SilhouetteVisualizer
import matplotlib.pyplot as plt
import numpy as np

def silhouette(data, max_clusters=10):
    """
    Función para seleccionar el número óptimo de clusters utilizando el coeficiente de Silhouette.
    """
    silhouette_scores = []
    for k in range(2, max_clusters + 1):
        kmeans = KMeans(n_clusters=k, n_init=10)
        labels = kmeans.fit_predict(data)
        silhouette_avg = silhouette_score(data, labels)
        silhouette_scores.append(silhouette_avg)
    best_k = 2 + silhouette_scores.index(max(silhouette_scores))
    return best_k

def silhouette_plot(X, max_k=10):
    """
    Genera un gráfico de silhouette para diferentes valores de k.
    """
    
    plt.rcParams['font.family'] = 'DejaVu Sans'  # Fuente de los gráficos de matplotlib forzada a DejaVu Sans para evitar problemas 
    n_plots = max_k - 2 + 1  # Cantidad de gráficos necesarios
    rows = int(np.ceil(n_plots / 2))  # Número de filas necesarias
    cols = min(n_plots, 2)  # Máximo 2 columnas

    fig, ax = plt.subplots(rows, cols, figsize=(15, 5 * rows))

    # Si solo hay una fila, ax no es un array de arrays
    if rows == 1:
        ax = np.array([ax])  

    for i, k in enumerate(range(2, max_k+1)):  
        km = KMeans(n_clusters=k, init='k-means++', n_init=10, max_iter=100, random_state=42)
        q, mod = divmod(i, 2)
        visualizer = SilhouetteVisualizer(km, colors='yellowbrick', ax=ax[q][mod])
        
        km.fit_predict(X)
        score = silhouette_score(X, km.labels_, metric='euclidean')
        
        ax[q][mod].set_title(f'Silhouette plot para k = {k}, Score = {score:.2f}')
        visualizer.fit(X)
    
    plt.show()

def plot_silhouette(X, range_n_clusters):
    """
    Función para generar un gráfico de Silhouette para diferentes valores de k.
    """

    import matplotlib.cm as cm
    import matplotlib.pyplot as plt
    import numpy as np

    from sklearn.cluster import KMeans
    from sklearn.datasets import make_blobs
    from sklearn.metrics import silhouette_samples, silhouette_score

    for n_clusters in range(2,range_n_clusters+1):

        # Creamos subplot con 1 fila y 2 columnas
        fig, (ax1, ax2) = plt.subplots(1, 2)
        fig.set_size_inches(18, 7)


        # El primer subplot es el gráfico de silhouette
        # El coeficiente silhouette puede variar desde -1, 1
        ax1.set_xlim([-1, 1])
        
        # Los (n_clusters+1)*10 son para insertar espacio en blanco entre los 
        # coeficientes silhouette de las diferentes instancias
        # graficando individualmente los clusters, para demarcarlos claramente.
        
        ax1.set_ylim([0, len(X) + (n_clusters + 1) * 10])

        # Inicializamos el clusterer con el valor de n_clusters y una semilla
        # de generador aleatorio de 10 para reproducibilidad.
        
        clusterer = KMeans(n_clusters=n_clusters, random_state=10)
        cluster_labels = clusterer.fit_predict(X)


        # El valor silhouette_score es el promedio de todos los valores silhouette
        # y nos da una perspectiva de la densidad y separación de los clústers formados.
        silhouette_avg = silhouette_score(X, cluster_labels)
        print(
            "Para n_clusters =",
            n_clusters,
            "La media de silhouette_score is :",
            silhouette_avg,
        )


        # Calculamos el coeficiente silhouette de cada muestra
        
        sample_silhouette_values = silhouette_samples(X, cluster_labels)

        y_lower = 10
        for i in range(n_clusters):

            # Agregamos los coeficientes silhouette para las muestras 
            # que pertenecen al clúster i y los ordenamos
            ith_cluster_silhouette_values = sample_silhouette_values[cluster_labels == i]

            ith_cluster_silhouette_values.sort()

            size_cluster_i = ith_cluster_silhouette_values.shape[0]
            y_upper = y_lower + size_cluster_i

            color = cm.nipy_spectral(float(i) / n_clusters)
            ax1.fill_betweenx(
                np.arange(y_lower, y_upper),
                0,
                ith_cluster_silhouette_values,
                facecolor=color,
                edgecolor=color,
                alpha=0.7,
            )


            # Etiquetamos los gráficos silhouette con los números de los clústers en el medio
            
            ax1.text(-0.05, y_lower + 0.5 * size_cluster_i, str(i))

          
            # Calculamos el nuevo y_lower para el siguiente gráfico
            y_lower = y_upper + 10  # 10 para los espacios en blanco

        ax1.set_title("Gráfica silhouette para varios clusters.")
        ax1.set_xlabel("Valores para los coeficientes silhouette")
        ax1.set_ylabel("Etiqueta del clúster")

       
        # La línea vertical para el valor promedio de silhouette_score de todos los valores
        ax1.axvline(x=silhouette_avg, color="red", linestyle="--")

        ax1.set_yticks([])  # Limpiamos los ticks del eje Y
        ax1.set_xticks([-1, -0.8, -0.6, -0.4, -0.2, 0, 0.2, 0.4, 0.6, 0.8, 1])

        
        # 2do. gráfico que muestra los clústers reales formados
        colors = cm.nipy_spectral(cluster_labels.astype(float) / n_clusters)
        ax2.scatter(
            X[:, 0], X[:, 1], marker=".", s=30, lw=0, alpha=0.7, c=colors, edgecolor="k"
        )


        # Etiquetamos los clústers
        centers = clusterer.cluster_centers_
        

        # Dibujamos círculos blancos en los centros de los clústers
        ax2.scatter(
            centers[:, 0],
            centers[:, 1],
            marker="o",
            c="white",
            alpha=1,
            s=200, 
            edgecolor="k",
        )

        for i, c in enumerate(centers):
            ax2.scatter(c[0], c[1], marker="$%d$" % i, alpha=1, s=50, edgecolor="k")

        ax2.set_title("Distribución de clústers")
        ax2.set_xlabel("1ra. característica")
        ax2.set_ylabel("2da. característica")

        plt.suptitle(
            "Análisis de Silhouette para KMeans con n_clusters = %d"
            % n_clusters,
            fontsize=14,
            fontweight="bold",
        )

    plt.show()