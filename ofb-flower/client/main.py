import argparse, torch, sys
import flwr as fl
sys.path.append("..")
from utils import load_model, load_cifar
from src.client import CifarClient
# pylint: disable=no-member
DEVICE = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
# pylint: enable=no-member

class Args:
    @staticmethod
    def get_args():
        parser = argparse.ArgumentParser(description="Flower")
        parser.add_argument(
            "--server_address",
            type=str,
            required=True,
            help=f"gRPC server address",
        )
        parser.add_argument(
            "--cid", type=str, required=True, help="Client CID (no default)"
        )
        parser.add_argument(
            "--log_host",
            type=str,
            help="Logserver address (no default)",
        )
        parser.add_argument(
            "--data_dir",
            type=str,
            help="Directory where the dataset lives",
        )
        parser.add_argument(
            "--model",
            type=str,
            default="ResNet18",
            choices=["Net", "ResNet18", "ViT"],
            help="model to train",
        )
        return parser.parse_args()

def main() -> None:
    """Load data, create and start CifarClient."""
    args = Args.get_args()
    # Configure logger
    fl.common.logger.configure(f"client_{args.cid}", host=args.log_host)
    # model
    model = load_model(args.model)
    model.to(DEVICE)
    # load (local, on-device) dataset
    trainset, testset = load_cifar()
    # Start client
    client = CifarClient(args.cid, model, trainset, testset)
    print("[CLIENT] Starting client ..")
    fl.client.start_client(args.server_address, client)

if __name__ == "__main__":
    main()

