import sys,numpy as np
from PIL import Image
from scipy import ndimage as nd
from scipy.cluster.vq import kmeans2
src,k,out,L=sys.argv[1],int(sys.argv[2]),sys.argv[3],int(sys.argv[4])
im=Image.open(src).convert('RGB')
s=L/max(im.size); im=im.resize((round(im.width*s),round(im.height*s)),Image.LANCZOS)
a=np.asarray(im).astype(np.float32); H,W,_=a.shape
lab=a.reshape(-1,3)
np.random.seed(0); samp=lab[np.random.choice(len(lab),200000)]
C,_=kmeans2(samp,k,minit='++',seed=1,iter=30)
# assign in chunks
lb=np.empty(len(lab),np.int32)
for i in range(0,len(lab),2_000_000):
    d=((lab[i:i+2_000_000,None,:]-C[None])**2).sum(2); lb[i:i+2_000_000]=d.argmin(1)
lb=lb.reshape(H,W)
# smooth labels: blur one-hot
sig=float(sys.argv[5]) if len(sys.argv)>5 else 3
P=np.stack([nd.gaussian_filter((lb==c).astype(np.float32),sig) for c in range(k)]); lb=P.argmax(0)
border=np.concatenate([lb[0],lb[-1],lb[:,0],lb[:,-1]])
bc=np.bincount(border,minlength=k)/len(border)
bg=[c for c in range(k) if bc[c]>0.05]
cols=np.array([a[lb==c].mean(0) if (lb==c).any() else [0,0,0] for c in range(k)])
print('clusters',[(c,cols[c].astype(int).tolist(),round(bc[c],2),round((lb==c).mean(),3)) for c in range(k)],'bg',bg)
fg=~np.isin(lb,bg)
n_l,n=nd.label(fg); sz=nd.sum(fg,n_l,range(1,n+1))
fg&=np.concatenate([[False],sz>=(L/4500)**2*1500])[n_l]
# fill tiny bg holes (specks) but keep real negative space
h_l,hn=nd.label(~fg); hs=nd.sum(~fg,h_l,range(1,hn+1))
fg|=np.concatenate([[False],hs<(L/4500)**2*300])[h_l]
# reassign filled pixels' label to nearest fg label
_,(iy,ix)=nd.distance_transform_edt(np.isin(lb,bg)&fg,return_indices=True)
lb=lb[iy,ix]
rgb=cols[lb]
alpha=nd.gaussian_filter(fg.astype(np.float32),1.0)
alpha=np.clip((alpha-0.5)*2.2+0.5,0,1)
# colour AA between fg classes
rgb=np.stack([nd.gaussian_filter(rgb[...,i],0.7) for i in range(3)],-1)
ys,xs=np.where(alpha>0); p=30
o=np.dstack([rgb,alpha*255]).clip(0,255).astype(np.uint8)[max(ys.min()-p,0):ys.max()+p,max(xs.min()-p,0):xs.max()+p]
Image.fromarray(o,'RGBA').save(out,dpi=(300,300)); print(o.shape)
