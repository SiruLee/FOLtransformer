# -*- coding: utf-8 -*-
"""
Created on Tue Jun  4 14:37:21 2024

@author: jhlee
"""
import os

import matplotlib.pyplot as plt


def run_mace4(fm="", output_dir="output", out_name="temp-output", axiom=None, domain_size=1, max_models=1, max_seconds=60, model_output=0):
    assert axiom is not None, "no axiom provided"

    os.system(f"cat {axiom} > ./mace4/input/temp-input.in")
    file = open("./mace4/input/temp-input.in", "r")
    contents = file.readlines()
    file.close()
    i = contents.index("formulas(assumptions).\n")
    contents.insert(i + 1, fm)
    w = open("./mace4/input/temp-input.in", "w")
    contents = "".join(contents)
    w.write(contents)
    w.close()
    print(f"\n\nRunning Mace4 with domain size starting from {domain_size}, finding {max_models} models in {max_seconds} seconds.")
    os.system(f"./mace4/mace4 -n {domain_size} -s 60 -b -1 -N -1 -n {domain_size} -i 1 -m {max_models} -t {max_seconds} -P {model_output} -p 0 -f ./mace4/input/temp-input.in > ./mace4/{output_dir}/{out_name}.out")
    # os.system("rm temp-input")
    

def measure_time(dirname, filename):
    file = open(f"../outputs/{dirname}/{filename}.out")
    line = file.readline()
    while not ("User_CPU" in line and "System_CPU" in line and "Wall_clock" in line) :
        line = file.readline()
    
    # end of statistics
    splited = line.split(',')
    time = float(splited[0].lstrip("User_CPU="))
    return time


def parameters():
    fm = input("Enter a desired formula: ")
    filename = input("Enter a name of an output file: ")
    domain_size = int(input("Starting Domain Size: "))
    max_models = int(input("Model Number: "))
    max_seconds = int(input("Maximum Time of Search: "))
    return fm, filename, domain_size, max_models, max_seconds
    

def single_analysis():
    fm, filename, domain_size, max_models, max_seconds = parameters()
    run_mace4(fm=fm, out_name=filename, domain_size=domain_size, max_models=max_models, 
              max_seconds=max_seconds)
    print(f"Generating {max_models} models took " + str(measure_time(filename)) + " seconds")
    
    
def generate_plot(sizes, times, fm, filename):
    plt.figure(figsize=(30,21))
    plt.xlabel("Number of Models Generated", fontsize="35")
    plt.xticks(fontsize="30")
    plt.ylabel("Time (s)", fontsize="35")
    plt.yticks(fontsize="30")
    plt.plot(sizes, times, 'ro-', label="CPU time elasped for generating models")
    plt.legend(frameon=True, fontsize="35")
    plt.title("Performance of Mace4 with respect to the Number of Model Generated\nGiven the Formula: " + fm, pad=20, fontsize="40", loc="left")
    plt.savefig(f"../plots/{filename}.png")
    
    
def performance_analysis():
    difficulty = input("Enter the complexity of a model (S/M/L): ").lower()
    if difficulty == 'l':
        sizes = [1, 5, 10, 50, 100]
    elif difficulty == "m":
        sizes = [10, 50, 100, 500, 1000]
    else:
        sizes = [100, 500, 1000, 5000, 10000]
    times = []
    fm = input("Enter a desired formula: ")
    filename = input("Enter a name of an output file: ")
    domain_size = int(input("Starting Domain Size: "))
    if not os.path.exists(f"../outputs/{filename}"):
        os.system(f"mkdir ../outputs/{filename}")
    for i, size in enumerate(sizes):
        new_filename = filename + str(size)
        model_output = 0
        if i == 0:
            model_output = 1
        run_mace4(fm=fm, output_dir=filename, out_name=new_filename, domain_size=domain_size, max_models=size, 
                  max_seconds=-1, model_output=model_output)
        times.append(measure_time(filename, new_filename))
        
    generate_plot(sizes, times, fm, filename)
    

if __name__ == "__main__":
    run_mace4("", "output", "example", "./input/fusion.in")
    