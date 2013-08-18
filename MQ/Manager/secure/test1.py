import os

#Prueba
#Nombre que identifica la pruena
#Tipo de retorno de la prueba
#  1= yes(1) - no(0) , 2= 1-10
#addData En caso de necesitar informacion extra de la db
# true(1)/false(0)

name = "numero de bs en el codigo"
type = 1


def runTest(id, path, db):
    print "secure 1"
    print 'reading files'
    #numbres of a
    count = 0
    letter='a'
    files = [os.path.join(dirpath, f)
        for dirpath, dirnames, files in os.walk(path)
        for f in files]
        # for f in files if f.endswith('.txt')]
    for archivo in files:
        print archivo
        count += countLettersFiles(archivo,letter)
    return count

def countLettersFiles(path,letter):
    count=0
    with open(path, 'r') as infile:
        data = infile.read()
        for c in data:
            if c == letter:
                count += 1
    return count