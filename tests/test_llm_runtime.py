import numpy as np
import shutil
import torch
import unittest

from transformers import AutoTokenizer, TextStreamer
from intel_extension_for_transformers.transformers import AutoModel, WeightOnlyQuantConfig, AutoModelForCausalLM
from intel_extension_for_transformers.llm.runtime.graph.scripts.convert import convert_model
from intel_extension_for_transformers.llm.runtime.graph import Model

def cmpData(numa, numb):
    totalErr = ((np.abs(numa - numb))**2).sum()
    totalNum = (np.abs(numa)**2).sum()
    diff2 = np.sqrt(totalErr/totalNum)

    cos = np.dot(numa, numb)/(np.linalg.norm(numa)*np.linalg.norm(numb))
    return {"diff2": diff2, "cos": cos}

class TestLLMRUNTIME(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree("./runtime_outs", ignore_errors=True)

    def test_llm_runtime(self):
        model_name = "/tf_dataset2/models/nlp_toolkit/llama-2-7b-chat/Llama-2-7b-chat-hf"
        woq_config = WeightOnlyQuantConfig(compute_dtype="int8", weight_dtype="int4", use_cache=True, not_quant=True)
        prompt = "What is the meaning of life?"

        tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
        inputs = tokenizer(prompt, return_tensors="pt")

        # pytorch fp32
        pt_model = AutoModelForCausalLM.from_pretrained(model_name, trust_remote_code=True)
        pt_model.eval() 
        pt_logits = pt_model(input_ids=inputs.input_ids).logits[:,-1]
        pt_generate_ids = pt_model.generate(input_ids=inputs.input_ids, do_sample=False, max_new_tokens=100)[0].tolist()
        print(tokenizer.decode(pt_generate_ids))

        itrex_model = AutoModel.from_pretrained(model_name, quantization_config=woq_config, use_llm_runtime=True, trust_remote_code=True)
        itrex_outputs = itrex_model(inputs.input_ids)
        itrex_generate_ids = itrex_model.generate(inputs.input_ids, do_sample=False, max_new_tokens=100)[0]
        print(tokenizer.decode(itrex_generate_ids))
        print(cmpData(pt_logits.detach().numpy().flatten(), itrex_outputs.flatten()))

        for i in range(len(pt_generate_ids)):
            self.assertEqual(pt_generate_ids[i], itrex_generate_ids[i])

    def test_beam_search(self):
        model_name = "/tf_dataset2/models/pytorch/gpt-j-6B"  # or local path to model
        prompts = [
           "she opened the door and see",
           "tell me 10 things about jazz music",
           "What is the meaning of life?",
           "To be, or not to be, that is the question: Whether 'tis nobler in the mind to suffer"\
            " The slings and arrows of outrageous fortune, "\
            "Or to take arms against a sea of troubles."\
            "And by opposing end them. To die—to sleep,"
            ]

        tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True,
                                                  padding_side="left")
        tokenizer.pad_token = tokenizer.eos_token
        pad_token = tokenizer(tokenizer.pad_token)['input_ids'][0]
        inputs = tokenizer(prompts, padding=True, return_tensors='pt')

        # pytorch fp32
        pt_model = AutoModelForCausalLM.from_pretrained(model_name, trust_remote_code=True)
        pt_model.eval()
        pt_generate_ids = pt_model.generate(**inputs, max_new_tokens=128, min_new_tokens=30,
                                            early_stopping=True, num_beams=4).tolist()
        # llm runtime fp32
        woq_config = WeightOnlyQuantConfig(not_quant=True)
        itrex_model = AutoModelForCausalLM.from_pretrained(
            model_name, quantization_config=woq_config, trust_remote_code=True)
        itrex_generate_ids = itrex_model.generate(
            inputs.input_ids, num_beams=4, max_new_tokens=128, min_new_tokens=30, early_stopping=True, pad_token=pad_token)
        for i in range(len(itrex_generate_ids)):
            self.assertListEqual(pt_generate_ids[i], itrex_generate_ids[i])


if __name__ == "__main__":
    unittest.main()
