# Minimal Perspective Autocalibration

### Create Conda environment
```
conda create --name RPAC --file requirements.txt
conda activate RPAC
pip install networkx
```

### 0. Configurations
This code supports 32 calibration configurations which are encoded as 5 character strings of "0" and "1", with "0" indicating an unknown parameter and "1" indicating a known parameter. The order of parameters is the following: f_x, f_y, c_x, c_y, s.
For instance:
1. 01010: unknown f_x, c_x, s; known f_y, c_y
2. 00111: unknown f_x, f_y; known c_x, c_y, s

### 1. Generate all possible ways to remove constraints 
After choosing a configuration, e.g., 00001 in this example, run the following commands.
```
cd combinatorics
python combs.py --config 00001
cd ..
```

### 2. Generate equivalence classes
First, run vertex permutation:
```
cd isomorphism
python isomorphism.py --config 00001
```
Next, run view-pair permutation:
```
python sym1.py --config 00001
cd ..
```

### 3. Compute the number of complex and real solutions for all configurations
```
python monodromy/monodromy.py --config 00001
cd monodromy/results/00001/m2
M2 monodromy.m2
```

## Legacy

### Generate all graphs
```
python combs-parallel/combs.py --config <YOUR_CONFIG>
```

### Build equivalence classes
```
python isomorphism/isomorphism.py --config <YOUR_CONFIG>
```

### Monodromy
Compute number of complex and real solutions for a given configuration on all equivalence classes
```
python monodromy/monodromy.py --config <YOUR_CONFIG>
```

### Example
For the 3V5P with f_x, f_y, c_x, c_y as unknowns.
