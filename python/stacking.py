from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import numpy as np
import pandas as pd
from sklearn.metrics import roc_curve, auc
import matplotlib.pyplot as plt
from sklearn.svm import SVC
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import confusion_matrix
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPClassifier
from sklearn.linear_model import LogisticRegression

data1_1 = pd.read_csv('./data/15 Lipid.CSV',header=0)
data1 = np.array(data1_1)
data2 = pd.read_csv('./data/SVM C.CSV',header=0,index_col=0)
data3 = pd.read_csv('./data/SVM gamma.CSV',header=0,index_col=0)
c_m = np.array(data2)
g_m = np.array(data3)
data4 = pd.read_csv('./data/RF n trees.CSV',header=0,index_col=0)
data5 = pd.read_csv('./data/RF max_depth.CSV',header=0,index_col=0)
c = np.array(data4)
g = np.array(data5)
np.random.seed(98)
permutation = np.random.permutation(data1[:,0].shape[0])
data1 = data1[permutation]
x = data1[:,1:]
y = data1[:,0]
from sklearn.preprocessing import StandardScaler
st = StandardScaler().fit(x)
x1 = st.transform(x)
pca = PCA(n_components=0.99)
pca.fit(x1)
x1 = pca.transform(x1)
sen = []
spe = []
acc = []
for i in range(20):
    print(i)
    skf = StratifiedKFold(n_splits=5, random_state=i, shuffle=True).split(x1, y)
    for k,(train, test) in enumerate(skf):
        skf1 = StratifiedKFold(n_splits=5, random_state=i, shuffle=True).split(x, y)
        for j,(a, b) in enumerate(skf1):
            if j == k:
                x_train = x[a]
                x_test = x[b]
        svm = SVC(C=c_m[i,k], gamma=g_m[i,k]/10000,probability=True).fit(x1[train], y[train])
        RF = RandomForestClassifier(n_estimators=int(c[i, k]), max_depth=g[i, k], random_state=11).fit(x_train,y[train])
        y_pre1 = svm.predict(x1[train])
        y_pre2 = RF.predict(x_train)
        y_pre = np.column_stack([y_pre1,y_pre2])
        y_pre1 = svm.predict(x1[test])
        y_pre2 = RF.predict(x_test)
        y_pre_1 = np.column_stack([y_pre1,y_pre2])
        meta_learner = SVC(C=20, gamma=0.001, probability=True).fit(y_pre, y[train])
        y_p = meta_learner.predict(y_pre_1)
        cn = confusion_matrix(y[test], y_p)
        print(cn)
        sen1 = cn[0, 0] / (cn[0, 0] + cn[0, 1])
        spe1 = cn[1, 1] / (cn[1, 1] + cn[1, 0])
        acc1 = (cn[0, 0] + cn[1, 1]) / (cn[0, 0] + cn[0, 1] + cn[1, 1] + cn[1, 0])
        spe.append(spe1)
        sen.append(sen1)
        acc.append(acc1)
print('accuracy:', np.mean(acc), 'std:', np.std(acc))
print('sensitivity:', np.mean(sen), 'std:', np.std(sen))
print('specificity:', np.mean(spe), 'std:', np.std(spe))

aucs = []
hold = np.linspace(0, 1, 100)
mean_fpr = np.linspace(0, 1, 1000)
tprs = []
for i in range(20):
    skf = StratifiedKFold(n_splits=5, random_state=i, shuffle=True).split(x1, y)
    for k,(train, test) in enumerate(skf):
        skf1 = StratifiedKFold(n_splits=5, random_state=i, shuffle=True).split(x, y)
        for j, (a, b) in enumerate(skf1):
            if j == k:
                x_train = x[a]
                x_test = x[b]
        svm = SVC(C=c_m[i,k], gamma=g_m[i,k]/10000,probability=True).fit(x1[train], y[train])
        y_pro1 = svm.predict_proba(x1[test])
        RF = RandomForestClassifier(n_estimators=int(c[i, k]), max_depth=g[i, k], random_state=11).fit(x_train,y[train])
        y_pro2 = RF.predict_proba(x_test)
        y_pre1 = svm.predict(x1[train])
        y_pre2 = RF.predict(x_train)
        y_pre = np.column_stack([y_pre1, y_pre2])
        y_pre1 = np.zeros((len(y[test]),))
        y_pre2 = np.zeros((len(y[test]),))
        tpr = []
        fpr = []
        for h in hold:
            for j in range(len(y[test])):
              if y_pro1[j,1] > h :
                  y_pre1[j] = 1
              else:
                  y_pre1[j] = 0

              if y_pro2[j,1] > h :
                  y_pre2[j] = 1
              else:
                  y_pre2[j] = 0
            y_pre_1 = np.column_stack([y_pre1, y_pre2])
            meta_learner = SVC(C=20, gamma=0.001, probability=True).fit(y_pre, y[train])
            y_p = meta_learner.predict(y_pre_1)
            cn = confusion_matrix(y[test], y_p)
            tpr1 = cn[0,0] / (cn[0,0] + cn[0,1])
            fpr1 = cn[1,0] / (cn[1,0] + cn[1,1])
            tpr.append(tpr1)
            fpr.append(fpr1)
        roc_auc = auc(fpr,tpr)
        aucs.append(roc_auc)
        interp_tpr = np.interp(mean_fpr, fpr, tpr)
        interp_tpr[0] = 0.0
        tprs.append(interp_tpr)
