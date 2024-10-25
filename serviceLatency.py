#!/usr/bin/env python3
import os
import argparse
import numpy as np
import seaborn as sns
import pandas as pd
import statistics as st
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import matplotlib as mpl
from matplotlib import colormaps

"""
Show the latency experienced by EDs in an escenario.
For this matter, boxplots are used.
"""


def dir_path(path):

    """ Check if the input directories do really exist"""
    
    if os.path.isdir(path):
        return path
    else:
        raise argparse.ArgumentTypeError(
            f"readable_dir:{path} is not a valid path")

def parse_arguments() -> argparse.Namespace:

    """ Read the input parameters into a dict"""
    
    parser = argparse.ArgumentParser(
        description='Show the latency experienced by EDs in an scenario')
    parser.add_argument('--sources', nargs='*', type=dir_path)
    parser.add_argument('--ms', type=int)
    return parser.parse_args()
   
def prepare_sns() -> None:
    
    """ Set the parameters of sns to generate the images"""
    
    sns.set_theme(style="white",
                  palette=["salmon", "lightblue", "yellowgreen"],
                  rc={'figure.figsize':(6,8),
                      'axes.titlesize':30,
                      'axes.labelsize':20,
                      'patch.linewidth': 1.0})
    
def prepare_boxplot(data: pd.DataFrame, 
                    approaches: list[str],
                    microservices: list[str] = None) -> None:
                    
    """ Create the boxplot with the resulting DataFrame"""

    print(data)
    if (microservices == None):
    
        boxplot = sns.boxplot(data=data, 
                              x='Approach',
                              y='RTT',
                              hue='Approach',
                              order=approaches,
                              hue_order=microservices,
                              showmeans=True,
                              linewidth=2,
                              medianprops=dict(color="black", alpha=1),
                              meanprops={"markeredgecolor": "maroon",
                                         "markerfacecolor": "maroon",
                                         "markersize": "10"})
    else:
        boxplot = sns.boxplot(data=data, 
                              x='Approach',
                              y='RTT',
                              hue='Approach',
                              order=approaches,
                              hue_order=microservices)
    boxplot.set_xlabel('')
    boxplot.set_ylabel('RTT (ms)')
    boxplot.tick_params(axis='y', which='both', labelsize=16)
    boxplot.tick_params(axis='x', which='major', labelsize=16, rotation=16)
    #boxplot.legend(loc=2, prop={'size': 14})
    boxplot.set_ylim([0,0.1])
    

    hatches = ['//', '..', 'xx']
    patches = [patch for patch in boxplot.patches if type(patch) == mpl.patches.PathPatch]
    h = hatches * (len(patches) // len(hatches))

    for patch, hatch in zip(patches, h):
        patch.set_hatch(hatch)
        patch.set_edgecolor('w')
        
#    plt.savefig("figure.png",
#                dpi=300,
#                bbox_inches="tight")
    plt.show()
    
def checkApproach(filename: str) -> None:

    """Check the method used (ILP or heuristics)"""

    if ('globalLatency' in filename):
        return 1
    if ('fairness' in filename):
        return 2
    else:
        return 0

def main() -> None:

    """Create boxplot with the data obtained from the experiment"""
     
    args = parse_arguments()
    
    dataDirs = [os.path.join(source, 'shared') for source in args.sources]
    hostFiles = []
    approaches = ['ILP Model',
              'Heuristic Global Latency',
              'Heuristic Fairness']
    hostLatency = 0
    dataDirsGroups = np.array(dataDirs).reshape((-1,3))
    approach = None
    resultDf = []
    for dataDirsGroup in dataDirsGroups:
        approach = approaches[checkApproach(dataDirsGroup[0])]
        for index, dataDir in enumerate(dataDirsGroup):
            hostLatencyAcc = 0
            hostsFiles = os.listdir(dataDir)
            for hostFile in hostsFiles:
                hostFile = hostFile.decode('utf-8')
                output = open(os.path.join(dataDir, hostFile), 'r').read()
                mdev = float(
                    output[output.rfind('/') + 1: output.rfind(' ')])
                outputAux = output[:output.rfind('/')]
                maximum = float(outputAux[outputAux.rfind('/') + 1:])
                outputAux = outputAux[:outputAux.rfind('/')]
                minimum = float(outputAux[outputAux.rfind('/') +1 :])
                outputAux = outputAux[:outputAux.rfind('/')]
                hostLatency = float(outputAux[outputAux.rfind(' ') +1 :])
                resultDf.append({'Approach': approach,
                                 'Experiment': index,
                                 'Host': hostFile,
                                 'RTT': hostLatency})


    groupedData = pd.DataFrame(resultDf)[['Approach', 'Host', 'RTT']]\
        .groupby(['Approach', 'Host']).mean().reset_index()
    print(pd.DataFrame(resultDf)[['Approach','Experiment', 'RTT']]\
        .groupby(['Approach']).mean().reset_index())
    print(groupedData)


    prepare_sns()
    prepare_boxplot(groupedData[['Approach', 'RTT']],
                    approaches)



if __name__ == "__main__":
    main()
