# Network-Katharizer
Network-Katharizer is a simulator that creates a emulated UAV-based network from the specification given in the input file. It configures the networking aspects of the system and performs Round Trip Time (RTT) experimients. The output is written to the host machine's filesystem so it persists and it can be later anaylized.

Some input data is provided in the input folder.


To execute run the following command specifying valid parameters:

    python NetworkKatharizer/TedLab.py \
        <input_file.csv> \
        <output_folder> \
        <mode (1 for normal and 2 for scalable)>

The scalable mode will launch the least number of containers and the normal model will launch a container for each device specified in the input file.

## Generate Figures
Some output data that is published in papers is also provided, you can generate the figures yourserlf using the following commands:

    python serviceLatency.py --sources \
        output/paper2_small_00_0/ \
        output/paper2_small_00_1/ \
        output/paper2_small_00_2/ \
        output/paper2_small_00_MANETOptiServ_globalLatency_0/ \
        output/paper2_small_00_MANETOptiServ_globalLatency_1/ \
        output/paper2_small_00_MANETOptiServ_globalLatency_2/ \
        output/paper2_small_00_MANETOptiServ_fairness_0/ \
        output/paper2_small_00_MANETOptiServ_fairness_1/ \
        output/paper2_small_00_MANETOptiServ_fairness_2/ \
        --ms 4

    python serviceLatency.py --sources \
        output/paper2_small_01_0/ \
        output/paper2_small_01_1/ \
        output/paper2_small_01_2/ \
        output/paper2_small_01_MANETOptiServ_globalLatency_0/ \
        output/paper2_small_01_MANETOptiServ_globalLatency_1/ \
        output/paper2_small_01_MANETOptiServ_globalLatency_2/ \
        output/paper2_small_01_MANETOptiServ_fairness_0/ \
        output/paper2_small_01_MANETOptiServ_fairness_1/ \
        output/paper2_small_01_MANETOptiServ_fairness_2/ \
        --ms 4

    python serviceLatency.py --sources \
        output/paper2_small_02_0/ \
        output/paper2_small_02_1/ \
        output/paper2_small_02_2/ \
        output/paper2_small_02_MANETOptiServ_globalLatency_0/ \
        output/paper2_small_02_MANETOptiServ_globalLatency_1/ \
        output/paper2_small_02_MANETOptiServ_globalLatency_2/ \
        output/paper2_small_02_MANETOptiServ_fairness_0/ \
        output/paper2_small_02_MANETOptiServ_fairness_1/ \
        output/paper2_small_02_MANETOptiServ_fairness_2/ \
        --ms 4

    python serviceLatency.py --sources \
        output/paper2_large_00_0/ \
        output/paper2_large_00_1/ \
        output/paper2_large_00_2/ \
        output/paper2_large_00_MANETOptiServ_globalLatency_0/ \
        output/paper2_large_00_MANETOptiServ_globalLatency_1/ \
        output/paper2_large_00_MANETOptiServ_globalLatency_2/ \
        output/paper2_large_00_MANETOptiServ_fairness_0/ \
        output/paper2_large_00_MANETOptiServ_fairness_1/ \
        output/paper2_large_00_MANETOptiServ_fairness_2/ \
        --ms 4

    python serviceLatency.py --sources \
        output/paper2_large_01_0/ \
        output/paper2_large_01_1/ \
        output/paper2_large_01_2/ \
        output/paper2_large_01_MANETOptiServ_globalLatency_0/ \
        output/paper2_large_01_MANETOptiServ_globalLatency_1/ \
        output/paper2_large_01_MANETOptiServ_globalLatency_2/ \
        output/paper2_large_01_MANETOptiServ_fairness_0/ \
        output/paper2_large_01_MANETOptiServ_fairness_1/ \
        output/paper2_large_01_MANETOptiServ_fairness_2/ \
        --ms 4
        
    python serviceLatency.py --sources \
        output/paper2_veryLarge_01_0 \
        output/paper2_veryLarge_01_1 \
        output/paper2_veryLarge_01_2 \
        output/paper2_veryLarge_01_MANETOptiServ_globalLatency_0/ \
        output/paper2_veryLarge_01_MANETOptiServ_globalLatency_1/ \
        output/paper2_veryLarge_01_MANETOptiServ_globalLatency_2/ \
        output/paper2_veryLarge_01_MANETOptiServ_fairness_0/ \
        output/paper2_veryLarge_01_MANETOptiServ_fairness_1/ \
        output/paper2_veryLarge_01_MANETOptiServ_fairness_2/ \
        --ms 4 
        
    python serviceLatency.py --sources \
        output/paper2_large_00_0/ \
        output/paper2_large_00_1/ \
        output/paper2_large_00_2/ \
        output/paper2_large_00_MANETOptiServ_globalLatency_3/ \
        output/paper2_large_00_MANETOptiServ_globalLatency_4/ \
        output/paper2_large_00_MANETOptiServ_globalLatency_5/ \
        output/paper2_large_00_MANETOptiServ_fairness_0/ \
        output/paper2_large_00_MANETOptiServ_fairness_1/ \
        output/paper2_large_00_MANETOptiServ_fairness_2/ \
        --ms 4

    python serviceLatency.py --sources \
        output/paper2_large_01_0/ \
        output/paper2_large_01_1/ \
        output/paper2_large_01_2/ \
        output/paper2_large_01_MANETOptiServ_globalLatency_3/ \
        output/paper2_large_01_MANETOptiServ_globalLatency_4/ \
        output/paper2_large_01_MANETOptiServ_globalLatency_5/ \
        output/paper2_large_01_MANETOptiServ_fairness_0/ \
        output/paper2_large_01_MANETOptiServ_fairness_1/ \
        output/paper2_large_01_MANETOptiServ_fairness_2/ \
        --ms 4
