import numpy as np
from PIL import Image
from scipy import ndimage as nd
im=np.asarray(Image.open('method-trials/12/x4anime.png').convert('RGB')).astype(np.float32)
mn=im.min(2)
near=mn>228  # near-white candidate
lab,_=nd.label(near)
border=np.unique(np.concatenate([lab[0],lab[-1],lab[:,0],lab[:,-1]])); border=border[border>0]
bg=np.isin(lab,border)
# soft edge: in a 3px band around bg, alpha from whiteness
band=nd.binary_dilation(bg,iterations=6)&~bg
a=np.ones(mn.shape,np.float32)
w=np.clip((245-mn)/(245-150),0,1)
a[band]=w[band]; a[bg]=0
a=np.where(band|bg, nd.gaussian_filter(a,1.0), a)
a[bg & ~nd.binary_dilation(~bg,iterations=2)]=0
# decontaminate: edge pixels take colour of nearest solid pixel
solid=a>=0.98
_,(iy,ix)=nd.distance_transform_edt(~solid,return_indices=True)
rgb=im.copy(); e=~solid
rgb[e]=im[iy[e],ix[e]]
out=np.dstack([rgb,a*255]).astype(np.uint8)
ys,xs=np.where(a>0.05); pad=40
out=out[max(ys.min()-pad,0):ys.max()+pad, max(xs.min()-pad,0):xs.max()+pad]
o=Image.fromarray(out,'RGBA'); s=4500/o.width
o=o.resize((4500,round(o.height*s)),Image.LANCZOS)
o.save('12-ranch-water.png',dpi=(375,375))
p=Image.new('RGB',o.size,'white'); p.paste(o,mask=o.split()[3]); p.save('crops/12-ranch-water-preview.png')
# interior whites retained count
print(o.size, 'interior near-white px kept:', int((near&~bg).sum()))
c=o.crop((3150,2700,3900,3450)); ck=Image.new('RGB',c.size,(40,60,40)); ck.paste(c,mask=c.split()[3]); ck.save('crops/12-glass-on-dark.png')
