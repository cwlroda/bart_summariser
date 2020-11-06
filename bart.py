import os
import math
import time
import json
import torch
from transformers import BartTokenizer, BartForConditionalGeneration

with open('config.json', 'r') as file:
    config = json.load(file)
data_path = config['paths']['data']

print(">>> Initialising model")
model_path = config['paths']['model']
model = BartForConditionalGeneration.from_pretrained(model_path, output_past=True)
tokenizer = BartTokenizer.from_pretrained(model_path, output_past=True)

if torch.cuda.is_available(): device = torch.device('cuda')
else: device = torch.device('cpu')

def summarise(path):
    try:
        with open(path) as f:
            article = f.read()
        
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
            
            tokens = tokenizer.encode(article,
                                      return_tensors='pt',
                                      truncation=True,
                                      max_length=1024
                                     ).to(device)
            
            summary_length = config['params']['summary_length']
            num_words = math.ceil(total_words * summary_length) if summary_length else config['params']['num_words']
            num_beams = config['params']['num_beams']
            min_length_buffer = config['params']['min_length_buffer']
            max_length_buffer = config['params']['max_length_buffer']
            no_repeat_ngram_size = config['params']['no_repeat_ngram_size']
            repetition_penalty = config['params']['repetition_penalty']
            length_penalty = config['params']['length_penalty']
            early_stopping = config['params']['early_stopping']
            do_sample = config['params']['do_sample']
            top_k = config['params']['top_k']
            top_p = config['params']['top_p']
            temperature = config['params']['temperature']
            use_cache = config['params']['use_cache']
            num_return_sequences = config['params']['num_return_sequences']
            
            min_length = num_words - min_length_buffer
            max_length = num_words + max_length_buffer
            
            if summary_length:
                print(">>> Generating summary at {:.1%} ({} words)".format(summary_length, num_words))
            else:
                print(">>> Generating summary with {} words".format(num_words))
            
            start = time.time()
            summary_ids = model.generate(tokens,
                                         num_beams=num_beams,
                                         no_repeat_ngram_size=no_repeat_ngram_size,
                                         repetition_penalty=repetition_penalty,
                                         length_penalty=length_penalty,
                                         min_length=min_length,
                                         max_length=max_length,
                                         early_stopping=early_stopping,
                                         do_sample=do_sample,
                                         top_k=top_k,
                                         top_p=top_p,
                                         temperature=temperature,
                                         use_cache=use_cache,
                                         num_return_sequences=num_return_sequences
                                        )
            
            output = [tokenizer.decode(i,
                                       skip_special_tokens=True,
                                       clean_up_tokenization_spaces=False
                                      ) for i in summary_ids]
            end = time.time()
            print(">>> Time taken: {:.2f}s".format(end - start))
            return output[0]
            
        else:
            return 'Empty input'
    
    except Exception as ex:
        print(str(ex))

def run_all():
    dir = data_path + config['input']['folder']
    files = os.listdir(dir)
    article_num = 1
    
    titles_file = data_path + config['input']['titles']
    urls_file = data_path + config['input']['urls']
    titles = open(titles_file).readlines()
    urls = open(urls_file).readlines()
    
    for file, title, url in zip(files, titles, urls):
        try:
            path = dir + file
            article_name = "summary_{:04d}".format(article_num)
            
            print(">>> Summary {}".format(article_num))
            output = summarise(path)
            
            out_dir = data_path + config['output']['folder']
            filename = "{}{}.txt".format(out_dir, article_name)
            with open(filename, 'w') as f:
                f.write(title)
                f.write(url+'\n')
                f.write(output)
            
            print(">>> Summary {} has been saved to: {}".format(article_num, filename))
            
            article_num += 1
            
        except:
            article_num += 1
            continue

if __name__ == '__main__':
    model.to(device)
    model.eval()
    
    if config['summarisation']['run_all']:
        run_all()
        
    else:
        path = data_path + config['input']['file']
        output = summarise(path)
        
        if config['summarisation']['write_to_file']:
            filename = data_path + config['output']['file']
            with open(filename, 'w') as f:
                f.write(output)
            
            print(">>> Summary has been saved to: {}".format(filename))
        
        else:
            print(output)