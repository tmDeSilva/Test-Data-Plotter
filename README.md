# READ ME
## Description
This repository contains the python files needed to run the simple PyQt5 GUI for plotting test data (.csv format) and a brief overview of what to download, how to use the GUI and how it works.

### Downloading a virtual environment and setting up the files
* PyQt5 can only be installed or earlier versions of python (3.5 to 3.8) so a virtual environment has to be created if you've got a higher version of python downloaded already
* For windows the commands are:	
	- `cd same/folder/as/program/files`
	- `python -m venv venv`
	- `venv\Scripts\ativate`
	- `pip install PyQt5`
	- `pip install matplotlib`
* Make sure the venv and the other two python files are all in the same folder

### How to use the GUI
* First click the *change directory* button and select a path to be the root of the file (tree) structure
	* By default this is set to the hard drive's path
* Navigate through the file explorer window in the GUI and select the .csv files you want to process (you can choose multiple at once)
* To the right of the file exlporer window is the list of parameters
	* This will only appear if you've selected a .csv file
* Choose the unit of the parameters you want using the drop-down menus next to each parameter
	* All parameters with the same unit will share the same axis
	* By choosing the unit of a certain parameter and then shift clicking (upwards) everything highlighted will get the same unit as the first item selected
		* This is mainly useful for `BmsCellVolt_{n}` scenarios
* Once the parameters you want to plot have been selected, the *PLOT* button will be enabled, allowing data to be plotted
* Use the time start/end sliders to zoom in on a certain section of the data
* After data has been plotted, it can be exported as a .png or .jpeg
	* Control the size of this image with the width and height sliders
* Press *esc* to unselect .csv files and parameters or use the refresh button to unselect everything and clear the chart

### Code explanation

* Class: `plotCsv`
	- `__init__`
		* Set up the buttons, sliders, dialogue box and canvas for the graph
	- `open_directory_dialog`
		* When the "choose directory" button is pressed a window will pop up allowing the user to select the root directory of the file structure
	- `keyPressEvent`
		* Clears the .csv file selection and clears the parameter widget entirely when the  *esc* key is pressed
	- `on_tree_view_clicked`
		* Allows the user to navigate from there chosen root directory to a .csv file
	- `load_keys`
		* When a .csv file has been selected load all the keys to the parameters window 
	- `on_item_selection_change`
		 * Allows you to select multiple parameters with a shift click
		 * Only enables the *PLOT* button when a parameter to graph has been chosen
	- `select_range`
		* Responsible for iterating through the items to multiselect
	- `plot_selected_keys`
		* Checks if a .csv file and a parameter has been selected
		* Creates a list of all the parameters chosen and each of the chosen parameters' type (unit)
	- `process_csv_files`
		* Uses the functions from the `csvProccesor.py` file to create a dictionary of all the data based on the .csv file
		* Sets up the `time` list
		* Calls the `plot_data` method
	- `plot_data`
		* Plots the data based on the time start/end sliders
		* Groups parameters into axes based on their type
		* Reads the title entered by the user and displays it
		* Creates a legend of all the parameters and their corresponding graph colours
	- `update_plot_range`
		* If the start/end time sliders are changed edit the plot to create a smooth transition
	- `update_plot_title`
		* Call on the `plot_data` method when the title has been changed
	- `export_graph`
		* Creates and plots a new graph on a new invisible canvas so a .png or .jpeg can be downloaded to any location
	- `refresh_keys`
		* Refreshes all the class variables, clears the graph and unselects all the files and parameters
* Class: `KeyItemWidget`
	- `__init__`
		* Sets up all the drop-down menus so the user can select the parameter that each parameter corresponds to
	

