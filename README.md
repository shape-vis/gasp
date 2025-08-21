# GASP: A Gradient-Aware Shortest Path Algorithm for Boundary-Confined of 2-Manifold Reeb Graph Visualization


## Description
This project generates Reeb graphs for 3D models using axis aligned height and geodesic distance functions computed from the most spatially extreme point functions, offering two approaches: Boundary and Interior.

## Installation

To get started, ensure you have Python installed on your local machine. This project also requires several additional Python libraries listed in the 'requirements.txt' file.

1. Install Python if you haven't already.
2. Navigate to the project directory
3. On Linux/Mac, running `./run.sh` will setup a virtual envirnoment, install, and run the everything. After installing the libraries, it will take 20-30 minutes to generate all Reeb graphs at the current set up. On windows or manually, run `pip install -r requirements.txt` to install the required libraries.



## Usage

After setting up the environment and required libraries, execute the `python generate_all.py` script to start generating Reeb graphs. The script is preconfigured to generate all the Reeb graph variants presented in the paper and appendix, with options for parameter tuning.

### Parameter Descriptions in generate_all.py:

1. __contour_spaces__: Defines the spacing between contours, with a default of 0.05. Our tested contours are 0.025, 0.05 and 0.1, affecting the number of contours between critical points to observe its effect on the quality of the produced Reeb graphs.

2. __contour_type__: This variable is a list of tuples. The first element of the tuple chooses the algorithm variant, with 'interior' for the Interior approach and 'boundary' for the Boundary approach. The second element of the tuple selects the buffer size for the interior approach which determines the distance candidate points should from a contour's boundary. Tested values are 0.00 (no buffer), 0.025, 0.05 (default). This parameter impacts how candidate points are selected from each contour. If the buffer is too large, the algorithm defaults to selecting the midpoint inside the contour. This parameter is ignored for the Boundary approach with a 'None' value, which always selects points on the contour's boundary.

3. __function_type__: This variable is also a list of two-element tuples. The first element determines which type of scalar function is used: 'Height' or 'Geodesic.' The second element of the tuples is the direction of the functions. For the height function, we utilized all three principle directions: x, y, and z. For the geodesic function, we have used 'top,' 'bottom,' 'left,' 'right,' 'front,' and 'back' directions. 

## Output

Successful execution of generate_all.py will generate Reeb graphs in the 'Output' directory. To generate Reeb Graphs for all models, this program may take 20-30 minutes. You can reduce some models, to finish the program quickly. Respective model and the function for a Reeb graph with the similar name (in .vtk format) can be found in either 'Data/Height' or 'Data/Geodesic' directory.

