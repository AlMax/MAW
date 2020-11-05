import ctypes
import os
import time
import datetime
import xlsxwriter
from lxml import etree
from io import StringIO
import traceback
import openpyxl
from string import ascii_uppercase
import win32com.client as win32

currentDirectory = os.getcwd()
excel = win32.gencache.EnsureDispatch('Excel.Application')
wb = excel.Workbooks.Open(currentDirectory + "\Log.xlsx")
ws = wb.Worksheets("Sheet1")
ws.Columns.AutoFit()
wb.Save()
excel.Application.Quit()

today = datetime.date.today().strftime("%d-%m-%Y")
now = datetime.datetime.now().strftime("%H.%M.%S")

def creaCartelle(nomi_cartelle):
    """Dato in input un array di stringe, creerà delle cartelle con le relative stringhe.
    Ritoenrà infine una stringa con gli esiti delle varie creazioni"""
    if isinstance(nomi_cartelle,list):
        for directory in nomi_cartelle:
            try:
                os.mkdir(directory)
                logOperazioni("Cartella " + directory + " creata.\n")
            except OSError as erroreCartella:
                logOperazioni("\tERRORE nel creare la cartella --> " + str(erroreCartella) + "\n")
    else:
        try:
            os.mkdir(nomi_cartelle)
            logOperazioni("Cartella " + nomi_cartelle + " creata.\n")
        except OSError:
            logOperazioni("\tERRORE nel creare la cartella " + nomi_cartelle + ", probabilmente esiste già.\n")

def logOperazioni(log):
    """Scrittura dei log su apposito file"""
    fileLog = open("Log.txt", "a")
    if log == "":
        if os.stat("Log.txt").st_size == 0:
            logOperazioni("Scorrere in basso per avere i log piu' recenti.\nI Log vengono registrati ogni volta che viene lanciato il programma.")
        logOperazioni("\n\n\nI seguenti Log fanno riferimento al giorno " + today + " alle ore " + now + "\n")
    fileLog.write(log)
    fileLog.close()

def logExcel(colonna1, colonna2, colonna3, colonna4, colonna5, colonna6):
    workbook = xlsxwriter.Workbook('Log.xlsx')
    worksheet = workbook.add_worksheet()

    row = 0

    for cella1 in colonna1:
        worksheet.write(row, 0, cella1)
        row += 1

    row = 0

    for cella2 in colonna2:
        worksheet.write(row, 1, cella2)
        row += 1

    row = 0

    for cella3 in colonna3:
        worksheet.write(row, 2, cella3)
        row += 1

    row = 0

    for cella4 in colonna4:
        worksheet.write(row, 3, cella4)
        row += 1

    row = 0
    
    for cella5 in colonna5:
        worksheet.write(row, 4, cella5)
        row += 1

    row = 0
    
    for cella6 in colonna6:
        worksheet.write(row, 5, cella6)
        row += 1

    sistemaColonneExcel('Log.xlsx')
    workbook.close()

def sistemaColonneExcel(excelName):
    wb = openpyxl.load_workbook(filename = excelName)        
    worksheet = wb.active

    for col in worksheet.columns:
        max_length = 0
        column = col[0].column_letter # Get the column name
        # Since Openpyxl 2.6, the column name is  ".column_letter" as .column became the column number (1-based) 
        for cell in col:
            try: # Necessary to avoid error on empty cells
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = str((max_length + 2) * 20)
        worksheet.column_dimensions[column].width = adjusted_width
        print("ok")

def verifica_XML_XSD(filename_xml, filename_xsd):
    txt_conclusivo = ""

    # open and read schema file
    with open(filename_xsd, 'r') as schema_file:
        schema_to_check = schema_file.read()

    # open and read xml file
    with open(filename_xml, 'r') as xml_file:
        xml_to_check = xml_file.read()

    xmlschema_doc = etree.parse(StringIO(schema_to_check))
    xmlschema = etree.XMLSchema(xmlschema_doc)

    try:
        doc = etree.parse(StringIO(xml_to_check))
        txt_conclusivo += "Sintassi XML OK; \n"

    # check for file IO error
    except IOError as ioError:
        txt_conclusivo += "ERRORE File non valido: " + str(ioError) + "; \n"

    # check for XML syntax errors
    except etree.XMLSyntaxError as err:
        txt_conclusivo += "ERRORE Sinstassi XML: " + str(err) +"; \n"
        logOperazioni("\n\t\tERRORE Sinstassi XML: " + str(err.error_log))

    except Exception as errore:
        txt_conclusivo += "ERRORE Eccezione Sintassi XML: " + str(errore) + "; \n"
        logOperazioni("\n\t\tERRORE Eccezione Sintassi XML: " + str(errore))


    # validate against schema
    try:
        xmlschema.assertValid(doc)
        txt_conclusivo += "Schema XML Valido; \n"

    except etree.DocumentInvalid as err:
        txt_conclusivo += "ERRORE schema XML non valido: " + str(err) + "; \n"
        logOperazioni("\n\t\tERRORE schema XML non valido: " + str(err.error_log))

    except:
        txt_conclusivo += "ERRORE sconosciuto con lo schema: " + str(traceback.format_exc()) + "; \n"
        logOperazioni("\n\t\tERRORE sconosciuto con lo schema: " + str(traceback.format_exc()))

    xml_file = etree.parse(filename_xml)
    xml_validator = etree.XMLSchema(file=filename_xsd)

    is_valid = xml_validator.validate(xml_file)

    txt_conclusivo += "L'XML rispetta la struttura definita nell' XSD? " + str(is_valid)
    logOperazioni("\n\t\tL'XML rispetta la struttura definita nell' XSD? " + str(is_valid))

    if txt_conclusivo == "Sintassi XML OK; \nSchema XML Valido; \nL'XML rispetta la struttura definita nell' XSD? True":
        return "Convalidazione Corretta"
    return txt_conclusivo

def Mbox(title, text):
    """Messaggi Pop-up"""
    return ctypes.windll.user32.MessageBoxW(0, text, title, 1)

