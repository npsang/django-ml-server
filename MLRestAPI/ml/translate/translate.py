from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

class Translate:
    def __init__(self) -> None:
        self.tokenizer_vi2en = AutoTokenizer.from_pretrained("vinai/vinai-translate-vi2en", src_lang="vi_VN")
        self.model_vi2en = AutoModelForSeq2SeqLM.from_pretrained("vinai/vinai-translate-vi2en")
        self.tokenizer_en2vi = AutoTokenizer.from_pretrained("vinai/vinai-translate-en2vi", src_lang="en_XX")
        self.model_en2vi = AutoModelForSeq2SeqLM.from_pretrained("vinai/vinai-translate-en2vi")
    
    def translate_vi2en(self, vi_text: str) -> str:
        input_ids = self.tokenizer_vi2en(vi_text, return_tensors="pt").input_ids
        output_ids = self.model_vi2en.generate(
            input_ids,
            do_sample=True,
            top_k=100,
            top_p=0.8,
            decoder_start_token_id=self.tokenizer_vi2en.lang_code_to_id["en_XX"],
            num_return_sequences=1,
        )
        en_text = self.tokenizer_vi2en.batch_decode(output_ids, skip_special_tokens=True)
        en_text = " ".join(en_text)
        return en_text

    tokenizer_en2vi = AutoTokenizer.from_pretrained("vinai/vinai-translate-en2vi", src_lang="en_XX")
    model_en2vi = AutoModelForSeq2SeqLM.from_pretrained("vinai/vinai-translate-en2vi")

    def translate_en2vi(self, en_text: str) -> str:
        input_ids = self.tokenizer_en2vi(en_text, return_tensors="pt").input_ids
        output_ids = self.model_en2vi.generate(
            input_ids,
            do_sample=True,
            top_k=100,
            top_p=0.8,
            decoder_start_token_id=self.tokenizer_en2vi.lang_code_to_id["vi_VN"],
            num_return_sequences=1,
        )
        vi_text = self.tokenizer_en2vi.batch_decode(output_ids, skip_special_tokens=True)
        vi_text = " ".join(vi_text)
        return vi_text