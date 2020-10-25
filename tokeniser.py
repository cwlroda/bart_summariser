import os
import json
import xlsxwriter
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize

with open('config.json', 'r') as file:
    config = json.load(file)
data_path = config['paths']['data']

def tokenise():
    dir = data_path+config['input']['folder']
    files = os.listdir(dir)
    
    article_num = 1
    
    for i in files:
        path = dir + i
        file = open(path)
        article = file.read()
        file.close()
        
        article_name = "tokens_{:04d}".format(article_num)
        print(">>> Tokenising: {}/{}".format(article_num, len(files)), end='\r')
        tokens = word_tokenize(article)
        tokens = nltk.pos_tag(tokens)
        
        out_dir = data_path+config['output']['folder']
        filename = "{}{}.xlsx".format(out_dir, article_name)
        workbook = xlsxwriter.Workbook(filename)
        worksheet = workbook.add_worksheet()
        
        row = 0
        col = 0
        
        for word, pos in tokens:
            worksheet.write(row, col, word)
            worksheet.write(row, col+1, pos)
            row += 1
            
        workbook.close()
        print(">>> Article {} tokens have been saved to: {}".format(article_num, filename))
        article_num += 1

if __name__ == '__main__':
    nltk.download('averaged_perceptron_tagger')
    tokenise()