tprs = np.array(tprs)
fig, ax = plt.subplots()
ax.plot([-0.05, 1.05], [-0.05, 1.05], linestyle='-', lw=1.5, color='gray',alpha=0.5)
mean_tpr = np.mean(tprs, axis=0)
mean_tpr[-1] = 1.0
mean_auc = auc(mean_fpr, mean_tpr)
std_auc = np.std(aucs)
print('mean roc auc:',mean_auc,'std:',std_auc)
ax.plot(mean_fpr, mean_tpr, color='#990000',
        label='AUC = %0.3f $\pm$ %0.3f' % (mean_auc, std_auc),
        lw=3, alpha=0.8)

font1 = {'family' : 'Arial',
'weight' : 'book',
'size'   : 16,}
font2 = {'family' : 'Arial',
'weight' : 'book',
'size'   : 16,}
ax.set(xlim=[-0.05, 1.05], ylim=[-0.05, 1.05])
plt.yticks(fontproperties = 'Arial', size = 16)
plt.xticks(fontproperties = 'Arial', size = 16)
ax.spines['bottom'].set_linewidth(2)
ax.spines['left'].set_linewidth(2)
ax.spines['top'].set_linewidth(2)
ax.spines['right'].set_linewidth(2)
ax.tick_params(width=2)
ax.legend(loc="lower right",prop = font2,frameon = False)
plt.xlabel('1 - Specificity',font1)
plt.ylabel('Sensitivity',font1)


aucs = []
hold = np.linspace(0, 1, 100)
mean_recall = np.linspace(0, 1, 1000)
precs = []
for i in range(20):
    skf = StratifiedKFold(n_splits=5, random_state=i, shuffle=True).split(x1, y)
    for k,(train, test) in enumerate(skf):
        skf1 = StratifiedKFold(n_splits=5, random_state=i, shuffle=True).split(x, y)
        for j, (a, b) in enumerate(skf1):
            if j == k:
                x_train = x[a]
                x_test = x[b]
        svm = SVC(C=c_m[i, k], gamma=g_m[i, k] / 10000, probability=True).fit(x1[train], y[train])
        y_pro1 = svm.predict_proba(x1[test])
        RF = RandomForestClassifier(n_estimators=int(c[i, k]), max_depth=g[i, k], random_state=11).fit(x_train,y[train])
        y_pro2 = RF.predict_proba(x_test)
        y_pre1 = svm.predict(x1[train])
        y_pre2 = RF.predict(x_train)
        y_pre = np.column_stack([y_pre1, y_pre2])
        y_pre1 = np.zeros((len(y[test]),))
        y_pre2 = np.zeros((len(y[test]),))
        recall = []
        prec = []
        for h in hold:
            for j in range(len(y[test])):
                if y_pro1[j, 1] > h:
                    y_pre1[j] = 1
                else:
                    y_pre1[j] = 0

                if y_pro2[j, 1] > h:
                    y_pre2[j] = 1
                else:
                    y_pre2[j] = 0
            y_pre_1 = np.column_stack([y_pre1, y_pre2])
            meta_learner = SVC(C=20, gamma=0.001, probability=True).fit(y_pre, y[train])
            y_p = meta_learner.predict(y_pre_1)
            cn = confusion_matrix(y[test], y_p)
            recall1 = cn[0,0] / (cn[0,0] + cn[0,1])
            if (cn[0,0]==0)and(cn[1,0]==0):
                prec1 = 1
            else:
                prec1 = cn[0,0] / (cn[0,0] + cn[1,0])
            recall.append(recall1)
            prec.append(prec1)
        pr_auc = auc(recall,prec)
        aucs.append(pr_auc)
        interp_prec = np.interp(mean_recall, recall, prec)
        interp_prec[0] = 1
        precs.append(interp_prec)
precs= np.array(precs)
fig1, ax1 = plt.subplots()
ax1.plot([-0.05, 1.05], [0.33, 0.33], linestyle='-', lw=1.5, color='gray',
         alpha=0.5)
mean_prec = np.mean(precs, axis=0)
mean_prec[-1] = 0.333
mean_auc = auc(mean_recall, mean_prec)
std_auc = np.std(aucs)
print('mean PR auc:',mean_auc,'std:',std_auc)
ax1.plot(mean_recall, mean_prec, color='#990000',lw=3, alpha=0.8,
         label='AUC = %0.3f $\pm$ %0.3f' % (mean_auc, std_auc))

font1 = {'family' : 'Arial',
'weight' : 'book',
'size'   : 16,}
font2 = {'family' : 'Arial',
'weight' : 'book',
'size'   : 16,}
ax1.set(xlim=[-0.05, 1.05], ylim=[-0.05, 1.05])
plt.yticks(fontproperties = 'Arial', size = 16)
plt.xticks(fontproperties = 'Arial', size = 16)
ax1.spines['bottom'].set_linewidth(2)
ax1.spines['left'].set_linewidth(2)
ax1.spines['top'].set_linewidth(2)
ax1.spines['right'].set_linewidth(2)
ax1.tick_params(width=2)
ax1.legend(loc="lower right",prop = font2,frameon = False)
plt.xlabel('Recall',font1)
plt.ylabel('Precision',font1)
plt.rcParams['figure.figsize'] = (8.0, 8.0)
plt.rcParams['savefig.dpi'] = 2000
plt.rcParams['figure.dpi'] = 300
plt.show()
