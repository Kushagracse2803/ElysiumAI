import torch
import tiktoken
import os
import sys

# --- PATH SETUP (Flat Structure Fix) ---
# Kyunki weights aur model file ab isi folder mein hain
current_dir = os.path.dirname(os.path.abspath(__file__))

# Import locally from the same directory
from .elysium_model import GPT, GPTConfig

def run_test():
    print("🚀 Launching Elysium (SFT Instruction Mode)...")
    
    # 1. Architecture Config (355M Model Parameters)
    # n_layer=24 aur n_embd=1024 gpt2-medium ke liye zaroori hain
    config = GPTConfig(
        block_size=1024, 
        vocab_size=50257, 
        n_layer=24, 
        n_head=16, 
        n_embd=1024
    )
    model = GPT(config)
    
    # Weights ab script ke pados mein hi hain
    weights_path = os.path.join(current_dir, "gpt2-medium355M-sft.pth")
    
    if not os.path.exists(weights_path):
        print(f"❌ Weights not found at {weights_path}")
        print("💡 Tip: Ensure the .pth file is in the same folder as this script.")
        return

    try:
        print("⏳ Mapping weights with mmap (Low RAM Mode)...")
        # map_location="cpu" use kar rahe hain kyunki CUDA available nahi mila tha
        state_dict = torch.load(
            weights_path, 
            map_location="cpu", 
            weights_only=True, 
            mmap=True
        )
        model.load_state_dict(state_dict, strict=True)
        print("✅ SUCCESS: Elysium is Online!")
        
    except Exception as e:
        print(f"❌ Load Failed: {e}")
        return

    model.eval()
    enc = tiktoken.get_encoding("gpt2")

    print("\n--- Terminal Ready (Type 'exit' to quit) ---")
    
    while True:
        user_input = input("\nUser >>> ")
        if user_input.lower() in ['exit', 'quit']: 
            break
        if not user_input.strip(): 
            continue
        
        # 2. SFT Prompt Template
        # Is template ke bina model instructions sahi se decode nahi kar payega
        prompt = (
            "Below is an instruction that describes a task. "
            "Write a response that appropriately completes the request.\n\n"
            f"### Instruction:\n{user_input}\n\n### Response:\n"
        )
        
        input_ids = enc.encode(prompt)
        context = torch.tensor([input_ids], dtype=torch.long)
        
        print("Elysium is thinking...", end="\r")
        
        with torch.no_grad():
            # 3. Generation Logic (Matches your updated model.py)
            result_tokens = model.generate(
                context, 
                max_new_tokens=50, # Thoda lamba response allow karte hain 
                temperature=0.4, 
                top_k=50
            )
            
        # 4. Clean Output Parsing
        full_text = enc.decode(result_tokens[0].tolist())
        
        # Sirf Response wala part nikalna hai aur garbage tokens clean karne hain
        try:
            if "### Response:" in full_text:
                response_part = full_text.split("### Response:")[1]
                clean_response = response_part.split("<|endoftext|>")[0]
                print(f"Elysium >>> {clean_response.strip()}")
            else:
                print(f"Elysium >>> {full_text.strip()}")
        except Exception:
            print(f"Elysium >>> {full_text.strip()}")

if __name__ == "__main__":
    run_test()