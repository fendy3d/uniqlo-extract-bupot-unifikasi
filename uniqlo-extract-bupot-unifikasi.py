import re
from re import sub
from decimal import Decimal
import pdfplumber
import pandas as pd
from collections import namedtuple
import datetime
import os
import csv
from enum import Enum

pathToPdfs = os.getcwd()+"/dropPdfHere/"
header_row = [
'Nomor',
'Nama yang pemotong pajak',
'Kota',
'NPWP yang pemotong pajak',
'Objek Pemotongan - Transaksi',
'Dasar Pengenaan Pajak',
'PPh yang Dipotong',
'Tanggal Dokumen',
'Nomor BUPOT', 
'Tanggal yang pemotong pajak',
'Nama yang dipotong pajak', 
'NPWP yang dipotong pajak', 
'Masa Pajak',
'Kode Objek Pajak',
'Tarif Lebih Tinggi 100% (Tidak Memiliki NPWP)',
'Tarif (%)',
'Nama Dokumen',
'Nomor Dokumen',
'Nama Penandatangan',
]
list_of_rows = []
header_line_items_row = ['Nomor Seri Faktur Pajak', 'Number', 'Line Item', 'Line Amount']
list_of_line_items_rows = []
nomor = 0

def reformatNPWP(old_npwp): #adds dash and dot on the npwp
    old_npwp = old_npwp.replace(' ', '') # remove spaces
    new_npwp = ""
    for index in range(len(old_npwp)):
        if (index == 2 or index == 5 or index == 8 or index == 12):
            new_npwp += "."
        elif(index == 9):
            new_npwp += "-"
        new_npwp += old_npwp[index]
    return (new_npwp)

def reformatDate(old_date): # removes dd mm yyyy with hyphen
    # remove the dd,mm,yyyy text
    new_date = old_date.replace(' ', '').replace('dd','-').replace('mm','-').replace('yyyy','')
    return new_date

def reformatAmount(old_amount): #removes decimal and thousandth separator
    new_amount = old_amount.split(',')[0].replace('.','')
    return new_amount

for _, _, files in os.walk(pathToPdfs):
    for filename in files:
        if '.pdf' in filename:
            print ("Extracting " + filename)
            nomor += 1
            pdf = pdfplumber.open(pathToPdfs + filename)
            page = pdf.pages[0] # get the page
            

            number_of_pages = len(pdf.pages)

            if number_of_pages == 1:

                texts = page.extract_text()
                list_of_texts = texts.split('\n')
                counter = 0
                
                for text in list_of_texts:
                    print(str(counter)+ ': '+text)
                    counter += 1

                nomor_bupot = list_of_texts[4].split(': ')[-1].split(' H.4')[0].replace(' ','')
                nama_yang_dipotong_pajak = list_of_texts[10].split(': ')[-1]
                npwp_yang_dipotong_pajak = reformatNPWP(list_of_texts[8].split(': ')[-1]).replace(' ','')
                
                penghasilan_information = list_of_texts[17].split(' ')
                
                if (len(penghasilan_information) == 5):
                    masa_pajak = penghasilan_information[0]
                    kode_objek_pajak = penghasilan_information[1]
                    dasar_pengenaan_pajak = reformatAmount(penghasilan_information[2])
                    tarif_lebih_tinggi_100 = "XXX"
                    tarif = penghasilan_information[3]
                    pph_yang_dipotong = reformatAmount(penghasilan_information[4])
                elif (len(penghasilan_information) == 6):
                    masa_pajak = penghasilan_information[0]
                    kode_objek_pajak = penghasilan_information[1]
                    dasar_pengenaan_pajak = reformatAmount(penghasilan_information[2])
                    tarif_lebih_tinggi_100 = penghasilan_information[3]
                    tarif = penghasilan_information[4]
                    pph_yang_dipotong = reformatAmount(penghasilan_information[5])

                nama_dokumen = list_of_texts[20].split('Nama Dokumen ')[-1].split(' Tanggal')[0]
                nomor_dokumen = list_of_texts[19].split('Nomor Dokumen ')[-1]
                tanggal_dokumen = reformatDate(list_of_texts[20].split('Tanggal ')[-1])

                npwp_yang_pemotong_pajak = reformatNPWP(list_of_texts[29].split(': ')[-1]).replace(' ','')
                nama_yang_pemotong_pajak = list_of_texts[30].split(': ')[-1]
                tanggal_yang_pemotong_pajak = reformatDate(list_of_texts[31].split(': ')[-1])
                nama_penandatangan = list_of_texts[32].split(': ')[-1]

                kota = "XXX"
                object_pemotongan_transaksi = list_of_texts[18].split(': ')[-1]
                

                    
                list_of_rows.append([
                    nomor,
                    nama_yang_pemotong_pajak,
                    kota,
                    npwp_yang_pemotong_pajak,
                    object_pemotongan_transaksi,
                    dasar_pengenaan_pajak,
                    pph_yang_dipotong,
                    tanggal_dokumen,
                    nomor_bupot,
                    tanggal_yang_pemotong_pajak,
                    nama_yang_dipotong_pajak, 
                    npwp_yang_dipotong_pajak, 
                    masa_pajak, 
                    kode_objek_pajak, 
                    tarif_lebih_tinggi_100,
                    tarif,
                    nama_dokumen,
                    nomor_dokumen,
                    nama_penandatangan,
                    ])

            else:
                print("Warning!! " + filename + " has more than one page.")
            
    #Exporting csv
    df = pd.DataFrame(list_of_rows, columns=header_row)
    df.to_csv('output.csv',index=False)

    print("Success! All hail Lord Fendy!")