import sys,json,numpy as np
from PIL import Image
from scipy import ndimage as nd
from scipy.cluster.vq import kmeans2
cfg=json.loads(sys.argv[1])
src,out,L=cfg['src'],cfg['out'],cfg.get('L',4500); w=cfg.get('w',3.0); sig=cfg.get('sig',3)
im=Image.open(src).convert('RGB')
if 'crop' in cfg: im=im.crop(cfg['crop'])
s=L/max(im.size); im=im.resize((round(im.width*s),round(im.height*s)),Image.LANCZOS)
a=np.asarray(im).astype(np.float32); H,W,_=a.shape
def feat(x): return np.concatenate([x,w*(x[...,1:2]-x[...,0:1]),w*(x[...,1:2]-x[...,2:3])],-1)
F=feat(a).reshape(-1,5)
if 'pal' in cfg: C=feat(np.array(cfg['pal'],np.float32))
else:
    np.random.seed(0); C,_=kmeans2(F[np.random.choice(len(F),200000)],cfg['k'],minit='++',seed=1,iter=30)
k=len(C); lb=np.empty(len(F),np.int32)
for i in range(0,len(F),1_000_000):
    lb[i:i+1_000_000]=((F[i:i+1_000_000,None,:]-C[None])**2).sum(2).argmin(1)
lb=lb.reshape(H,W); core=lb.copy()
P=np.stack([nd.gaussian_filter((lb==c).astype(np.float32),sig) for c in range(k)]); lb=P.argmax(0); del P
# merge small components of any class into neighbours
minA=cfg.get('minA',800)
for it in range(2):
    bad=np.zeros((H,W),bool)
    for c in range(k):
        if c in cfg.get('keep',[]): continue
        l,n=nd.label(lb==c)
        if n: sz=nd.sum(np.ones_like(lb),l,range(1,n+1)); bad|=np.concatenate([[False],sz<minA])[l]
    _,(iy,ix)=nd.distance_transform_edt(bad,return_indices=True); lb=lb[iy,ix]
border=np.concatenate([lb[0],lb[-1],lb[:,0],lb[:,-1]]); bc=np.bincount(border,minlength=k)/len(border)
cols=[]
for c in range(k):
    m=(lb==c)&(core==c); cols.append(a[m].mean(0) if m.any() else a[lb==c].mean(0) if (lb==c).any() else np.zeros(3))
cols=np.array(cols)
if cfg.get('usepal'): cols=np.array(cfg['pal'],np.float32)
if 'force' in cfg:
    for c,v in cfg['force'].items(): cols[int(c)]=v
bg=cfg.get('bg',[c for c in range(k) if bc[c]>0.05])
print('clusters',[(c,cols[c].astype(int).tolist(),round(bc[c],2),round((lb==c).mean(),3)) for c in range(k)],'bg',bg,flush=True)
fg=~np.isin(lb,bg)
if cfg.get('outside_only'):  # bg only where connected to outside
    l,n=nd.label(~fg); edge=set(np.unique(np.concatenate([l[0],l[-1],l[:,0],l[:,-1]])))-{0}
    fg=~np.isin(l,list(edge))
if cfg.get('holeFill'):
    l,n=nd.label(~fg); hs=nd.sum(~fg,l,range(1,n+1)); fg|=np.concatenate([[False],hs<cfg['holeFill']])[l]
    lbl=lb.copy(); m=np.isin(lb,bg)&fg; _,(iy,ix)=nd.distance_transform_edt(m,return_indices=True); lb=lb[iy,ix]
l,n=nd.label(fg); sz=nd.sum(fg,l,range(1,n+1)); fg&=np.concatenate([[False],sz>=cfg.get('minFg',1500)])[l]
rgb=cols[lb]
if bg:
    m=np.isin(lb,bg)
    _,(iy,ix)=nd.distance_transform_edt(m,return_indices=True); rgb=rgb[iy,ix]
rgb=np.stack([nd.gaussian_filter(rgb[...,i],0.7) for i in range(3)],-1)
alpha=np.clip((nd.gaussian_filter(fg.astype(np.float32),1.0)-0.5)*2.2+0.5,0,1)
ys,xs=np.where(alpha>0); p=30
o=np.dstack([rgb,alpha*255]).clip(0,255).astype(np.uint8)[max(ys.min()-p,0):ys.max()+p,max(xs.min()-p,0):xs.max()+p]
Image.fromarray(o,'RGBA').save(out,dpi=(300,300)); print(o.shape)
