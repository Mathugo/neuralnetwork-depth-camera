import argparse
from src.utils import load_model, load_cifar
from src.client import CifarClient, get_weights, set_weights

def main() -> None:
    """Load data, create and start CifarClient."""
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
        choices=["Net", "ResNet18"],
        help="model to train",
    )
    args = parser.parse_args()

    # Configure logger
    fl.common.logger.configure(f"client_{args.cid}", host=args.log_host)

    # model
    model = utils.load_model(args.model)
    model.to(DEVICE)
    # load (local, on-device) dataset
    trainset, testset = utils.load_cifar()

    # Start client
    client = CifarClient(args.cid, model, trainset, testset)
    fl.client.start_client(args.server_address, client)


if __name__ == "__main__":
    main()
