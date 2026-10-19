from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

ROOT = Path('/Users/vaidehisaxena/Documents/GitHub/neurips')
OUT = Path(__file__).resolve().parent / 'figures'
OUT.mkdir(exist_ok=True)
PINK = ['#fef5ec', '#fed8e5', '#ffc4c4', '#fb6478']
INK = '#5c3a47'
MODELS = ['tabpfn', 'random_forest', 'xgboost', 'lightgbm']
MODEL_LABEL = {'tabpfn':'TabPFN', 'random_forest':'Random forest', 'xgboost':'XGBoost', 'lightgbm':'LightGBM'}
ACQS = ['random', 'entropy', 'entropy_diversity']
ACQ_LABEL = {'random':'Random', 'entropy':'Entropy', 'entropy_diversity':'Entropy--diversity'}

def save(fig, name):
    fig.savefig(OUT / f'{name}.pdf', bbox_inches='tight')
    fig.savefig(OUT / f'{name}.png', dpi=300, bbox_inches='tight')
    plt.close(fig)

def bootstrap_ci(values, seed=42, n=10000):
    x = np.asarray(values, float)
    rng = np.random.default_rng(seed)
    means = rng.choice(x, (n, len(x)), replace=True).mean(axis=1)
    return x.mean(), *np.quantile(means, [0.025, 0.975])

sns.set_theme(style='whitegrid', font_scale=.85)
ecfp = pd.read_csv(ROOT/'results/tables_ecfp4/aulc_trajectories.csv').assign(representation='ECFP4')
rdk = pd.read_csv(ROOT/'results/tables_rdkit2d/aulc_trajectories.csv').assign(representation='RDKit2D')
keys = ['dataset','seed','model','acquisition']
paired = rdk.merge(ecfp, on=keys, suffixes=('_rdkit','_ecfp'))
paired['gain'] = paired['aulc_rdkit'] - paired['aulc_ecfp']

# Main evidence: means and bootstrap intervals, not distributional boxplots.
fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.15), gridspec_kw={'width_ratios':[1.08,1]})
macro = pd.concat([ecfp, rdk]).groupby(['representation','model','acquisition'], as_index=False).aulc.mean()
for j, rep in enumerate(['ECFP4','RDKit2D']):
    sub = macro[macro.representation.eq(rep)]
    x = np.arange(len(MODELS)); w=.22
    for i,a in enumerate(ACQS):
        vals = [sub[(sub.model.eq(m))&(sub.acquisition.eq(a))].aulc.iloc[0] for m in MODELS]
        axes[0].bar(x+(i-1)*w, vals, w, label=ACQ_LABEL[a], color=PINK[min(i+1,3)], edgecolor=INK, linewidth=.45, hatch=['','///','xx'][i], alpha=.95)
    axes[0].text((j*.0), .99, '', transform=axes[0].transAxes)
axes[0].cla()
x=np.arange(len(MODELS)); w=.34
for i,rep in enumerate(['ECFP4','RDKit2D']):
    vals=[]
    for m in MODELS:
        vals.append(macro[(macro.representation.eq(rep))&(macro.model.eq(m))].aulc.mean())
    axes[0].bar(x+(i-.5)*w, vals, w, label=rep, color=[PINK[1],PINK[3]][i], edgecolor=INK, linewidth=.5, hatch=['///',''][i])
axes[0].set_xticks(x, [MODEL_LABEL[m] for m in MODELS], rotation=20, ha='right')
axes[0].set_ylim(.72,.88); axes[0].set_ylabel('Macro normalized AULC')
axes[0].set_title('(a) Representation changes model ranking', loc='left', fontweight='bold')
axes[0].legend(frameon=False, ncol=2, fontsize=8)

rows=[]
for mi,m in enumerate(MODELS):
    for ai,a in enumerate(ACQS):
        v=paired[(paired.model.eq(m))&(paired.acquisition.eq(a))].gain
        mean,lo,hi=bootstrap_ci(v, seed=42+mi*3+ai)
        rows.append((m,a,mean,lo,hi))
for ai,a in enumerate(ACQS):
    rr=[r for r in rows if r[1]==a]
    y=np.arange(len(MODELS))+(ai-1)*.18
    mean=np.array([r[2] for r in rr]); lo=np.array([r[3] for r in rr]); hi=np.array([r[4] for r in rr])
    axes[1].errorbar(mean,y,xerr=[mean-lo,hi-mean],fmt=['o','s','D'][ai],color=[PINK[1],PINK[2],PINK[3]][ai],mec=INK,mew=.4,label=ACQ_LABEL[a],capsize=2,lw=1.1,ms=4)
