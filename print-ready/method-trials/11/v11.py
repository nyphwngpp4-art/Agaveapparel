from PIL import Image
import numpy as np, vtracer, cairosvg
from scipy.ndimage import gaussian_filter
from sklearn.cluster import KMeans
src='/home/box/agent-data/agents/318d93b2-b422-4a32-9848-e92f3e7899f4/attachments/1cb94f24ce20e9ed0cda7270c8084068248d826459f2e1c325aab620685d055b.png'
im=np.array(Image.open(src).convert('RGBA')).astype(float); H,W=im.shape[:2]
pal=np.array([[221,179,118],[154,70,23],[129,134,107],[168,97,53],[198,125,72]],float)
px=im[...,:3].reshape(-1,3); d=((px[:,None]-pal[None])**2).sum(-1)
lab=d.argmin(1); cream=(px.mean(1)>200)&(px[:,2]>150)  # light halo/bg-ish -> transparent
op=(im[...,3].reshape(-1)>128)&~cream
S=10; maps=[]
for k in range(5):
  m=((lab==k)&op).reshape(H,W).astype(float)
  m=np.array(Image.fromarray((m*255).astype(np.uint8)).resize((W*S,H*S),Image.BICUBIC)).astype(float)
  maps.append(gaussian_filter(m,9))
bgm=np.array(Image.fromarray(((~op).reshape(H,W)*255).astype(np.uint8)).resize((W*S,H*S),Image.BICUBIC)).astype(float)
maps.append(gaussian_filter(bgm,9))
L=np.argmax(np.stack(maps),0)
out=np.zeros((H*S,W*S,4),np.uint8)
for k in range(5): out[L==k,:3]=pal[k]; out[L==k,3]=255
Image.fromarray(out).save('/tmp/q11b.png')
vtracer.convert_image_to_svg_py('/tmp/q11b.png','11-agave-to-tequila.svg',colormode='color',hierarchical='stacked',mode='spline',filter_speckle=200,color_precision=8,layer_difference=1,corner_threshold=60,length_threshold=8,splice_threshold=45,path_precision=2)
cairosvg.svg2png(url='11-agave-to-tequila.svg',write_to='/tmp/r.png',output_width=4500)
p=Image.open('/tmp/r.png'); p.save('11-agave-to-tequila.png',dpi=(300,300)); print(p.size)
bg=Image.new('RGBA',p.size,(30,30,30,255));bg.alpha_composite(p);bg.convert('RGB').resize((1500,590)).save('/tmp/dark3.png')
