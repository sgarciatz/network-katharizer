# Network-Katharizer
Network-Katharizer is a simulator that creates a emulated UAV-based network from the specification given in the input file. It configures the networking aspects of the system and performs Round Trip Time (RTT) experimients. The output is written to the host machine's filesystem so it persists and it can be later anaylized.

Some input data is provided in the input folder.


To execute run the following command specifying valid parameters:

    python NetworkKatharizer/TedLab.py \
        <input_file.csv> \
        <output_folder> \
        <mode (1 for normal and 2 for scalable)>

The scalable mode will launch the least number of containers and the normal model will launch a container for each device specified in the input file.
