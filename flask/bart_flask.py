import math
import time
import json
import torch
from transformers import BartTokenizer, BartForConditionalGeneration

class Bart():
    def __init__(self):
        file = open('config.json', 'r')
        self.config = json.load(file)
        file.close()

        print(">>> Initialising model")
        model_path = self.config['paths']['model']
        self.model = BartForConditionalGeneration.from_pretrained(model_path, output_past=True)
        self.tokenizer = BartTokenizer.from_pretrained(model_path, output_past=True)

        if torch.cuda.is_available(): self.device = torch.device('cuda')
        else: self.device = torch.device('cpu')

    def summarise(self, article):
        try:
            article_words = article.split()
            total_words = len(article_words)
            print(">>> Article length: {} words".format(total_words))
            
            if article != '':
                """ # check article tokens
                text = tokenizer.tokenize(article)
                for i in text:
                    print(i)
                print(len(text))
                sys.exit(0) """
                
                tokens = self.tokenizer.encode(article,
                                        return_tensors='pt',
                                        truncation=True,
                                        max_length=1024
                                        ).to(self.device)
                
                summary_length = self.config['params']['summary_length']
                num_words = math.ceil(total_words * summary_length) if summary_length else self.config['params']['num_words']
                num_beams = self.config['params']['num_beams']
                min_length_buffer = self.config['params']['min_length_buffer']
                max_length_buffer = self.config['params']['max_length_buffer']
                no_repeat_ngram_size = self.config['params']['no_repeat_ngram_size']
                repetition_penalty = self.config['params']['repetition_penalty']
                length_penalty = self.config['params']['length_penalty']
                num_return_sequences = self.config['params']['num_return_sequences']
                
                min_length = num_words - min_length_buffer
                max_length = num_words + max_length_buffer
                
                if summary_length:
                    print(">>> Generating summary at {:.1%} ({} words)".format(summary_length, num_words))
                else:
                    print(">>> Generating summary with {} words".format(num_words))
                
                start = time.time()
                summary_ids = self.model.generate(tokens,
                                            num_beams=num_beams,
                                            no_repeat_ngram_size=no_repeat_ngram_size,
                                            repetition_penalty=repetition_penalty,
                                            length_penalty=length_penalty,
                                            min_length=min_length,
                                            max_length=max_length,
                                            num_return_sequences=num_return_sequences
                                            )
                
                output = [self.tokenizer.decode(i,
                                        skip_special_tokens=True,
                                        clean_up_tokenization_spaces=False
                                        ) for i in summary_ids]
                end = time.time()
                print(">>> Time taken: {:.2f}s".format(end - start))
                return output[0]
                
            else:
                return 'Empty input'
        
        except Exception as ex:
            print("Error"+str(ex))

    def run(self):
        self.model.to(self.device)
        self.model.eval()
        
        article = self.config['input']['text']
        output = self.summarise(article)
            
        return output

