# dia_fsm_c_code_generation
Generate C code from [Dia tool](https://sourceforge.net/projects/dia-installer/) Finite State machine.
Starting point from this project was done by **Tomáš Pospíšek** [here](https://github.com/tpo/dia-uml-stm-generation). 
I got useful information from [Tomáš blog](http://blog.sourcepole.ch/2012/06/07/generating-state-machines-with-dia/) when I wrote this plugin. 

## Usage 
Create a finite FSM. Here is FSM `./fsm_example/fsm_example.dia` used as example for `dia_fsm_c_code_generation` plugin

<img src="https://raw.githubusercontent.com/Lahorde/dia_fsm_c_code_generation/master/fsm_example/fsm_example.png" width="1200">

    # Clone this repo to Dia user python files
    cd ~/.dia/python
    git clone https://github.com/Lahorde/dia_fsm_c_code_generation.git
    
Generate C fsm code either :
* From python console :

```
from dia_fsm_c_code_generation import fsm_c_export
import dia

render = fsm_c_export.CFSMExporter()
render.begin_render(dia.active_display().diagram.data, "your_source_file.c")
render.end_render()
```
   
* or 
* From python console :

```
from dia_fsm_c_code_generation import fsm_c_export
```

then export fsm selecting `State Machine C` exporter

Then implement missing functions. All user code (not automatically generated by this plugin) must be inserted between tags :

    /** USER CODE BEGIN Types */
    your code...
    /** USER CODE END Types */
    
This user code won't be overwritten after fsm C code generation when code is exported from python console. **User code will be overwritten when code is exported from Dia export menu**

Destination file must be `(.+)_fsm.c`, e.g. : `heater_fsm.c` in this case it will generate some Types, functions prefixed such as : `typdef enum {...}HeaterState;` `void heater_action_...()`

## Test 
### Files
`./fsm_example/fsm_example.dia` is a state machine created from Dia 

`./fsm_example/example_fsm.c` is a C source file containing User code implementing :
* state machine run time (see main implementation)
* action, guards implementation
i.e : all code that cannot be generated by an FSM generator.

### Code generation
Open `./fsm_example/fsm_example.dia` and export state machine from python console :  

```
from dia_fsm_c_code_generation import fsm_c_export
import dia

render = fsm_c_export.CFSMExporter()
render.begin_render(dia.active_display().diagram.data, "project_path/fsm_example/example_fsm.c")
render.end_render()
```

### compilation and run

    cd fsm_example
    gcc -I "./fsm" -o fsm_generation_example example_fsm.c ./fsm/fsm.c main.c
    ./fsm_generation_example
  
### check test

    if diff fsm_generation_example.log <(./fsm_generation_example) ;then echo "test OK"; else echo "test KO"; fi
