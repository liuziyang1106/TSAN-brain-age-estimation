import os
from numpy.core.fromnumeric import size
import sklearn
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn import svm,metrics
from sklearn.metrics import mean_absolute_error
from sklearn.linear_model import LinearRegression
from scipy.stats import pearsonr,spearmanr
from pandas import Series, DataFrame
from sklearn.metrics import roc_curve,confusion_matrix,roc_auc_score,accuracy_score
from sklearn.model_selection import StratifiedShuffleSplit
np.random.seed(12345)

def get_correction_parameter(Regresstion_fit_data_root=None):
    # ==========-   load  prediction and target  ========== #
    Regresstion_fit_target = np.load(os.path.join(Regresstion_fit_data_root
                                                ,'target.npy'))
    Regresstion_fit_prediction = np.load(os.path.join(Regresstion_fit_data_root
                                                ,'prediction.npy'))

    # ==========   reshape numpy array   ========== #
    Regresstion_fit_prediction = np.expand_dims(Regresstion_fit_prediction,axis=1)
    Regresstion_fit_target = np.expand_dims(Regresstion_fit_target,axis=1)
    Regresstion_fit_predicted_age_difference = Regresstion_fit_prediction - Regresstion_fit_target
    print('number of sample: ',Regresstion_fit_predicted_age_difference.shape[0])

    reg = LinearRegression()
    reg.fit(Regresstion_fit_target,Regresstion_fit_predicted_age_difference)
    print("The linear model is: Y = {:.5} + {:.5}X".format(reg.intercept_[0]
                                                        , reg.coef_[0][0]))

    return reg.intercept_[0], reg.coef_[0][0]


def Bias_correction(target, prediction, beta, alpha):
    correct_prediction = prediction - (alpha*target + beta)
    correct_gap = correct_prediction - target
    return correct_prediction, target, correct_gap

def load_cla_data(cla_data_root,model_name,subgroup):
    target = np.load(cla_data_root + model_name + subgroup +'.npz')['target']
    predicton = np.load(cla_data_root + model_name + subgroup +'.npz')['target']
    brain_age_difference = predicton - target
    return predicton, target, brain_age_difference

def classfication(NC_PAD, MCI_PAD, AD_PAD, cli_type=1):
    
    MCI_PAD = np.expand_dims(MCI_PAD,axis=1)
    AD_PAD = np.expand_dims(AD_PAD,axis=1)
    NC_PAD = np.expand_dims(NC_PAD,axis=1)
    
    NC_PAD = np.concatenate([NC_PAD,np.zeros_like(NC_PAD)],axis=1)
    if cli_type == 1:
        AD_PAD = np.concatenate([AD_PAD,np.zeros_like(AD_PAD)+1],axis=1)
        Input_PAD = np.concatenate([NC_PAD, AD_PAD], axis=0)
    if cli_type == 2:
        MCI_PAD = np.concatenate([MCI_PAD,np.zeros_like(MCI_PAD)+1],axis=1)
        Input_PAD = np.concatenate([NC_PAD, MCI_PAD], axis=0)
    if cli_type == 3:
        AD_PAD = np.concatenate([AD_PAD,np.zeros_like(AD_PAD)],axis=1)
        MCI_PAD = np.concatenate([MCI_PAD,np.zeros_like(MCI_PAD)+1],axis=1)
        Input_PAD = np.concatenate([MCI_PAD, AD_PAD], axis=0)

    sss = StratifiedShuffleSplit(n_splits=3, test_size=0.33, random_state=0)
    x = np.expand_dims(Input_PAD[:,0],axis=1)
    y = Input_PAD[:,1]
    ACC = []
    AUC = []
    SEN = []
    SPE = []
    TARGET = []
    PROB = []
    # ======== cross validation ======== #
    '''
    Best estimator found by grid search:
    SVC  C=10, , cache_size=200, class_weight='balanced', gamma=0.125
    '''

    for train_index, test_index in sss.split(x, y):
        x_train, x_test = x[train_index], x[test_index]
        y_train, y_test = y[train_index], y[test_index]

        clf = svm.SVC(kernel='rbf',C = 10,class_weight='balanced', probability=True)
        clf.fit(x_train,y_train)

        y_pred = clf.predict(x_test)
        predict_probas = clf.predict_proba(x_test)[:,1]
        clf.score(x_test, y_test)
        acc=accuracy_score(y_test, y_pred)

        auc=roc_auc_score(y_test,y_pred)
        tn, fp, fn, tp = confusion_matrix(y_test, y_pred).ravel()
        sen = tp / (tp + fn)
        spe = tn / (tn + fp)
        print(
            'test: [+/- {0}/{1}],      AUC,    ACC,    SEN,    SPE\n\t\t\t'
            '{auc:.3f},   {acc:.3f},   {sen:.3f},   {spe:.3f}'.format(
            np.sum(y_test==1), np.sum(y_test==0), auc=auc, acc=acc, sen=sen, spe=spe))
        ACC.append(acc)
        AUC.append(auc)
        SEN.append(sen)
        SPE.append(spe)
        PROB.append(predict_probas)
        TARGET.append(y_test)

    # ======== output result ======== #
    print('mean AUC : ',np.mean(AUC))
    print('mean ACC : ',np.mean(ACC))
    print('mean SEN : ',np.mean(SEN))
    print('mean SPE : ',np.mean(SPE))
    PROB = (np.asarray(PROB)).flatten()
    TARGET = (np.asarray(TARGET,dtype=int)).flatten()
    return PROB, TARGET

