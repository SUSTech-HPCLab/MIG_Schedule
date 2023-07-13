import torch
def unet():
    return torch.hub.load('mateuszbuda/brain-segmentation-pytorch', 'unet',
    in_channels=3, out_channels=1, init_features=32, pretrained=True)

model = unet
model = model().cuda(0).eval()

input =  torch.randn(32, 3, 256, 256).cuda(0)

torch.cuda.synchronize()
with torch.no_grad():
    for i in range(0, 100):
        output= model(input).cpu()