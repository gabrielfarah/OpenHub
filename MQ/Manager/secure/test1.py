import os

#Prueba
#Nombre que identifica la pruena
#Tipo de retorno de la prueba
#  1= yes(1) - no(0) , 2= 1-10
#addData En caso de necesitar informacion extra de la db
# true(1)/false(0)

name = "numero de as en el codigo"
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



    return count