=====================================
Variations of the Processing Pipeline
=====================================


.. blockdiag::

    blockdiag {
        read_img [label="Read Image Data"];
        convert_grey [label="Convert to Greyscale"];
        curvelet [label="Apply Curvelet Transform"];
        subdivide [label="Divide into regular grid"]
        mean_stddev [label="Calculate Means and Stddevs"];
        rank_euclid [label="Calculate Euclidean Distance"]
        filter_sobel [label="Apply Sobel Edge Detector"]
        filter_canny [label="Apply Canny Edge Detector"]

        read_img -> convert_grey -> curvelet;
        read_img -> filter_sobel -> curvelet -> subdivide -> mean_stddev -> rank_euclid;
        read_img -> filter_canny -> curvelet -> subdivide -> mean_stddev -> rank_euclid;

        group input {
            label = "Input";

            read_img;
        }

        group preprocess {
            label = "Preprocessing"

            convert_grey;
            filter_sobel;
            filter_canny;
        }

        group feaure_extract {
            label = "Feature Extraction"

            curvelet;
            subdivide;
            mean_stddev;
        }

        group rank {
            label = "Calculate Ranking";

            rank_euclid;
        }
    }
