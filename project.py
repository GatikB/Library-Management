import mysql.connector as sqlctr
import sys
from datetime import datetime

mycon = sqlctr.connect(host='localhost', user='root', password='enter_own_passwd')
if mycon.is_connected():
    print('\n')
    print('Successfully connected to localhost')
else:
    print('Error while connecting to localhost')
cursor = mycon.cursor()
cursor.execute("create database if not exists new_library")
cursor.execute("use new_lib")
cursor.execute("create table if not exists books(sid int(10) primary key,name varchar(255) not null,quantity int(20),rate int(20),unique(name))")
cursor.execute("create table if not exists borrower(sid int(10) primary key,borrower_name varchar(255),book_lent varchar(255),date date,contact_no bigint)")

def command(st):
    cursor.execute(st)


def fetch():
    data = cursor.fetchall()
    for i in data:
        print(i)

# function to show both tables

def all_data(tname):
    li = []
    st = 'desc '+tname
    command(st)
    data = cursor.fetchall()
    for i in data:
        li.append(i[0])
    st = 'select * from '+tname
    command(st)
    print('\n')
    print('-------ALL_DATA_FROM_TABLE_'+tname+'_ARE-------\n')
    print(tuple(li))
    fetch()

# function to show borrower table

def detail_burrower(name,contact):
    tup=('sid','borrower_name','book_lent','date','contact_no')
    print('\n---Details for borrower '+name+'---\n')
    print(tup)
    st='select * from borrower where borrower_name like "{}" and contact_no={}'.format(name,contact)
    command(st)
    fetch()

# function to find days between borrowed date and return date (7 days borrowing is free after that money is charged)
def days_between(d1, d2):
    d1 = datetime.strptime(d1, "%Y-%m-%d")
    d2 = datetime.strptime(d2, "%Y-%m-%d")
    global days
    days=abs((d2 - d1).days) - 7

# Calculates fine

def price_book(days,book_name):
    st1 = 'select rate from books where name="{}"'.format(book_name)
    command(st1)
    data = cursor.fetchall()
    for i in data:
        global t_price
        t_price=int(i[0])*days
        print('No. of days {} book is kept : {}'.format(book_name,days))
        print('Price per day for book {} is Rs.{}'.format(book_name,i[0]))
        print('Total fare for book '+book_name +'-',t_price)

# function to lend a book

def lend():
    flag='True'
    while flag=='True':
        print('\n___AVAILABLE BOOKS___\n')
        st0 = 'select name from books where quantity>=1'
        command(st0)
        fetch()
        st1='select max(sid) from borrower'
        command(st1)
        data_sn=cursor.fetchall()

        # data_sn will contain the maximum serial number so that another entry can be added as sn + 1. i[0] contains the maximum sn value. is None checks if the table is empty or not. If empty it uses 0
        for i in data_sn:
            if i[0] is None:
                sid=1
            else:
                sid=i[0]+1        
        book_lent=str(input('Enter name of book from above list : '))
        borrower_name=str(input('Enter Borrower Name : '))
        date=str(input('Enter date (YYYY-MM-DD) : '))
        contact=int(input('Enter contact no. : '))
        st_insert='insert into borrower values({},"{}","{}","{}",{})'.format(sid,borrower_name,book_lent,date,contact)
        command(st_insert)
        st_quantity='select quantity from books where name="{}"'.format(book_lent)
        command(st_quantity)
        data_quantity=cursor.fetchall()
        for quantity in data_quantity:
            qty=quantity[0]-1
        st_dec='update books set quantity={} where name="{}"'.format(qty,book_lent)
        command(st_dec)
        dec=str(input('Do you want to add more records (Y/N) : '))
        if dec.upper=="Y":
            flag= 'True'
        else:
            flag='False'
        

def borrowers():
    print('\n\n___OPTIONS AVAILABLE___\n\nEnter 1 : To Show detail of all borrowers \nEnter 2 : To check detail of a particular borrower \nEnter 3 : To calculate total fine of a borrower \nEnter 4 : To go Back \nEnter 5 : To commit all the changes and exit')
    dec = input('enter your choice-')
    if dec=='1':
        all_data('borrower')
    elif dec=='2':
        name = str(input('\nenter borrower name-'))
        contact = str(input('enter borrower contact no.-'))
        detail_burrower(name,contact)
    elif dec=='3':
        tfine()
    elif dec=='4':
        action_list()
    elif dec=='5':
        close()
    borrowers()

