#from asyncore import write
import canopen
import csv
import sys

class ind:
     #classe para conseguir guardar a string com o valor em hexa bem como o index e subindex guardados para conseguir pesquisar de maneira mais simples
    def __init__(self, string) -> None:
        self.index=string[2:6]
        self.sub=string[6:8]
        self.all=string
        self.name=''
        self.tpdono=0


##
def readdic():
    f=open('/Users/goncalovieiradasilva/Desktop/Tecnico/TESE/codigo/out.csv', 'r')
    index=[]
    subindex=[]
    name=[]
    scale=[]
    unit=[]
    csvreader = csv.DictReader(f)
    for row in csvreader:
    
        index.append(row["Index"].lower())      #os dois lowers sao usados para que depois mais a frente a comparação entre estes nao dê bronca
        subindex.append(row["subIndex"].lower())
        name.append(row["Name"])
        scale.append(row["Scale"])
        unit.append(row["Unit"])
    
    for x in subindex:
        if x == '':
            aux = subindex.index(x)
            subindex[aux] = index[aux] + 'sub0'
    f.close()
    return index,subindex,name,scale,unit

def createNetwork(dcfFile):
	network = canopen.Network()
	with open(dcfFile, encoding="latin1") as file:
		return [network,network.add_node(1, file)]

def getDictionaryObject(node):
	return node.object_dictionary

def fetchpdo(od):
    # receives the node dictionary and finds/stores the TPDO's and saves them into a list
    # input: node
    # output: tpdo_list 
    tpdo_list = []
    tpdo_str = 'Transmit PDO mapping parameters'
    
    
    rpdo_list = []
    rpdo_str = 'Receive PDO mapping parameters'
    

    for obj in od.values():
        if tpdo_str in obj.name:
            tpdo_list.append(obj)
        if rpdo_str in obj.name:
            rpdo_list.append(obj)
	
    return tpdo_list, rpdo_list

##

def maps(pdos):
    #
    #input: lista com os pdos
    #output: tabela com os indices dos mapas de cada pdo
    mapa =[]
    for x in pdos:
        mapa.append(x.subindices)
    return mapa

def info (indices_maps):
    #quero tirar a informação dos mapas (qual o parametro naquele mapa)
    #input: tabela com os indices dos mapas de cada pdo
    #output: acaba por ser uma restruturação do input.  ja nao me lembro do porque mas se usar so a variavel de input a função seguinte nao funciona
    infos = []
    for h in indices_maps:
        col= []
        for z in h:
            col.append(h[z])
        infos.append(col)
    return infos

def getRawindex (pdo):
     #para umcaso mas vou tirar os valores raw de um dos mapas de modo a depois pesquisar os mapas
     # output: lista com os indices e subs de um pdo, guardado numa classe criada acima
    val_hex=[]
    aux=[]
    for x in pdo:
        if x.name != 'Number of mapped objects':
            #val.append(int(x.value_raw,16))
            aux=ind(x.value_raw)
            val_hex.append(aux)

    return val_hex 

#def norm (val):
    # o objectivo é formatar os indexes para conseguir pesquisar no dcf os parametros a ler no escrever nos tpdo
    indexes= []
    sub='sub'
    aux2=[]
    
    for x in val:
        if x[6:8] != 0:
             aux_index= x[2:6]
             aux_subindex= x[6:8]
        aux2.append(aux_index+sub+aux_subindex)
    for y in aux2:
        if y[7]=='0':
            aux= y[0:7]+y[8:]  
        indexes.append(aux)
    return indexes

def fetchname(od,indexes):
#ja tenho os indices dos tpdos e agora é ir buscar ao dicionario
#input: dicionario + os indices a pesquisar
#output: lista de entrada, indexes, mas completo com os nomes
    lista = []
    aux=[]
    for x in indexes:
        for obj in od.values():
                if int(x.index,16) == obj.index:
                    lista.append(obj)       #aqui estou a obter os nomes dos index, agora com a posição destes posso pesquisar dentro de cada com o sub index e fico com o nome
    for y in indexes:
         z=int(y.index,16)
         aux.append(od[z][int(y.sub,16)].name)
    for xx in range(len(aux)):
         indexes[xx].name=aux[xx]  
    return indexes



     # to do:


if __name__ == "__main__":
    doc_write = "test1.txt"

    [network,node] = createNetwork('/Users/goncalovieiradasilva/Desktop/Tecnico/TESE/codigo/viena_30_06_2022_2.dcf')
    od = getDictionaryObject(node)
    [tpdo_list, rpdo_list] = fetchpdo(od)


    
    mapas = maps(tpdo_list)

    infos = info(mapas)
    tpdo1_hex = getRawindex(infos[0])
    tpdo1info = fetchname(od,tpdo1_hex)
    ##
    #para a interface será ler a informação que esta no pdo ainda na função info e mandar juntamente o nome extraido
    #preciso de começar a ver os sdo e como é que faço alteração no dicionário, o acesso pode ser como apresentado em baixo, ja tenho também uma lista com os nomes de todos os parametros
    #integrar a lista com as escalas 
    
    
    ##
    x=node.sdo['S-Curve Control']['Ramp change delay speed'] 
    print(x.name)
    
    onem = mapas [1]
   
