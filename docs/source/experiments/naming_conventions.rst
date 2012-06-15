==================
Naming Conventions
==================

Input Readers
=============

luma
----

Extracts the luminance value as follows:

.. math::
    L = \frac{299}{1000}R + \frac{587}{1000}G + \frac{114}{1000}B

sobel
-----

Extracts the luminance value like in the luma reader and applies a sobel filter.

canny
-----

Extracts the luminance value like in the luma reader and applies a canny filter.


Feature Extractors
==================

mean
----

Subdivides the curvelet response image :math:`C` for each scale :math:`s` and angle :math:`\alpha \in 1,...,a` into :math:`n \times n` grid cells :math:`G_{x,y}\text{ with }x,y \in 1,...,n` of approximately equal size:

.. math::
    C_{s,\alpha} =
    \begin{pmatrix}
        G_{s,\alpha,1,1} & G_{s,\alpha,1,2} & \cdots & G_{s,\alpha,1,n} \\
        G_{s,\alpha,2,1} & G_{s,\alpha,2,2} & \cdots & G_{s,\alpha,2,n} \\
        \vdots  & \vdots  & \ddots & \vdots  \\
        G_{s,\alpha,n,1} & G_{s,\alpha,n,2} & \cdots & G_{s,\alpha,n,n} \\
    \end{pmatrix}

It then calculates the mean :math:`\bar{C}_{s,\alpha}` and standard deviation :math:`\sigma_{s,\alpha}` in each grid cell and stores the results as the feature vector:

.. math::
    \bar{C}_{s,\alpha} =
    \begin{pmatrix}
        mean(G_{s,\alpha,1,1}) & mean(G_{s,\alpha,1,2}) & \cdots & mean(G_{s,\alpha,1,n}) \\
        mean(G_{s,\alpha,2,1}) & mean(G_{s,\alpha,2,2}) & \cdots & mean(G_{s,\alpha,2,n}) \\
        \vdots  & \vdots  & \ddots & \vdots  \\
        mean(G_{s,\alpha,n,1}) & mean(G_{s,\alpha,n,2}) & \cdots & mean(G_{s,\alpha,n,n}) \\
    \end{pmatrix}

.. math::
    \sigma_{s,\alpha} =
    \begin{pmatrix}
        \sigma(G_{s,\alpha,1,1}) & \sigma(G_{s,\alpha,1,2}) & \cdots & \sigma(G_{s,\alpha,1,n}) \\
        \sigma(G_{s,\alpha,2,1}) & \sigma(G_{s,\alpha,2,2}) & \cdots & \sigma(G_{s,\alpha,2,n}) \\
        \vdots  & \vdots  & \ddots & \vdots  \\
        \sigma(G_{s,\alpha,n,1}) & \sigma(G_{s,\alpha,n,2}) & \cdots & \sigma(G_{s,\alpha,n,n}) \\
    \end{pmatrix}

pmean
-----

Subdivides the curvelet response into grid cells and calculates the means :math:`\bar{C}_{s,\alpha}` as in `mean`_.

.. math::
    \bar{C}_{s,\alpha} =
    \begin{pmatrix}
        mean(G_{s,\alpha,1,1}) & mean(G_{s,\alpha,1,2}) & \cdots & mean(G_{s,\alpha,1,n}) \\
        mean(G_{s,\alpha,2,1}) & mean(G_{s,\alpha,2,2}) & \cdots & mean(G_{s,\alpha,2,n}) \\
        \vdots  & \vdots  & \ddots & \vdots  \\
        mean(G_{s,\alpha,n,1}) & mean(G_{s,\alpha,n,2}) & \cdots & mean(G_{s,\alpha,n,n}) \\
    \end{pmatrix} =
    \begin{pmatrix}
        \bar{c}_{s,\alpha,1,1} & \bar{c}_{s,\alpha,1,2} & \cdots & \bar{c}_{s,\alpha,1,n} \\
        \bar{c}_{s,\alpha,2,1} & \bar{c}_{s,\alpha,2,2} & \cdots & \bar{c}_{s,\alpha,2,n} \\
        \vdots  & \vdots  & \ddots & \vdots  \\
        \bar{c}_{s,\alpha,n,1} & \bar{c}_{s,\alpha,n,2} & \cdots & \bar{c}_{s,\alpha,n,n} \\
    \end{pmatrix}

It then slides a window of size :math:`m \times m, m < n` across it, producing :math:`\bar{W}_{s,\alpha,u,v}\text{ with }u,v \in 1,...,n-m+1`:

.. math::
    \bar{W}_{s,\alpha,u,v} =
    \begin{pmatrix}
        \bar{c}_{s,\alpha,u,v} & \bar{c}_{s,\alpha,u,v+1} & \cdots & \bar{c}_{s,\alpha,u,v+m} \\
        \bar{c}_{s,\alpha,u+1,v} & \bar{c}_{s,\alpha,u+1,v+1} & \cdots & \bar{c}_{s,\alpha,u+1,v+m} \\
        \vdots  & \vdots  & \ddots & \vdots  \\
        \bar{c}_{s,\alpha,u+m,v} & \bar{c}_{s,\alpha,u+m,v+1} & \cdots & \bar{c}_{s,\alpha,u+m,v+m} \\
    \end{pmatrix} =
    \begin{pmatrix}
        \bar{c}_{s,\alpha,u,v,1} \\
        \bar{c}_{s,\alpha,u,v,2} \\
        \vdots \\
        \bar{c}_{s,\alpha,u,v,m} \\
    \end{pmatrix}

and stores the stacked mean submatrices :math:`\bar{W}_{s,u,v}` as the feature vectors:

.. math::
    \bar{W}_{s,u,v} =
    \begin{pmatrix}
        \bar{c}_{s,1,u,v,1} & \bar{c}_{s,1,u,v,2} & \cdots & \bar{c}_{s,1,u,v,m} \\
        \bar{c}_{s,2,u,v,1} & \bar{c}_{s,2,u,v,2} & \cdots & \bar{c}_{s,2,u,v,m} \\
        \vdots & \vdots & \ddots & \vdots \\
        \bar{c}_{s,a,u,v,1} & \bar{c}_{s,a,u,v,2} & \cdots & \bar{c}_{s,a,u,v,m} \\
    \end{pmatrix}

pmean2
------

TBD


metrics
=======

mean_l2
-------

TBD

mean_sel_l2
-----------

TBD

hist
----

Calculates the distance :math:`d` between two images' signatures :math:`a = (a_0,a_1,...,a_N)` and :math:`b = (b_0,b_1,...,b_N)` using the histogram intersection:

.. math::
    d_{a,b} = \frac{\sum_{i=0}^N min(a_i, b_i)}{\sum_{i=0}^N b_i}

hist_stop
---------

Sets the signature components (bin counts) of the most frequent clusters to 0 so they do not impact the distance calculation. Then it performs the distance calculation as in `hist`_.

hist_weights
------------

Multiplies the signature components (bin counts) with :math:`\frac{1}{n_i^2}` where :math:`n_i` is the number of occurences of the cluster i in the training data set. Then it performs the distance calculation as in `hist`_.
