import unsloth
import torch


print(f"Torch version: {torch.__version__}")
print(f"CUDA version:{torch.version.cuda}")
if torch.cuda.is_available():
    print("CUDA available")
    device = torch.device("cuda")
    print(f"Device name: {torch.cuda.get_device_name(device)}")
    print(f"Device type: {torch.cuda.current_device()}")
    print(f"VRAM available: {torch.cuda.mem_get_info()}")