axes[1].axvline(0,color='#444',lw=.7)
axes[1].set_yticks(np.arange(len(MODELS)),[MODEL_LABEL[m] for m in MODELS]); axes[1].invert_yaxis()
axes[1].set_xlabel('Mean paired AULC gain (RDKit2D − ECFP4)')
axes[1].set_title('(b) Mean effects with 95% bootstrap CIs', loc='left', fontweight='bold')
axes[1].legend(frameon=False, fontsize=7, loc='lower right')
fig.tight_layout(); save(fig,'figure_main_ci')

# Endpoint heterogeneity as point intervals.
fig, ax = plt.subplots(figsize=(6.5,3.0))
order=['HIA_Hou','DILI','Bioavailability_Ma','BBB_Martins','Pgp_Broccatelli']
labels=['HIA','DILI','Bioavailability','BBB','P-glycoprotein']
for i,d in enumerate(order):
    mean,lo,hi=bootstrap_ci(paired[paired.dataset.eq(d)].gain, seed=100+i)
    ax.errorbar(mean,i,xerr=[[mean-lo],[hi-mean]],fmt='o',color=PINK[3],mec=INK,ecolor=INK,capsize=3,ms=5)
ax.axvline(0,color='#444',lw=.7); ax.set_yticks(range(5),labels); ax.invert_yaxis()
ax.set_xlabel('Mean paired AULC gain (RDKit2D − ECFP4)'); ax.set_title('Representation effect varies substantially by endpoint',loc='left',fontweight='bold')
fig.tight_layout(); save(fig,'figure_endpoint_ci')

# Original endpoint distributional view, recolored to the Figure 1 palette.
fig, ax = plt.subplots(figsize=(6.5,3.0))
vals=[paired[paired.dataset.eq(d)].gain.values for d in order]
bp=ax.boxplot(vals,vert=False,patch_artist=True,labels=labels,showfliers=False,
              boxprops=dict(facecolor=PINK[2],edgecolor=PINK[3],linewidth=.9),
              medianprops=dict(color=PINK[3],linewidth=1.2),
              whiskerprops=dict(color=PINK[3],linewidth=.8),capprops=dict(color=PINK[3],linewidth=.8))
ax.axvline(0,color=INK,lw=.7,ls='--'); ax.set_xlabel('Paired RDKit2D − ECFP4 AULC')
ax.set_title('Representation gains vary substantially by endpoint',loc='left',fontweight='bold',color=INK)
fig.tight_layout(); save(fig,'figure_endpoint_boxplots')

# Representation-by-model interaction in the same palette.
fig, ax = plt.subplots(figsize=(7.0,2.7)); comps=['random_forest','xgboost','lightgbm']; offsets=[-.16,0,.16]
for ci_,comp in enumerate(comps):
    means=[]; los=[]; his=[]
    for ai,a in enumerate(ACQS):
        t=paired[(paired.model.eq('tabpfn'))&(paired.acquisition.eq(a))][['dataset','seed','gain']]
        c=paired[(paired.model.eq(comp))&(paired.acquisition.eq(a))][['dataset','seed','gain']]
        v=t.merge(c,on=['dataset','seed'],suffixes=('_t','_c'))
        mean,lo,hi=bootstrap_ci(v.gain_t-v.gain_c,seed=350+ci_*10+ai); means.append(mean);los.append(lo);his.append(hi)
    xx=np.arange(3)+offsets[ci_]
    ax.errorbar(xx,means,yerr=[np.array(means)-los,np.array(his)-means],fmt=['o','s','D'][ci_],
                color=[PINK[1],PINK[2],PINK[3]][ci_],mec=INK,mew=.5,ecolor=INK,capsize=2,lw=.9,
                label=f"TabPFN minus {MODEL_LABEL[comp]}")
ax.axhline(0,color=INK,lw=.7,ls='--'); ax.set_xticks(range(3),[ACQ_LABEL[a] for a in ACQS]); ax.set_ylabel('Change in paired model contrast\n(RDKit2D − ECFP4)')
ax.set_title('Representation disproportionately improves TabPFN relative to tree ensembles',loc='left',fontweight='bold',color=INK)
ax.legend(frameon=False,ncol=3,fontsize=6.5,loc='upper left'); fig.tight_layout(); save(fig,'figure_interaction')

# Runtime and secondary predictive metrics, aggregate across datasets/seeds/budgets.
metric_frames=[]
for rep,fn in [('ECFP4','ecfp4_metrics.csv'),('RDKit2D','rdkit2d_metrics.csv')]:
    x=pd.read_csv(ROOT/'results'/fn)
    x['representation']=rep
    x['runtime_seconds']=x['fit_runtime']+x['prediction_runtime']+x['acquisition_prediction_runtime']
    metric_frames.append(x)
