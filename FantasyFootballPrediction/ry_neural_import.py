'''
File for using tensor flow imports
'''

import numpy as np
import tensorflow as tf
import pandas as pd

def main():
    '''
    Main body for executing code
    '''
    #load data in from source
    data = np.load("train.npy", np.float32)
    print("**************************************************")
    print("This is an example print using just a numpy array")
    print("**************************************************\n")
    print(data)
    print("\n***************************************************")
    print("This is an example print using a pandas data frame")
    print("***************************************************")
    df = pd.DataFrame(data=data)
    print(df)

    #TODO Shape the data using information found in
    #https://www.tensorflow.org/programmers_guide/datasets#consuming_numpy_arrays
    

if __name__ == "__main__":
    main()
