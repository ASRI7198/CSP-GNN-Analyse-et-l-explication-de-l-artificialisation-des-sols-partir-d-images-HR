import sys
sys.path.append('/home/rida/GNN')

import torch
from Embedding_phase.MGCN.Multi_GCN import MGCN
from sklearn.model_selection import train_test_split
from Train import train_model
from Test import test_model
import Embedding_phase.Generate_data.config as args
from Embedding_phase.Generate_data.Generate_training import transform_to_float
import sys



if __name__ == "__main__":

    torch.cuda.empty_cache()
    data = torch.load(args.DATA_PATH_12, weights_only=False)
    print("Données d'entraînement chargées avec succès.")

    data = transform_to_float(data)
    print("Données transformées en float.")


    train_data, temp_data = train_test_split(data, test_size=0.4, random_state=42)
    valid_data, test_data = train_test_split(temp_data, test_size=0.5, random_state=42)
    print("Données divisées en ensembles d'entraînement, de validation et de test.")

    input_dim = data[0][0].x.shape[1]
    hidden_dim = 64
    out_dim = 16
    
    
    model = MGCN(input_dim, hidden_dim, out_dim)
    

    if len(sys.argv) > 1 and sys.argv[1] == "test":
        
        model.load_state_dict(torch.load(args.MODEL_SAVE_PATH_12))
        test_model(model, test_data)
    else:

        train_model(model, train_data, valid_data)



    

