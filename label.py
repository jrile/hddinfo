from fpdf import FPDF
from barcode.writer import ImageWriter
import barcode
import time

class Label():


    def label(self, serial, f_list, username):
        pdf = FPDF()
        pdf.add_page()
    # put barcode here
        self.createBarcode(serial)
        pdf.image('barcode.png', 15, 13, 50)
        pdf.set_font('Arial', 'B', 15)
        pdf.cell(80)
        pdf.cell(60, 10, serial, 0, 2)
        pdf.ln(20)
        pdf.cell(30, 15, "Added on " + time.strftime("%c") + " by " + username, ln=2)
        pdf.cell(30, 10, "Contains:", ln=2)
        
    # print folder directory
        pdf.set_font('Times', '', 12)
        for f in f_list:
            pdf.cell(0, 5, f, 0, 1)
            
        pdf.output('label.pdf')
        
    def createBarcode(self, serial):
        code39 = barcode.get_barcode_class('code39')
        c39 = code39(str(serial), writer=ImageWriter())
        fullname = c39.save('barcode')
    

if __name__ == "__main__":
    l = Label()
    directory = ["test1", "test2", "test3", "test4"]
    l.label("TESTINGBARCODES", directory, "jrile")
