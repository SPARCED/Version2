# YAML Protocol File Structure

## Global Experimental Settings

### Paths, files, directories
  - ```name``` _(string)_: Name of the protocol
  - ```model``` _(Path or string)_: Path to model folder
  - ```output_directory``` _(Path or string)_:  Folder where to store the outputs
  - ```sbml```_(list of string)_: list of input SBML files

The SBML file's full paths are reconstructed by the following: ```model``` / ```sbml```.

The output folder is the following: ```model```/```output_directory```.

Within the output folder, output files names will start by the prefix ```name```.

### Experimental settings
  - ```nb_cells``` _(int)_: Number of cells on which the protocol is ran
  - ```solver``` _(string)_: Name of the ODE solver that should be used

The worker assigns cells to itself based on ```nb_cells```, and sets the ```solver``` accordingly.

## Protocol Steps

### Protocol
  - ```protocol```: Beginning of the protocol list of steps

### Steps
  - ```step```_(int)_: The step's number within the protocol
  - ```name``` _(string)_: Human-readable name -- no incidence, just for help
  - ```duration```_(int)_: Step duration (in seconds)
  - ```exchange``` _(int)_: Exchange time / step time (in seconds)
  - ```input``` _(dictionnary)_: See bellow
  - ```modifications``` _(dictionnary)_: See bellow
  - ```simulation_mode``` _(string)_: Simulation mode (select between ```deterministic```, ```stochastic```, and ```lineage```)

### Input
  - ```name``` _(string)_: Input data file prefix, if different from current protocol
  - ```origin``` _(int)_: Step number of the input data
  - ```timepoint``` _(string)_: Mode of data retrieval (select between ```first```, ```last```, or ```random```)

The input file name's prefix is either the current protocol's name or ```name``` if specified, followed by ```origin``` (which corresponds to a step number) and then the cell number.

The input data is retrieved according to the method specified by ```timepoint```.

### Modifications

Modifications can affect one of the following: ```compartments```, ```parameters```, ```ratelaws```, or ```species```. The modifications are loaded as key-value pairs _after_ input data is loaded.