met=pd.concat(metric_frames,ignore_index=True)
summ=met.groupby(['representation','model','acquisition'],as_index=False).agg(
    auprc=('test_auprc','mean'),brier=('brier','mean'),nll=('nll','mean'),runtime_minutes=('runtime_seconds',lambda s:s.sum()/60))
summ.to_csv(Path(__file__).resolve().parent/'secondary_metrics_summary.csv',index=False)
fig,axes=plt.subplots(1,2,figsize=(7.2,3.0))
rt=summ.groupby(['representation','model'],as_index=False).runtime_minutes.sum()
rx=np.arange(len(MODELS))
for i,rep in enumerate(['ECFP4','RDKit2D']):
    vals=[rt[(rt.representation.eq(rep))&(rt.model.eq(m))].runtime_minutes.iloc[0] for m in MODELS]
    axes[0].bar(rx+(i-.5)*w,vals,w,label=rep,color=[PINK[1],PINK[3]][i],edgecolor=INK,linewidth=.5,hatch=['///',''][i])
axes[0].set_yscale('log'); axes[0].set_xticks(rx,[MODEL_LABEL[m] for m in MODELS],rotation=20,ha='right'); axes[0].set_ylabel('Total runtime (minutes, log scale)'); axes[0].set_title('(a) Computational cost',loc='left',fontweight='bold'); axes[0].legend(frameon=False,fontsize=8)
cal=summ.groupby(['representation','model'],as_index=False)[['brier','nll']].mean()
for i,rep in enumerate(['ECFP4','RDKit2D']):
    sub=cal[cal.representation.eq(rep)]
    axes[1].scatter(sub.brier,sub.nll,s=55,color=[PINK[1],PINK[3]][i],edgecolor=INK,label=rep,zorder=3)
    for _,r in sub.iterrows(): axes[1].annotate(MODEL_LABEL[r.model],(r.brier,r.nll),xytext=(3,2),textcoords='offset points',fontsize=6.5)
axes[1].set_xlabel('Mean Brier score ↓'); axes[1].set_ylabel('Mean NLL ↓'); axes[1].set_title('(b) Probability quality',loc='left',fontweight='bold'); axes[1].legend(frameon=False,fontsize=8)
fig.tight_layout(); save(fig,'figure_secondary_metrics')

# Query similarity: mean and seed-level bootstrap CI for every model/policy/representation.
div=[]
for rep,fn in [('ECFP4','tables_ecfp4/query_diversity.csv'),('RDKit2D','tables_rdkit2d/query_diversity.csv')]:
    q=pd.read_csv(ROOT/'results'/fn); q['representation']=rep; div.append(q)
div=pd.concat(div,ignore_index=True)
fig,ax=plt.subplots(figsize=(6.9,3.2)); xpos=np.arange(len(MODELS)); offsets={'ECFP4':-.16,'RDKit2D':.16}
for ri,rep in enumerate(['ECFP4','RDKit2D']):
  for ai,a in enumerate(ACQS):
    means=[];los=[];his=[]
    for mi,m in enumerate(MODELS):
      v=div[(div.representation.eq(rep))&(div.model.eq(m))&(div.acquisition.eq(a))].mean_within_batch_tanimoto
      mean,lo,hi=bootstrap_ci(v,seed=200+ri*20+ai*4+mi); means.append(mean);los.append(lo);his.append(hi)
    xx=xpos+offsets[rep]+(ai-1)*.08
    ax.errorbar(xx,means,yerr=[np.array(means)-los,np.array(his)-means],fmt=['o','s','D'][ai],color=[PINK[1],PINK[2],PINK[3]][ai],mec=INK,mew=.4,mfc='white' if rep=='ECFP4' else [PINK[1],PINK[2],PINK[3]][ai],label=f'{rep}, {ACQ_LABEL[a]}' if ri==0 or ai==0 else None,capsize=2,lw=.8,ms=4)
ax.set_xticks(xpos,[MODEL_LABEL[m] for m in MODELS]); ax.set_ylabel('Mean within-batch ECFP4 Tanimoto ↓'); ax.set_title('Selection redundancy across representations and policies',loc='left',fontweight='bold')
ax.legend(frameon=False,fontsize=6,ncol=2); fig.tight_layout(); save(fig,'figure_diversity')

paired.to_csv(Path(__file__).resolve().parent/'paired_representation_effects.csv',index=False)
