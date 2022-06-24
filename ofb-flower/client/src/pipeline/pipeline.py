from torch.utils.data import Dataset
import pandas as pd
import torch, os, sys
from skimage import io
import numpy as np
from torchvision import transforms, datasets


sys.path.append("../..")
from models import *


""" torch transforms """

mobile_ViT_transform = {
    'train': transforms.Compose([
        transforms.Resize(224),
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])]),

    'val': transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
}

""" Ex : 
data_dir = 'data/hymenoptera_data'
image_datasets = {x: datasets.ImageFolder(os.path.join(data_dir, x),
                                          data_transforms[x])
                  for x in ['train', 'val']}
dataloaders = {x: torch.utils.data.DataLoader(image_datasets[x], batch_size=4,
                                             shuffle=True, num_workers=4)
              for x in ['train', 'val']}
dataset_sizes = {x: len(image_datasets[x]) for x in ['train', 'val']}
class_names = image_datasets['train'].classes

"""

class GearDataset(Dataset):
    """ Gear Dataset """
    
    def __init__(self, csv_file: str, root_dir: str, transform=None):
        """
        Args:
            csv_file (string): Path to the csv file with annotations.
            root_dir (string): Directory with all the images.
            transform (callable, optional): Optional transform to be applied
                on a sample.
        """
        self._gear_labels = pd.read_csv(csv_file, delimiter=',')
        self._root_dir = root_dir
        self._transform = transform

    def __len__(self) -> int:
        return len(self._gear_labels)
    
    def __getitem__(self, idx: int):
        if torch.is_tensor(idx):
            idx = idx.tolist()

        img_name = os.path.join(self._root_dir,
                                self._gear_labels.iloc[idx, 0])
        image = io.imread(img_name)
        labels = self._gear_labels.iloc[idx, 1:]
        labels = np.array([labels])
        sample = {'image': image, 'labels': labels}

        if self.transform:
            sample = self.transform(sample)
        return sample