# function to check fine

def tfine():
    name=str(input('\nEnter borrower name : '))
    contact=input('Enter borrower contact_no : ')        
    detail_burrower(name, contact)
    st1 = 'select book_lent from borrower where borrower_name ="{}" and contact_no={}'.format(name,contact)
    command(st1)
    data=cursor.fetchall()
    for i in data:
        book_name=i[0]
        st2 = 'select date from borrower where borrower_name="{}" and book_lent="{}"'.format(name,book_name)
        command(st2)
        data1=cursor.fetchall()
        for date in data1:
            date_taken=date[0]
            date_return = str(input('\nEnter returning date for book "{}" (YYYY-MM-DD) , Press ENTER to skip-'.format(book_name)))
            while date_return!='':
                days_between(str(date_return),str(date_taken))
                price_book(days,i[0])
                print('\nEnter Y : If Rs.{} is paid and book is returned.\nEnter N : If fare is not paid and book is not returned.'.format(t_price))
                dec=str(input('Enter (Y?N) : ')) 
                if dec.upper()=="Y":
                    st= 'select sid , quantity from books where name ="{}"'.format(i[0])
                    command(st)
                    data2=cursor.fetchall()
                    for price in data2:
                        update('books', 'quantity',price[1]+1,price[0])
                    st_del = 'delete from borrower where borrower_name="{}" and book_lent="{}"'.format(name,book_name)
                    command(st_del)
                    break
                else:
                    print("\n\nPLEASE PAY THE FARE AND RETURN BOOK AFTER READING.\n\n")
                    break
        

def insert():
    flag = 'true'
    while flag=='true':
        licol=[]
        li1=[]
        li_val=[]
        command('desc books')
        data=cursor.fetchall()
        for i in data:
            licol.append(i[0])   
        command('select max(sid) from books')
        dta=cursor.fetchall()
        
        # same concept as lend
        
        for j in dta:
            if j[0] is None:
                li_val.append(1)
            else:
                li_val.append(j[0]+1)
        for k in range(1,4):
            val = str(input('Enter '+licol[k]+'-'))
            li_val.append(val)
        li1.append(tuple(li_val))
        values = ', '.join(map(str, li1))
        st1 = "INSERT INTO books VALUES {}".format(values)
        command(st1)
        all_data('books')
        print('\n')
        print("\nDATA INSERTED SUCCESSFULLY\n")
        dec = str(input('Do u want to insert more data?(Y/N)-'))
        if dec.upper() == "Y":
            flag='true'
        else:
            flag='false' 
    action_list()

def update(tname,col1,post_value,pre_value):
    st = str('update %s set %s=%s where sid=%s') % (tname, col1, "'%s'", "'%s'") % (post_value, pre_value)
    command(st)
    all_data(tname)
    print('\nVALUE UPDATED SUCCESSFULLY')
     

def close():
    mycon.commit()
    mycon.close()
    if mycon.is_connected():
        print('still connected to localhost')
    else:
        print('\n\nconnection closed successfully.')
    sys.exit()


def action_list():
    print('\n')
    print('#### LIBRARY MANAGEMENT SYSTEM ####\n\nEnter 1 : To View details of all available Books\nEnter 2 : To check detail of a particular book\nEnter 3 : To lend a book \nEnter 4 : To add new books in list\nEnter 5 : To view details of borrowers \nEnter 6 : To commit all changes and exit')
    dec = input('\nenter your choice-')
    if dec == '1':
        all_data('books')
    elif dec=='2':
        tup=('sid','name','quantity','rate')
        tup1 = ('sid', 'borrower_name', 'book_lent', 'contact_no')
        in1=str(input('enter keywords for a book'))
        print('\n___ALL DATA OF BOOKS HAVING "{}" IN THEIR NAME FROM BOTH TABLE____'.format(in1))
        st =str('select * from books where name like "{}"'.format('%'+in1+'%'))
        st1=str('select * from borrower where book_lent like "{}"'.format('%'+in1+'%'))
        print('\n__DATA FROM TABLE BOOKS__\n')
        command(st)
        print(tup)
        fetch()
        print('\n__DATA FROM TABLE BORROWER__\n')
        command(st1)
        print(tup1)
        fetch()
        print()
    elif dec == '3':
        lend()
    elif dec=='4':
        insert()
    elif dec=='5':
        borrowers()
    elif dec=='6':
        close()
    action_list()


action_list()
