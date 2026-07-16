import torch
import tiktoken
import os
# Class name change: GPTModel -> GPT
from .elysium_model import GPT, GPTConfig 

# Naye architecture ke hisaab se config
config = GPTConfig(
    block_size=1024,
    vocab_size=50257,
    n_layer=24,
    n_head=16,
    n_embd=1024
)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
tokenizer = tiktoken.get_encoding("gpt2")

def load_slm():
    # Nayi class use kar rahe hain
    model = GPT(config)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(current_dir, "gpt2-medium355M-sft.pth")
    #model_path = os.path.join("backend", "model", "gpt2-medium355M-sft.pth")
    
    # Weights load karo
    state_dict = torch.load(model_path, map_location=device, weights_only=True, mmap=True)
    model.load_state_dict(state_dict)
    
    model.to(device)
    model.eval()
    return model

print(f"Loading SLM on {device}...")
slm_model = load_slm()

def generate_response(prompt):
    formatted_prompt = f"Below is an instruction that describes a task. Write a response that appropriately completes the request.\n\n### Instruction:\n{prompt}\n\n### Response:\n"
    
    input_ids = torch.tensor(tokenizer.encode(formatted_prompt)).unsqueeze(0).to(device)
    
    # Nayi generate method use kar rahe hain jo class ke andar hi hai
    with torch.no_grad():
        out_ids = slm_model.generate(
            input_ids, 
            max_new_tokens=100, 
            temperature=0.5, # Diverse responses ke liye
            top_k=50        # Sirf best tokens chunne ke liye
        )
    
    full_response = tokenizer.decode(out_ids.squeeze(0).tolist())
    
    # Response clean karo
    if "### Response:" in full_response:
        response_only = full_response.split("### Response:")[-1].strip()
    else:
        response_only = full_response
        
    return response_only.replace("<|endoftext|>", "").strip()

if __name__ == "__main__":
    query = "Hi, how are you?"
    print(f"User: {query}")
    print(f"SLM: {generate_response(query)}")