from collections import OrderedDict
import numpy as np
import flwr as fl
import torch, sys
sys.path.append("..")
from models import *
from pathlib import Path
from typing import Tuple
from time import time

DATA_ROOT = Path("data")

""" train test load """
def load_model(model_name: str, n_classes=10, img_size=32) -> nn.Module:

    if model_name == "Net":
        return Net()
    elif model_name == "ResNet18":
        return ResNet18()
    elif model_name == "ViT":
        return ViT(n_classes=n_classes, img_size=img_size, emb_size=98)
    else:
        raise NotImplementedError(f"model {model_name} is not implemented")
# pylint: disable=unused-argument
def load_cifar(download=True) -> Tuple[datasets.CIFAR10, datasets.CIFAR10]:
    """Load CIFAR-10 (training and test set)."""
    transform = transforms.Compose(
        [
            transforms.ToTensor(),
            transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010)),
        ]
    )
    trainset = datasets.CIFAR10(
        root=DATA_ROOT / "cifar-10", train=True, download=download, transform=transform
    )
    testset = datasets.CIFAR10(
        root=DATA_ROOT / "cifar-10", train=False, download=download, transform=transform
    )
    return trainset, testset

def get_weights(model: torch.nn.ModuleList) -> fl.common.Weights:
    """Get model weights as a list of NumPy ndarrays."""
    return [val.cpu().numpy() for _, val in model.state_dict().items()]

def set_weights(model: torch.nn.ModuleList, weights: fl.common.Weights) -> None:
    """Set model weights from a list of NumPy ndarrays."""
    state_dict = OrderedDict(
        {
            k: torch.tensor(np.atleast_1d(v))
            for k, v in zip(model.state_dict().keys(), weights)
        }
    )
    model.load_state_dict(state_dict, strict=True)

# TODO Criterion focal loss for unbalanced dataset

def train(
    net: Net,
    trainloader: torch.utils.data.DataLoader,
    epochs: int,
    device: torch.device,  # pylint: disable=no-member
) -> None:
    """Train the network."""
    # Define loss and optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.SGD(net.parameters(), lr=0.001, momentum=0.9)

    print(f"Training {epochs} epoch(s) w/ {len(trainloader)} batches each")
    t = time()
    # Train the network
    print_interval = 10
    for epoch in range(epochs):  # loop over the dataset multiple times
        running_loss = 0.0
        for i, data in enumerate(trainloader, 0):
            images, labels = data[0].to(device), data[1].to(device)

            # zero the parameter gradients
            optimizer.zero_grad()

            # forward + backward + optimize
            outputs = net(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            # print statistics
            running_loss += loss.item()
            if (i+1) % print_interval == 0: 
                print("[%d, %d] loss: %.3f" % (epoch + 1, i*len(images), running_loss / i))
                #running_loss = 0.0

    print(f"Epoch took: {time() - t:.2f} seconds")

def test(
    net: Net,
    testloader: torch.utils.data.DataLoader,
    device: torch.device,  # pylint: disable=no-member
) -> Tuple[float, float]:
    """Validate the network on the entire test set."""
    criterion = nn.CrossEntropyLoss()
    correct = 0
    total = 0
    loss = 0.0
    print_interval = 10
    print("[Sample | Batch]")
    with torch.no_grad():
        for i, data in enumerate(testloader, 0):
            images, labels = data[0].to(device), data[1].to(device)
            outputs = net(images)
            loss += criterion(outputs, labels).item()
            _, predicted = torch.max(outputs.data, 1)  # pylint: disable=no-member
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
            if (i+1)%print_interval == 0: 
                print("[%d, %d] loss: %.3f accuracy %.3f" % ( i+ 1, i*len(images), loss/i, (correct / total)*100) )

    accuracy = correct / total
    return loss, accuracy
