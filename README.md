# FOL Transformer
## Introduction
The project includes an LLM with the base model of GPT-2 Medium (355M parameters) which was finetuned with the dataset of NL-FOL pairs. Specifically, this model is designed 
to simulate the MACE4 Model Generator under a pre-defined ontology for industrial design.

## Download
Due to the large file storage limit on Github, the repository does not include GPT's weight data files (~3.2GB in total). Please download this project from the OneDrive link I provided.

## How-To-Use
### Execution
The program can be executed via `main.py`.
```
python3 main.py
```

### Loading necessary modules and files
The program will load requisite modules for the language model such as PyTorch. This step may raise some warnings, but you can ignore them.

The program then checks if the base model is present at `./gpt/gpt2/355M`. If not, it downloads the weight file that is available online.

### MACE4 Configuration
The user will be asked two options for MACE4 Execution: a domain size and the number of models to find. Note that the domain size takes the value from the minimum value of 2.

### User Input
The user has two options for the input prompt; a natural language prompt, or an explicit FOL formula. 

A natural language prompt does not require other specific instructions.
Below are two examples of natural language input:
```
Input Prompt: There is a box.
```
```
Input Prompt: There is a cylinder.
```

In case of providing an explicit FOL formula due to the lack of performance of the language model, start the prompt with the flag `-ignore`. This will ignore the language model to run MACE4 directly with the formula 
provided by the user. Below is an example of explicit input:
```
Input Prompt: -ignore exists x exists y (is_box(x) & is_cylinder(y))
```

### MACE4-JSON Parsing
Given the user input combined with the ontology input at `./mace4/input/fusion.in`, MACE4 will run to generate a desired number of models. After the models are generated, the output file at `./mace4/output/`
will be parsed to create a JSON file that contains the necessary information on shapes.

### Fusion360
With the path of the JSON file specified in `./parser/json_to_fusion.py`, the user can load the script on Fusion360 to generate the objects and run generative design functionality manually.

## Notes
### Language Model
The current model was not trained on the rigorous dataset, and GPT-2 is just as big as a normal personal laptop can handle with a reasonable time scale. Therefore, the language model would rather signify its functionality as
generating a First-Order logic formula from natural language in accordance with the ontology. 

### Extensible Ontology
Ontology can be readily extended to incorporate more complex concepts of shapes and objects depending on what 3D simulation software is used.

### MACE4
Although not included in the current version, a utility provided along with MACE4, `isofilter`, can be used to remove isomorphic structures in the outputs from MACE4.

### Connections & Joints
The concept of connection is limitedly implemented in JSON format. However, since the current version only takes unary relations from MACE4 structures to generate a JSON file, it does not extract connection information from
MACE4 structures. It can be incorporated by designing a parsing algorithm for the relations in the higher order.
