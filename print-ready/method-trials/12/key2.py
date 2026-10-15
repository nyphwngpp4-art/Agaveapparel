import numpy as np
from PIL import Image
from scipy import ndimage as nd
im=np.asarray(Image.open('method-trials/12/x4anime.png').convert('RGBA')).astype(np.float32)
rgb=im[...,:3].copy(); a=im[...,3]/255
a[a<0.04]=0
# drop tiny isolated specks
lab,n=nd.label(a>0); sz=nd.sum(np.ones_like(a),lab,range(1,n+1))
keep=np.concatenate([[False],sz>=400]); a[~keep[lab]]=0
solid=a>=0.9
_,(iy,ix)=nd.distance_transform_edt(~solid,return_indices=True)
e=~solid; rgb[e]=rgb[iy[e],ix[e]]; rgb[a==0]=0
out=np.dstack([rgb,a*255]).astype(np.uint8)
ys,xs=np.where(a>0); pad=40
out=out[max(ys.min()-pad,0):ys.max()+pad, max(xs.min()-pad,0):xs.max()+pad]
o=Image.fromarray(out,'RGBA'); s=4500/o.width
o=o.resize((4500,round(o.height*s)),Image.LANCZOS)
o.save('12-ranch-water.png',dpi=(375,375))
p=Image.new('RGB',o.size,'white'); p.paste(o,mask=o.split()[3]); p.save('crops/12-ranch-water-preview.png')
print(o.size,n)
for nm,box in [('glass',(3300,2900,4300,3900)),('text',(300,1100,1500,1900)),('soda',(1350,2600,2050,3500))]:
  c=o.crop(box);k=Image.new('RGB',c.size,(40,70,50));k.paste(c,mask=c.split()[3]);k.save(f'crops/12-{nm}-on-dark.png')
d=Image.new('RGB',o.size,(40,70,50));d.paste(o,mask=o.split()[3]);d.resize((900,1125)).save('crops/12-on-dark-small.png')