def roc(targets, probas, auc):
    fpr, tpr, thrh = roc_curve(targets, probas)
    plt.plot(fpr, tpr, label=' ROC curver for HC vs. AD (AUC = {0:.3f})'.format(auc))
    plt.plot([0,1],[0,1],'k--')

    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.0])
    plt.xlabel('False Positive Rate', fontsize=16)
    plt.ylabel('True Positive Rate', fontsize=16)
    plt.legend(loc="lower right", fontsize=14)

    plt.title('ROC', fontsize=20)

def main():
    Regresstion_fit_data_root = './TMI_result/old_result/model6/'
    beta, alpha = get_correction_parameter(Regresstion_fit_data_root) 

    cla_data_root = './TMI_result/supply_result/classfication/'
    model_name = 'tsan-mse-ranking-'
    NC_predicion, NC_target, NC_brain_age_difference = load_cla_data(
                                                      cla_data_root
                                                     ,model_name
                                                     ,'NC')
    MCI_predicion, MCI_target, MCI_brain_age_difference = load_cla_data(
                                                      cla_data_root
                                                     ,model_name
                                                     ,'MCI')
    AD_predicion, AD_target, AD_brain_age_difference = load_cla_data(
                                                      cla_data_root
                                                      ,model_name
                                                      ,'AD')

    Bias_corrected_NC = Bias_correction(NC_target, NC_predicion
                                      , beta, alpha)
    Bias_corrected_MCI = Bias_correction(MCI_target, MCI_predicion
                                      , beta, alpha)
    Bias_corrected_AD = Bias_correction(AD_target, AD_predicion
                                      , beta, alpha)

    Bias_corrected_AD_PAD = Bias_corrected_AD[2]
    Bias_corrected_MCI_PAD = Bias_corrected_MCI[2]
    Bias_corrected_NC_PAD = Bias_corrected_NC[2]

    cli_type = 3
    
    print('===== Without Bias correction =====')
    a = classfication(NC_brain_age_difference
                    , MCI_brain_age_difference
                    , AD_brain_age_difference
                    , cli_type)

    print('===== Bias correction =====')
    a = classfication(Bias_corrected_NC_PAD
                    , Bias_corrected_MCI_PAD
                    , Bias_corrected_AD_PAD
                    , cli_type)

main()

