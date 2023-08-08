
import torch
import torch.nn.functional as F   # 激励函数的库
from torchvision import datasets
import torchvision.transforms as transforms
import numpy as np
import time


class MLP(torch.nn.Module):   
    def __init__(self):
        super(MLP,self).__init__()    
        self.fc1 = torch.nn.Linear(784,512)  
        self.fc2 = torch.nn.Linear(512,128)  
        self.fc3 = torch.nn.Linear(128,10)  
        
    def forward(self,din):
        din = din.view(-1,28*28)      
        dout = F.relu(self.fc1(din))   
        dout = F.relu(self.fc2(dout))
        dout = F.softmax(self.fc3(dout), dim=1) 
        return dout

def MLP_train():
    n_epochs = 10     
    batch_size = 32  

    train_data = datasets.MNIST(root = './data', train = True, download = True, transform = transforms.ToTensor())
    test_data = datasets.MNIST(root = './data', train = True, download = True, transform = transforms.ToTensor())
    train_loader = torch.utils.data.DataLoader(train_data, batch_size = batch_size, num_workers = 0)
    test_loader = torch.utils.data.DataLoader(test_data, batch_size = batch_size, num_workers = 0)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = MLP()
    model = model.to(device)
    lossfunc = torch.nn.CrossEntropyLoss()
    optimizer = torch.optim.SGD(params = model.parameters(), lr = 0.01)
    for epoch in range(n_epochs):
        for data,target in train_loader:
            start = time.time()
            optimizer.zero_grad()  
            data = data.to(device)
            target = target.to(device)
            output = model(data)   
            loss = lossfunc(output,target)  
            loss.backward()        
            optimizer.step()        
            print(time.time() - start)
MLP_train()
