## Only openvino 2021 works
from pathlib import PosixPath
import blobconverter
import onnx
from os import path

__VERSION__ = "2021.4"

class Pipeline(object):
    def __init__(self) -> None:
        """ from weights file .pt --> export to onnx --> prune onnx -> use mo model optimizer -> blobconverter form bin and xml (choose shaves carefully)"""
        """
        !mo \
        --input_model /content/gear_yolov5s_pruned.onnx \
        --model_name yolov5 \
        --data_type FP16 \
        --output_dir /content/ \
        --reverse_input_channel \
        --scale 255 \
        --output "output1_yolov5,output2_yolov5,output3_yolov5"
        """
    
    @staticmethod
    def prune_onnx(self, onnx_model: str, output_dir: str="output", output_model: str="pruned.onnx") -> None:
        """Prune yolov5 onnx model to be run on edge """
        print("[*] Pruning model {} ..".format(onnx_model))
        onnx_model = onnx.load(onnx_model)
        conv_indices = []
        for i, n in enumerate(onnx_model.graph.node):
            if "Conv" in n.name:
                conv_indices.append(i)

        input1, input2, input3 = conv_indices[-3:]
        sigmoid1 = onnx.helper.make_node(
            'Sigmoid',
            inputs=[onnx_model.graph.node[input1].output[0]],
            outputs=['output1_yolov5'],
        )

        sigmoid2 = onnx.helper.make_node(
            'Sigmoid',
            inputs=[onnx_model.graph.node[input2].output[0]],
            outputs=['output2_yolov5'],
        )

        sigmoid3 = onnx.helper.make_node(
            'Sigmoid',
            inputs=[onnx_model.graph.node[input3].output[0]],
            outputs=['output3_yolov5'],
        )

        onnx_model.graph.node.append(sigmoid1)
        onnx_model.graph.node.append(sigmoid2)
        onnx_model.graph.node.append(sigmoid3)
        output_path = path.join(output_dir, output_model)
        print("[*] Done, now saving to {} ..".format(output_path))
        onnx.save(onnx_model, output_path)
        print("[*] Done")

    @staticmethod
    def convert_to_blob(type: str="onnx", shaves: int=6, output_dir: str="output", onnx_model: str=None, xml_file: str=None) -> PosixPath:
        """Convert a model (pytorch or openvino) to a blob model for the Myriad X 
        shaves: int=4 -> shaves are vector processors in DepthAI/OAK. For 1080p image, 13 SHAVES (of 16) are free for neural network stuff.
        """
        print("[!] Converting openvino model to blob format ..")
        if type == "onnx":
            blob_path = blobconverter.from_onnx(
                model=onnx_model,
                data_type="FP16",
                shaves=shaves,
                version=__VERSION__,
                use_cache=False,
                output_dir=output_dir
            )
        elif type == "ir":
            blob_path = blobconverter.from_openvino(
                xml=xml_file,
                bin=xml_file.replace('.xml','.bin'),
                data_type="FP16",
                shaves=shaves,
                version=__VERSION__,
                use_cache=False,
                output_dir=output_dir
            )
        print("[*] Done, saved to {}".format(output_dir))
        return blob_path
