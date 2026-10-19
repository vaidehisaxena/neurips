from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path('/Users/vaidehisaxena/Documents/GitHub/neurips')
OUT = Path(__file__).resolve().parent / 'figures'
PINK = {'random':'#fed8e5', 'entropy':'#ffc4c4', 'entropy_diversity':'#fb6478'}
EDGE = '#5c3a47'
LS = {'random':(0,(1,1)), 'entropy':(0,(5,2)), 'entropy_diversity':'-'}
MARK = {'random':'o', 'entropy':'s', 'entropy_diversity':'D'}
LABEL = {'random':'Random', 'entropy':'Entropy', 'entropy_diversity':'Entropy–diversity'}
MODELS = ['tabpfn','random_forest','xgboost','lightgbm']
MODEL_LABEL = {'tabpfn':'TabPFN','random_forest':'Random forest','xgboost':'XGBoost','lightgbm':'LightGBM'}
DATASETS = ['DILI','HIA_Hou','Bioavailability_Ma','Pgp_Broccatelli','BBB_Martins']
DATASET_LABEL = {'DILI':'DILI','HIA_Hou':'HIA','Bioavailability_Ma':'Bioavailability','Pgp_Broccatelli':'P-glycoprotein','BBB_Martins':'BBB'}

def ci(x):
    a=np.asarray(x,float); return 1.96*a.std(ddof=1)/np.sqrt(len(a))

def learning_figure(rep, filename):
    d=pd.read_csv(ROOT/'results'/f'{rep.lower()}_metrics.csv')
    fig,axes=plt.subplots(1,5,figsize=(10.6,2.45),sharey=True)
    for ax,ds in zip(axes,DATASETS):
        sub=d[d.dataset.eq(ds)]
        for m in MODELS:
            for acq in ['random','entropy','entropy_diversity']:
                q=sub[(sub.model.eq(m))&(sub.acquisition.eq(acq))].groupby('budget').test_auroc.agg(['mean',ci]).reset_index()
                # Policy is encoded by color/line; model by marker frequency and opacity.
                ax.plot(q.budget,q['mean'],color=PINK[acq],ls=LS[acq],lw=.85,alpha=.55+.1*MODELS.index(m),
                        marker=MARK[acq],markevery=4,ms=1.8,mec=EDGE,mew=.25)
        ax.set_title(DATASET_LABEL[ds],fontsize=8,fontweight='bold')
        ax.set_xlabel('Labels',fontsize=7); ax.tick_params(labelsize=6)
    axes[0].set_ylabel('Test AUROC',fontsize=8)
    handles=[plt.Line2D([0],[0],color=PINK[a],ls=LS[a],marker=MARK[a],ms=3,lw=1,label=LABEL[a]) for a in ['random','entropy','entropy_diversity']]
    fig.legend(handles=handles,loc='upper center',ncol=3,frameon=False,fontsize=7,bbox_to_anchor=(.5,1.04))
    fig.suptitle(f'{rep}: learning trajectories across budgets',y=1.13,fontsize=10,fontweight='bold',color=EDGE)
    fig.tight_layout(); fig.savefig(OUT/f'{filename}.pdf',bbox_inches='tight'); fig.savefig(OUT/f'{filename}.png',dpi=300,bbox_inches='tight'); plt.close(fig)

def acquisition_figure(rep, filename):
    d=pd.read_csv(ROOT/'results'/f'tables_{rep.lower()}'/'aulc_trajectories.csv')
    pairs=[('entropy_diversity','entropy'),('entropy_diversity','random'),('entropy','random')]
    rows=[]
    for m in MODELS:
        wide=d[d.model.eq(m)].pivot(index=['dataset','seed'],columns='acquisition',values='aulc')
        for a,b in pairs:
            v=wide[a]-wide[b]; rows.append((m,a,b,v.mean(),ci(v)))
    fig,ax=plt.subplots(figsize=(6.7,3.7)); y=np.arange(len(rows))[::-1]
    for yy,(m,a,b,mean,err) in zip(y,rows):
        ax.errorbar(mean,yy,xerr=err,fmt='o',ms=4,color=PINK[a],mec=EDGE,mew=.5,ecolor=EDGE,lw=.8,capsize=2)
    ax.axvline(0,color='#555',lw=.7); ax.set_yticks(y,[f'{MODEL_LABEL[m]}: {LABEL[a]} − {LABEL[b]}' for m,a,b,_,_ in rows],fontsize=6.5)
    ax.set_xlabel('Paired AULC difference',fontsize=8); ax.set_title(f'{rep}: acquisition-policy contrasts',fontsize=10,fontweight='bold',color=EDGE)
    ax.tick_params(axis='x',labelsize=7); fig.tight_layout(); fig.savefig(OUT/f'{filename}.pdf',bbox_inches='tight'); fig.savefig(OUT/f'{filename}.png',dpi=300,bbox_inches='tight'); plt.close(fig)

learning_figure('ECFP4','learning_curves_ecfp4_pink')
learning_figure('RDKIT2D','learning_curves_rdkit2d_pink')
acquisition_figure('ECFP4','acquisition_ecfp4_pink')
acquisition_figure('RDKIT2D','acquisition_rdkit2d_pink')
