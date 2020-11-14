import sys
from nltk.corpus import stopwords

class RougeScoreCalculator():
    def __init__(self):
        self.punc = '''!()[]{};:'"\,<>./?#^&*_~'''
        self.stop = stopwords.words('english')
    
    def calculate(self, gSum, rSum):
        for c in gSum:
            if c in self.punc:
                gSum = gSum.replace(c, '')
        
        for c in rSum:
            if c in self.punc:
                rSum = rSum.replace(c, '')
        
        gList = gSum.split()
        rList = rSum.split()
        gDict = {}
        rDict = {}
        
        for word in gList:
            word = word.lower()
            
            if word not in self.stop:
                if word not in gDict:
                    gDict[word] = 1
                else:
                    gDict[word] += 1
                    
        for word in rList:
            word = word.lower()
            
            if word not in self.stop:
                if word not in rDict:
                    rDict[word] = 1
                else:
                    rDict[word] += 1

        gCount = 0
        rCount = len(rDict)
        
        for gKey in sorted(gDict.keys()):
            for rKey in sorted(rDict.keys()):
                if gKey == rKey:
                    gCount += min(gDict[gKey], rDict[rKey])
                    break
                
        return float(gCount/rCount)

if __name__ == "__main__":
    gFile = sys.argv[1]
    rFile = sys.argv[2]
    
    with open(gFile, 'r') as f:
        lines = f.read().splitlines()
        gSum = lines[3]
        
    with open(rFile, 'r') as f:
        lines = f.read().splitlines()
        rSum = lines[0]
    
    calc = RougeScoreCalculator()
    print("ROUGE Score: {:.2%}".format(calc.calculate(gSum, rSum)))

