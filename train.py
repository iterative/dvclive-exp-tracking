import os

import pytorch_lightning as pl

from dvclive.lightning import DVCLiveLogger
from torch import optim, nn, utils, Tensor
from torchvision.datasets import MNIST
from torchvision.transforms import ToTensor


# define the LightningModule
class LitAutoEncoder(pl.LightningModule):
    def __init__(self, encoder_size):
        super().__init__()

        # Saves any args passed to __init__ (for example, encoder_size)
        self.save_hyperparameters()

        self.encoder = nn.Sequential(nn.Linear(28 * 28, encoder_size), nn.ReLU(), nn.Linear(encoder_size, 3))
        self.decoder = nn.Sequential(nn.Linear(3, encoder_size), nn.ReLU(), nn.Linear(encoder_size, 28 * 28))

    def training_step(self, batch, batch_idx):
        # training_step defines the train loop.
        # it is independent of forward
        x, y = batch
        x = x.view(x.size(0), -1)
        z = self.encoder(x)
        x_hat = self.decoder(z)
        loss = nn.functional.mse_loss(x_hat, x)
        # Logging to TensorBoard by default
        self.log("train_loss", loss)
        return loss

    def configure_optimizers(self):
        optimizer = optim.Adam(self.parameters(), lr=1e-3)
        return optimizer


# setup data
dataset = MNIST(os.getcwd(), download=True, transform=ToTensor())
train_loader = utils.data.DataLoader(dataset)

# train the model
autoencoder = LitAutoEncoder(encoder_size=64)
trainer = pl.Trainer(limit_train_batches=100, max_epochs=5, logger=DVCLiveLogger(save_dvc_exp=True))
trainer.fit(model=autoencoder, train_dataloaders=train_loader)