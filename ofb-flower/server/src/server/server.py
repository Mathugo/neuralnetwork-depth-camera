import argparse, torchvision, sys
from collections import OrderedDict
sys.path.append("..")
import utils
from typing import Callable, Dict, Optional, Tuple
import flwr as fl
import torch, torchvision

# pylint: disable=no-member
DEVICE = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
# pylint: enable=no-member

class Server:
    def __init__(self, args: argparse.ArgumentParser):
        """ Federated Server - server-side parameter initialization """
        assert (
        args.min_sample_size <= args.min_num_clients
        ), f"Num_clients shouldn't be lower than min_sample_size"
        self._args = args

        # Configure logger
        fl.common.logger.configure("server", host=args.log_host)
        print("[SERVER] Loading data ..")
        # Load evaluation data
        _, testset = utils.load_cifar(download=True)
        print("[SERVER] Loading model and weights ..")
        # model
        self._model = utils.load_model(self._args.model, 10)

        if self._args.model_path != None:
            # TODO load_weight from .pt
            pass
        # initial weight
        self._model_weight = utils.get_weights(self._model)
        print("[SERVER] Done")

        # Create client_manager, strategy, and server
        self._client_manager = fl.server.SimpleClientManager()

        self._strategy = fl.server.strategy.FedAvg(
            fraction_fit=args.sample_fraction,
            min_fit_clients=args.min_sample_size,
            min_available_clients=args.min_num_clients,
            eval_fn=self._get_eval_fn(testset),
            on_fit_config_fn=self._fit_config,
            on_evaluate_config_fn=self._evaluate_config,
            initial_parameters=fl.common.weights_to_parameters(self._model_weight)
        )
        self._server = fl.server.Server(client_manager=self._client_manager, strategy=self._strategy)

    def _evaluate_config(self, rnd: int):
        """Return evaluation configuration dict for each round.

        Perform five local evaluation steps on each client (i.e., use five
        batches) during rounds one to three, then increase to ten local
        evaluation steps.
        """
        val_steps = 5 if rnd < 4 else 10
        return {"val_steps": val_steps}

    def _fit_config(self, rnd: int) -> Dict[str, fl.common.Scalar]:
        """Return a configuration with static batch size and (local) epochs."""
        config = {
        "epoch_global": str(rnd),
        "epochs": str(1),
        "batch_size": str(self._args.batch_size),
        "num_workers": str(self._args.num_workers),
        "pin_memory": str(self._args.pin_memory),
        }
        return config

    def _get_eval_fn(
        self,
        testset: torchvision.datasets.CIFAR10,
    ) -> Callable[[fl.common.Weights], Optional[Tuple[float, float]]]:
        """Return an evaluation function for centralized evaluation."""

        def evaluate(weights: fl.common.Weights) -> Optional[Tuple[float, float]]:
            """Use the entire CIFAR-10 test set for evaluation."""
            # TODO check is eval loss is better than before 

            self._model.to(DEVICE)
            utils.set_weights(self._model, weights)
            testloader = torch.utils.data.DataLoader(testset, batch_size=32, shuffle=False)
            loss, accuracy = utils.test(self._model, testloader, device=DEVICE)
            return loss, {"accuracy": accuracy}

        return evaluate
    
    def start(self):
        # Run server
        fl.server.start_server(
            server_address=self._args.server_address,
            server=self._server,
            config={"num_rounds": self._args.rounds},
        )