import extracao as ext

local_arquivo = r'/home/fanty/Documentos/GitHub/Policia-Civil-Extracao/Artigo/Grafo/DECCC.csv' #input('Digite o local do arquivo: ')
nome_coluna_relatos = 'relato' #input('Digite o nome da coluna relato: ')

df = ext.run(local_arquivo=local_arquivo, nome_coluna_relatos = nome_coluna_relatos)
print(df)
df.to_csv("BOS_cincoK.xlsx", index=False)



# class Extrair:
#     def __init__(self, local_arquivo:str, nome_coluna_relatos:str):
#         self.file_path:str = local_arquivo
#         self.col_name:str = nome_coluna_relatos

#     def toExcel(self, filename:str, index:bool=True):
#         try:
#             df = ext.run(local_arquivo=self.file_path, nome_coluna_relatos=self.col_name)
#             df.to_excel(filename, index=index)
#         except Exception as e:
#             return e
        
#     def toCsv(self, filename:str, index:bool=True):
#         try:
#             df = ext.run(local_arquivo=self.file_path, nome_coluna_relatos=self.col_name)
#             df.to_csv(filename, index=index)
#         except Exception as e:
#             return e
        


# Extrair("/home/fanty/Documentos/GitHub/Policia-Civil-Extracao/Artigo/Grafo/DECCC.csv", "relato").toCsv()