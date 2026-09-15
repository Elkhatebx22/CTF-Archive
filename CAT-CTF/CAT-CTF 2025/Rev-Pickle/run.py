import rehyd       
import pickle

with open("chall.pkl", "rb") as fh:
    check_flag = pickle.load(fh)  

check_flag()                     
