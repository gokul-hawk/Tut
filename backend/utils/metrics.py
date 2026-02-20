import numpy as np
from sklearn.metrics import roc_auc_score, mean_squared_error, mean_absolute_error, accuracy_score

def calculate_metrics(y_true, y_pred):
    """
    Calculates standard Knowledge Tracing metrics.
    
    Args:
        y_true (list or np.array): Binary ground truth labels (0 or 1).
        y_pred (list or np.array): Predicted probabilities (0.0 to 1.0).
        
    Returns:
        dict: A dictionary containing AUC, ACC, RMSE, and MAE.
    """
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    
    # Classification metrics (using 0.5 threshold for Accuracy)
    y_pred_binary = (y_pred >= 0.5).astype(int)
    
    try:
        auc = roc_auc_score(y_true, y_pred)
    except ValueError:
        # AUC is undefined if y_true has only one class (all 0s or all 1s)
        auc = 0.5 
        
    acc = accuracy_score(y_true, y_pred_binary)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mae = mean_absolute_error(y_true, y_pred)
    
    return {
        "AUC": auc,
        "ACC": acc,
        "RMSE": rmse,
        "MAE": mae
    }
