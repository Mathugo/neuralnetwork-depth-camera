"""Minimal example on how to start a simple Flower server."""
import argparse
from src.server import Server

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
            "--rounds",
            type=int,
            default=1,
            help="Number of rounds of federated learning (default: 1)",
        )
        parser.add_argument(
            "--sample_fraction",
            type=float,
            default=1.0,
            help="Fraction of available clients used for fit/evaluate (default: 1.0)",
        )
        parser.add_argument(
            "--min_sample_size",
            type=int,
            default=2,
            help="Minimum number of clients used for fit/evaluate (default: 2)",
        )
        parser.add_argument(
            "--min_num_clients",
            type=int,
            default=2,
            help="Minimum number of available clients required for sampling (default: 2)",
        )
        parser.add_argument(
            "--log_host",
            type=str,
            help="Logserver address (no default)",
        )
        parser.add_argument(
            "--model",
            type=str,
            default="ResNet18",
            choices=["Net", "ResNet18", "ViT"],
            help="model to train",
        )
        parser.add_argument(
            "--model_path",
            type=str,
            default=None,
            help="path to model's weight"
        )
        parser.add_argument(
            "--batch_size",
            type=int,
            default=32,
            help="training batch size",
        )
        parser.add_argument(
            "--num_workers",
            type=int,
            default=4,
            help="number of workers for dataset reading",
        )
        parser.add_argument("--pin_memory", action="store_true")
        return parser.parse_args()

def main() -> None:
    """Start server and train five rounds."""
    serv = Server(Args.get_args())
    serv.start()

if __name__ == "__main__":
    main()

