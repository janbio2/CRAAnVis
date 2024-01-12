[![Project Status: Active – The project has reached a stable, usable state and is being actively developed.](https://www.repostatus.org/badges/latest/active.svg)](https://www.repostatus.org/#active)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![made-with-PyQt6](https://img.shields.io/badge/Made%20with-PyQt6-2CDE85.svg)](https://www.riverbankcomputing.com/software/pyqt/intro)



# CRISPR Array Ancestry Visualization (CRAAnVis) <img src="https://github.com/janbio2/CRAAnVis/blob/release/images/icon.png" width="100px">
Visualization tool for SpacerPlacer output.

![small GUI overview](https://github.com/janbio2/CRAAnVis/blob/release/images/g_502_c_title.png)


## Contents:
1. Introduction
2. Components
3. Installation
4. Tool Usage

## 1. Introduction
CRAAnVis is a GUI tool to visualize the reconstructed ancestries of CRISPR arrays produced by SpacerPlacer.
It is written in Python and depends on PyQt6.

## 2. Components
```
CRAAnVis/
├── CRAAnVis/
│   ├── model/                        # main data structures and business logic
│   │   ├── __init__.py
│   │   ├── arrays.py                 # manage CRISPR array data model
│   │   ├── app_config.py             # tool configurations and settings
│   │   ├── file_reader.py            # reads and deserializes input data
│   │   ├── helper_functions.py       # helper functions
│   │   ├── model_container.py        # managing all combined model data
│   │   ├── newick_parser.py          # parses phylogenetic trees adapted from ete toolkit
│   │   └── tree.py                   # manage the tree data model
│   ├── view/                         # user interface and item rendering
│   │   ├── array_rendering/          # visualization related array model
│   │   │   ├── __init__.py
│   │   │   └── render_arrays.py      # "
│   │   ├── colors/                   # manage everything related to colors and highlighting
│   │   │   ├── __init__.py
│   │   │   ├── color_schemes.py      # predefined color schemes
│   │   │   ├── colors.py             # color map and highlighting management, color map creation
│   │   │   └── highlighting.py       # mixin class to provide highlighting functionality to items
│   │   ├── exporting/                # managing export functionalities
│   │   │   ├── __init__.py
│   │   │   └── exporting.py          # "
│   │   ├── legend/                   # manage the legends of the array and the tree
│   │   │   ├── __init__.py
│   │   │   └── render_legend.py      # "
│   │   ├── tree_rendering/           # visualizing the phylogenetic tree and evolutionary events
│   │   │   ├── __init__.py
│   │   │   ├── adapted_biopython_tree_layouting.py # adaptation of tree layout function from Biopython
│   │   │   ├── tree_events.py        # visualization related tree events model
│   │   │   └── tree_view_model.py    # visualization related tree model
│   │   ├── ui/                       # user interface components
│   │   │   ├── __init__.py
│   │   │   ├── main_window.ui        # UI layout file created with Qt Designer
│   │   │   └── main_window_ui.py     # main_window.ui file translated to Python
│   │   └── view.py                   # setup of application view
│   └── craanvis.py        # main tool executable and module for importing
├── example_data/          # example data for demonstrating tool functionality with mock metadata
├── images/                # images for tool documentation
├── LICENSE.txt            # license information
├── .gitignore             # files to be ignored by git
├── requirements.txt       # dependencies for tool installation
└── README.md              # tool documentation
```

## 3. Installation

### 3.1 Download the repository and change into the directory
```bash
git clone ADD LINK HERE
cd CRAAnVis
```
### 3.2 Create a virtual environment, activate it and install dependencies
```bash
python3 -m venv crannvis_venv
source crannvis_venv/bin/activate
pip install -r requirements.txt
```
### 3.3 Run the tool

```bash
python CRAAnVis/crannvis.py
```
Running this will start the GUI.
## 4. Tool Usage
### 4.1 Visualizing SpacerPlacer Experiments
To select a SpacerPlacer experiment for visualization, select **File -> Open SpacerPlacer Experiment...** or press
**Ctrl + O** to open a native folder selection dialog. Alternatively, select **File -> Open Recent** to choose the folder 
path from a list of recently opened SpacerPlacer experiments.

### 4.2 Exporting the Visualization as .PNG File
To export a visualization as a .PNG file, select **File -> Export as PNG...**
 This opens a resolution selection dialog that allows adaptation of the default export resolution. 
After selecting the desired resolution, a native file selection dialog opens, 
and the visualization is saved to the selected path. 
Alternatively, the visualization can be quickly and conveniently saved as a .PNG in default 
resolution to the clipboard by selecting **Edit -> Copy Image** or pressing **Ctrl + C**.

### 4.3 Exporting the Visualization as .PDF File
To export a visualization as a .PDF file, select **File -> Export as PDF...** 
This opens a native file selection dialog, and the visualization is saved to the selected path.

### 4.4 Single Color Mode
CRAAnVis offers two distinct color options for visualizing CRISPR array ancestries.
 The first, *Single Color Mode*, assigns a unique color to each distinct CRISPR spacer 
in the array.
 To activate *Single Color Mode*, select **Color -> Single Color Mode**. 
*Single Color Mode* produces a tidy look with visually distinctive and contrasting spacer colors up to a medium number of spacers.



![visualization in single color mode](https://github.com/janbio2/CRAAnVis/blob/release/images/single_color_mode.png)



### 4.5 Two Color Mode
The second color mode, *Two Color Mode*, assigns two colors, an inner and an outer color, to each distinct CRISPR spacer in the array.
 The combination of two colors in *Two Color Mode* allows for more distinctive color coding at higher numbers of spacers.
 To activate *Two Color Mode*, select **Color -> Two Color Mode**.  
After activating *Two Color Mode*, two layout options for color coding the evolutionary events are available. 
The *InnerOuter Two Color Event Split* option displays colors
 in an inner-outer fashion inside the evolutionary events, similar to the spacers.
 To activate the *InnerOuter Two Color Event Split* option, select **Color -> InnerOuter Two Color Event Split**.

![visualization in two color horizontal event split mode](https://github.com/janbio2/CRAAnVis/blob/release/images/two_color_io.png)


The *Horizontal Two Color Event Split* option displays 
the colors stacked horizontally inside the evolutionary events. 
To activate the *Horizontal Two Color Event Split* option, select **Color -> Horizontal Two Color Event Split**.

![visualization in two color horizontal event split mode](https://github.com/janbio2/CRAAnVis/blob/release/images/two_color_h.png)

### 4.6 Coloring Arrays by Spacer Frequency
The color of the spacers in the CRISPR arrays can be set to reflect the frequency of 
the spacers in the SpacerPlacer experiment, including or excluding deletions of spacers. To activate this option, 
select **Color -> Color by Metadata... -> 
Value Range of Spacer Frequency / Value Range of Spacer Frequency with Deletions**. 
Legends for the frequency color coding are provided below the array visualization.

![color by spacer frequency](https://github.com/janbio2/CRAAnVis/blob/release/images/color_by_frequency.png)

### 4.7 Coloring Arrays by Metadata
Adding a metadata file (see section 5.2) to the SpacerPlacer experiment expands the spacer tooltip information available 
and more importantly allows for metadata-based color coding of the CRISPR arrays. 
Two kinds of metadata categories produce color coding schemes in CRAAnVis:  
metadata categories with numerical values and metadata categories resembling lists of strings. 
From numerical metadata categories, CRAAnVis produces 
gradient color coding schemes with varying color saturation reflecting the min-max scaled numerical values. 
From metadata categories resembling lists of strings, CRAAnVis produces 
categorical color coding schemes with colors reflecting distinct combinations of the strings in the lists.   
To activate a metadata-based color map, select **Color -> Color by Metadata...** and select the desired metadata 
coloring option from the sub-menu. 
CRAAnVis provides legends for activated metadata-based color maps below the array visualization.

![color categorical by mock metadata](https://github.com/janbio2/CRAAnVis/blob/release/images/color_by_metadata.png)

### 4.8 Manual Spacer Color Assignment
CRAAnVis allows for manual color assignment of individual spacers. To manually assign a color to a spacer, 
right-click to open the spacer's context menu and select **Pick New Spacer Color**. A native color selection dialog opens, 
and the selected color is assigned to the spacer. When the arrays are colored according to group membership in a 
metadata category, this option is replaced by **Pick New Group Color**, which works correspondingly.
<div>
    <img src="https://github.com/janbio2/CRAAnVis/blob/release/images/manual_color.png" style="height: 200px; width: auto; display: inline-block;">
    <img src="https://github.com/janbio2/CRAAnVis/blob/release/images/manual_color2.png" style="height: 200px; width: auto; display: inline-block;">
</div>
Color picking.

![changed group color](https://github.com/janbio2/CRAAnVis/blob/release/images/new_group_color.png)

### 4.9 Importing and Exporting Color Maps
A current color map can be exported to a CSV file by selecting **Color -> Save Current Color Map to .csv**. 
A native file selection dialog subsequently opens, and the color map is saved to the selected path. 
Accordingly, a color map can be imported from a CSV file by selecting **Color -> Import Color Map**. 
A native file selection dialog subsequently opens, and the color map is imported from the selected path. 
As a blueprint for the required CSV file structure, a template for such a color map can be exported by selecting 
**Color -> Save Color Map Template to .csv**. 
A native file selection dialog opens for selecting the path for saving the template.

### 4.10 Highlighting Spacers
Specific spacers and their corresponding evolutionary events can be highlighted in several ways.
To highlight spacers and their corresponding evolutionary events,
right-click the spacer to open the spacer's context menu and select **Highlight Spacer in Tree**.
To remove the highlight, repeat the procedure.  
To highlight all spacers with duplicates in the array, select **Arrays -> Highlight Spacers with Duplicates**.
To highlight all spacers that are hypothesized to have only been gained in the ancestry
of a single array in the experiment, select **Arrays -> Highlight Singular Leaf Acquisitions**.
When highlighting the duplicates or the singular leaf acquisitions, other highlights are removed.

![highlighting singular leaf acquisitions](https://github.com/janbio2/CRAAnVis/blob/release/images/highlighting.gif)


### 4.11 Static and Dynamic Highlighting
As dynamic blinking highlights cannot be recorded in a static image, highlighting of spacers and their corresponding
evolutionary events can be switched between static and dynamic highlighting. To activate static highlighting, select
**Colors -> Static Black and White Highlights**.   
To activate dynamic highlighting, select
**Colors -> Blinking Highlights**. All highlights are set static when exporting the visualization as a .PNG or .PDF file.

![highlighting singular leaf acquisitions static](https://github.com/janbio2/CRAAnVis/blob/release/images/highlighting.png)

### 4.12 Rearranging the Phylogenetic Tree and the Arrays
Rearranging the phylogenetic tree and the arrays is possible by swapping the order child nodes at internal nodes.
To swap the order of child nodes at an internal node, right-click the node to open the node's context menu and select
**Swap Child Nodes**. The order of the child nodes is swapped and the visualization is updated accordingly, with the
arrays being aligned to their corresponding leaf nodes.

![swapping tree nodes](https://github.com/janbio2/CRAAnVis/blob/release/images/swap_nodes.gif)


### 4.13 Resizing the Phylogenetic Tree
The length of the phylogenetic tree in the visualization can be increased by selecting **Tree -> Extend Tree Length** or pressing
**Ctrl + T**. To decrease the tree length, select **Tree -> Reduce Tree Length** or press **Ctrl + Shift + T**.   
To set the tree length as short as possible while maintaining visibility of the shortest
branch lengths, select **Tree -> Set Tiny Tree Scale**. To reset the tree length to the default length, select
**Tree -> Reset Tree Scale**.

![resize tree](https://github.com/janbio2/CRAAnVis/blob/release/images/tree_resize.gif)

### 4.14 Pooling of Evolutionary Events
To improve information density of the visualization, evolutionary events in the tree can be pooled. Pooling aggregates
several evolutionary event items into a single pool item when three or more evolutionary events of the same type and with 
names constituting a consecutive incremental number sequence are adjacent to each other in the tree. To activate pooling,
select **Tree -> Pool Evolutionary Events**. 

![visualization with unpooled events](https://github.com/janbio2/CRAAnVis/blob/release/images/unpooled_events.png)
Visualization with unpooled events 

![visualization with pooled events](https://github.com/janbio2/CRAAnVis/blob/release/images/pooled.png)
Visualization with pooled events

### 4.15 Showing hypothesized Ancestral Array Compositions
To show the hypothesized composition of the ancestral arrays at any internal node in the tree, right-click the node to
open the node's context menu and select **Show Set of Spacers at Node**. Repeat the procedure to hide the hypothesized
ancestral array composition.

![showing hypthesized ancestral array composition](https://github.com/janbio2/CRAAnVis/blob/release/images/show_inner.png)

### 4.16 Adjusting the Array Header
The array header shows in its upper part the full set of spacers available in all arrays with the names that SpacerPlacer assigned to them.
In its lower part in grey the array header shows the original names of the spacers prior to the SpacerPlacer experiment.
To hide the description tags of the header, deselect **Arrays -> Show Tags for Template and Org Names**.
To hide the display of the original names, deselect **Arrays -> Show Original Names**.
To hide the display of the set of spacers with the names that SpacerPlacer assigned to them, deselect 
**Arrays -> Show Template**.

![adjusting the header](https://github.com/janbio2/CRAAnVis/blob/release/images/adjust_header.gif)


### 4.17 Collapsing Singular Array Parts
To improve the density of information in the visualization, spacers that are singular leaf acquisitions can be collapsed
and superposed instead of being arranged next to each other. To collapse singular leaf acquisitions, select
**Arrays -> Collapse Singular Leaf Acquisitions**. To expand them again repeat the procedure.

![collapsing singular leaf acquisitions](https://github.com/janbio2/CRAAnVis/blob/release/images/collapsing_array.gif)

### 4.18 Non-GUI Usage as a Python Module
CRAAnVis can also be used as a Python module to visualize SpacerPlacer experiments.
Without further adaptation of the module, the following visualization options are conveniently accessible:
Visualization of SpacerPlacer experiments can be produced in *Single Color Mode* and *Two Color Mode*.
And for *Two Color Mode* the *InnerOuter Two Color Event Split*
and *Horizontal Two Color Event Split* options are available. Pooling of evolutionary events can also be activated.
The visualizations can be exported as .PNG or .PDF file. 
The Python module can be used as follows:
```bash
source crannvis_venv/bin/activate
cd CRAAnVis/CRAAnVis
python
```
```python
from craanvis import CRAAnVis
sp_vis_tool = CRAAnVis(headless_mode=True)
sp_vis_tool.view.print_headless(outformats=["pdf"],  # or ["png"] or both ["pdf","png"]
                                input_folder_path="in_folder_path",
                                output_folder_path="out_folder_path",
                                color_mode="single_color",  # or "iosplit" or "hsplit"
                                pooling=False)  # or pooling=True
```
Using the *view.print_headless()* method the SpacerPlacer
experiment located in the *in_folder_path* can be visualized in the specified *color_mode*
("single_color" for *Single Color Mode* or "iosplit" or "hsplit" for *Two Color Mode* for *Two Color Mode* 
with the *InnerOuter Two Color Event Split* or *Horizontal Two Color Event Split* options activated, respectively).
*pooling* of evolutionary events can be activated (True) or deactivated (False).
The produced visualization is saved to the *out_folder_path* as a .PNG or .PDF file or both, depending on the specified 
*outformats*.

## 5. Input Files
CRAAnVis requires the output of a SpacerPlacer experiment as input.
This SpacerPlacer output consists of a folder containing defined files of defined structure.
In addition to the SpacerPlacer output, the visualization of the CRISPR array ancestries can be customized by
adding a metadata file to the SpacerPlacer experiment folder.

### 5.1 SpacerPlacer Experiment Files 
The SpacerPlacer experiment folder should contain the following SpacerPlacer files:
```
spacer_placer_experiment_folder/
├── experiment_id_other_events.json
├── experiment_id_rec_gains_losses.json
├── experiment_id_rec_spacers.json
├── experiment_id_spacer_names_to_numbers.json
├── experiment_id_top_order.json
└── experiment_id_tree.nwk
```

### 5.2 Metadata Files
To enable metadata related functionalities, a metadata file needs to be added to the SpacerPlacer experiment folder.
```
spacer_placer_experiment_folder/
... regular files ...
└── experiment_id_metadata.json
```
The metadata needs to be serialized and saved as a JSON file.
The JSON must contain a dictionary with every spacer id as key and a dictionary of metadata categories as value.
The dictionary of metadata categories needs to contain a dictionary with the metadata category names as key and a
dictionary of the metadata value type and the metadata value as value.
If the metadata value type is "list", the metadata value needs to be a list of dictionaries with the keys "type" and
"value" and the corresponding values for the list items. Switching to a relational database for input data could 
improve the usability considerably.   
This is a mock example of a metadata file for a single spacer in a SpacerPlacer experiment
(in practice, metadata files need to contain metadata for all spacers in the experiment):
```
{"1":                              # spacer_id
    {"gc_content":                 # metadata category
        {"type": "float",          # metadata value type float
         "value": 0.53},           # value
    "targets":                     # metadata category 
        {"type": "list",           # metadata value type list
         "value": [                # value
                   {"type":"str",         # list item 1 type
                    "value": "phageC"},   # list item 1 value
                    {"type": "str",       # list item 2 type
                     "value": "phageB"}]}}# list item 2 value 
}
```


